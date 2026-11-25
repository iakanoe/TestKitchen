"""Deterministic steps and gates of the delivery workflow (playbooks/deliver.md).

Agents and people use it so that picking a ticket, reading its context, and deciding
whether work may move on never depend on a model's judgment or memory.

Usage (from any directory in the repository):

    python3 scripts/deliver.py next                     # ticket to take, other ready ones, why the rest wait
    python3 scripts/deliver.py context US-PAY-03        # criteria, cited requirement text, ADRs, related tickets, body
    python3 scripts/deliver.py pr-body US-PAY-03        # change-request description skeleton, one plan row per live criterion
    python3 scripts/deliver.py gate red US-PAY-03       # each live criterion has a tagged test that runs and fails
    python3 scripts/deliver.py record --body-file=F --branch=B [--cr=N] [--url=U]   # keep the description in the repo
    python3 scripts/deliver.py gate pr (--body-file=F | --from-record) --branch=B [--base=REV] [--head=REV]
    python3 scripts/deliver.py gate merge N --head=SHA  # host state + gate pr; the guard runs it before a merge
    python3 scripts/deliver.py merge-command N --head=SHA   # the one allowed merge command for this host
    python3 scripts/deliver.py check                    # backlog_check + self-tests + check_command or the full test run
    python3 scripts/deliver.py status                   # one screen: ready, in progress, blocked, decisions, gaps, debt
    python3 scripts/deliver.py release-notes [SLICE]    # markdown from done stories, grouped by epic
    python3 scripts/deliver.py --self-test              # checks itself on a temporary git repository; exit 0/1

Output: `next` prints `NEXT`, `READY`, `WAIT`, `DECIDE`, and `REFINE` lines; gates print
each failure as `FAIL <reason>` and end with `PASS <what>` or exit 1. Usage errors exit 2.
Without --base, `gate pr` measures from `origin/<default branch>`, or from the local default
branch (with a NOTE) when origin does not have it. History checks include merge commits.

The script encodes a few workflow conventions itself (backlog/README.md documents them):
the freeze commit message `test: <ID> failing tests`, the reviewer's closing lines
`Reviewed commit: <sha>` and `CRITICAL: n, WARNING: n, SUGGESTION: n`, and the delivery
record's marker line. Requires PyYAML and git; `next` and `gate merge` also use the host's
CLI (`gh` or `glab`) when the host is github or gitlab.
"""
from __future__ import annotations

import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kitchen_lib as kl  # noqa: E402
import hosts  # noqa: E402
import backlog_check as bc  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent
TALLY = re.compile(r"CRITICAL: (\d+), WARNING: (\d+), SUGGESTION: (\d+)")
# The reviewer names the commit it reviewed; no code or test file may change after it.
REVIEWED = re.compile(r"Reviewed commit: ([0-9a-f]{7,40})")
# The commit that freezes a ticket's tests (playbooks/deliver.md, tests first).
FREEZE_MSG = "test: {} failing tests"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
PRIORITY_RANK = {"high": 2, "normal": 1, "low": 0}
# Skipped or focused tests may not be added after the freeze: a skipped test proves
# nothing, and a focused one silently skips the rest. Checked on added lines of test
# files only (product code may call `.skip(` legitimately). Covers JS/TS (vitest, jest,
# mocha, playwright), Python (pytest, unittest), Go, JVM (JUnit 4/5), and Ruby (RSpec,
# minitest); guide/test-runners.md lists them.
SKIP_MARKERS = re.compile(
    r"\.(?:skip|only|todo|fixme)\s*\("                                    # it.skip( test.only( describe.todo( test.fixme(
    r"|\b(?:xit|xdescribe|xtest|xcontext|fit|fdescribe|fcontext)(?:\s*\(|\s+['\"])"  # xit( fdescribe( / RSpec xit "…"
    r"|@pytest\.mark\.(?:skip|skipif|xfail)\b|\bpytest\.(?:skip|xfail)\s*\("
    r"|@unittest\.(?:skip|skipIf|skipUnless|expectedFailure)\b|\bself\.skipTest\s*\("
    r"|\.Skip(?:f|Now)?\s*\("                                             # Go: t.Skip( t.Skipf( t.SkipNow(
    r"|@(?:Disabled|Ignore)\b"                                            # JUnit 5 / JUnit 4
    r"|^\s*(?:skip|pending)(?:\s*$|\s*\(|\s+['\"])"                       # Ruby: skip / pending statements
)
# Everything after this line in a delivery record is the change-request description, verbatim.
RECORD_MARKER = kl.RECORD_MARKER


class Stop(Exception):
    """A command cannot continue: printed as `FAIL <message>`, exit 1."""


class Project:
    """The repository the scripts belong to: root, configuration, backlog (loaded once), host."""

    def __init__(self, root=None):
        self.root = Path(root) if root else kl.repo_root()
        self.cfg = kl.load_config(self.root)
        self._backlog = None

    @property
    def backlog(self):
        if self._backlog is None:
            self._backlog = bc.Backlog(self.root, self.cfg)
        return self._backlog

    @property
    def host(self):
        return hosts.get_host(self.cfg, self.root)

    def git(self, *args):
        return kl.git(self.root, *args)

    def ok(self, *args):
        """True when `git <args>` exits 0."""
        return kl.run(kl.git_argv(*args), self.root).returncode == 0

    def ticket(self, tid):
        t = self.backlog.tickets.get(tid)
        if not t:
            raise Stop(f"{tid} does not exist")
        return t

    def default_branch(self):
        return kl.default_branch(self.root)


def report(failures, what):
    """Print each failure and the verdict; True when nothing failed."""
    for f in failures:
        print("FAIL", f)
    if not failures:
        print(f"PASS {what}")
    return not failures


# --- next ------------------------------------------------------------------------------------

class Order:
    """The order `next` (and `status`, and the define hand-off) ranks tickets in.

    (1) release slice, when slices are on (no release sorts last); (2) effective priority:
    a ticket inherits the highest priority of every unfinished ticket it transitively
    unblocks, so a low-priority blocker of urgent work is urgent; (3) how many unfinished
    tickets it directly blocks, most first; (4) the person running it owns it; (5) ID.
    """

    def __init__(self, p, me):
        self.tickets, self.releases, self.me = p.backlog.tickets, p.cfg.releases, me
        # Unfinished for ranking: not done and not parked.
        self.active = {tid for tid, t in self.tickets.items() if t.status not in ("done", "deferred")}
        self.blocks = defaultdict(set)  # blocker -> tickets that name it in blocked_by
        for tid, t in self.tickets.items():
            for b in t.list("blocked_by"):
                if b in self.tickets:
                    self.blocks[b].add(tid)

    def downstream(self, tid):
        """Unfinished tickets that `tid` blocks, directly or through other tickets."""
        seen, todo = set(), list(self.blocks[tid])
        while todo:
            u = todo.pop()
            if u in seen or u == tid:
                continue
            seen.add(u)
            todo.extend(self.blocks[u])
        return {u for u in seen if u in self.active}

    def priority(self, tid):
        rank = lambda t: PRIORITY_RANK.get(self.tickets[t].fm.get("priority") or "normal", 1)  # noqa: E731
        return max([rank(tid)] + [rank(u) for u in self.downstream(tid)])

    def key(self, tid):
        t = self.tickets[tid]
        rel = t.fm.get("release")
        slice_ = (self.releases.index(rel) if rel in self.releases else len(self.releases)) if self.releases else 0
        direct = len([u for u in self.blocks[tid] if u in self.active])
        mine = bool(self.me) and str(t.fm.get("owner") or "") == self.me
        return (slice_, -self.priority(tid), -direct, not mine, kl.ticket_sort_key(tid))


