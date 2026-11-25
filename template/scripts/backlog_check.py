# test-kitchen: no-trace (this file describes TODO markers and example tickets; its text is not trace)
"""Validate the backlog and requirements, report coverage, gaps, refinement findings, and test debt.

Reads `kitchen.yml`, `docs/requirements/*.md`, `docs/decision-log.md`, every ticket under
`backlog/`, and the project's test and code files (the `tests` and `code` globs), and
checks them against the conventions in `backlog/README.md`:

- tickets: parseable frontmatter with the required fields and allowed values; ID matching
  type, file name, and epic; existing epic, `blocked_by`, `fixes`, and `source_reqs`
  targets; no `blocked_by` cycles; release slices (when `releases` is set) in order with
  their blockers; criteria in the `- AC<n>: …` form, numbered upwards; every `…/AC<n>`
  reference naming a live criterion; readiness (owner, answered open questions, a live
  criterion, a release); a `done` ticket has no unfinished blocker;
- trace: test tags (`[US-PAY-03/AC2]` or `us_pay_03_ac2`) name a live criterion of a
  started ticket; a `done` story has a tagged test for every live criterion (adopted
  stories report missing ones as test debt instead); every TODO/FIXME/XXX/HACK names a
  ticket; every `DEC-…` mention exists (decided ones are listed for revisiting);
- coverage: every requirement that is not superseded is cited by a story or task that is
  not deferred (requirements of deferred epics excepted).

Usage (from any directory in the repository):

    python3 scripts/backlog_check.py                 # validate; ERROR lines exit 1, WARN lines don't
    python3 scripts/backlog_check.py --strict        # uncovered requirements are errors
    python3 scripts/backlog_check.py --pr-body=FILE  # also check a change-request description (or a delivery record)
    python3 scripts/backlog_check.py --gaps          # what keeps the product from being fully defined; exit 1 if any
    python3 scripts/backlog_check.py --refine        # refinement findings (the script part); exit 0
    python3 scripts/backlog_check.py --test-debt     # adopted done stories' criteria with no tagged test; exit 0
    python3 scripts/backlog_check.py --self-test     # checks itself on a temporary fixture; exit 0/1

Every finding is one line: a fixed label (`ERROR`, `WARN `, `GAP  `, `REFINE`, `DEBT `),
then `<file or ID>: <message>`. Requires PyYAML.
"""
from __future__ import annotations

import datetime
import re
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kitchen_lib as kl  # noqa: E402

TYPES = tuple(kl.PREFIX)  # epic, story, task, decision, spike
STATUS = ("draft", "ready", "in-progress", "done", "deferred")
# Statuses that claim readiness: the ticket must be complete enough to build.
STARTED = {"ready", "in-progress", "done"}
ASSIGNEE = ("human", "agent", "either")
PRIORITY = ("high", "normal", "low")
REQUIRED = ("id", "type", "title", "owner", "assignee_type", "status")
REQUIRED_NON_EPIC = ("epic", "source_reqs", "blocked_by")
KNOWN_FIELDS = set(REQUIRED + REQUIRED_NON_EPIC) | {
    "priority", "release", "refined", "adopted", "hotfix", "fixes", "code"}
# Kinds of ticket that hold acceptance criteria.
WITH_CRITERIA = ("story", "task")

AC_LINE = re.compile(r"^- AC(\d+):[ \t]*(.*?)\s*$")
# A removed criterion keeps its number forever: `- AC4: (removed 2026-11-24, <reason or ticket>)`.
REMOVED = re.compile(r"^\(removed \d{4}-\d\d-\d\d, .+\)$")
# A criterion of this ticket named in an open question's interim behavior ("Until decided: AC3 …").
OWN_AC = re.compile(r"(?<![/\w])AC(\d+)\b")
TODO = re.compile(r"\b(?:TODO|FIXME|XXX|HACK)\b")
OBSERVED = re.compile(r"^\(observed in code\)")
SUPERSEDED = re.compile(rf"^\(superseded (\d{{4}}-\d\d-\d\d) by ({kl.CODE}-R\d{{2,}})\)")
LOG_REF = re.compile(r"\bLog: (.+?)\.?\s*$")
# Change-request description sections checked here, and what each bullet must point to.
CR_SECTIONS = {"Gaps found": "ticket", "Decisions": "log", "Platform changes": "log"}
# With `self_contained_tickets: true`, tickets are read outside the repository (a tracker,
# another team), so a body may not link to repository files or name repository documents.
REPO_LINK = re.compile(r"\]\((?!https?://|mailto:|#)[^)]+\)")
REPO_NAME = re.compile(r"(?<![\w.-])(?:docs|backlog|playbooks|scripts)/|\bdecision[- ]log\b"
                       r"|(?<![\w/.-])[\w./-]+\.md\b|\bkitchen\.(?:yml|lock)\b", re.I)


