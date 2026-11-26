# test-kitchen: no-trace (this file describes TODO markers and example tickets; its text is not trace)
"""Shared library of the Test Kitchen scripts: configuration, paths, globs, tags, ticket IDs, git.

`backlog_check.py`, `deliver.py`, `hosts.py`, and the Claude Code guard all import this
module, so each rule it holds (where the repository root is, what `kitchen.yml` may say,
what a test file is, what a test tag looks like, what a ticket ID looks like) is defined
once and every tool reads it the same way.

Usage as a library (from any directory):

    import sys; sys.path.insert(0, "<project>/scripts")
    import kitchen_lib
    root = kitchen_lib.repo_root()                 # the git top level of the scripts' project
    cfg = kitchen_lib.load_config(root)            # raises kitchen_lib.ConfigError
    kitchen_lib.is_test("tests/test_pay.py", cfg)  # True / False, ignore-aware
    kitchen_lib.find_tags("test_us_pay_03_ac2_x")  # [("US-PAY-03", 2)]

Usage from the command line:

    python3 scripts/kitchen_lib.py --self-test   # prints "PASS self-test" or the failures; exit 0/1
    python3 scripts/kitchen_lib.py --config      # prints the loaded kitchen.yml, or its errors; exit 0/1

Standard library plus PyYAML (imported lazily, so `repo_root` and the glob and tag helpers
work without it). Python 3.9 compatible.
"""
from __future__ import annotations

import functools
import json
import os
import posixpath
import re
import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import FrozenSet, List, Optional, Tuple

CONFIG_FILE = "kitchen.yml"
LOCK_FILE = "kitchen.lock"
# init.py offers an edited framework file's new version next to it under this suffix.
NEW_SUFFIX = ".kitchen-new"

# --- identifiers ----------------------------------------------------------------------
#
# An epic code (`PAY`, `AUTH`, `CI2`) is an upper-case letter followed by 1 to 9 upper-case
# letters or digits: short enough to read in a branch name, long enough to be meaningful.
CODE = r"[A-Z][A-Z0-9]{1,9}"
CODE_RE = re.compile(rf"^{CODE}$")
# Ticket IDs: `EP-PAY` for epics; `US-PAY-03`, `TASK-PAY-03`, `DEC-PAY-03`, `SPK-PAY-03`
# for the rest (two or more digits, so `-03` sorts and reads the same everywhere).
TICKET_ID = re.compile(rf"^(?:(EP)-({CODE})|(US|TASK|DEC|SPK)-({CODE})-(\d{{2,}}))$")
# A ticket ID mentioned in free text. Not preceded by a word character or `-` (so
# `XUS-PAY-03` is not a mention), and an epic ID not followed by `-` (so the `EP-PAY` in
# `EP-PAY-01`, which is no valid ID, is not one either).
TICKET_REF = re.compile(rf"(?<![\w-])(?:EP-{CODE}(?![\w-])|(?:US|TASK|DEC|SPK)-{CODE}-\d{{2,}}(?!\w))")
# Requirement IDs (`PAY-R03`) and requirement lines (`- PAY-R03: <text>`), the only form
# docs/requirements/*.md defines requirements in; other text in those files is free.
REQ_ID = re.compile(rf"(?<![\w-]){CODE}-R\d{{2,}}(?!\w)")
REQ_LINE = re.compile(rf"^- ({CODE}-R\d{{2,}}):[ \t]*(.*)$", re.M)
# A criterion reference: `US-PAY-03/AC2`, `TASK-CI-01/AC1`.
AC_REF = re.compile(rf"(?<![\w-])((?:US|TASK)-{CODE}-\d{{2,}})/AC(\d+)(?!\d)")
# HTML comments in markdown (template hints) are not content.
COMMENT = re.compile(r"<!--.*?-->", re.S)

PREFIX = {"epic": "EP", "story": "US", "task": "TASK", "decision": "DEC", "spike": "SPK"}
TYPE_OF_PREFIX = {v: k for k, v in PREFIX.items()}