def plan_next(p, held, me):
    """(ready IDs in order, [(ID, why it waits)], [(DEC, blocked IDs)], [draft IDs]); no output."""
    tickets, order = p.backlog.tickets, Order(p, me)
    ready, waiting = [], []
    for tid in sorted(tickets, key=kl.ticket_sort_key):
        t = tickets[tid]
        if t.type not in ("story", "task", "spike") or t.status not in ("ready", "in-progress"):
            continue
        open_blockers = [b for b in t.list("blocked_by") if b not in tickets or tickets[b].status != "done"]
        if t.fm.get("assignee_type") == "human":
            waiting.append((tid, "assigned to a person"))
        elif open_blockers:
            waiting.append((tid, "blocked by " + ", ".join(open_blockers)))
        elif t.branch in held:
            waiting.append((tid, f"branch `{t.branch}` is taken (open change request or pushed branch)"))
        elif t.status == "in-progress":
            waiting.append((tid, "in-progress with no branch: ask who holds it"))
        else:
            ready.append(tid)
    ready.sort(key=order.key)
    # Decisions that block waiting work, directly or through other unfinished tickets. A
    # deferred DEC is parked on purpose (deferring is itself a decision), so it is not
    # offered for deciding; the tickets it blocks still wait.
    blocked_by_dec = defaultdict(set)
    for tid, why in waiting:
        if not why.startswith("blocked by"):
            continue
        seen, todo = set(), list(tickets[tid].list("blocked_by"))
        while todo:
            b = todo.pop()
            if b in seen or b not in tickets or tickets[b].status == "done":
                continue
            seen.add(b)
            if tickets[b].type == "decision" and tickets[b].status != "deferred":
                blocked_by_dec[b].add(tid)
            todo.extend(tickets[b].list("blocked_by"))
    decide = sorted(blocked_by_dec, key=lambda d: (-len(order.downstream(d)), kl.ticket_sort_key(d)))
    drafts = sorted((tid for tid, t in tickets.items() if t.type in ("story", "task", "spike") and t.status == "draft"),
                    key=order.key)
    return ready, waiting, [(d, sorted(order.downstream(d), key=kl.ticket_sort_key)) for d in decide], drafts


def me_of(p):
    return kl.run(kl.git_argv("config", "user.name"), p.root).stdout.strip()


def cmd_next(p):
    try:
        held = p.host.open_branches()
    except hosts.HostError as e:
        raise Stop(f"cannot tell which branches are taken: {e}")
    tickets = p.backlog.tickets
    ready, waiting, decide, drafts = plan_next(p, held, me_of(p))
    if ready:
        t = tickets[ready[0]]
        print(f"NEXT {t.id} ({t.title}) branch `{t.branch}`")
    elif decide or drafts:
        print("NEXT none: nothing is ready; decide the DECIDE tickets, then refine the REFINE tickets (run /define)")
    elif waiting:
        print(f"NEXT none: nothing is ready; {len(waiting)} waiting (see WAIT lines)")
    else:
        print("NEXT none: nothing is ready or waiting; run /define to plan more work")
    for tid in ready[1:]:
        print(f"READY {tid} ({tickets[tid].title})")
    for tid, why in waiting:
        print(f"WAIT {tid}: {why}")
    if not ready:
        for d, blocked in decide:
            print(f"DECIDE {d} ({tickets[d].title}): blocks {len(blocked)} ticket(s): {', '.join(blocked)}")
        for tid in drafts:
            print(f"REFINE {tid} ({tickets[tid].title})")
    return 0


# --- context ---------------------------------------------------------------------------------

ADR_REF = re.compile(r"\bADR-\d{3,}\b")
ADR_STATUS = re.compile(r"^Status:\s*(.+?)\s*$", re.M)


def adrs(p):
    """{ADR-nnn: (path, status)} from docs/architecture/ADR-nnn-<slug>.md."""
    out = {}
    for rel in p.backlog.files:
        m = re.match(r"^docs/architecture/(ADR-\d{3,})-.+\.md$", rel)
        if m:
            s = ADR_STATUS.search(kl.read_text(p.root / rel) or "")
            out[m.group(1)] = (rel, s.group(1) if s else "no Status line")
    return out


def cmd_context(p, tid):
    t, bl = p.ticket(tid), p.backlog
    fm = t.fm
    epic = bl.tickets.get(str(fm.get("epic") or ""))
    print(f"# {tid} {t.title}\nfile: {t.rel}\nbranch: {t.branch}\ntype: {t.type}  status: {t.status}  "
          f"owner: {fm.get('owner')}  priority: {fm.get('priority') or 'normal'}"
          + (f"  release: {fm.get('release')}" if p.cfg.releases else "")
          + ("  hotfix" if fm.get("hotfix") is True else "") + ("  adopted" if fm.get("adopted") is True else ""))
    if epic:
        print(f"epic: {epic.id} ({epic.title})" + (f"  code: {', '.join(epic.list('code'))}" if epic.list("code") else ""))
    if t.type in bc.WITH_CRITERIA:
        print("\nLive criteria (the only requirements):", ", ".join(f"AC{n}" for n in t.live()) or "none")
    print("\n## Cited requirements (verbatim)")
    for r in t.list("source_reqs"):
        req = bl.reqs.get(r)
        print(f"- {r}: {req.text if req else 'NOT FOUND in docs/requirements/'}")
    if not t.list("source_reqs"):
        print("- none")
    print("\n## ADRs (accepted ones bind every ticket)")
    found, named = adrs(p), set(ADR_REF.findall(t.body))
    for a in sorted(set(found) | named):
        rel, status = found.get(a, ("NOT FOUND in docs/architecture/", "?"))
        if a in named or status.startswith("accepted"):
            print(f"- {a} ({status}){' named in the ticket' if a in named else ''}: {rel}")
    print("\n## Related tickets")
    related = set(kl.TICKET_REF.findall(t.body)) | set(t.list("blocked_by"))
    related |= {kl.AC_REF.fullmatch(f).group(1) for f in t.list("fixes") if kl.AC_REF.fullmatch(f)}
    for r in sorted(related - {tid}, key=kl.ticket_sort_key):
        rt = bl.tickets.get(r)
        print(f"- {r} ({rt.title}): {rt.status}" if rt else f"- {r}: does not exist")
    print("\n## Ticket body\n" + t.body.strip())
    return 0


# --- pr-body ---------------------------------------------------------------------------------