@dataclass
class Requirement:
    id: str
    text: str
    rel: str
    observed: bool = False
    superseded_by: Optional[str] = None


@dataclass
class Ticket:
    id: str
    type: str
    rel: str  # repository-relative path, '/'-separated
    fm: dict
    body: str
    criteria: Dict[int, bool] = field(default_factory=dict)  # number -> live

    @property
    def status(self):
        return self.fm.get("status")

    @property
    def title(self):
        return str(self.fm.get("title") or "")

    @property
    def branch(self):
        """The ticket's branch: its file name without `.md`, lowercased."""
        return Path(self.rel).stem.lower()

    @property
    def folder(self):
        return str(Path(self.rel).parent.as_posix())

    @property
    def code(self):
        p = kl.parse_ticket_id(self.id)
        return p[1] if p else None

    def live(self):
        return sorted(n for n, ok in self.criteria.items() if ok)

    def list(self, key):
        v = self.fm.get(key)
        return [str(x) for x in v] if isinstance(v, list) else []

    def open_questions(self):
        return kl.bullets(kl.section(self.body, "Open questions"))


class Backlog:
    """Requirements, tickets, and the trace from tests and code, loaded and validated once.

    `errors` and `warnings` hold (where, message) pairs; `tagged` maps a ticket ID to the
    criterion numbers its test tags name; `debt` lists adopted done stories' untested criteria.
    """

    def __init__(self, root, cfg):
        self.root, self.cfg = Path(root), cfg
        self.errors, self.warnings, self.debt = [], [], []
        self.reqs: Dict[str, Requirement] = {}
        self.tickets: Dict[str, Ticket] = {}
        self.tagged = defaultdict(set)
        self.files = [f for f in kl.tracked_files(self.root) if not kl.is_ignored(f, cfg)]
        self._load_requirements()
        self._load_tickets()
        self._validate()
        self._trace()

    def error(self, where, msg):
        self.errors.append((str(where), msg))

    def warn(self, where, msg):
        self.warnings.append((str(where), msg))

    # --- requirements -----------------------------------------------------------------

    def _load_requirements(self):
        for rel in self.files:
            if not rel.startswith("docs/requirements/") or not rel.endswith(".md") or rel.endswith("/README.md"):
                continue
            name = Path(rel).name
            m = re.match(rf"^({kl.CODE})-.+\.md$", name)
            if not m:
                self.error(rel, "requirement files are named `<CODE>-<name>.md` (one per epic code)")
                continue
            for line in kl.REQ_LINE.finditer(kl.read_text(self.root / rel) or ""):
                rid, text = line.group(1), line.group(2)
                if rid.rsplit("-R", 1)[0] != m.group(1):
                    self.error(rel, f"{rid} does not belong in a {m.group(1)} file")
                if rid in self.reqs:
                    self.error(rel, f"{rid} is defined twice (also in {self.reqs[rid].rel})")
                    continue
                sup = SUPERSEDED.match(text)
                self.reqs[rid] = Requirement(rid, text, rel, bool(OBSERVED.match(text)), sup.group(2) if sup else None)
        for r in self.reqs.values():
            if r.superseded_by and r.superseded_by not in self.reqs:
                self.error(r.rel, f"{r.id} is superseded by {r.superseded_by}, which is not defined")

    # --- tickets ------------------------------------------------------------------------

    def _ticket_files(self):
        for rel in self.files:
            parts = rel.split("/")
            # Delivery records (deliver.py record) are change-request descriptions kept as
            # history, not tickets: no frontmatter, and they may name anything.
            if parts[0] == "backlog" and rel.endswith(".md") and parts[-1] != "README.md" and "delivery" not in parts:
                yield rel

    def _load_tickets(self):
        for rel in self._ticket_files():
            text = kl.read_text(self.root / rel)
            if text is None:
                self.error(rel, "not readable as UTF-8 text")
                continue
            try:
                fm, body = kl.parse_frontmatter(text)
            except Exception as e:  # yaml.YAMLError; PyYAML is imported lazily by kitchen_lib
                self.error(rel, f"invalid YAML frontmatter: {str(e).splitlines()[0]}")
                continue
            if fm is None:
                self.error(rel, "missing frontmatter (a `---` block at the top)")
                continue
            if not isinstance(fm, dict):
                self.error(rel, "frontmatter must be a mapping of fields")
                continue
            self._check_fields(rel, fm, body)

    def _check_fields(self, rel, fm, body):
        tid, ttype = str(fm.get("id", "")), fm.get("type")
        for key in REQUIRED + (() if ttype == "epic" else REQUIRED_NON_EPIC):
            if key not in fm:
                self.error(rel, f"missing `{key}`")
        for key in fm:
            if key not in KNOWN_FIELDS:
                self.warn(rel, f"unknown field `{key}` (a typo?)")
        parsed = kl.parse_ticket_id(tid)
        if ttype not in TYPES:
            self.error(rel, f"type `{ttype}` not in {', '.join(TYPES)}")
        elif not parsed or parsed[0] != kl.PREFIX[ttype]:
            self.error(rel, f"id `{tid}` does not match type `{ttype}` (expected {kl.PREFIX[ttype]}-…)")
        name = Path(rel).name
        if ttype == "epic":
            if name != "epic.md":
                self.error(rel, "an epic's file is named epic.md")
            elif parsed and not re.match(rf"^{parsed[1]}-.+$", Path(rel).parent.name):
                self.error(rel, f"an epic's folder is named `{parsed[1]}-<slug>`")
            if len(rel.split("/")) != 3:
                self.error(rel, "an epic lives in its own folder directly under backlog/")
        elif not re.match(rf"^{re.escape(tid)}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$", name):
            self.error(rel, f"file name must be `{tid}-<kebab-case-slug>.md`")
        if fm.get("status") not in STATUS:
            self.error(rel, f"status `{fm.get('status')}` not in {', '.join(STATUS)}")
        if fm.get("assignee_type") not in ASSIGNEE:
            self.error(rel, f"assignee_type `{fm.get('assignee_type')}` not in {', '.join(ASSIGNEE)}")
        if ttype == "decision" and fm.get("assignee_type") != "human":
            self.error(rel, "decisions are assigned to humans (assignee_type: human)")
        if "priority" in fm and fm["priority"] not in PRIORITY:
            self.error(rel, f"priority `{fm['priority']}` not in {', '.join(PRIORITY)}")
        if "refined" in fm and not _is_date(fm["refined"]):
            self.error(rel, f"refined `{fm['refined']}` is not a date (YYYY-MM-DD)")
        for key in ("adopted", "hotfix"):
            if key in fm and not isinstance(fm[key], bool):
                self.error(rel, f"`{key}` is true or false")
        for key in ("source_reqs", "blocked_by", "fixes", "code"):
            if key in fm and not isinstance(fm[key], list):
                self.error(rel, f"`{key}` is a list (use [] for none)")
        if "code" in fm and ttype != "epic":
            self.error(rel, "`code:` globs belong on epics only")
        t = Ticket(tid, ttype, rel, fm, body)
        if ttype in WITH_CRITERIA:
            self._criteria(t)
        if tid in self.tickets:
            self.error(rel, f"duplicate id `{tid}` (also {self.tickets[tid].rel})")
        else:
            self.tickets[tid] = t
        if self.cfg.self_contained_tickets:
            for n, line in enumerate(body.splitlines(), 1):
                for m in REPO_LINK.finditer(line):
                    self.error(rel, f"body line {n}: links to a repository file `{m.group(0)}` (self_contained_tickets)")
                for m in REPO_NAME.finditer(line):
                    self.error(rel, f"body line {n}: names a repository path or document `{m.group(0)}` (self_contained_tickets)")

    def _criteria(self, t):
        """Read `## Acceptance criteria`: stories as `- AC<n>: Given …`, tasks as `- AC<n>: <checkable statement>`."""
        found = t.criteria
        for line in kl.bullets(kl.section(t.body, "Acceptance criteria")):
            line = "- " + line
            m = AC_LINE.match(line)
            if not m:
                self.error(t.rel, f"criterion not in `- AC<n>: …` form: `{line[:60]}`")
                continue
            n, text = int(m.group(1)), m.group(2)
            if found and n <= max(found):
                self.error(t.rel, f"AC{n} is duplicated or out of order (numbers only grow; never renumber)")
                continue
            if REMOVED.match(text):
                found[n] = False
            elif t.type == "story" and not text.startswith("Given "):
                self.error(t.rel, f"AC{n}: a story's criterion reads `Given …, when …, then ….`")
                found[n] = True
            elif not text:
                self.error(t.rel, f"AC{n} is empty")
            else:
                found[n] = True

    # --- cross-ticket rules ---------------------------------------------------------------

    def _validate(self):
        tickets, releases = self.tickets, self.cfg.releases
        for tid, t in tickets.items():
            fm, rel = t.fm, t.rel
            if t.type != "epic" and t.type in TYPES:
                epic = str(fm.get("epic") or "")
                if epic not in tickets or tickets[epic].type != "epic":
                    self.error(rel, f"epic `{epic}` does not exist")
                else:
                    if tickets[epic].folder != t.folder:
                        self.error(rel, f"not in its epic's folder ({tickets[epic].folder})")
                    if t.code and f"EP-{t.code}" != epic:
                        self.error(rel, f"id code `{t.code}` does not match epic `{epic}`")
            for b in t.list("blocked_by"):
                if b == tid:
                    self.error(rel, "blocked_by names the ticket itself")
                elif b not in tickets:
                    self.error(rel, f"blocked_by `{b}` does not exist")
                elif t.status == "done" and tickets[b].status != "done":
                    # blocked_by means "can start, can't finish".
                    self.error(rel, f"done, but blocker {b} is `{tickets[b].status}`")
            for r in t.list("source_reqs"):
                if r not in self.reqs:
                    self.error(rel, f"source_reqs `{r}` is not defined in docs/requirements/")
            if t.type == "story" and t.status in STARTED and not t.list("source_reqs"):
                self.error(rel, f"{t.status} stories cite at least one requirement (source_reqs)")
            for ref in t.list("fixes"):
                m = kl.AC_REF.fullmatch(ref)
                if not m:
                    self.error(rel, f"fixes `{ref}` is not a criterion reference (`US-PAY-01/AC2`)")
                elif not self.is_live(m.group(1), int(m.group(2))):
                    self.error(rel, f"fixes `{ref}` is not a live acceptance criterion")
            self._release_rules(t, releases)
            for m in kl.AC_REF.finditer(t.body):
                if not self.is_live(m.group(1), int(m.group(2))):
                    self.error(rel, f"`{m.group(0)}` is not a live acceptance criterion")
            if t.type != "epic" and t.status in STARTED:
                self._readiness(t)
        self._cycles()

    def is_live(self, tid, n):
        t = self.tickets.get(tid)
        return bool(t and t.criteria.get(n))

    def _release_rules(self, t, releases):
        rel, release = t.rel, t.fm.get("release")
        if t.type == "epic" or release is None:
            return
        if not releases:
            self.warn(rel, f"release `{release}` is ignored: kitchen.yml lists no releases")
            return
        if release not in releases:
            self.error(rel, f"release `{release}` not in kitchen.yml releases {releases}")
            return
        if t.status == "deferred" and release != releases[-1]:
            self.error(rel, f"deferred tickets go to the last slice (`{releases[-1]}`)")
        for b in t.list("blocked_by"):
            bt = self.tickets.get(b)
            if bt and bt.status != "done" and bt.fm.get("release") in releases \
                    and releases.index(bt.fm["release"]) > releases.index(release):
                self.error(rel, f"release `{release}` is earlier than unfinished blocker {b} (`{bt.fm['release']}`)")

    def _readiness(self, t):
        rel = t.rel
        if str(t.fm.get("owner") or "").strip() in ("", "TBD"):
            self.error(rel, f"{t.status} tickets need an owner (not TBD)")
        if self.cfg.releases and t.type in ("story", "task", "spike") and not t.fm.get("release"):
            self.error(rel, f"{t.status} tickets need a release (kitchen.yml lists releases)")
        if t.type not in WITH_CRITERIA:
            return
        live = set(t.live())
        if not live:
            self.error(rel, f"a {t.status} {t.type} needs at least one live acceptance criterion")
        for q in t.open_questions():
            if q.startswith("None"):
                continue
            refs = [r for r in kl.TICKET_REF.findall(q) if r.startswith(("DEC-", "SPK-"))]
            if not refs:
                self.error(rel, f"open question is unanswered: start it with `None` or name a DEC or SPK: `{q[:60]}`")
            for r in refs:
                if r not in self.tickets:
                    self.error(rel, f"open question names unknown ticket `{r}`")
                elif self.tickets[r].status != "done" and r not in t.list("blocked_by"):
                    after = q.partition("Until decided:")[2]
                    if not any(int(n) in live for n in OWN_AC.findall(after)):
                        self.error(rel, f"open {r} needs `Until decided: …` naming one of this ticket's live criteria")

    def _cycles(self):
        """Report each `blocked_by` cycle once (a cycle can never be finished)."""
        graph = {tid: [b for b in t.list("blocked_by") if b in self.tickets and b != tid]
                 for tid, t in self.tickets.items()}
        state, path, seen = {}, [], set()

        def visit(u):
            state[u] = 1
            path.append(u)
            for v in graph[u]:
                if state.get(v) == 1:
                    cycle = path[path.index(v):]
                    i = cycle.index(min(cycle))
                    key = tuple(cycle[i:] + cycle[:i])
                    if key not in seen:
                        seen.add(key)
                        self.error(self.tickets[key[0]].rel, "blocked_by cycle " + " -> ".join(key + (key[0],)))
                elif not state.get(v):
                    visit(v)
            path.pop()
            state[u] = 2

        for tid in sorted(graph):
            if not state.get(tid):
                visit(tid)

    # --- trace: tests and code ------------------------------------------------------------

    def _trace(self):
        cfg = self.cfg
        for rel in self.files:
            test, code = kl.is_test(rel, cfg), kl.is_code(rel, cfg)
            if not (test or code):
                continue
            text = kl.read_text(self.root / rel)
            if text is None:
                continue  # binary file
            if kl.no_trace(text):
                continue  # declared data, not trace (kitchen_lib.NO_TRACE)
            if test:
                for tid, n in sorted(set(kl.find_tags(text))):
                    t = self.tickets.get(tid)
                    tag = f"{tid}/AC{n}"
                    if not self.is_live(tid, n):
                        self.error(rel, f"tag `{tag}` is not a live acceptance criterion")
                    elif t.status not in ("in-progress", "done"):
                        self.error(rel, f"tag `{tag}` belongs to a `{t.status}` ticket (tags name started tickets)")
                    else:
                        self.tagged[tid].add(n)
            # Both product code and tests: a TODO in either is a gap someone must own.
            for i, line in enumerate(text.splitlines(), 1):
                if TODO.search(line) and not any(r in self.tickets for r in kl.TICKET_REF.findall(line)):
                    self.error(f"{rel}:{i}", "TODO/FIXME/XXX/HACK names no existing ticket")
            for d in sorted({r for r in kl.TICKET_REF.findall(text) if r.startswith("DEC-")}):
                if d not in self.tickets:
                    self.error(rel, f"`{d}` does not exist")
                elif self.tickets[d].status == "done":
                    self.warn(rel, f"{d} is decided; revisit this seam")
        for tid, t in sorted(self.tickets.items()):
            if t.type != "story" or t.status not in ("in-progress", "done"):
                continue
            missing = [n for n in t.live() if n not in self.tagged[tid]]
            if not missing:
                continue
            names = ", ".join(f"AC{n}" for n in missing)
            if t.status == "in-progress":
                self.warn(t.rel, f"no tagged test yet for {names}")
            elif t.fm.get("adopted") is True:
                self.debt += [(f"{tid}/AC{n}", "adopted behavior with no tagged test") for n in missing]
            else:
                self.error(t.rel, f"done, but no tagged test for {names}")

    # --- reports ------------------------------------------------------------------------

    def epic_codes(self, deferred):
        return {t.code for t in self.tickets.values() if t.type == "epic" and (t.status == "deferred") == deferred}

    def uncovered(self):
        """Requirements not superseded, outside deferred epics, cited by no live story or task."""
        cited = set()
        for t in self.tickets.values():
            if t.type in WITH_CRITERIA and t.status != "deferred":
                cited.update(t.list("source_reqs"))
        deferred = self.epic_codes(deferred=True)
        return [r for r in sorted(self.reqs, key=_req_key) if not self.reqs[r].superseded_by
                and r.rsplit("-R", 1)[0] not in deferred and r not in cited]

    def counts(self):
        c = defaultdict(int)
        for t in self.tickets.values():
            c[t.type] += 1
        return c