def parse_ticket_id(tid):
    """`US-PAY-03` -> ("US", "PAY", "03"); `EP-PAY` -> ("EP", "PAY", None); else None."""
    m = TICKET_ID.match(str(tid or ""))
    if not m:
        return None
    if m.group(1):
        return m.group(1), m.group(2), None
    return m.group(3), m.group(4), m.group(5)


def ticket_sort_key(tid):
    """Natural order for IDs: `US-PAY-9` style numbers compare as numbers, not text."""
    p = parse_ticket_id(tid)
    if not p:
        return ("~", str(tid), 0)
    return (p[0] + "-" + p[1], "", int(p[2]) if p[2] else -1)


# --- test tags ------------------------------------------------------------------------
#
# A test proves a criterion by carrying its tag in the test's name as the runner reports
# it (JUnit XML). Two equivalent forms exist because many languages (Python, Go, Java)
# report function names, which cannot hold brackets:
#   canonical:  [US-PAY-03/AC2]   anywhere in the test name or a describe/class name
#   identifier: us_pay_03_ac2     any case: test_us_pay_03_ac2_refund, TestUS_PAY_03_AC2
TAG_CANONICAL = re.compile(rf"\[((?:US|TASK)-{CODE}-\d{{2,}})/AC(\d+)\]")
TAG_IDENTIFIER = re.compile(r"(us|task)_([a-z][a-z0-9]{1,9})_(\d{2,})_ac(\d+)(?![a-z0-9])", re.I)


# A file whose first lines hold this marker (in any comment syntax) is data, not
# trace: its text is never scanned for tags, TODOs, or DEC mentions, and tags in it
# never prove a criterion. It exists for tests of tools that handle tickets (Test
# Kitchen's own tests are full of example tickets), whose text would otherwise be
# read as real references. Gates still see changes to the file: it stays a test or
# code file for the freeze and review checks.
NO_TRACE = "test-kitchen: no-trace"
NO_TRACE_LINES = 10


def no_trace(text):
    """True when `text` carries the no-trace marker in its first lines."""
    return any(NO_TRACE in line for line in (text or "").splitlines()[:NO_TRACE_LINES])


def trace_text(text):
    """The text the trace scans read: empty for a no-trace file."""
    return "" if no_trace(text) else (text or "")


def find_tags(text):
    """Every tag in `text`, both forms, in order: [("US-PAY-03", 2), ...] (duplicates kept).

    The identifier form must be bounded: on the right by a non-alphanumeric character or
    the end; on the left by the start, a non-alphanumeric character, or a case change into
    an upper-case prefix (so `TestUS_PAY_03_AC2`, Go's naming style, counts, while
    `focus_pay_03_ac2` and `bonus_pay_03_ac2` do not).
    """
    found = []
    for m in TAG_CANONICAL.finditer(text):
        found.append((m.start(), m.group(1), int(m.group(2))))
    for m in TAG_IDENTIFIER.finditer(text):
        s = m.start()
        prev = text[s - 1] if s else ""
        if prev and prev.isalnum() and not ((prev.islower() or prev.isdigit()) and text[s].isupper()):
            continue
        tid = f"{m.group(1).upper()}-{m.group(2).upper()}-{m.group(3)}"
        found.append((s, tid, int(m.group(4))))
    return [(tid, n) for _, tid, n in sorted(found, key=lambda x: x[0])]


# --- globs ------------------------------------------------------------------------------