def cmd_pr_body(p, tid):
    t = p.ticket(tid)
    reqs = ", ".join(t.list("source_reqs")) or "none"
    if t.type in bc.WITH_CRITERIA:
        ticket = f"{tid} {t.title} (requirements {reqs}). Status: `{t.status}`." + (" Hotfix." if t.fm.get("hotfix") else "")
        rows = "\n".join(f"| {tid}/AC{n} | |" for n in t.live())
        plan = f"| Criterion | Tests |\n| --- | --- |\n{rows}\n\nConstrained by:"
    else:
        # Only stories and tasks make ticket change requests; the rest record their work.
        ticket = f"None. Delivers {tid} {t.title}."
        plan = "None."
    if p.cfg.autonomy == "supervised":
        plan += "\n\nPlan approved by: \nTests approved by: "
    hotfix = ('\n<!-- Hotfix: replace "None" with "- <why the hotfix lane was used>. Log: <decision-log entry title>", '
              'and name the follow-up ticket under "Gaps found". -->') if t.fm.get("hotfix") else ""
    print(f"""## Ticket

{ticket}

## Plan

{plan}

## Gaps found

- None

## Decisions
{hotfix}
- None

## Platform changes

- None

## Test changes

None

## Review report

## Checks
""")
    return 0


# --- gate red --------------------------------------------------------------------------------

def parse_junit(path):
    """[(name, classname, state)] for every <testcase>: failure/error -> failed, skipped -> skipped, else passed."""
    out = []
    for case in ET.parse(str(path)).getroot().iter("testcase"):
        kids = {c.tag for c in case}
        state = "failed" if kids & {"failure", "error"} else "skipped" if "skipped" in kids else "passed"
        out.append((case.get("name") or "", case.get("classname") or "", state))
    return out


def tagged_test_files(p, tid):
    return [rel for rel in p.backlog.files if kl.is_test(rel, p.cfg)
            and any(x == tid for x, _ in kl.find_tags(kl.trace_text(kl.read_text(p.root / rel))))]