def _is_date(v):
    if isinstance(v, datetime.date) and not isinstance(v, datetime.datetime):
        return True
    try:
        datetime.date.fromisoformat(str(v))
        return bool(re.fullmatch(r"\d{4}-\d\d-\d\d", str(v)))
    except ValueError:
        return False


def _req_key(rid):
    code, _, n = rid.rpartition("-R")
    return code, int(n)


# --- change-request description ---------------------------------------------------------------

def cr_body_errors(text, backlog):
    """Check that a change-request description files every gap, decision, and platform change.

    Every bullet under "Gaps found" names an existing ticket; every bullet under "Decisions"
    and "Platform changes" ends `Log: <decision-log entry title>` (the title must exist) or
    names a done DEC; any of them may instead be a single `- None…` bullet.
    """
    errors, tickets = [], backlog.tickets
    text = kl.COMMENT.sub("", text.replace("\r\n", "\n"))
    titles = kl.decision_log_titles(backlog.root)
    where = "change request description"
    for name, kind in CR_SECTIONS.items():
        body = kl.section(text, name)
        if body is None:
            errors.append((where, f'missing "## {name}" section'))
            continue
        items = kl.bullets(body)
        if not items:
            errors.append((where, f'"{name}" needs at least one bullet, or "- None"'))
        if len(items) == 1 and items[0].startswith("None"):
            continue
        for b in items:
            refs = kl.TICKET_REF.findall(b)
            for r in refs:
                if r not in tickets:
                    errors.append((f"{where}, {name}", f"`{r}` does not exist"))
            if kind == "ticket":
                ok = bool(refs)
            else:
                log = LOG_REF.search(b)
                if log and log.group(1).strip() not in titles:
                    errors.append((f"{where}, {name}", f'no decision-log entry titled "{log.group(1).strip()}"'))
                    continue
                ok = bool(log) or any(r.startswith("DEC-") and r in tickets and tickets[r].status == "done" for r in refs)
            if not ok:
                want = "a ticket ID" if kind == "ticket" else '"Log: <entry title>" or a done DEC'
                errors.append((f"{where}, {name}", f"`{b[:60]}` needs {want}"))
    return errors