@functools.lru_cache(maxsize=None)
def glob_to_regex(pattern):
    """Compile a `kitchen.yml` glob into a regex matched against a whole repository path.

    `**` matches any number of path segments, including none (`tests/**`, `**/*.test.ts`,
    `src/**/x.py` also match `src/x.py`); `*` matches anything but `/`; `?` one character
    but `/`. Everything else is literal: no `[...]` classes and no `{a,b}` alternatives,
    so a pattern means the same thing in every shell and language. A leading `./` is ignored.
    """
    p = pattern.strip()
    while p.startswith("./"):
        p = p[2:]
    out, i, n = [], 0, len(p)
    while i < n:
        if p.startswith("/**", i) and i + 3 == n:
            out.append("(?:/.*)?")  # trailing `/**`: the folder's whole tree
            break
        if p.startswith("**", i):
            seg_start = i == 0 or p[i - 1] == "/"
            if seg_start and p.startswith("/", i + 2):
                out.append("(?:.*/)?")  # `**/`: zero or more whole segments
                i += 3
                continue
            out.append(".*")  # a bare `**` (whole pattern, or inside a segment)
            i += 2
            continue
        c = p[i]
        out.append("[^/]*" if c == "*" else "[^/]" if c == "?" else re.escape(c))
        i += 1
    return re.compile("".join(out) + r"\Z")


def matches(path, patterns):
    """True when the repository-relative path matches any of the globs."""
    path = str(path).replace(os.sep, "/")
    while path.startswith("./"):
        path = path[2:]
    return any(glob_to_regex(p).match(path) for p in patterns or [])


def is_ignored(path, cfg):
    """Excluded from every scan: matches `ignore`, or is a Test Kitchen framework file (kitchen.lock).

    Framework files are excluded even when the project's globs cover them (`code:
    ["**/*.py"]` covers scripts/*.py): their TODO and DEC example strings are not the
    project's code, and their changes arrive through init.py update, not through tickets.
    """
    path = str(path).replace(os.sep, "/")
    return path in cfg.framework or matches(path, cfg.ignore)


def is_test(path, cfg):
    """A test file (or test helper): matches `tests` and is not ignored."""
    return not is_ignored(path, cfg) and matches(path, cfg.tests)


def is_code(path, cfg):
    """Product code: matches `code`, is not ignored, and not `tests` (a file matching both is a test)."""
    return not is_ignored(path, cfg) and not matches(path, cfg.tests) and matches(path, cfg.code)


# --- configuration ----------------------------------------------------------------------

class ConfigError(Exception):
    """kitchen.yml is missing or invalid; the message lists every problem, one per line."""


HOSTS = ("github", "gitlab", "manual")
AUTONOMY = ("merge", "pr", "supervised")


@dataclass
class Config:
    """The project's kitchen.yml, validated, with defaults filled in (guide/configuration.md)."""
    tests: List[str]
    code: List[str]
    test_command: str
    check_command: Optional[str] = None
    verify: Optional[str] = None
    host: str = "manual"
    host_detected: bool = True  # True when `host` was not in kitchen.yml and came from the origin URL
    autonomy: str = "merge"
    split_threshold: int = 6
    self_contained_tickets: bool = False
    releases: Optional[List[str]] = None  # None: release slices are off
    ignore: List[str] = field(default_factory=list)
    # Not a kitchen.yml key: the framework files kitchen.lock lists (and their `.kitchen-new`
    # copies), excluded from every scan like `ignore`. Empty when there is no lock.
    framework: FrozenSet[str] = frozenset()


KNOWN_KEYS = ("tests", "code", "test_command", "check_command", "verify", "host", "autonomy",
              "split_threshold", "self_contained_tickets", "releases", "ignore")


def _yaml():
    try:
        import yaml  # noqa: WPS433 (lazy: repo_root and globs must work without PyYAML)
    except ImportError:
        raise ConfigError("PyYAML is required: install it with `python3 -m pip install pyyaml`")
    return yaml