def gate_red(p, tid):
    """Run when the tests are written and before any implementation: every live criterion has a
    tagged test that runs and fails (because the behavior is missing)."""
    t = p.ticket(tid)
    if t.type not in bc.WITH_CRITERIA:
        raise Stop(f"gate red applies to stories and tasks; {tid} is a {t.type}")
    files = tagged_test_files(p, tid)
    if not files:
        if t.type == "task":
            # Tasks are tested first only when their criteria are testable.
            print(f"PASS red: {tid} is a task with no tagged tests, so gate red does not apply")
            return True
        raise Stop(f"no test file tags {tid} (tests match the `tests` globs and carry [{tid}/ACn] or "
                   f"{tid.lower().replace('-', '_')}_acn in a test name)")
    if not t.live():
        raise Stop(f"{tid} has no live criteria")
    if "{report}" not in p.cfg.test_command:
        raise Stop("test_command has no {report} placeholder: gate red reads the JUnit XML report it writes")
    tmp = Path(tempfile.mkdtemp(prefix="kitchen-red-"))  # outside the repository, never committed
    try:
        out = tmp / "report.xml"
        cmd = kl.render_command(p.cfg.test_command, files, out)
        print("running:", cmd, flush=True)
        r = subprocess.run(cmd, shell=True, cwd=str(p.root), capture_output=True, text=True)
        if not out.exists():
            raise Stop("the test command wrote no JUnit report, so the tests could not run:\n" + (r.stdout + r.stderr)[-2000:])
        try:
            results = parse_junit(out)
        except ET.ParseError as e:
            raise Stop(f"the JUnit report is not valid XML ({e})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    failures = []
    for n in t.live():
        mine = [(name, st) for name, cls, st in results if (tid, n) in kl.find_tags(f"{cls} {name}")]
        for name, st in mine:
            print(f"{st.upper():7} {name}")
        ran = [st for _, st in mine if st != "skipped"]
        if not ran:
            failures.append(f"AC{n}: no tagged test ran" + (" (only skipped ones)" if mine else ""))
        elif "failed" not in ran:
            failures.append(f"AC{n}: every tagged test already passes, so none proves the missing behavior")
    return report(failures, f"red: every live criterion of {tid} has a failing tagged test")


# --- record ----------------------------------------------------------------------------------
#
# A change-request description holds delivery evidence that lives nowhere else (plan, test
# changes, review report, checks). The host keeps it only as long as the repository stays
# there, so every change request commits a verbatim copy, a "delivery record", and
# `gate pr` fails when the committed copy differs from the description. Ticket change
# requests: backlog/<epic folder>/delivery/<ID>.md. Others: backlog/delivery/<branch, "/"
# as "-">.md. backlog_check.py skips both: they are history, not tickets.

def ticket_of(body):
    """The US-/TASK- ticket a description's `## Ticket` section starts with, or None.

    Markdown around the ID (`US-…`, **US-…**, - US-…, [US-…](x)) still starts the section;
    "None. Follows up US-PAY-01." names a ticket but makes a non-ticket change request.
    """
    text = kl.COMMENT.sub("", kl.section(body, "Ticket") or "")
    m = re.match(r"[\s`*_>\[(\-]*(" + kl.TICKET_REF.pattern + ")", text)
    return m.group(1) if m and m.group(1).startswith(("US-", "TASK-")) else None


def record_rel(branch, ticket=None):
    """Repository-relative path of a change request's delivery record."""
    if ticket:
        return f"{ticket.folder}/delivery/{ticket.id}.md"
    return f"backlog/delivery/{branch.replace('/', '-')}.md"


def record_text(body, branch, tid=None, number=None, url=None):
    """A delivery record: where it came from, then the description as it was."""
    lines = [f"# Delivery record: {tid or branch}", "", f"- Branch: `{branch}`", f"- Ticket: {tid or 'None'}"]
    if number or url:
        lines.append("- Change request: " + " ".join(([f"#{number}"] if number else []) + ([url] if url else [])))
    lines += ["", "Written by `scripts/deliver.py record`. Everything below the marker is the change request's "
                  "description, verbatim; `deliver.py gate pr` fails when it differs from the current description.",
              "", RECORD_MARKER, "", body.replace("\r\n", "\n").strip(), ""]
    return "\n".join(lines)


def record_body(text):
    """The description inside a delivery record, or None when the marker is missing (CRLF-safe)."""
    return kl.record_description(text)


def record_identity(text):
    """What makes a record one change request's: its branch and change-request lines."""
    return [line for line in text.replace("\r\n", "\n").splitlines() if line.startswith(("- Branch: ", "- Change request: "))]


def cmd_record(p, body, branch, number=None, url=None):
    """Write the record; never overwrite another change request's.

    A record is the same change request's when its branch and change-request lines match,
    so rerunning after the description changed replaces it. Otherwise (a follow-up change
    request for the same ticket; colliding branch names such as docs/a-b and docs-a/b; a
    number that restarted on a new host) the record goes to `<name>-cr<number>.md`, which
    needs --cr.
    """
    if number is not None and not str(number).isdigit():
        raise Stop(f"--cr must be a change-request number, got {number!r}")
    tid = ticket_of(body)
    ticket = p.ticket(tid) if tid else None
    base = record_rel(branch, ticket)
    text = record_text(body, branch, tid, number, url)
    options = [base] + ([f"{base[:-3]}-cr{number}.md"] if number else [])
    for rel in options:
        path = p.root / rel
        if not path.exists() or record_identity(path.read_text(encoding="utf-8")) == record_identity(text):
            break
    else:
        raise Stop(f"{base} already records another change request"
                   + (f", and so does {options[1]}" if number else ": pass --cr=<number> to give this one its own record"))
    (p.root / rel).parent.mkdir(parents=True, exist_ok=True)
    (p.root / rel).write_text(text, encoding="utf-8")
    print(rel)
    return 0


def record_failures(p, body, rel, head):
    """A record committed at `head` (at `rel` or a `-cr<n>` variant) must hold exactly this description."""
    stem = rel[:-3]
    listed = kl.run(kl.git_argv("ls-tree", "-z", "--name-only", head, rel.rsplit("/", 1)[0] + "/"), p.root).stdout.split("\0")
    found = [f for f in listed if f == rel or re.fullmatch(re.escape(stem) + r"-cr\d+\.md", f)]
    if not found:
        return [f"no delivery record at {rel}: run `python3 scripts/deliver.py record --body-file=<file> "
                f"--branch=<branch>` (plus --cr=<number> when the host numbers it) and commit it"]
    want = body.replace("\r\n", "\n").strip()
    if not any(record_body(text) == want for text in read_at(p, head, found).values()):
        return [f"no delivery record ({', '.join(found)}) matches the description: rerun `deliver.py record` and commit it"]
    return []


def body_from_record(p, branch, base, head):
    """The description in the delivery record this branch committed (for CI that cannot read it live)."""
    base = p.git("merge-base", base, head).strip()
    changed = branch_changes(p, base, head)
    records = [rel for rel in sorted(changed) if rel.split("/")[0] == "backlog" and "delivery" in rel.split("/")
               and rel.endswith(".md")]
    mine = []
    for rel, text in sorted(read_at(p, head, records).items()):
        if f"- Branch: `{branch}`" in record_identity(text) and record_body(text) is not None:
            mine.append((rel, record_body(text)))
    if len(mine) != 1:
        raise Stop(f"--from-record needs exactly one delivery record for branch `{branch}` committed on it; found "
                   + (", ".join(r for r, _ in mine) or "none"))
    print(f"description read from {mine[0][0]}")
    return mine[0][1]


# --- gate pr ---------------------------------------------------------------------------------

# History is read commit by commit, merge commits included: a merge can carry changes of
# its own (a conflict resolved by writing new code, or code slipped into an otherwise
# trivial merge), and those must be checked like any other commit. Paths are read with -z
# and every git call runs with kitchen_lib.GIT_SAFE, so neither unusual file names nor the
# person's git configuration (quotePath, noprefix, colors) changes what is seen.

def parents(p, sha):
    return p.git("rev-list", "--parents", "-n", "1", sha).split()[1:]


def commit_diff(p, sha, path, n_parents):
    """The commit's -U0 diff of one path (a combined `--cc` diff for a merge), file header removed."""
    args = ["--literal-pathspecs", "diff-tree", "-p", "--no-color", "--no-ext-diff", "-U0", "--no-commit-id", "--no-renames"]
    if n_parents > 1:
        args.append("--cc")
    elif n_parents == 0:
        args.append("--root")
    lines = p.git(*args, sha, "--", path).split("\n")
    first = next((i for i, line in enumerate(lines) if line.startswith("@@")), None)
    if first is None:  # no hunk: a binary change, a mode change, or nothing
        return [line for line in lines if line.strip()]
    return lines[first:]


def files_of(p, sha):
    """Paths a commit changed itself.

    For an ordinary commit, every path it touched. For a merge, only the paths whose merged
    content cannot be explained by its parents: git's combined diff (`--cc`) leaves out a
    file whose every hunk is taken unchanged from one side, so a clean merge of the default
    branch changes nothing here, while code written inside the merge does.
    """
    ps = parents(p, sha)
    args = ["diff-tree", "--no-commit-id", "--name-only", "-r", "-z", "--no-renames"]
    if len(ps) > 1:
        candidates = [f for f in p.git(*args, "--cc", sha).split("\0") if f]
        return [f for f in candidates if commit_diff(p, sha, f, len(ps))]
    return [f for f in p.git(*args, *([] if ps else ["--root"]), sha).split("\0") if f]


def branch_changes(p, base, head, since=None):
    """Paths changed by the branch's own commits (merges included) after `since` (default: base)."""
    revs = p.git("rev-list", f"{since or base}..{head}", f"^{base}").split()
    return {f for c in revs for f in files_of(p, c)}


def read_at(p, rev, paths):
    """{path: text} for files at a revision, read in one `git cat-file --batch` call."""
    if not paths:
        return {}
    data = "".join(f"{rev}:{path}\n" for path in paths).encode()
    r = subprocess.run(kl.git_argv("cat-file", "--batch"), cwd=str(p.root), input=data, capture_output=True)
    out, i, texts = r.stdout, 0, {}
    for path in paths:
        nl = out.index(b"\n", i)
        header = out[i:nl].split()
        i = nl + 1
        if len(header) == 3 and header[1] == b"blob":
            size = int(header[2])
            texts[path] = out[i:i + size].decode("utf-8", "replace").replace("\r\n", "\n")
            i += size + 1
    return texts


def tag_counts(p, rev):
    """Tag occurrences per (ticket, criterion) in the test files at a revision."""
    r = kl.run(kl.git_argv("grep", "-l", "-z", "-I", "-i", "-E", r"(us|task)[-_][a-z][a-z0-9]{1,9}[-_][0-9]{2,}", rev, "--"), p.root)
    prefix = rev + ":"
    paths = [x[len(prefix):] for x in r.stdout.split("\0") if x.startswith(prefix)]
    counts = Counter()
    for text in read_at(p, rev, [x for x in paths if kl.is_test(x, p.cfg)]).values():
        counts.update(kl.find_tags(kl.trace_text(text)))  # no-trace files prove nothing
    return counts


def freeze_commits(p, tid, base, head):
    want = FREEZE_MSG.format(tid)
    lines = p.git("log", "--reverse", "--format=%H%x00%s", f"{base}..{head}").splitlines()
    return [sha for sha, _, subject in (line.partition("\0") for line in lines) if subject == want]


def skip_additions(p, commit):
    """Added lines with a skip/focus marker in the test files a commit changes.

    Each test file's diff is read on its own, so no diff header has to be parsed. In a
    merge's combined diff a line is the merge's own only when it is new against every
    parent (`++` for two parents); lines taken from one side are that side's change.
    """
    n = len(parents(p, commit))
    found, width = [], max(n, 1)  # marker columns: one per parent
    for path in files_of(p, commit):
        if not kl.is_test(path, p.cfg):
            continue
        for line in commit_diff(p, commit, path, n):
            if line[:width] == "+" * width and not line.startswith("@@") and SKIP_MARKERS.search(line[width:]):
                found.append((path, line[width:].strip()))
    return found


def listed_tokens(text):
    """Whole paths and file names a "## Test changes" section names: `backticked` spans and plain words.

    Matching whole tokens, not substrings, keeps `tests/data.txt` from also covering `tests/a.txt`.
    """
    tokens = {t.strip() for t in re.findall(r"`([^`]+)`", text)}
    for word in re.sub(r"`[^`]*`", " ", text).split():
        tokens.add(word.lstrip("*_([<'\"").rstrip("*_)]>,;:.!?'\""))
    return tokens - {""}


def review_failures(p, body, base, head):
    """The final review ran on what is being merged: a tally with CRITICAL: 0, and its
    `Reviewed commit:` is on the branch with no code or test file changed after it."""
    failures, cfg = [], p.cfg
    review = kl.section(body, "Review report") or ""
    tallies = TALLY.findall(review)
    if not tallies:
        failures.append('Review report has no reviewer tally ("CRITICAL: n, WARNING: n, SUGGESTION: n")')
    elif int(tallies[-1][0]):
        failures.append(f"the last review reports {tallies[-1][0]} CRITICAL finding(s)")
    reviewed = REVIEWED.findall(review)
    if not reviewed:
        failures.append('Review report has no "Reviewed commit: <sha>" line')
        return failures
    sha = kl.run(kl.git_argv("rev-parse", "--verify", "-q", reviewed[-1] + "^{commit}"), p.root).stdout.strip()
    if not sha or not p.ok("merge-base", "--is-ancestor", sha, head):
        failures.append(f"reviewed commit {reviewed[-1]} is not on the branch")
        return failures
    later = sorted(f for f in branch_changes(p, base, head, since=sha) if kl.is_code(f, cfg) or kl.is_test(f, cfg))
    if later:
        failures.append(f"code or tests changed after the reviewed commit {reviewed[-1][:8]} "
                        f"({', '.join(later[:3])}): review again")
    return failures


def approved(plan, what):
    m = re.search(rf"^.*?\b{what} approved by:[ \t]*(\S.*?)\s*$", plan, re.M)
    return bool(m) and not m.group(1).startswith("<") and m.group(1) not in ("TBD", "-")


def gate_pr(p, body, branch, base, head):
    """Check a change request's description and history against the workflow; True when it passes."""
    raw = body.replace("\r\n", "\n")
    body = kl.COMMENT.sub("", raw)
    ticket_text = kl.section(body, "Ticket") or ""
    tid = ticket_of(raw)
    head = p.git("rev-parse", head).strip()
    if not tid:
        # A ticket-named branch must not skip the ticket checks by leaving the ID out.
        if re.match(r"^(?:us|task)-", branch):
            return report([f'branch `{branch}` is a ticket branch, but "## Ticket" names no US- or TASK- ticket first'], "pr")
        failures = record_failures(p, raw, record_rel(branch), head)
        # A change request without a ticket still may not merge unreviewed code or tests.
        base = p.git("merge-base", base, head).strip()
        touched = sorted(f for f in branch_changes(p, base, head) if kl.is_code(f, p.cfg) or kl.is_test(f, p.cfg))
        if touched:
            print(f"Not a ticket change request, but it changes code or tests ({', '.join(touched[:3])}): "
                  "the delivery record and the review checks apply.")
            failures += review_failures(p, body, base, head)
        else:
            print("Not a ticket change request: only the description checks (backlog_check.py --pr-body) "
                  "and the delivery record apply.")
        return report(failures, "pr")
    if tid not in p.backlog.tickets:
        return report([f"{tid} does not exist"], "pr")
    t, cfg = p.backlog.tickets[tid], p.cfg
    failures = []
    if branch != t.branch:
        failures.append(f"branch `{branch}` is not the ticket's file name `{t.branch}`")
    # Measure from where the branch left the default branch, so a stale base or a merge of
    # the default branch into this one changes nothing.
    base = p.git("merge-base", base, head).strip()
    failures += record_failures(p, raw, record_rel(branch, t), head)
    # Every live criterion is planned. `(?!\d)`: a row for AC10 is not a row for AC1.
    plan = kl.section(body, "Plan") or ""
    for n in t.live():
        if not re.search(re.escape(f"{tid}/AC{n}") + r"(?!\d)", plan):
            failures.append(f"Plan has no row for {tid}/AC{n}")
    # The final review ran on the code being merged and left no CRITICAL finding.
    failures += review_failures(p, body, base, head)
    # The ticket is done, or the description says why not and names the ticket holding the rest.
    if t.status != "done":
        others = [x for x in kl.TICKET_REF.findall(ticket_text) if x != tid]
        if t.status != "in-progress" or "in-progress" not in ticket_text or not others:
            failures.append(f"{tid} is `{t.status}`: set it to done, or say in Ticket why it stays in-progress "
                            "and name the ticket that holds the rest")
    # Tests came first and were not weakened. Tasks are tested first only when testable: a
    # task whose tests carry its tags is testable, so it needs the freeze like a story.
    freezes = freeze_commits(p, tid, base, head)
    now = tag_counts(p, head)
    tagged_task = t.type == "task" and any(x == tid for x, _ in now)
    if len(freezes) > 1:
        failures.append(f'{len(freezes)} commits named "{FREEZE_MSG.format(tid)}"; there must be exactly one')
    elif not freezes and (t.type == "story" or tagged_task):
        failures.append(f'no commit "{FREEZE_MSG.format(tid)}" on the branch: tests were not frozen before the implementation'
                        + (" (the task's tests carry its tags, so it is tested first)" if tagged_task else ""))
    elif freezes:
        freeze = freezes[0]
        for c in p.git("rev-list", f"{base}..{freeze}").split():
            for path in files_of(p, c):
                if kl.is_code(path, cfg):
                    failures.append(f"{path} changed in {c[:8]}, at or before the freeze commit: "
                                    "implementation must come after the failing tests")
        then = tag_counts(p, freeze)
        for n in t.live():
            if then[(tid, n)] < 1:
                failures.append(f"{tid}/AC{n} had no tagged test at the freeze commit")
            elif now[(tid, n)] < then[(tid, n)]:
                failures.append(f"{tid}/AC{n}: {then[(tid, n)]} tagged test(s) at the freeze, {now[(tid, n)]} now")
        # Only the branch's own commits: changes merged in from the default branch are not this one's.
        listed = listed_tokens(kl.section(body, "Test changes") or "")
        own = p.git("rev-list", f"{freeze}..{head}", f"^{base}").split()
        for path in sorted({f for c in own for f in files_of(p, c)}):
            if kl.is_test(path, cfg) and path not in listed and Path(path).name not in listed:
                failures.append(f'{path} changed after the freeze but is not listed under "Test changes"')
        for c in own:
            for path, line in skip_additions(p, c):
                failures.append(f"{c[:8]} adds a skipped or focused test in {path}: `{line[:70]}`")
    # The hotfix lane skips the plan review and questions round, so it must say why it was
    # used (a decision-log entry) and where the follow-up refinement lives.
    if t.fm.get("hotfix") is True:
        if not any(bc.LOG_REF.search(b) for b in kl.bullets(kl.section(body, "Decisions"))):
            failures.append('hotfix: "## Decisions" needs a bullet saying why the hotfix lane was used, ending "Log: <entry title>"')
        if not [x for x in kl.TICKET_REF.findall(kl.section(body, "Gaps found") or "") if x != tid]:
            failures.append('hotfix: "## Gaps found" must name the follow-up ticket')
    # With supervised autonomy a person approves the plan and the tests, by name.
    if cfg.autonomy == "supervised":
        for what in ("Plan", "Tests"):
            if not approved(plan, what):
                failures.append(f'autonomy is supervised: "## Plan" needs "{what} approved by: <name>"')
    return report(failures, f"pr: {tid}")


# --- gate merge ------------------------------------------------------------------------------

def default_base(p):
    """`origin/<default>` when it exists, else the local default branch (with a NOTE), else Stop.

    A project without an origin, or whose default branch was never pushed, can still run
    `gate pr` locally; CI and `gate merge` always have origin.
    """
    default = p.default_branch()
    if p.ok("rev-parse", "--verify", "--quiet", f"refs/remotes/origin/{default}"):
        return f"origin/{default}"
    if p.ok("rev-parse", "--verify", "--quiet", f"refs/heads/{default}"):
        print(f"NOTE origin/{default} does not exist: measuring from the local {default} branch")
        return default
    raise Stop(f"neither origin/{default} nor a local {default} branch exists: pass --base=<rev>")


def merge_failures(cr, head, default, word="change request"):
    """What the host's view of the change request says against merging it at `head`."""
    failures = []
    if head != cr.head_sha:
        failures.append(f"the merge pins {head[:8]}, but the {word}'s head is {cr.head_sha[:8]}: "
                        "wait for the checks on the new head, then merge with its sha")
    if cr.state != "open":
        failures.append(f"the {word} is {cr.state}")
    if cr.draft:
        failures.append(f"the {word} is a draft")
    if cr.base != default:
        failures.append(f"the {word} targets {cr.base}, not {default}")
    if cr.mergeable is False:
        failures.append(f"the host reports it cannot be merged ({cr.mergeable_detail}): "
                        f"merge origin/{default} into the branch, push, and wait for the check")
    elif cr.mergeable is None:
        failures.append(f"the host has not decided whether it can be merged ({cr.mergeable_detail}): wait and retry")
    if not any(c.name == "check" and c.state == "pass" for c in cr.checks):
        failures.append("no passing `check` job on the head commit")
    for c in cr.checks:
        if c.state in ("fail", "pending"):
            failures.append(f"check `{c.name}` is {'failing' if c.state == 'fail' else 'pending'}: "
                            "never merge on a failing or pending check")
    return failures


def gate_merge(p, number, head):
    """Run by the guard before the host's merge command. True when the merge may happen."""
    host = p.host
    if not host.cli:
        print("FAIL the host is manual: a person checks and merges the change request")
        return False
    try:
        cr = host.view(number)
    except (hosts.HostError, ValueError) as e:
        print(f"FAIL cannot read {host.word} {number}: {e}")
        return False
    default = p.default_branch()
    failures = merge_failures(cr, head, default, host.word)
    if kl.run(kl.git_argv("fetch", "-q", "origin", default), p.root).returncode:
        failures.append(f"could not fetch origin/{default}, so cannot tell whether the branch is up to date")
    # The gate reads the backlog from this checkout, so it must be the head being merged, unchanged.
    here = kl.run(kl.git_argv("rev-parse", "HEAD"), p.root).stdout.strip()
    dirty = kl.run(kl.git_argv("status", "--porcelain", "--untracked-files=no"), p.root).stdout.strip()
    if here != cr.head_sha or dirty:
        failures.append(f"run the merge from a clean checkout of the {host.word}'s head "
                        f"({cr.head_sha[:8]}, branch {cr.head_branch}), pushed")
        return report(failures, f"merge {number}")
    if not p.ok("merge-base", "--is-ancestor", f"origin/{default}", cr.head_sha):
        failures.append(f"the branch is behind origin/{default}: merge it in, push, and wait for the check")
    # What `backlog_check.py --pr-body` reports: the backlog's own errors and the description's.
    failures += [f"backlog: {where}: {msg}" for where, msg in p.backlog.errors]
    failures += [f"{where}: {msg}" for where, msg in bc.cr_body_errors(cr.body, p.backlog)]
    print(f"{host.word} {number} head {cr.head_sha[:8]}")
    if not gate_pr(p, cr.body, cr.head_branch, f"origin/{default}", cr.head_sha):
        failures.append("gate pr failed (above)")
    return report(failures, f"merge {number}")


def cmd_merge_command(p, number, head):
    try:
        argv = p.host.merge_argv(number, head)
    except ValueError as e:
        raise Stop(str(e))
    if argv is None:
        raise Stop("the host is manual: there is no merge command; a person merges the change request")
    print(" ".join(shlex.quote(a) for a in argv))
    if p.cfg.autonomy != "merge":
        print(f"NOTE autonomy is `{p.cfg.autonomy}`: a person runs this merge, not an agent", file=sys.stderr)
    return 0


# --- check -----------------------------------------------------------------------------------

def cmd_check(p):
    """What CI runs: the backlog check, every self-test, then check_command or the full test run."""
    py = sys.executable or "python3"
    steps = [("backlog_check", [py, str(SCRIPTS / "backlog_check.py")])]
    steps += [(f"self-test {name}", [py, str(SCRIPTS / f"{name}.py"), "--self-test"])
              for name in ("kitchen_lib", "hosts", "backlog_check", "deliver")]
    for name, cmd in steps:
        print(f"== {name}", flush=True)
        if subprocess.run(cmd, cwd=str(p.root)).returncode:
            print(f"FAIL {name}")
            return 1
    tmp = Path(tempfile.mkdtemp(prefix="kitchen-check-"))
    try:
        if p.cfg.check_command:
            name, cmd = "check_command", p.cfg.check_command
        else:
            # A full run: `{files}` is empty, so the command must run the whole suite.
            name, cmd = "test_command (full run)", kl.render_command(p.cfg.test_command, [], tmp / "report.xml")
        print(f"== {name}: {cmd}", flush=True)
        code = subprocess.run(cmd, shell=True, cwd=str(p.root)).returncode
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if code:
        print(f"FAIL {name} exited {code}")
        return 1
    print("PASS check")
    return 0


# --- status ----------------------------------------------------------------------------------

def origin_tracking(p):
    """Branches origin had at the last fetch (local remote-tracking refs: no network)."""
    out = kl.run(kl.git_argv("for-each-ref", "--format=%(refname)", "refs/remotes/origin/"), p.root).stdout
    return {line[len("refs/remotes/origin/"):] for line in out.splitlines() if line != "refs/remotes/origin/HEAD"}


def last_deliveries(p, limit=5):
    """[(date, record path)] of the most recently committed delivery records, newest first.

    Read with -z, so record paths with spaces or non-ASCII names count. Each commit starts
    with a \\x01-marked date token; the names that follow are NUL-separated.
    """
    out = kl.run(kl.git_argv("log", "-z", "--no-renames", "--format=%x01%cs", "--name-only", "--diff-filter=AM",
                             "--", "backlog"), p.root).stdout
    seen, date = {}, ""
    for token in out.split("\0"):
        token = token.strip("\n")
        if token.startswith("\x01"):
            date, _, token = token[1:].partition("\n")
        if token and "/delivery/" in f"/{token}" and token.endswith(".md") and token not in seen \
                and (p.root / token).exists():
            seen[token] = date
    return sorted(((d, f) for f, d in seen.items()), key=lambda x: x[0], reverse=True)[:limit]


def cmd_status(p):
    bl = p.backlog
    tickets = bl.tickets
    work = {tid: t for tid, t in tickets.items() if t.type != "epic"}
    counts = Counter(t.status for t in work.values())
    print("STATUS " + "  ".join(f"{s}: {counts[s]}" for s in bc.STATUS)
          + (f"  ({len(bl.errors)} backlog error(s): run scripts/backlog_check.py)" if bl.errors else ""))
    pushed = origin_tracking(p)
    # The same claims as `next`, so a ticket someone holds is not shown as ready. Without the
    # host CLI (offline), the branches origin had at the last fetch stand in.
    try:
        held = p.host.open_branches()
    except hosts.HostError as e:
        held = pushed
        print(f"NOTE claimed branches read from the last fetch: {str(e).splitlines()[0]}")
    ready, waiting, decide, drafts = plan_next(p, held, me_of(p))
    print("\nREADY (in `next` order)")
    for tid in ready:
        print(f"  {tid} {tickets[tid].title}")
    print("\nIN PROGRESS")
    for tid, t in sorted(work.items(), key=lambda x: kl.ticket_sort_key(x[0])):
        if t.status == "in-progress":
            print(f"  {tid} {t.title} (branch `{t.branch}`, {'on origin' if t.branch in pushed else 'not on origin'})")
    print("\nBLOCKED")
    for tid, t in sorted(work.items(), key=lambda x: kl.ticket_sort_key(x[0])):
        open_b = [b for b in t.list("blocked_by") if b not in tickets or tickets[b].status != "done"]
        if t.status not in ("done", "deferred") and open_b:
            print(f"  {tid} {t.title}: blocked by {', '.join(open_b)}")
    print("\nOPEN DECISIONS AND SPIKES")
    for tid, t in sorted(work.items(), key=lambda x: kl.ticket_sort_key(x[0])):
        if t.type in ("decision", "spike") and t.status not in ("done", "deferred"):
            print(f"  {tid} {t.title} ({t.status})")
    found = bc.gaps(bl)
    print(f"\nGAPS {len(found)}" + (" (backlog_check.py --gaps lists them all)" if len(found) > 5 else ""))
    for where, msg in found[:5]:
        print(f"  {where}: {msg}")
    print(f"\nTEST DEBT {len(bl.debt)}")
    print("\nLAST DELIVERIES")
    for date, rel in last_deliveries(p):
        print(f"  {date} {rel}")
    return 0


# --- release notes ---------------------------------------------------------------------------

SO_THAT = re.compile(r"^As an? .*?\bso that (.+?)\s*$", re.M)


def outcome(t):
    """A story's "so that …" outcome as written (first letter capitalized), or its title."""
    m = SO_THAT.search(t.body)
    text = m.group(1).rstrip(".").strip() if m else t.title
    return text[:1].upper() + text[1:]


def cmd_release_notes(p, slice_=None):
    bl, cfg = p.backlog, p.cfg
    done = [t for t in bl.tickets.values() if t.type in bc.WITH_CRITERIA and t.status == "done"]
    if slice_:
        if not cfg.releases:
            raise Stop("kitchen.yml lists no releases, so there are no slices")
        if slice_ not in cfg.releases:
            raise Stop(f"`{slice_}` is not in kitchen.yml releases {cfg.releases}")
        chosen, heading = [t for t in done if t.fm.get("release") == slice_], f"# Release notes: {slice_}"
    else:
        tag = kl.run(kl.git_argv("describe", "--tags", "--abbrev=0"), p.root).stdout.strip()
        if tag:
            added = [f for f in p.git("diff", "--name-only", "-z", "--no-renames", "--diff-filter=A", tag, "HEAD", "--",
                                      "backlog").split("\0") if f]
            ids = {re.sub(r"-cr\d+$", "", Path(f).stem) for f in added if "/delivery/" in f"/{f}"}
            chosen, heading = [t for t in done if t.id in ids], f"# Release notes since {tag}"
        else:
            chosen, heading = done, "# Release notes"
    print(heading + "\n")
    if not chosen:
        print("No changes.")
        return 0
    by_epic, other = defaultdict(list), []
    for t in sorted(chosen, key=lambda x: kl.ticket_sort_key(x.id)):
        if t.type == "task" or t.fm.get("hotfix") is True:
            other.append(f"- {t.title} ({t.id}{', hotfix' if t.fm.get('hotfix') is True else ''})")
        else:
            by_epic[str(t.fm.get("epic") or "")].append(f"- {outcome(t)}. ({t.id})")
    for epic in sorted(by_epic, key=kl.ticket_sort_key):
        e = bl.tickets.get(epic)
        print(f"## {e.title if e else epic}\n\n" + "\n".join(by_epic[epic]) + "\n")
    if other:
        print("## Other changes\n\n" + "\n".join(other) + "\n")
    return 0


# --- self-test -------------------------------------------------------------------------------

RUNNER = '''"""Fixture test runner: each line `<test name> pass|fail` in a test file is a test case."""
import sys
from xml.sax.saxutils import quoteattr
report, files = sys.argv[1], sys.argv[2:]
cases = []
for f in files:
    for line in open(f):
        if line.strip():
            name, outcome = line.split()
            body = "<failure message='x'/>" if outcome == "fail" else ""
            cases.append("<testcase classname=%s name=%s>%s</testcase>" % (quoteattr(f), quoteattr(name), body))
open(report, "w").write("<testsuite>%s</testsuite>" % "".join(cases))
sys.exit(1 if any("failure" in c for c in cases) else 0)
'''


def self_test():
    """Walk one story through next, gate red, record, and gate pr in a temporary git repository."""
    failures = []
    saved = dict(os.environ)
    # The fixture must not depend on the person's git configuration (signing, hooks, names).
    os.environ.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                       "GIT_AUTHOR_NAME": "Self Test", "GIT_AUTHOR_EMAIL": "self-test@example.invalid",
                       "GIT_COMMITTER_NAME": "Self Test", "GIT_COMMITTER_EMAIL": "self-test@example.invalid"})
    tmp = Path(tempfile.mkdtemp(prefix="kitchen-deliver-self-test-"))
    out = io.StringIO()
    real_stdout = sys.stdout
    try:
        root = tmp / "project"
        files = dict(bc.FIXTURE)
        # A JSON string is a valid YAML double-quoted scalar, whatever the interpreter's path holds.
        command = json.dumps(f"{shlex.quote(sys.executable)} tools/runner.py {{report}} {{files}}")
        files["kitchen.yml"] = f'tests: ["tests/**"]\ncode: ["src/**"]\nhost: manual\ntest_command: {command}\n'
        story = files.pop("backlog/PAY-payments/US-PAY-01-refund-limit.md")
        files.pop("tests/test_refund.py")
        files.pop("src/refund.py")
        files["tools/runner.py"] = RUNNER
        files["backlog/PAY-payments/US-PAY-01-refund-limit.md"] = story.replace("status: done", "status: ready")
        for rel, text in files.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")

        def git(*args):
            return kl.git(root, *args).strip()

        def commit(msg):
            git("add", "-A")
            git("commit", "-q", "-m", msg)
            return git("rev-parse", "HEAD")

        git("init", "-q")
        git("symbolic-ref", "HEAD", "refs/heads/main")
        base = commit("chore: fixture")
        sys.stdout = out
        p = Project(root)
        ready = plan_next(p, set(), "")[0]
        if ready != ["US-PAY-01"]:
            failures.append(f"next: got {ready}, want ['US-PAY-01']")
        git("checkout", "-q", "-b", "us-pay-01-refund-limit")
        path = root / "backlog/PAY-payments/US-PAY-01-refund-limit.md"
        path.write_text(story.replace("status: done", "status: in-progress"), encoding="utf-8")
        commit("chore: start US-PAY-01")
        (root / "tests").mkdir()
        (root / "tests/refund.txt").write_text("test_us_pay_01_ac1_refused fail\n")
        commit("test: US-PAY-01 failing tests")
        if not gate_red(Project(root), "US-PAY-01"):
            failures.append("gate red did not pass on a failing tagged test")
        (root / "src").mkdir()
        (root / "src/refund.py").write_text("# Refund rules (US-PAY-01).\n")
        (root / "tests/refund.txt").write_text("test_us_pay_01_ac1_refused pass\n")
        path.write_text(story, encoding="utf-8")
        reviewed = commit("feat: US-PAY-01 refund limit")
        body = (f"## Ticket\n\nUS-PAY-01 Refund limit.\n\n## Plan\n\n| US-PAY-01/AC1 | t |\n\n## Gaps found\n\n- None\n\n"
                f"## Decisions\n\n- None\n\n## Platform changes\n\n- None\n\n"
                f"## Test changes\n\n- `tests/refund.txt`: the implementation makes it pass\n\n"
                f"## Review report\n\nReviewed commit: {reviewed}\nCRITICAL: 0, WARNING: 0, SUGGESTION: 0\n")
        p = Project(root)
        cmd_record(p, body, "us-pay-01-refund-limit")
        commit("docs: delivery record")
        if not gate_pr(Project(root), body, "us-pay-01-refund-limit", base, "HEAD"):
            failures.append("gate pr did not pass on a branch that follows the workflow")
        if gate_pr(Project(root), body.replace("CRITICAL: 0", "CRITICAL: 1"), "us-pay-01-refund-limit", base, "HEAD"):
            failures.append("gate pr passed with a CRITICAL finding")
    except Exception as e:  # a self-test reports, it does not crash
        failures.append(f"{type(e).__name__}: {e}")
    finally:
        sys.stdout = real_stdout
        os.environ.clear()
        os.environ.update(saved)
        shutil.rmtree(tmp, ignore_errors=True)
    if failures:
        print(out.getvalue())
    return failures