# --- modes ------------------------------------------------------------------------------------

def gaps(bl):
    """What keeps the product from being fully defined. Test debt is not a gap."""
    out, tickets = [], bl.tickets
    for tid, t in sorted(tickets.items(), key=lambda x: kl.ticket_sort_key(x[0])):
        if t.type in ("decision", "spike") and t.status not in ("done", "deferred"):
            out.append((tid, f"open {t.type}: {t.title}"))
        elif t.type in ("story", "task") and t.status == "draft":
            out.append((tid, f"draft {t.type}: {t.title}"))
        if t.type in WITH_CRITERIA and t.status not in ("done", "deferred"):
            for q in t.open_questions():
                if not q.startswith("None") and not any(r.startswith(("DEC-", "SPK-")) for r in kl.TICKET_REF.findall(q)):
                    out.append((tid, f"unanswered open question: {q[:80]}"))
        if t.type in ("story", "task", "spike") and t.status in ("ready", "in-progress") and not t.fm.get("refined"):
            out.append((tid, f"{t.status} but not refined (no `refined:` date)"))
    for r in bl.uncovered():
        out.append((r, "not cited by any story or task"))
    for r in sorted(bl.reqs, key=_req_key):
        if bl.reqs[r].observed and not bl.reqs[r].superseded_by:
            out.append((r, "observed in code, not yet confirmed by a person"))
    claims = [g for t in tickets.values() if t.type == "epic" for g in t.list("code")]
    if claims:
        for rel in bl.files:
            if kl.is_code(rel, bl.cfg) and not kl.matches(rel, claims):
                out.append((rel, "code that no epic's `code:` globs claim"))
    return out