def _globs(data, key, errors, required):
    if key not in data:
        if required:
            errors.append(f"`{key}` is required: a list of globs, e.g. {key}: [\"{'tests/**' if key == 'tests' else 'src/**'}\"]")
        return []
    v = data[key]
    if not isinstance(v, list) or not v and required or not all(isinstance(g, str) and g.strip() for g in v):
        errors.append(f"`{key}` must be a {'non-empty ' if required else ''}list of glob strings, got {v!r}")
        return []
    # Paths are compared with `/` on every system; a backslash would silently match nothing.
    bad = [g for g in v if "\\" in g]
    if bad:
        errors.append(f"`{key}` globs use `/` between folders, never a backslash: {bad!r}")
    # Paths are relative to the repository root, so a glob starting with `/` would also
    # silently match nothing. It is judged after trimming and removing one leading `./`,
    # the same normalization matching applies, and listed as written (CONF-R28, US-CONF-17).
    rooted = [g for g in v if _without_dot_slash(g.strip()).startswith("/")]
    if rooted:
        errors.append(f"`{key}` globs are relative to the repository root and never start with `/`: {rooted!r}")
    if bad or rooted:
        return []  # every problem is reported at once (CONF-R05), so both checks run first
    return [g.strip() for g in v]


def _without_dot_slash(glob):
    """`glob` without one leading `./`."""
    return glob[2:] if glob.startswith("./") else glob


def _text(data, key, errors, required=False):
    if key not in data or data[key] is None:
        if required:
            errors.append(f"`{key}` is required: a shell command run from the repository root")
        return None
    v = data[key]
    if not isinstance(v, str) or not v.strip():
        errors.append(f"`{key}` must be a non-empty string, got {v!r}")
        return None
    return v.strip()


def parse_config(data, root=None):
    """Validate a kitchen.yml mapping and return a Config; raise ConfigError listing every problem.

    Unknown keys are errors (typo protection: a misspelled optional key would otherwise be
    ignored silently and its default used).
    """
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ConfigError(f"{CONFIG_FILE}: must be a mapping of keys to values")
    errors = []
    for key in data:
        if key not in KNOWN_KEYS:
            errors.append(f"unknown key `{key}` (known: {', '.join(KNOWN_KEYS)})")
    tests = _globs(data, "tests", errors, True)
    code = _globs(data, "code", errors, True)
    ignore = _globs(data, "ignore", errors, False)
    test_command = _text(data, "test_command", errors, required=True)
    check_command = _text(data, "check_command", errors)
    verify = _text(data, "verify", errors)
    host, detected = data.get("host"), "host" not in data or data.get("host") is None
    if detected:
        host = detect_host(root) if root is not None else "manual"
    elif host not in HOSTS:
        errors.append(f"`host` must be one of {', '.join(HOSTS)}, got {host!r}")
    autonomy = data.get("autonomy", "merge")
    if autonomy not in AUTONOMY:
        errors.append(f"`autonomy` must be one of {', '.join(AUTONOMY)}, got {autonomy!r}")
    split = data.get("split_threshold", 6)
    # bool is an int subclass in Python: `split_threshold: true` must not read as 1.
    if isinstance(split, bool) or not isinstance(split, int) or split < 1:
        errors.append(f"`split_threshold` must be a positive whole number, got {split!r}")
    self_contained = data.get("self_contained_tickets", False)
    if not isinstance(self_contained, bool):
        errors.append(f"`self_contained_tickets` must be true or false, got {self_contained!r}")
    releases = data.get("releases")
    if releases is not None:
        # Slice names are compared as text; YAML would read `[1, 2]` as numbers.
        if not isinstance(releases, list) or not releases or not all(isinstance(r, str) and r.strip() for r in releases):
            errors.append(f"`releases` must be a non-empty list of slice names (remove the key to turn slices off), got {releases!r}")
            releases = None
        elif len(set(releases)) != len(releases):
            errors.append(f"`releases` lists a slice twice: {releases!r}")
    if errors:
        raise ConfigError("\n".join(f"{CONFIG_FILE}: {e}" for e in errors))
    return Config(tests=tests, code=code, test_command=test_command, check_command=check_command,
                  verify=verify, host=host, host_detected=detected, autonomy=autonomy,
                  split_threshold=split, self_contained_tickets=self_contained,
                  releases=list(releases) if releases else None, ignore=ignore)