# --- command line ----------------------------------------------------------------------------

# Options each command accepts, so a misspelled option is an error rather than ignored.
OPTIONS = {
    ("record",): {"body-file", "branch", "cr", "url"},
    ("gate", "pr"): {"body-file", "from-record", "branch", "base", "head"},
    ("gate", "merge"): {"head"},
    ("merge-command",): {"head"},
}


def usage():
    print(__doc__, file=sys.stderr)
    return 2


def main(argv):
    opts, pos = {}, []
    for a in argv:
        if a.startswith("--"):
            k, eq, v = a[2:].partition("=")
            opts[k] = v if eq else True
        else:
            pos.append(a)
    if opts == {"self-test": True} and not pos:
        problems = self_test()
        for f in problems:
            print("FAIL", f)
        print("PASS self-test" if not problems else f"FAIL self-test: {len(problems)} failure(s)")
        return 1 if problems else 0
    action = parse(pos, opts)
    if action is None:
        return usage()
    try:
        return action(Project())
    except (Stop, kl.ConfigError, kl.GitError, hosts.HostError, OSError) as e:
        for line in str(e).splitlines() or [type(e).__name__]:
            print("FAIL", line)
        return 1


def parse(pos, opts):
    """The command line as a function of the Project, or None for a usage error (checked before
    kitchen.yml is read, so a typo is reported as one)."""
    cmd = tuple(pos[:2]) if pos[:1] == ["gate"] else tuple(pos[:1])
    if any(k not in OPTIONS.get(cmd, set()) for k in opts):
        return None
    text = lambda k: isinstance(opts.get(k), str) and bool(opts[k])  # noqa: E731
    if pos == ["next"]:
        return cmd_next
    if len(pos) == 2 and pos[0] == "context":
        return lambda p: cmd_context(p, pos[1])
    if len(pos) == 2 and pos[0] == "pr-body":
        return lambda p: cmd_pr_body(p, pos[1])
    if len(pos) == 3 and pos[:2] == ["gate", "red"]:
        return lambda p: 0 if gate_red(p, pos[2]) else 1
    if pos == ["record"] and text("body-file") and text("branch"):
        return lambda p: cmd_record(p, Path(opts["body-file"]).read_text(encoding="utf-8"), opts["branch"],
                                    opts.get("cr"), opts.get("url"))
    if pos == ["gate", "pr"] and text("branch") and text("body-file") != (opts.get("from-record") is True):
        def gate_pr_cmd(p):
            base = opts.get("base") or default_base(p)
            head = opts.get("head") or "HEAD"
            if opts.get("from-record"):
                body = body_from_record(p, opts["branch"], base, head)
            else:
                body = Path(opts["body-file"]).read_text(encoding="utf-8")
            return 0 if gate_pr(p, body, opts["branch"], base, head) else 1
        return gate_pr_cmd
    # A merge is pinned to a full sha: an abbreviated one could match a commit pushed later.
    if len(pos) == 3 and pos[:2] == ["gate", "merge"] and pos[2].isdigit() and FULL_SHA.match(str(opts.get("head", ""))):
        return lambda p: 0 if gate_merge(p, pos[2], opts["head"]) else 1
    if len(pos) == 2 and pos[0] == "merge-command" and text("head"):
        return lambda p: cmd_merge_command(p, pos[1], opts["head"])
    if pos == ["check"]:
        return cmd_check
    if pos == ["status"]:
        return cmd_status
    if pos[:1] == ["release-notes"] and len(pos) <= 2:
        return lambda p: cmd_release_notes(p, pos[1] if len(pos) == 2 else None)
    return None


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