def refine(bl, origin_branches=None):
    """Refinement findings the script can see; the reviewer's `ticket` mode does the rest."""
    out, cfg = [], bl.cfg
    for tid, t in sorted(bl.tickets.items(), key=lambda x: kl.ticket_sort_key(x[0])):
        if t.type == "epic" or t.status == "deferred":
            continue
        unfinished = t.status != "done"
        if t.type == "story" and unfinished and len(t.live()) > cfg.split_threshold:
            out.append((tid, f"{len(t.live())} live criteria, more than split_threshold {cfg.split_threshold}: consider a split"))
        for r in t.list("source_reqs"):
            req = bl.reqs.get(r)
            if req and req.superseded_by:
                out.append((tid, f"cites {r}, superseded by {req.superseded_by}"
                                 + (": a change becomes a new ticket" if not unfinished else "")))
        if unfinished:
            for q in t.open_questions():
                for r in kl.TICKET_REF.findall(q):
                    if r.startswith(("DEC-", "SPK-")) and r in bl.tickets and bl.tickets[r].status == "done":
                        out.append((tid, f"open question names {r}, which is done: re-check it"))
        if cfg.releases and t.type in ("story", "task", "spike") and unfinished and not t.fm.get("release"):
            out.append((tid, "no release slice"))
        if t.fm.get("hotfix") is True and t.status == "done" and not t.fm.get("refined"):
            out.append((tid, "hotfix done: refine it and file its follow-up (set `refined:` when it passes)"))
        if t.status == "in-progress" and t.type in ("story", "task", "spike") and origin_branches is not None \
                and t.branch not in origin_branches:
            out.append((tid, f"in-progress, but branch `{t.branch}` is not on origin"))
    return out