def load_config(root):
    """Read and validate `<root>/kitchen.yml`. The host is detected from origin when absent.

    A missing file, a file that is not UTF-8, invalid YAML, or invalid values raise
    ConfigError, whose text lists every problem, one per line.

    The framework files kitchen.lock lists are loaded into `Config.framework`.
    """
    path = Path(root) / CONFIG_FILE
    if not path.is_file():
        raise ConfigError(f"{CONFIG_FILE}: not found at {path}; run init.py to install Test Kitchen")
    yaml = _yaml()
    # Only the read can fail on encoding: a file saved as Latin-1 or UTF-16 is one clear
    # configuration error, not a traceback (CONF-R26; US-CONF-16/AC1).
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise ConfigError(f"{CONFIG_FILE}: not valid UTF-8")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise ConfigError(f"{CONFIG_FILE}: invalid YAML: {e}")
    cfg = parse_config(data, root)
    cfg.framework = framework_files(root)
    return cfg


def framework_files(root):
    """Paths kitchen.lock lists under `files` (JSON written by init.py), plus their `.kitchen-new` copies.

    No lock: nothing is excluded. A lock that is not valid JSON raises ConfigError rather
    than silently scanning the framework's own files.
    """
    path = Path(root) / LOCK_FILE
    if not path.is_file():
        return frozenset()
    try:
        files = json.loads(path.read_text(encoding="utf-8")).get("files") or {}
    except (ValueError, AttributeError) as e:
        raise ConfigError(f"{LOCK_FILE}: not valid JSON ({e}); restore it from git history")
    if not isinstance(files, dict):
        raise ConfigError(f"{LOCK_FILE}: `files` is not a table of path to sha256; restore it from git history")
    names = {str(f).replace(os.sep, "/") for f in files}
    return frozenset(names | {n + NEW_SUFFIX for n in names})


# --- test commands ----------------------------------------------------------------------

PLACEHOLDER = re.compile(r"\{(files(?::[^{}]*)?|report)\}")


def render_command(command, files, report):
    """Fill `test_command` placeholders.

    `{files}`: the files, shell-quoted, root-relative, space-separated (empty for a full run);
    `{files:<dir>}`: the same paths relative to `<dir>` (for a runner started inside a
    subfolder: `cd app && npx vitest run {files:app}`); `{report}`: the JUnit XML path.
    Other braces (`${VAR}`, `{a,b}`) are left to the shell.
    """
    def sub(m):
        key = m.group(1)
        if key == "report":
            return shlex.quote(str(report))
        base = key.partition(":")[2].strip().strip("/")
        paths = [posixpath.relpath(f, base) if base else f for f in files]
        return " ".join(shlex.quote(p) for p in paths)
    return PLACEHOLDER.sub(sub, command)


# --- git and paths ----------------------------------------------------------------------

class GitError(Exception):
    """A git command the scripts depend on failed."""


def run(cmd, cwd, env=None, input=None):
    """Run a command without a shell and capture its output as text."""
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, env=env, input=input)


# Every git call the scripts parse runs with these settings, so the person's own git
# configuration cannot change what the scripts read: paths are never octal-quoted
# (core.quotePath), output is never colored, and `log` never adds signature lines.
# Diff commands also pass --no-color/--no-ext-diff and read paths with -z.
GIT_SAFE = ("-c", "core.quotePath=false", "-c", "color.ui=never", "-c", "log.showSignature=false")


def git_argv(*args):
    """argv for `git <args>` with GIT_SAFE settings."""
    return ["git", *GIT_SAFE, *args]


def git(root, *args):
    """`git <args>` in root; its stdout, or GitError with git's message."""
    r = run(git_argv(*args), root)
    if r.returncode:
        raise GitError(f"git {' '.join(args)} failed: {(r.stderr or r.stdout).strip()}")
    return r.stdout


def repo_root(start=None):
    """The repository root: `git rev-parse --show-toplevel` from `start`, else the parent of scripts/.

    `start` defaults to this file's folder, not the current directory, so a script finds
    its own project from any working directory (even one inside another repository).
    """
    here = Path(__file__).resolve().parent
    start = Path(start) if start else here
    if start.is_file():
        start = start.parent
    if start.is_dir():
        r = run(["git", "rev-parse", "--show-toplevel"], start)
        if r.returncode == 0 and r.stdout.strip():
            return Path(r.stdout.strip()).resolve()
    return here.parent


def detect_host(root):
    """The host named by the origin remote's URL: github.com -> github, "gitlab" -> gitlab, else manual."""
    r = run(git_argv("config", "--get", "remote.origin.url"), root)
    url = r.stdout.strip().lower() if r.returncode == 0 else ""
    if "github.com" in url:
        return "github"
    if "gitlab" in url:
        return "gitlab"
    return "manual"


def default_branch(root):
    """The default branch: origin/HEAD when set, else `main`, else `master`, else "main"."""
    r = run(git_argv("symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"), root)
    if r.returncode == 0 and r.stdout.strip().startswith("refs/remotes/origin/"):
        return r.stdout.strip()[len("refs/remotes/origin/"):]
    for name in ("main", "master"):
        for ref in (f"refs/remotes/origin/{name}", f"refs/heads/{name}"):
            if run(git_argv("rev-parse", "--verify", "--quiet", ref), root).returncode == 0:
                return name
    return "main"


def tracked_files(root, rev=None):
    """Repository-relative file paths ('/'-separated), sorted.

    Without `rev`: the working tree's tracked files plus untracked files git does not
    ignore (a test written but not yet added still counts), skipping deleted ones. With
    `rev`: the files (blobs) in that commit. Outside a git repository: every file under
    root except hidden folders.
    """
    root = Path(root)
    if rev:
        out = git(root, "ls-tree", "-r", "-z", "--full-tree", rev)
        files = []
        for entry in out.split("\0"):
            meta, _, path = entry.partition("\t")
            if path and meta.split(" ")[1:2] == ["blob"]:
                files.append(path)
        return sorted(files)
    r = run(git_argv("ls-files", "-z", "--cached", "--others", "--exclude-standard"), root)
    if r.returncode == 0:
        return sorted({p for p in r.stdout.split("\0") if p and (root / p).is_file()})
    files = []
    for d, dirs, names in os.walk(root):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        files += [Path(d, n).relative_to(root).as_posix() for n in names]
    return sorted(files)


def read_text(path):
    """A file's text with Windows line endings normalized, or None for an unreadable or binary file."""
    try:
        return Path(path).read_text(encoding="utf-8").replace("\r\n", "\n")
    except (UnicodeDecodeError, OSError):
        return None


# --- markdown -----------------------------------------------------------------------------

def parse_frontmatter(text):
    """Split `---` YAML frontmatter from a markdown body: (dict or None, body).

    Returns (None, text) when there is no frontmatter block; raises yaml.YAMLError when the
    block is not valid YAML. CRLF files read the same as LF files.
    """
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 3)
    if end < 0:
        if text.endswith("\n---"):
            end = len(text) - 4
        else:
            return None, text
    data = _yaml().safe_load(text[4:end]) if end > 3 else None
    return (data if data is not None else {}), text[end + 5:]


def section(text, name):
    """The text under `## <name>` up to the next `## ` heading, or None when there is no such section."""
    m = re.search(rf"^## {re.escape(name)}[ \t]*\n(.*?)(?=^## |\Z)", text.replace("\r\n", "\n"), re.S | re.M)
    return m.group(1) if m else None


def bullets(text):
    """Top-level `- ` bullets of a section, without the marker."""
    return [line[2:].strip() for line in (text or "").splitlines() if line.startswith("- ")]


# A delivery record (`deliver.py record`) is a short header, this marker line, then the
# change request's description verbatim. `<!-- pr-description -->` is read as the same
# marker, so a record written with the GitHub-flavored name still counts.
RECORD_MARKER = "<!-- change-request-description -->"
RECORD_MARKER_LINE = re.compile(r"^<!-- (?:change-request|pr)-description -->[ \t]*(?:\n|\Z)", re.M)