def origin_branches(root):
    """Branches on origin, or None (with the reason) when they cannot be listed."""
    import hosts  # local import: hosts imports kitchen_lib only, never this module
    try:
        return hosts.Host(root).pushed_branches(), None
    except hosts.HostError as e:
        return None, str(e)


# --- self-test --------------------------------------------------------------------------------

FIXTURE = {
    "kitchen.yml": "tests: [\"tests/**\"]\ncode: [\"src/**\"]\ntest_command: \"python3 -m unittest {files}\"\nhost: manual\n",
    "docs/requirements/PAY-payments.md": "# Payments\n\n- PAY-R01: Refunds never exceed the order total.\n",
    "docs/decision-log.md": "# Decision log\n\n### 2026-01-01 — Use refunds\n\nDecided.\n",
    "backlog/PAY-payments/epic.md": ("---\nid: EP-PAY\ntype: epic\ntitle: Payments\nowner: Team\n"
                                     "assignee_type: either\nstatus: ready\n---\n\nPayments.\n"),
    "backlog/PAY-payments/US-PAY-01-refund-limit.md": (
        "---\nid: US-PAY-01\ntype: story\ntitle: Refund limit\nepic: EP-PAY\nsource_reqs: [PAY-R01]\n"
        "blocked_by: []\nowner: Team\nassignee_type: either\nstatus: done\n---\n\n"
        "As a clerk, I want refunds capped, so that nobody is refunded twice.\n\n## Acceptance criteria\n\n"
        "- AC1: Given an order, when a refund exceeds its total, then it is refused.\n\n"
        "## Notes\n\n- None.\n\n## Open questions\n\n- None.\n"),
    "tests/test_refund.py": "def test_us_pay_01_ac1_refused():\n    pass\n",
    "src/refund.py": "# Refund rules (US-PAY-01).\n",
}


def self_test():
    """Validate a tiny fixture, then break it three ways; return a list of failures."""
    failures = []
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for rel, text in FIXTURE.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
        cfg = kl.load_config(root)
        bl = Backlog(root, cfg)
        if bl.errors or bl.uncovered():
            failures.append(f"the valid fixture has findings: {bl.errors} {bl.uncovered()}")
        if cr_body_errors("## Gaps found\n\n- None\n\n## Decisions\n\n- Chose X. Log: Use refunds\n\n"
                          "## Platform changes\n\n- None\n", bl):
            failures.append("a valid change-request description was rejected")
        (root / "tests/test_refund.py").write_text("def test_us_pay_01_ac2_x():\n    pass  # TODO later\n")
        msgs = " | ".join(m for _, m in Backlog(root, cfg).errors)
        for want in ("not a live acceptance criterion", "names no existing ticket", "no tagged test for AC1"):
            if want not in msgs:
                failures.append(f"missing finding `{want}` in: {msgs}")
    return failures


# --- command line -----------------------------------------------------------------------------

def emit(label, items):
    for where, msg in items:
        print(f"{label} {where}: {msg}")


def main(argv):
    modes = [a for a in argv if a in ("--gaps", "--refine", "--test-debt", "--self-test")]
    pr_bodies = [a.split("=", 1)[1] for a in argv if a.startswith("--pr-body=")]
    unknown = [a for a in argv if a not in modes and a != "--strict" and not a.startswith("--pr-body=")]
    if unknown or len(modes) > 1 or (modes and (pr_bodies or "--strict" in argv)):
        print(__doc__)
        return 2
    if modes == ["--self-test"]:
        problems = self_test()
        for p in problems:
            print("FAIL", p)
        print("PASS self-test" if not problems else f"FAIL self-test: {len(problems)} failure(s)")
        return 1 if problems else 0
    root = kl.repo_root()
    try:
        cfg = kl.load_config(root)
    except kl.ConfigError as e:
        for line in str(e).splitlines():
            print("ERROR", line)
        return 1
    bl = Backlog(root, cfg)
    note = [("backlog", f"{len(bl.errors)} validation error(s): run scripts/backlog_check.py")] if bl.errors else []
    if modes == ["--gaps"]:
        found = gaps(bl)
        emit("WARN ", note)
        emit("GAP  ", found)
        return 1 if found or bl.errors else 0
    if modes == ["--refine"]:
        branches, why = origin_branches(root)
        emit("WARN ", note + ([("origin", f"branches not checked: {why}")] if why else []))
        emit("REFINE", refine(bl, branches))
        return 0
    if modes == ["--test-debt"]:
        emit("WARN ", note)
        emit("DEBT ", bl.debt)
        return 0
    errors = list(bl.errors)
    for f in pr_bodies:
        text = kl.read_text(Path(f))
        if text is None:
            errors.append((f, "change-request description file not readable"))
        else:
            # A committed delivery record works too (CI on hosts whose pipelines cannot read
            # the live description): only the description after its marker line is checked.
            described = kl.record_description(text)
            errors += cr_body_errors(text if described is None else described, bl)
    c = bl.counts()
    print("backlog: " + ", ".join(f"{c[t]} {t}" for t in TYPES)
          + f"; {len(errors)} error(s), {len(bl.warnings)} warning(s)")
    emit("ERROR", errors)
    emit("WARN ", bl.warnings)
    strict = "--strict" in argv
    uncovered = [(r, "not cited by any story or task") for r in bl.uncovered()]
    emit("ERROR" if strict else "WARN ", uncovered)
    return 1 if errors or (strict and uncovered) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