def record_description(text):
    """The description inside a delivery record, or None when `text` has no marker line.

    Windows line endings are normalized first: a checkout with autocrlf must not hide the marker.
    """
    parts = RECORD_MARKER_LINE.split(text.replace("\r\n", "\n"), 1)
    return parts[1].strip() if len(parts) == 2 else None


# Decision-log entries: `### YYYY-MM-DD — Title` (em dash), newest first.
LOG_ENTRY = re.compile(r"^### (\d{4}-\d\d-\d\d) — (.+?)\s*$", re.M)


def decision_log_titles(root):
    text = read_text(Path(root) / "docs" / "decision-log.md") or ""
    return {m.group(2) for m in LOG_ENTRY.finditer(text)}


# --- self-test ----------------------------------------------------------------------------

def self_test():
    """Check globs, tags, IDs, placeholders, and config validation; return a list of failures."""
    failures = []

    def expect(what, got, want):
        if got != want:
            failures.append(f"{what}: got {got!r}, want {want!r}")

    for pattern, path, want in [
        ("tests/**", "tests/a/b.py", True), ("tests/**", "src/a.py", False),
        ("**/*.test.ts", "a.test.ts", True), ("**/*.test.ts", "x/y/a.test.ts", True),
        ("src/*.py", "src/a/b.py", False), ("src/**/b.py", "src/b.py", True),
        ("src/?.py", "src/a.py", True), ("./src/**", "src/a", True),
    ]:
        expect(f"glob {pattern} ~ {path}", bool(glob_to_regex(pattern).match(path)), want)
    for text, want in [
        ("it('[US-PAY-03/AC2] refunds', ...)", [("US-PAY-03", 2)]),
        ("test_us_pay_03_ac2_refund_denied", [("US-PAY-03", 2)]),
        ("TestUS_PAY_03_AC2", [("US-PAY-03", 2)]),
        ("task_ci_01_ac1", [("TASK-CI-01", 1)]),
        ("bonus_pay_03_ac2", []), ("us_pay_03_ac2x", []),
    ]:
        expect(f"tags in {text}", find_tags(text), want)
    expect("ticket id", parse_ticket_id("US-PAY-03"), ("US", "PAY", "03"))
    expect("epic id", parse_ticket_id("EP-PAY"), ("EP", "PAY", None))
    expect("bad id", parse_ticket_id("US-pay-3"), None)
    expect("render", render_command("cd app && run {files:app} --out={report}", ["app/t/a b.ts"], "/tmp/r.xml"),
           "cd app && run 't/a b.ts' --out=/tmp/r.xml")
    cfg = parse_config({"tests": ["tests/**"], "code": ["src/**"], "test_command": "t {files}", "ignore": ["src/gen/**"]})
    expect("is_test", is_test("tests/a.py", cfg), True)
    expect("is_code ignored", is_code("src/gen/a.py", cfg), False)
    try:
        parse_config({"tests": "x", "test_command": 3, "colour": 1, "autonomy": "always"})
        failures.append("an invalid config was accepted")
    except ConfigError as e:
        expect("config errors", len(str(e).splitlines()), 5)
    with tempfile.TemporaryDirectory() as d:
        Path(d, CONFIG_FILE).write_text("tests: [t/**]\ncode: [s/**]\ntest_command: run {files}\nhost: manual\n")
        try:
            expect("load_config host", load_config(d).host, "manual")
        except ConfigError as e:
            failures.append(f"load_config: {e}")
    return failures


def main(argv):
    if argv == ["--self-test"]:
        failures = self_test()
        for f in failures:
            print("FAIL", f)
        print("PASS self-test" if not failures else f"FAIL self-test: {len(failures)} failure(s)")
        return 1 if failures else 0
    if argv == ["--config"]:
        try:
            cfg = load_config(repo_root())
        except ConfigError as e:
            print("ERROR", str(e).replace("\n", "\nERROR "))
            return 1
        for k, v in vars(cfg).items():
            print(f"{k}: {v!r}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
