"""PreToolUse guard for Claude Code in a Test Kitchen project (CONTRIBUTING.md section 2).

Turns the workflow's hardest rules into decisions the model cannot talk itself past. Claude
Code runs it before every shell command and file edit, in every session and subagent of the
repository (`.claude/settings.json` registers it). It reads the tool call as JSON on stdin
and prints a decision as JSON (`deny` or `ask`), or prints nothing to let the call through.

The shell is read the way bash and zsh split it, without running anything: quotes
removed, `$'…'` decoded, run-time parts (`$x`, `${…}`, `$(…)`, backticks, backslashes)
marked, and commands inside `$(…)`, backticks, `sh -c`, `eval`, `xargs`, and `find -exec`
read too. A git, gh, or glab command whose program or subcommand is built at run time
(`git pu$'\x73'h`, `git pu$()sh`) is denied.

Merges and pushes are checked against an allowlist, not a list of bad shapes. A call that
names a push or a merge (a git/gh/glab command with the word, also spliced or quoted; an
unquoted `push`/`merge` word; text run by a shell or interpreter; `git-push`, `send-pack`,
`subtree`, `glab mr accept`) must be plain shell, as read by the guard's own tokenizer:
words of letters, digits, and `._/:=+,@-`; single quotes; double quotes without `$`,
backticks, or backslashes; the separators `;`, `&&`, `||`, `|`, and newlines; `#` comments
of plain words. Any other character is denied. Every program in such a call must be one the
workflow uses: `git` with an allowed subcommand and options (`fetch`/`pull` only from origin
by branch name), `gh pr`/`gh run` and `glab mr`/`glab ci` workflow subcommands,
`python3 scripts/deliver.py` or `scripts/backlog_check.py`, `rg` without `--pre`, and
`echo`, `cat`, `head`, `tail`, `wc`, `grep`, `ls`, `true`. Path parts (`tests/push.test.ts`)
and quoted search patterns in ordinary programs (`rg 'push'`) don't count. Within that:

- a push is exactly `git push [-u|--set-upstream] origin <branch>`: one existing local branch,
  never the default branch, no refspec (`a:b`), wildcard, `HEAD`, or `refs/`; only from this
  project's checkout and only while `remote.origin.push` and `remote.origin.mirror` are unset.
  A force push (`-f`, `--force…`, `+branch`) asks, even in sandbox mode;
- a merge (`gh pr merge …` or `glab mr merge …`) is allowed only when it is alone in its
  call, kitchen.yml says `autonomy: merge`, the host is not `manual`, its words equal
  exactly what `scripts/hosts.py` `merge_argv(<number>, <sha>)` returns for the configured
  host (the command `python3 scripts/deliver.py merge-command <number> --head=<sha>` prints):
      github: gh pr merge <number> --merge --match-head-commit <40-hex sha>
      gitlab: glab mr merge <number> --sha <40-hex sha> --auto-merge=false --yes
  and `python3 scripts/deliver.py gate merge <number> --head=<sha>` passes, run first by the
  guard from the project root. With `autonomy: pr` or `supervised`, or on the manual host,
  every merge is denied: a person merges. `--admin`, `--auto`, auto-merge, squash, rebase,
  merges by branch name or URL, and any other option are never allowed.

Elsewhere in the shell:

- `gh` and `glab` run freely only for reads and the workflow's change-request steps (GH_FREE,
  GLAB_FREE), whichever host kitchen.yml names (a machine may have both CLIs). Other
  built-in commands ask; a command that is not built in (an alias or extension) is denied.
  `gh api`/`glab api` calls that may write (a method other than GET, fields in any form,
  input, graphql) ask, and those that merge or move a branch (merge endpoints and
  mutations, git refs, commits to a branch) are denied. `glab mr create`/`new` with `--push`,
  `--fill` (which pushes), or `--auto-merge` is denied; `gh repo sync <repository>` is denied.
- Every `git config` that is not a read asks, so do `git -c`, `GIT_*` variables, and any
  command naming `.git`, `.gitconfig`, `.config/git`, `.config/gh`, `.config/glab-cli`, or a
  host token. A git alias (matched in any case, as git does) asks, or is denied when it
  pushes, merges, or runs a shell.
- A command that writes a protected path (below) asks: redirects (`>`, `1>`, `&>`, `>|`, …;
  not `>&N` or `/dev/null`), and the files writing programs name (`tee`, `cp`, `mv`, `rm`,
  `sed -i`, `perl -i`, `find -delete`, `curl -o`, `tar -x -C`, `git clean`/`checkout`, …),
  resolved against the call's folder and followed through `cd`; so does code run by a shell
  or interpreter that names a protected path or runs inside a protected folder. Reading
  stays free, and a heredoc for `cat` is data.

File edits (Edit, Write, MultiEdit, NotebookEdit) ask for the protected paths: `docs/`
except `docs/decision-log.md`, `.claude/`, `.github/`, `.gitlab/`, `.gitlab-ci.yml`, `.git/`,
`playbooks/`, `kitchen.yml`, `kitchen.lock`, `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, the
framework scripts, every file listed under `files` in kitchen.lock, and the git, gh, and glab
configuration files.

Paths compare after NFKC normalization and case folding, as macOS's file system does.

The guard imports `kitchen_lib` and `hosts` from `<project root>/scripts/` (the root is
`$CLAUDE_PROJECT_DIR`, else the git checkout this file sits in). When they cannot be
imported or kitchen.yml is invalid, every push and merge is denied, while reads and edits
outside protected paths go on. Any error in the guard itself denies the call (fails closed).
Every check runs before any ask is given, so asking about one part of a call never hides a
denial of another part.

Sandbox opt-in: with `KITCHEN_GUARD_SANDBOX=1` (set per machine in the git-ignored
`.claude/settings.local.json`), "ask" lets the call through without a prompt. Denials and
force pushes are unchanged.

Subagents: when the hook input carries an `agent_id` that is present and neither null nor an
empty string (a call made in a subagent), every ask left after the sandbox opt-in becomes a
deny whose reason keeps the ask's reasons and tells the subagent to hand the step back to the
main session, where the person is asked (GRD-R36). In Claude Code's auto permission mode a
subagent's ask is approved by a classifier, not the person. Allows and denies are unchanged.

settings.json runs the guard with `|| exit 2`: a guard that cannot
start (a syntax error, no python3) blocks the call instead of letting it through.

It reads commands literally: text built at run time (variables that assemble a command, an
interpreter's `-c`, a script written and then run, a build-tool target) is out of its
reach. It is a guardrail against mistakes, not a sandbox (CONTRIBUTING.md section 2).

Python 3.9 compatible; standard library only, plus the project's own scripts.
"""
import glob
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

# Seconds any one git or gate subprocess may take. The merge gate reads the host through its
# CLI and fetches origin, which can be slow; a timeout raises, and raising denies.
TIMEOUT = 300
# Where the playbooks say to stop; quoted in every "ask" so the person sees why.
STOP = "the delivery workflow stops for a person here (playbooks/deliver.md, \"Stop and ask\")"


def emit(decision, reason):
    """Print a decision for Claude Code and end the hook."""
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


def deny(reason):
    """Refuse the call at once: no later check can turn a denial into anything else."""
    emit("deny", reason)


# Asks are collected and given only after every check has run (finish()), so an ask on one
# part of a call (a force push, a host command) never hides a denial of a later part.
ASKS = []

# True when the call was made in a subagent (set by main() from the hook input's `agent_id`;
# GRD-R36). finish() then denies what it would ask, ending the reason with HAND_BACK.
SUBAGENT = False
HAND_BACK = ("This call came from a subagent, where the guard can't ask the person; hand this step back to the main "
             "session, which runs it and the person is asked there.")


def is_subagent(call):
    """True when the hook input's `agent_id` is present and neither null nor an empty string.

    Any other value (a number, an object, `false`, whitespace) counts as a subagent's call, so
    an unexpected value fails closed for asks; null and "" read as a main-session call so the
    main session is never blocked if Claude Code ever sends them there. `agent_type` alone
    does not count: it is also set in sessions started with `--agent`.
    """
    if "agent_id" not in call:
        return False
    value = call["agent_id"]
    return value is not None and not (isinstance(value, str) and value == "")


def ask(reason, firm=False):
    ASKS.append((reason, firm))


def finish():
    """Ask the person when any check asked; else print nothing, which lets the call through.

    Sandbox opt-in, per machine: with KITCHEN_GUARD_SANDBOX=1 (set in the git-ignored
    .claude/settings.local.json of a machine chosen to run unattended), asks let the call
    through, because the person has chosen not to be prompted there. The agent still stops
    for what the playbooks list, through its own questions. Denials never relax, and a
    `firm` ask (a force push, which rewrites remote history) keeps asking.
    """
    if not ASKS:
        return
    firm = any(f for _, f in ASKS)
    if not firm and os.environ.get("KITCHEN_GUARD_SANDBOX") == "1":
        return
    reasons = []
    for reason, f in sorted(ASKS, key=lambda x: not x[1]):  # firm reasons first
        if reason not in reasons:
            reasons.append(reason)
    # GRD-R36 (US-GRD-17): an ask from a subagent's call is denied instead, after the sandbox
    # opt-in above, because in Claude Code's auto permission mode a subagent's ask is approved
    # by a classifier rather than the person. The deny keeps the ask's reasons and ends with the
    # hand-back line, so the main session, where the ask reaches the person, runs the step.
    if SUBAGENT:
        emit("deny", "\n".join(reasons + [HAND_BACK]))
    emit("ask", "\n".join(reasons))


def sh(args, cwd):
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, timeout=TIMEOUT)


def toplevel(path):
    """The git checkout's top folder containing `path`, resolved; None outside git."""
    try:
        r = sh(["git", "rev-parse", "--show-toplevel"], path)
    except (OSError, subprocess.SubprocessError):
        return None
    out = r.stdout.strip()
    return Path(out).resolve() if r.returncode == 0 and out else None


def find_root():
    """The project root: $CLAUDE_PROJECT_DIR (Claude Code sets it for hooks), else this file's checkout.

    The checkout of this file, not of the call's working directory: the guard belongs to
    its own project, and a shell that wandered into another repository must not make the
    guard read that repository's rules. A CLAUDE_PROJECT_DIR inside a checkout counts as
    that checkout's top (Test Kitchen installs only at a repository's root).
    """
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env and Path(env).is_dir():
        return toplevel(env) or Path(env).resolve()
    here = Path(__file__).resolve().parent  # <root>/.claude/hooks
    return toplevel(here) or here.parents[1]


class Kitchen:
    """The project's own `kitchen_lib`, `hosts`, and kitchen.yml, loaded only when needed.

    Only pushes and merges need them, so a broken install (a missing script, invalid
    kitchen.yml, no PyYAML) blocks exactly those and nothing else.
    """

    def __init__(self, root):
        self.root = root
        self.kl = self.hosts = self.cfg = None
        self.error = None
        self._tried = False

    def load(self):
        if not self._tried:
            self._tried = True
            # Never write __pycache__ into the project's scripts/ from a hook that runs on
            # every tool call.
            sys.dont_write_bytecode = True
            sys.path.insert(0, str(self.root / "scripts"))
            try:
                import kitchen_lib  # noqa: E402 (the project's copy, from <root>/scripts)
                import hosts  # noqa: E402
                self.kl, self.hosts = kitchen_lib, hosts
                self.cfg = kitchen_lib.load_config(self.root)
            except (Exception, SystemExit) as e:  # any failure to load: refuse what depends on it
                self.error = f"{type(e).__name__}: {e}"
        return self.error is None

    def require(self, what):
        """Deny `what` (a push or a merge) unless the project's scripts and kitchen.yml load."""
        if not self.load():
            deny(f"The guard cannot check {what}: the project's scripts or kitchen.yml do not load "
                 f"({self.error}). Pushes and merges are refused until they do. Fix kitchen.yml or restore "
                 "scripts/ (`python3 init.py doctor` shows what is wrong).")


class Lock:
    """The framework files kitchen.lock lists (`files`), case-folded for matching (see fold()).

    kitchen.lock is JSON (init.py writes it), so it is read without PyYAML. A missing lock
    lists nothing (the fixed protected paths still apply); a lock that exists but cannot be
    read sets `ok` False, and then every file under scripts/ is protected, since the guard
    can no longer tell framework scripts from the project's own.
    """

    def __init__(self, root):
        self.paths, self.ok, self.lower = [], True, set()
        path = root / "kitchen.lock"
        if not path.exists():
            return
        try:
            files = json.loads(path.read_text(encoding="utf-8")).get("files")
            if not isinstance(files, dict):
                raise ValueError("no `files` table")
            listed = {str(k).replace("\\", "/") for k in files}
            # init.py writes a framework file's new version next to an edited one as
            # `<path>.kitchen-new`; kitchen_lib counts those as framework files too.
            self.paths = sorted(listed | {p + ".kitchen-new" for p in listed})
        except (OSError, ValueError, AttributeError):
            self.ok = False
        self.lower = {fold(p) for p in self.paths}


# --- merges and pushes: an allowlist ------------------------------------------------------

PLAIN_HELP = ("Run merges and pushes as plain commands: `git push [-u] origin <branch>` and, alone in its call, "
              "exactly the merge command `python3 scripts/deliver.py merge-command <number> --head=<sha>` prints. "
              "Write commit messages and descriptions to a file first (`git commit -F <file>`, a body file).")
SEPARATORS = set(";&|\n")
# Outside quotes, a word may hold only these characters, and a comment only these and
# spaces: an allowlist, so no shell syntax is missed.
WORD_CHAR = re.compile(r"[A-Za-z0-9._/:=+,@-]")
COMMENT = re.compile(r"[A-Za-z0-9._/:=+,@ \t-]*")


def plain_commands(command):
    """Split a plain shell command into simple commands (lists of words), or deny.

    Implements only the subset of shell the workflow needs, exactly: words of plain
    characters (WORD_CHAR), single quotes, double quotes without `$`, backticks, or
    backslashes, the separators `;`, `&&`, `||`, `|`, and newlines, and `#` comments of
    plain words. Any other character is denied, so what is checked here is what bash or
    zsh runs.
    """
    # Control characters other than tab and newline mean different things to the guard
    # and the shell (a carriage return is a separator to str.split but a word character
    # to bash and zsh), so none is accepted.
    if re.search(r"[\x00-\x08\x0b-\x1f\x7f]", command):
        deny("A control character (such as a carriage return) in a command that names a merge or push. " + PLAIN_HELP)
    out, current, word, i, n = [], [], None, 0, len(command)
    while i < n:
        c = command[i]
        if c == "'":
            j = command.find("'", i + 1)
            if j < 0:
                deny("Unterminated quote in a command that names a merge or push. " + PLAIN_HELP)
            word, i = (word or "") + command[i + 1:j], j + 1
        elif c == '"':
            j = command.find('"', i + 1)
            if j < 0:
                deny("Unterminated quote in a command that names a merge or push. " + PLAIN_HELP)
            if re.search(r"[$`\\]", command[i + 1:j]):
                deny("`$`, backticks, or backslashes inside double quotes in a command that names a merge or "
                     "push: the shell expands them. " + PLAIN_HELP)
            word, i = (word or "") + command[i + 1:j], j + 1
        elif c == "#" and word is None:
            # A comment runs to the end of the line. It may hold only plain words, so it
            # runs nothing even in a shell that doesn't treat `#` as a comment.
            j = command.find("\n", i)
            j = n if j < 0 else j
            if not COMMENT.fullmatch(command[i + 1:j]):
                deny("A comment in a command that names a merge or push may hold only letters, digits, "
                     "spaces, and .,:/_=+@-. " + PLAIN_HELP)
            i = j
        elif c == "&" and (command[i + 1:i + 2] != "&" or command[i - 1:i] == "|"):
            deny("A single `&` (background) or `|&` in a command that names a merge or push. " + PLAIN_HELP)
        elif c in " \t" or c in SEPARATORS:
            if word is not None:
                current.append(word)
                word = None
            if c in SEPARATORS and current:
                out.append(current)
                current = []
            i += 2 if c == "&" else 1
        elif WORD_CHAR.match(c):
            word, i = (word or "") + c, i + 1
        else:
            # Everything else, which the shell may give a meaning: `$`, backticks,
            # backslashes, redirects, subshells and groups, braces, globs, `~`, `!`, `^`.
            # (zsh's `=cmd` at a word's start only names a program's path; push and
            # merge arguments must start with a letter or digit anyway.)
            deny(f"`{c}` outside quotes in a command that names a merge or push: the guard checks only "
                 "plain commands (words of letters, digits, and ._/:=+,@-, quotes, ;, &&, ||, |, newlines, "
                 "comments). " + PLAIN_HELP)
    if word is not None:
        current.append(word)
    if current:
        out.append(current)
    return out


# What a call that merges or pushes may also run. fetch and pull are limited to
# FETCH_OPTIONS, from origin.
FETCH_OPTIONS = {"-q", "--quiet", "-p", "--prune", "--tags", "--ff-only", "--no-rebase"}
GIT_SUBCOMMANDS = {"push", "add", "commit", "status", "log", "diff", "show", "fetch", "pull", "merge", "merge-base",
                   "rev-parse", "branch", "switch", "checkout", "stash"}
# Host CLI subcommands such a call may run: the workflow's change-request steps and reads,
# for both hosts (a project may have both CLIs installed; the merge rule below decides
# which merge is the host's). `checkout` is left out: it moves the checkout under the merge.
CLI_SUBCOMMANDS = {
    "gh": {"pr": {"merge", "create", "view", "checks", "list", "diff", "edit", "ready", "comment", "status"},
           "run": {"watch", "view", "list"}},
    "glab": {"mr": {"merge", "create", "view", "list", "diff", "update", "note"},
             "ci": {"status", "list", "get", "trace"}},
}
MERGE_COMMANDS = {("gh", "pr", "merge"), ("glab", "mr", "merge")}
# Options a git subcommand other than push, fetch, and pull may take in such a call.
# An allowlist: git has options that write files (`--output`) or run programs
# (`merge -s <name>` runs git-merge-<name>), and accepts abbreviated long options.
GIT_OPTIONS = {"-q", "--quiet", "-v", "--verbose", "-m", "--message", "-F", "--file", "-a", "--all", "-u", "-b", "-c",
               "-n", "--", "--oneline", "--stat", "--name-only", "--name-status", "--short", "--porcelain",
               "--abbrev-ref", "--show-toplevel", "--symbolic-full-name", "--verify", "--is-ancestor", "--ff-only",
               "--no-ff", "--no-edit", "--abort", "--allow-empty", "--list"}
# Programs with no option that writes a file or runs another program (rg --pre,
# sort -o and --compress-program, and uniq's output file are why those are not here).
READ_ONLY = {"echo", "cat", "head", "tail", "wc", "grep", "ls", "true"}
WORKFLOW_SCRIPTS = re.compile(r"^(?:\.\./)?scripts/(?:deliver|backlog_check)\.py$")
# A branch name as a push or fetch may give it: no refspec (`:`), wildcard, leading `+`
# (force), or `refs/`, `heads/`, `tags/`, `remotes/`, `origin/` prefix that reaches another ref.
BRANCH = re.compile(r"^(?!(?:refs|heads|tags|remotes|origin)/)[A-Za-z0-9][A-Za-z0-9._/-]*$")
PUSH_OPTIONS = {"-u", "--set-upstream", "-n", "--dry-run", "-q", "--quiet", "-v", "--verbose"}
# Merge options that bypass the checks (--admin), defer the merge past the gate (--auto,
# auto-merge, when-pipeline-succeeds), or rewrite the commits the gates and the delivery
# record point to (squash, rebase). Named in the denial so the agent sees why.
BYPASS = re.compile(r"^(?:--(?:admin|auto|squash|rebase|when-pipeline-succeeds|disable-auto)|-[sr]$)")
ZERO_SHA = "0" * 40
PERSON_MERGES = ("An agent does not merge here ({why}): a person merges this change request. Stop at \"ready to "
                 "merge\" and report the change request, its head sha, and the gate result (playbooks/deliver.md, step 12).")


def guard_plain(command, cwd, k):
    cmds = plain_commands(command)
    for words in cmds:
        program = words[0]
        if program == "git":
            sub = words[1] if len(words) > 1 else ""
            if sub not in GIT_SUBCOMMANDS:
                deny(f"`git {sub}` can't run in a call that merges or pushes (git options before the "
                     "subcommand, such as -C or -c, included). " + PLAIN_HELP)
            if sub == "push":
                guard_push(words[2:], cwd, k)
            elif sub in {"fetch", "pull"}:
                guard_fetch(sub, words[2:])
            else:
                for a in words[2:]:
                    if a.startswith("-") and a.split("=", 1)[0] not in GIT_OPTIONS and not re.fullmatch(r"-\d+", a):
                        deny(f"`git {sub} {a}` isn't an option the workflow uses in a call that names a merge "
                             "or push. " + PLAIN_HELP)
        elif program in CLI_SUBCOMMANDS:
            group, sub = (words + ["", ""])[1:3]
            if sub not in CLI_SUBCOMMANDS[program].get(group, ()):
                deny(f"`{program} {group} {sub}` can't run in a call that names a merge or push (options "
                     "before the subcommand, such as -R, included). " + PLAIN_HELP)
            if (program, group, sub) in MERGE_COMMANDS:
                # Alone, so nothing (a commit, a push) can change the branch between the
                # merge gate and the merge.
                if len(cmds) > 1 or SEPARATORS & set(command.strip()):
                    deny(f"Run `{program} {group} merge` alone in its call, so nothing can change the branch "
                         "between the merge gate and the merge. " + PLAIN_HELP)
                guard_merge(words, cwd, k)
        elif program in {"python3", "python"} and len(words) > 1 and WORKFLOW_SCRIPTS.match(words[1]):
            pass
        elif program == "rg" and not any(a.startswith("--pre") for a in words[1:]):
            pass  # ripgrep only reads; --pre and --pre-glob would run a program on every file
        elif program not in READ_ONLY:
            deny(f"`{program}` can't run in a call that names a merge or push (shells, wrappers, interpreters, "
                 "and other programs included). " + PLAIN_HELP)


def guard_fetch(sub, args):
    # fetch and pull take options that run commands (`--upload-pack` runs its value
    # through sh for a local path, and git accepts abbreviations such as `--upload`),
    # so only these exact forms are allowed: from origin, by branch name.
    positional = [a for a in args if not a.startswith("-")]
    for a in args:
        if a.startswith("-") and a not in FETCH_OPTIONS:
            deny(f"`git {sub} {a}` isn't part of the workflow in a call that names a merge or push. " + PLAIN_HELP)
    if positional and (positional[0] != "origin" or not all(BRANCH.match(b) for b in positional[1:])):
        deny(f"`git {sub}` in a call that names a merge or push takes only origin and branch names. " + PLAIN_HELP)


def same_checkout(cwd, k, what):
    """Deny `what` unless the call runs in the project's own checkout.

    The gates read this checkout, and the guard reads this project's kitchen.yml; a push or
    merge from another checkout (a worktree, another clone, another repository) would be
    checked against the wrong files. The playbook works in one checkout only.
    """
    top = toplevel(cwd) if Path(cwd).is_dir() else None
    if top is None or top != Path(k.root).resolve():
        deny(f"Run {what} from this project's checkout ({k.root}), not from {cwd}: the guard and the gates "
             "read this checkout only.")


def guard_merge(words, cwd, k):
    """Allow a merge only in the one shape the host adapter defines, after the merge gate passes."""
    k.require("this merge")
    host = k.hosts.get_host(k.cfg, k.root)
    # Who merges comes first: under these settings no merge shape is acceptable.
    if not host.cli:
        deny(PERSON_MERGES.format(why="the host is manual"))
    if k.cfg.autonomy != "merge":
        deny(PERSON_MERGES.format(why=f"kitchen.yml sets autonomy: {k.cfg.autonomy}"))
    # The adapter's merge command with placeholder values shows where the number and the
    # pinned sha sit, so the guard needs no per-host parsing (a new adapter works as is).
    template = host.merge_argv(1, ZERO_SHA)
    n_at, sha_at = template.index("1"), template.index(ZERO_SHA)
    if words[:n_at] != template[:n_at]:
        # The other host's CLI (a machine may have both): never this project's merge.
        shape = " ".join("<number>" if i == n_at else "<sha>" if i == sha_at else w for i, w in enumerate(template))
        deny(f"This is not this project's merge command (the host is {host.name}): the only merge is `{shape}`, exactly "
             "as `python3 scripts/deliver.py merge-command <number> --head=<sha>` prints it, alone in its call.")
    for a in words[n_at:]:
        if a not in template and BYPASS.match(a):
            deny(f"`{a}`: merges never bypass or defer the checks and always make a merge commit "
                 "(no --admin, --auto, auto-merge, squash, or rebase). " + PLAIN_HELP)
    number = words[n_at] if len(words) > n_at else ""
    pin = template[sha_at - 1]
    sha = words[words.index(pin) + 1] if pin in words[:-1] else (words[sha_at] if len(words) > sha_at else "")
    try:
        expected = host.merge_argv(number, sha)
    except ValueError as e:
        deny(f"A merge names the change request by its number and pins the full 40-character head sha the "
             f"checks passed on ({e}); merges by branch name or URL are refused. " + PLAIN_HELP)
    if words != expected:
        deny(f"The only merge is exactly the command `python3 scripts/deliver.py merge-command {number} "
             f"--head={sha}` prints, alone in its call: `{' '.join(expected)}` (the host is {host.name}).")
    same_checkout(cwd, k, "the merge")
    gate = [sys.executable, str(Path(k.root) / "scripts" / "deliver.py"), "gate", "merge", expected[n_at],
            f"--head={sha}"]
    try:
        r = sh(gate, k.root)
    except subprocess.TimeoutExpired:
        deny(f"The merge gate (scripts/deliver.py gate merge) did not finish within {TIMEOUT} seconds.")
    if r.returncode:
        deny(f"Merge gate failed (scripts/deliver.py gate merge {expected[n_at]} --head={sha}):\n"
             + (r.stdout + r.stderr).strip())


def guard_push(args, cwd, k):
    forced, rest = False, []
    for a in args:
        if a in {"-f", "--force"} or a.startswith("--force"):
            forced = True
        elif a.startswith("-") and a not in PUSH_OPTIONS:
            deny(f"`git push {a}` isn't part of the workflow. " + PLAIN_HELP)
        elif not a.startswith("-"):
            rest.append(a)
    if len(rest) != 2 or rest[0] != "origin":
        deny("Push one branch to origin by name: `git push [-u] origin <branch>` (not a bare push, HEAD, "
             "another remote, or several branches).")
    name = rest[1][1:] if rest[1].startswith("+") else rest[1]
    forced = forced or rest[1].startswith("+")
    k.require("this push")
    same_checkout(cwd, k, "the push")
    default = k.kl.default_branch(k.root)
    full = (sh(["git", "rev-parse", "--symbolic-full-name", name], cwd).stdout.strip()
            if BRANCH.match(name) and name != "HEAD" else "")
    # Compared without case too: on a case-insensitive file system `MAIN` can name `main`.
    if name.lower() == default.lower() or full != f"refs/heads/{name}":
        deny(f"`{rest[1]}` is not a local branch other than the default branch ({default}). Nothing is "
             "pushed to the default branch directly, and a push names one branch, without a refspec (`a:b`), "
             "wildcard, `HEAD`, or `refs/`.")
    if sh(["git", "config", "--get-regexp", r"^remote\.origin\.(push|mirror)$"], cwd).stdout.strip():
        deny("remote.origin.push or remote.origin.mirror is set, so a push can land somewhere other than its "
             "branch. Remove the setting (a person approves git config changes).")
    if forced:
        ask(f"This is a force push, which rewrites the branch on origin; {STOP}.", firm=True)


# --- reading shell commands -----------------------------------------------------------------
#
# The checks below read a command the way bash and zsh split it, without running anything:
# words with quotes removed, `$'…'` decoded, and run-time parts (`$x`, `${…}`, `$(…)`,
# backticks) dropped from the word but marked, because their value is only known when the
# shell runs. Commands inside `$(…)`, backticks, `sh -c '…'`, `eval`, `xargs`, and
# `find -exec` are read too, and heredoc bodies are kept apart from the command line. This
# reader only finds what to deny or ask about: what a push or a merge may look like is
# decided by plain_commands() above, which refuses every run-time part outright.

MAX_DEPTH = 4  # nested commands read this deep; deeper text still meets the raw checks


class Cmd:
    """One simple command: its words, which of them hold run-time parts, its redirects and stdin text."""

    def __init__(self):
        self.words = []      # each word as the shell would pass it, run-time parts left out
        self.dynamic = []    # the word held `$`, a backtick, a backslash, or ANSI-C quoting
        self.quoted = []     # part of the word was quoted
        self.redirects = []  # (operator, target) of redirects that write: >, >>, >|, &>, 1>, >&file, <>
        self.bodies = []     # heredoc bodies and here-strings: text the command reads on stdin
        self.prog = 0        # index of the program word, after assignments and wrappers (env, xargs, …)
        self.indirect = False  # runs other text as commands: a shell, eval, a wrapper, find -exec, inline code
        self.code = False    # a shell or interpreter running code given inline or on stdin


ANSI_SIMPLE = {"a": "\a", "b": "\b", "e": "\x1b", "E": "\x1b", "f": "\f", "n": "\n", "r": "\r", "t": "\t",
               "v": "\v", "\\": "\\", "'": "'", '"': '"', "?": "?"}
ANSI_NUMERIC = re.compile(r"x([0-9a-fA-F]{1,2})|u([0-9a-fA-F]{1,4})|U([0-9a-fA-F]{1,8})|([0-7]{1,3})")


def ansi_c(s, i):
    """Decode `$'…'` from just after its opening quote; returns (text, index after the closing quote)."""
    out, n = [], len(s)
    while i < n and s[i] != "'":
        if s[i] == "\\" and i + 1 < n:
            d = s[i + 1]
            if d in ANSI_SIMPLE:
                out.append(ANSI_SIMPLE[d])
                i += 2
                continue
            m = ANSI_NUMERIC.match(s, i + 1)
            if m:
                digits = next(g for g in m.groups() if g is not None)
                try:
                    out.append(chr(int(digits, 8 if m.group(4) else 16)))
                except (ValueError, OverflowError):
                    pass
                i = m.end()
                continue
            if d == "c" and i + 2 < n:
                out.append(chr(ord(s[i + 2]) & 31))
                i += 3
                continue
            out.append("\\" + d)
            i += 2
            continue
        out.append(s[i])
        i += 1
    return "".join(out), i + 1


def skip_balanced(s, i, opener, closer):
    """Index of the `closer` that balances an `opener` already passed (quotes respected); len(s) if none."""
    depth, n = 1, len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c == "'" and opener == "(":
            j = s.find("'", i + 1)
            i = n if j < 0 else j + 1
            continue
        if c == '"':
            _, _, i = dquote(s, i + 1, [])
            continue
        if c == opener:
            depth += 1
        elif c == closer:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n


def backtick_end(s, i):
    n = len(s)
    while i < n:
        if s[i] == "\\":
            i += 2
            continue
        if s[i] == "`":
            return i
        i += 1
    return n


def dollar(s, i, nested):
    """Skip the expansion starting with `$` at s[i]; returns the index after it, or None for a lone `$`.

    `$(…)` contents are commands and go to `nested`; `$((…))` is arithmetic and does not.
    """
    if s.startswith("$((", i):
        return skip_balanced(s, i + 2, "(", ")") + 1
    if s.startswith("$(", i):
        j = skip_balanced(s, i + 2, "(", ")")
        nested.append(s[i + 2:j])
        return j + 1
    if s.startswith("${", i):
        return skip_balanced(s, i + 2, "{", "}") + 1
    m = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|[0-9@*#?$!-]").match(s, i + 1)
    return m.end() if m else None


def dquote(s, i, nested):
    """Read a double-quoted string from just after its opening quote; returns (text, dynamic, next index)."""
    out, dyn, n = [], False, len(s)
    while i < n and s[i] != '"':
        c = s[i]
        if c == "\\" and i + 1 < n:
            d = s[i + 1]
            if d != "\n":
                out.append(d if d in '"\\$`' else "\\" + d)
            dyn = True
            i += 2
            continue
        if c == "`":
            j = backtick_end(s, i + 1)
            nested.append(s[i + 1:j])
            dyn, i = True, j + 1
            continue
        if c == "$":
            j = dollar(s, i, nested)
            if j is not None:
                dyn, i = True, j
                continue
        out.append(c)
        i += 1
    return "".join(out), dyn, i + 1


REDIRECT = re.compile(r"<<<|<<-|<<|<&|<>|<\(|<|>>|>\||>&|>\(|>")
WRITE_REDIRECTS = {">", ">>", ">|", "&>", "&>>", "<>"}


def lex(s):
    """Split shell text into simple commands (Cmd) and the texts of `$(…)`/backtick commands inside it."""
    cmds, nested, heredocs = [], [], []
    state = {"cmd": Cmd(), "text": None, "dyn": False, "quo": False, "pending": None}

    def add(text, dyn=False, quo=False):
        state["text"] = (state["text"] or "") + text
        state["dyn"] = state["dyn"] or dyn
        state["quo"] = state["quo"] or quo

    def end_word():
        text, dyn, quo = state["text"], state["dyn"], state["quo"]
        if text is None:
            return
        state.update(text=None, dyn=False, quo=False)
        cmd, op = state["cmd"], state["pending"]
        if op is not None:
            state["pending"] = None
            if op in ("<<", "<<-"):
                heredocs.append((text, op == "<<-", cmd))
            elif op == "<<<":
                cmd.bodies.append(text)
            elif op in WRITE_REDIRECTS or (op == ">&" and not re.fullmatch(r"\d+|-", text)):
                cmd.redirects.append((op, text))
            return
        cmd.words.append(text)
        cmd.dynamic.append(dyn)
        cmd.quoted.append(quo)

    def end_cmd():
        end_word()
        state["pending"] = None
        cmd = state["cmd"]
        while cmd.words and cmd.words[0] in ("{", "}", "!"):  # grouping and negation are not programs
            del cmd.words[0], cmd.dynamic[0], cmd.quoted[0]
        if cmd.words or cmd.redirects or cmd.bodies:
            cmds.append(cmd)
        state["cmd"] = Cmd()

    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            if s[i + 1:i + 2] != "\n":  # a backslash-newline only joins lines
                add(s[i + 1:i + 2], dyn=True)
            i += 2
        elif c == "'":
            j = s.find("'", i + 1)
            j = n if j < 0 else j
            add(s[i + 1:j], quo=True)
            i = j + 1
        elif c == '"':
            text, dyn, i = dquote(s, i + 1, nested)
            add(text, dyn, True)
        elif c == "$" and s.startswith("$'", i):
            text, i = ansi_c(s, i + 2)
            add(text, True, True)
        elif c == "$" and s.startswith('$"', i):
            text, _, i = dquote(s, i + 2, nested)
            add(text, True, True)
        elif c == "$":
            j = dollar(s, i, nested)
            if j is None:
                add("$")
                i += 1
            else:
                add("", True)
                i = j
        elif c == "`":
            j = backtick_end(s, i + 1)
            nested.append(s[i + 1:j])
            add("", True)
            i = j + 1
        elif c == "#" and state["text"] is None:
            j = s.find("\n", i)
            i = n if j < 0 else j
        elif c in " \t":
            end_word()
            i += 1
        elif c == "\n":
            end_cmd()
            i += 1
            for delim, strip_tabs, owner in heredocs:  # bodies start on the next line
                body = []
                while i < n:
                    j = s.find("\n", i)
                    j = n if j < 0 else j
                    line, i = s[i:j], j + 1
                    if (line.lstrip("\t") if strip_tabs else line) == delim:
                        break
                    body.append(line)
                owner.bodies.append("\n".join(body))
            del heredocs[:]
        elif c in "<>":
            # Digits written right before the operator (`2>file`) name a descriptor, not a word.
            if state["text"] is not None and not state["quo"] and re.fullmatch(r"\d+", state["text"]):
                state.update(text=None, dyn=False, quo=False)
            else:
                end_word()
            op = REDIRECT.match(s, i).group(0)
            if op in ("<(", ">("):
                j = skip_balanced(s, i + 2, "(", ")")
                nested.append(s[i + 2:j])
                add("", True)
                i = j + 1
            else:
                state["pending"] = op
                i += len(op)
        elif c == "&" and s.startswith("&>", i):
            end_word()
            op = "&>>" if s.startswith("&>>", i) else "&>"
            state["pending"] = op
            i += len(op)
        elif c in ";&|()":
            end_cmd()
            i += 2 if s.startswith(("&&", "||", ";;"), i) else 1
        else:
            add(c)
            i += 1
    end_cmd()
    for delim, strip_tabs, owner in heredocs:  # a heredoc on the last line: the rest is its body
        owner.bodies.append("")
    return cmds, nested


def base(word):
    """A program word's name: `/usr/bin/git` -> `git`."""
    return word.rsplit("/", 1)[-1]


# Programs that run the rest of their words as a command. Their options are skipped, and the
# ones named in WRAPPER_VALUE_OPTIONS take a value (`timeout -s KILL 5 git …`, `xargs -I {} …`).
WRAPPERS = {"env", "command", "builtin", "exec", "nohup", "time", "nice", "timeout", "sudo", "doas", "stdbuf",
            "ionice", "chrt", "taskset", "caffeinate", "unbuffer", "watch", "xargs", "parallel", "nsenter"}
WRAPPER_VALUE_OPTIONS = {"-I", "-n", "-L", "-P", "-s", "-d", "-E", "-a", "-u", "-g", "-C", "-k", "-o", "-e"}
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\+?=")
DURATION = re.compile(r"^\d+(?:\.\d+)?[smhd]?$")
SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "mksh", "ash", "fish", "csh", "tcsh", "busybox"}
INTERPRETERS = re.compile(r"^(?:python[0-9.]*|pypy[0-9.]*|node|nodejs|deno|bun|perl|ruby|php|osascript|lua|tclsh|"
                          r"rscript|pwsh)$", re.I)


def program_index(cmd):
    """Index of the program word, past `X=y` assignments and wrappers; sets cmd.indirect for a wrapper."""
    words, i = cmd.words, 0
    while i < len(words):
        if ASSIGNMENT.match(words[i]):
            i += 1
        elif base(words[i]) in WRAPPERS:
            cmd.indirect = True
            i += 1
            while i < len(words) and (words[i].startswith("-") or DURATION.match(words[i])
                                      or ASSIGNMENT.match(words[i])):
                i += 2 if words[i] in WRAPPER_VALUE_OPTIONS else 1
        else:
            break
    return i


def interpreter_code(name, args):
    """True when an interpreter runs code given inline (`-c`, `-e`, …) or on stdin, not a script or module."""
    name = name.lower()
    for w in args:
        if name.startswith(("python", "pypy")) and w in ("-c", "-m"):
            return w == "-c"
        if name in ("node", "nodejs", "bun") and w in ("-e", "--eval", "-p", "--print"):
            return True
        if name in ("perl", "ruby") and w.startswith("-") and not w.startswith("--") and re.search(r"[eE]", w[1:]):
            return True
        if (name, w) in (("php", "-r"), ("osascript", "-e"), ("deno", "eval")):
            return True
        if w == "-":
            return True
        if not w.startswith("-"):
            return False  # a script file
    return True  # no script named: the code comes on stdin


def sub_cmd(cmd, start, end):
    sub = Cmd()
    sub.words, sub.dynamic, sub.quoted = cmd.words[start:end], cmd.dynamic[start:end], cmd.quoted[start:end]
    return sub


def analyze(text, depth=0):
    """Every simple command in `text`, nested ones included, with program, indirection, and code marked."""
    cmds, nested = lex(text)
    out = []
    for cmd in cmds:
        out.extend(expand(cmd, depth))
    if depth < MAX_DEPTH:
        for inner in nested:
            out.extend(analyze(inner, depth + 1))
    return out


def expand(cmd, depth):
    """The command itself, then the commands it runs: `sh -c '…'`, `eval …`, `xargs cmd`, `find -exec cmd`."""
    cmd.prog = program_index(cmd)
    out = [cmd]
    words, i = cmd.words, cmd.prog
    if i >= len(words):
        return out
    if cmd.dynamic[i]:
        cmd.indirect = True  # a program built at run time could be anything
    name, rest = base(words[i]), words[i + 1:]
    if name in SHELLS:
        cmd.indirect = True
        script = None
        for j, w in enumerate(rest):
            if w.startswith("-") and not w.startswith("--") and "c" in w[1:]:
                script = rest[j + 1] if j + 1 < len(rest) else ""
                break
            if not w.startswith("-"):
                break
        positional = [w for w in rest if not w.startswith("-")]
        cmd.code = script is not None or not positional or "-s" in rest
        if script is not None and depth < MAX_DEPTH:
            out.extend(analyze(script, depth + 1))
    elif name in ("eval", "source", "."):
        cmd.indirect = cmd.code = True
        if name == "eval" and depth < MAX_DEPTH:
            out.extend(analyze(" ".join(rest), depth + 1))
    elif name == "find":
        for j, w in enumerate(rest):
            if w in ("-exec", "-execdir", "-ok", "-okdir"):
                cmd.indirect = True
                end = next((k for k in range(j + 1, len(rest)) if rest[k] in (";", "+")), len(rest))
                out.extend(expand(sub_cmd(cmd, i + 2 + j, i + 1 + end), depth + 1))
    elif INTERPRETERS.match(name):
        cmd.code = interpreter_code(name, rest)
        cmd.indirect = cmd.indirect or cmd.code
    return out


# --- merges and pushes hidden in the shell -----------------------------------------------------

HOST_PROGRAMS = {"git", "gh", "glab"}
# Within git, gh, and glab commands the original, loose boundaries apply (`alias.p=push`,
# `remote.origin.push=…` count): a false alarm there only means the strict rules run.
LOOSE = re.compile(r"(?<![-\w])(?:push|merge)(?![-\w])")
# Program names that push without the word (`git-push`, `git-send-pack`, …).
PUSH_PROGRAM = re.compile(r"(?:^|-)(?:push|send-pack|receive-pack|http-push|subtree)$")
# The raw text, quotes and expansion characters removed, for shapes the reader might miss:
# a git/gh/glab program word followed in the same simple command by push, merge, or accept.
HOST_RAW = re.compile(r"(?:^|(?<=[\s;&|(`'\"=]))(?:[\w./~-]*/)?(?:git|gh|glab)(?=[\s'\"]|$)[^;&|\n]*?"
                      r"(?<![-\w])(?:push|merge|accept)(?![-\w])")
PUSH_RAW = re.compile(r"git-push|http-push|send-pack|receive-pack|(?<![\w.-])subtree(?![\w.-])")
# Whole shell words only: path parts (`tests/push.test.ts`, `src/merge.py`) are no push.
STRICT = re.compile(r"(?<![-\w./])(?:push|merge)(?![-\w./])")


def needs_plain(command, cmds):
    """Does this call name a push or a merge, so that the allowlist (guard_plain) must read it?"""
    cleaned = re.sub(r"['\"\\`$]", "", command.replace("\\\n", ""))
    if HOST_RAW.search(cleaned) or PUSH_RAW.search(cleaned):
        return True
    indirect = False
    for cmd in cmds:
        if cmd.prog >= len(cmd.words):
            continue
        name, args = base(cmd.words[cmd.prog]), cmd.words[cmd.prog + 1:]
        if name in HOST_PROGRAMS and any(LOOSE.search(w) for w in args):
            return True  # also catches words decoded or spliced at run time: git pu$'\x73'h
        if name == "glab" and "accept" in args:
            return True  # `glab mr accept` is glab's name for merge
        if PUSH_PROGRAM.search(name):
            return True
        # A bare, unquoted `push` or `merge` word anywhere (`make push`); a quoted one in an
        # ordinary program is data (`rg -n 'push' src/`).
        if any(w in ("push", "merge") and not q for w, q in zip(cmd.words, cmd.quoted)):
            return True
        indirect = indirect or cmd.indirect
    # Text that another program runs as commands (`echo '…' | bash`, `python3 -c`, eval).
    return indirect and bool(STRICT.search(cleaned))


# Words that, right after a program built at run time, show it is a host CLI.
HOSTISH = {"pr", "mr", "api", "repo", "run", "ci", "push", "merge", "accept", "config", "alias", "auth", "release",
           "workflow", "secret", "variable", "remote", "fetch", "pull", "commit", "branch", "checkout", "reset", "tag",
           "send-pack", "subtree", "update-ref"}
# git options before the subcommand that take a separate value.
GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env",
                     "--super-prefix", "--attr-source", "--list-cmds"}


def guard_dynamic(cmds):
    """Deny git/gh/glab commands whose program or subcommand is built at run time.

    `git pu$'\\x73'h`, `git pu$()sh`, ``git pu`true`sh``, `gh pr mer${x}ge`, `g$()it push`:
    the shell assembles a word the guard can only guess, so no check of it is trustworthy.
    Arguments after the subcommand may use expansions (`git commit -m "$(cat …)"`).
    """
    for cmd in cmds:
        i = cmd.prog
        if i >= len(cmd.words):
            continue
        name = base(cmd.words[i])
        if cmd.dynamic[i]:
            nxt = cmd.words[i + 1] if i + 1 < len(cmd.words) else ""
            if (name in HOST_PROGRAMS or name.startswith("git-") or nxt in HOSTISH
                    or (i + 1 < len(cmd.words) and cmd.dynamic[i + 1])):
                deny(f"`{cmd.words[i] or '…'} {nxt}`: a git, gh, or glab command whose program is built at run time "
                     "(`$`, backticks, backslashes) can't be checked. " + PLAIN_HELP)
            continue
        if name not in HOST_PROGRAMS and not name.startswith("git-"):
            continue
        need, j, found = (1 if name == "git" or name.startswith("git-") else 2), i + 1, 0
        while j < len(cmd.words) and found < need:
            w = cmd.words[j]
            if cmd.dynamic[j]:
                deny(f"`{name} … {w or '…'}`: a {name} subcommand built at run time (`$`, backticks, backslashes, "
                     "ANSI-C quoting) can't be checked; write it out plainly. " + PLAIN_HELP)
            if w.startswith("-"):
                j += 2 if w in GIT_VALUE_OPTIONS or w in ("-R", "--repo") else 1
                continue
            found += 1
            j += 1


# --- host CLIs ---------------------------------------------------------------------------------

# The host CLI commands that run without asking: reads, and the workflow's own
# change-request steps (playbooks/deliver.md, "Host commands"). Everything else asks,
# because both CLIs are mostly tools for changing the host (`gh workflow run` and `glab ci
# run` start pipelines, secrets, variables, releases, settings). None: any subcommand. `api`
# writes ask (or are denied, for merges and branch writes) in guard_host; `merge` goes
# through the merge rule above.
GH_FREE = {"pr": {"view", "list", "checks", "diff", "create", "edit", "ready", "comment", "status", "merge", "checkout"},
           "run": {"view", "list", "watch"}, "issue": {"view", "list", "status"}, "repo": {"view"},
           "workflow": {"view", "list"}, "release": {"view", "list"}, "auth": {"status"}, "label": {"list"},
           "api": None, "search": None, "status": None, "help": None, "version": None, "--version": None,
           "--help": None, None: None}
# glab subcommands checked against https://gitlab.com/gitlab-org/cli/-/tree/main/docs/source
# (mr/_index.md, ci/_index.md, ci/status.md). `ci view` is left out: it is an interactive
# view that can run, retry, and cancel jobs.
GLAB_FREE = {"mr": {"view", "list", "create", "update", "note", "checkout", "diff", "merge"},
             "ci": {"status", "list", "get", "trace", "lint"}, "issue": {"view", "list"}, "repo": {"view"},
             "release": {"view", "list"}, "auth": {"status"}, "label": {"list"},
             "api": None, "help": None, "version": None, "--version": None, "--help": None, None: None}
CLI_FREE = {"gh": GH_FREE, "glab": GLAB_FREE}
# Built-in top-level commands. Anything else is an alias or an extension, which the guard
# can't read and which may merge (`gh alias set m 'pr merge'`), so it is denied.
KNOWN_GROUPS = {
    "gh": {"accessibility", "agent-task", "alias", "api", "attestation", "auth", "browse", "cache", "co", "codespace",
           "completion", "config", "copilot", "extension", "gist", "gpg-key", "help", "issue", "label", "licenses",
           "org", "pr", "preview", "project", "release", "repo", "ruleset", "run", "search", "secret", "ssh-key",
           "status", "variable", "version", "workflow"},
    "glab": {"alias", "api", "attestation", "auth", "changelog", "check-update", "ci", "cluster", "completion",
             "config", "deploy-key", "duo", "gpg-key", "help", "incident", "issue", "iteration", "job", "label", "mr",
             "opentofu", "release", "repo", "runner", "schedule", "securefile", "snippet", "ssh-key", "stack",
             "token", "user", "variable", "version", "workitems"},
}
# Host API endpoints and GraphQL mutations that merge or move a branch: a written call to
# one is a merge or push outside the gate, so it is denied, not asked (sandbox mode must
# never open a merge path). GitHub: POST /repos/…/merges, PUT /pulls/<n>/merge, git/refs,
# contents (commits to a branch); GitLab: PUT /merge_requests/<n>/merge, repository/commits
# and repository/files (commit to a branch), merge_when_pipeline_succeeds, rebase.
MERGE_API = re.compile(r"/merges?\b|/rebase\b|merge_when_pipeline_succeeds|auto_merge|git/refs|/contents/"
                       r"|/repository/(?:commits|files|branches)\b|mergePullRequest|enablePullRequestAutoMerge"
                       r"|mergeBranch|updateRefs?\b|createRef\b|createCommitOnBranch", re.I)


def api_writes(words):
    """Does a `gh api`/`glab api` call (its words after `api`) write?

    Both default to GET and switch to POST when given fields, a form, or input (gh api
    --help; glab docs api/_index.md). Short options may be clustered or carry their value
    attached (`-fbase=main`, `-XPUT`), so any single-dash word holding f, F, or X counts.
    """
    for j, w in enumerate(words):
        nxt = words[j + 1] if j + 1 < len(words) else ""
        if w.lower() == "graphql":
            return True
        if w.startswith("--"):
            if w in ("--method",) and nxt.upper() != "GET":
                return True
            if w.startswith("--method=") and w.split("=", 1)[1].upper() != "GET":
                return True
            if w.split("=", 1)[0] in ("--field", "--raw-field", "--input", "--form"):
                return True
        elif w.startswith("-") and len(w) > 1:
            letters = w[1:]
            if "f" in letters or "F" in letters:
                return True
            if "X" in letters:
                method = letters.split("X", 1)[1] or nxt
                if method.upper() != "GET":
                    return True
    return False


def guard_glab_create(words):
    """`glab mr create` (alias `new`) can push and merge by itself (glab docs, mr/create.md).

    `--push` pushes the branch, `--fill` (`-f`) pushes it unless `--push=false`, and
    `--auto-merge` merges when the checks pass, after the gate's view went stale. A push is
    only `git push [-u] origin <branch>`, and a merge only the gated command.
    """
    no_push = "--push=false" in words
    for w in words:
        if w == "--push" or (w.startswith("--push=") and w != "--push=false"):
            deny("`glab mr create --push` pushes the branch; push with `git push [-u] origin <branch>` first, then "
                 "create the merge request.")
        if (w == "--fill" or w.startswith("--fill=") or re.fullmatch(r"-[A-Za-z]*f[A-Za-z]*", w)) and not no_push:
            deny("`glab mr create --fill` pushes the branch unless `--push=false` is given; push with "
                 "`git push [-u] origin <branch>` and pass the title and description yourself.")
        if w.startswith("--auto-merge") and w != "--auto-merge=false":
            deny("`--auto-merge` merges later, after the merge gate's view went stale; the only merge is the gated "
                 "command `python3 scripts/deliver.py merge-command` prints.")
        if w.startswith("--create-source-branch"):
            ask(f"`glab mr create --create-source-branch` creates a branch on the host outside the workflow's push; "
                f"{STOP}.")


def guard_host(cmd):
    """gh and glab, wherever they appear (a machine may have both): reads run, writes ask, merges deny."""
    if cmd.prog >= len(cmd.words):
        return
    name = base(cmd.words[cmd.prog])
    if name not in CLI_FREE:
        return
    rest = cmd.words[cmd.prog + 1:]
    group = rest[0] if rest else None
    sub = rest[1] if len(rest) > 1 else None
    if group and not group.startswith("-") and group not in KNOWN_GROUPS[name]:
        deny(f"`{name} {group}` is not a built-in {name} command: an alias or extension, which the guard can't read "
             f"(an alias can merge). Run the built-in command it stands for.")
    free = CLI_FREE[name].get(group, ())
    if free is not None and sub not in free:
        ask(f"`{name} {group or ''} {sub or ''}` isn't one of the {name} commands the workflow runs freely (reads and "
            "its change-request steps); it may change the host, so a person approves it.")
    if name == "glab" and "mr" in rest:
        after = rest[rest.index("mr") + 1:]
        if "accept" in after:
            deny("`glab mr accept` is glab's other name for `glab mr merge`; the only merge is the gated command "
                 "`python3 scripts/deliver.py merge-command` prints.")
        if "create" in after or "new" in after:
            guard_glab_create(rest)
    if (name, group, sub) == ("gh", "repo", "sync") and ([w for w in rest[2:] if not w.startswith("-")]
                                                       or "--force" in rest):
        deny("`gh repo sync <repository>` moves a branch on the host (with --force, resets it); branches change only "
             "through `git push [-u] origin <branch>` and the gated merge.")
    if "api" in rest[:2]:
        api = rest[rest.index("api") + 1:]
        if api_writes(api):
            if MERGE_API.search(" ".join(api)):
                deny("This host API call merges or moves a branch (a merge endpoint, a ref, or a commit to a branch). "
                     "The only merge is the gated command `python3 scripts/deliver.py merge-command` prints, and the "
                     "only push is `git push [-u] origin <branch>`.")
            ask(f"This is a host API call that may write; {STOP}.")


# --- git configuration and aliases --------------------------------------------------------------

# git config's read forms; any other git config is a write and asks.
CONFIG_READS = {"--get", "--get-all", "--get-regexp", "--get-urlmatch", "--list", "-l"}
# git's own commands win over aliases of the same name (git help config, alias.*), but only
# when spelled exactly: `git Log` is no built-in, while alias names match in any case.
GIT_BUILTINS = {
    "add", "am", "annotate", "apply", "archive", "bisect", "blame", "branch", "bugreport", "bundle", "cat-file",
    "check-attr", "check-ignore", "check-mailmap", "check-ref-format", "checkout", "checkout-index", "cherry",
    "cherry-pick", "citool", "clean", "clone", "column", "commit", "commit-graph", "commit-tree", "config",
    "count-objects", "credential", "describe", "diagnose", "diff", "diff-files", "diff-index", "diff-tree",
    "difftool", "fast-export", "fast-import", "fetch", "fetch-pack", "filter-branch", "fmt-merge-msg", "for-each-ref",
    "for-each-repo", "format-patch", "fsck", "gc", "grep", "gui", "hash-object", "help", "hook", "index-pack", "init",
    "interpret-trailers", "log", "ls-files", "ls-remote", "ls-tree", "maintenance", "merge", "merge-base",
    "merge-file", "merge-tree", "mergetool", "mktag", "mktree", "mv", "name-rev", "notes", "pack-objects",
    "pack-refs", "prune", "pull", "push", "range-diff", "read-tree", "rebase", "reflog", "remote", "repack",
    "replace", "request-pull", "rerere", "reset", "restore", "rev-list", "rev-parse", "revert", "rm", "send-pack",
    "shortlog", "show", "show-branch", "show-ref", "sparse-checkout", "stash", "status", "stripspace", "submodule",
    "switch", "symbolic-ref", "tag", "update-index", "update-ref", "var", "verify-commit", "verify-tag", "version",
    "whatchanged", "worktree", "write-tree",
}


def git_subcommand(words, start):
    """Index of git's subcommand among `words` (from `start`), past its global options; None if none."""
    j = start
    while j < len(words):
        w = words[j]
        if w in GIT_VALUE_OPTIONS:
            j += 2
        elif w.startswith("-"):
            j += 1
        else:
            return j
    return None


def git_aliases(cwd):
    """The git aliases in effect here: {name, case-folded: value}. git reads alias names in any case."""
    out = sh(["git", "config", "--get-regexp", r"^alias\."], cwd).stdout
    aliases = {}
    for line in out.splitlines():
        key, _, value = line.partition(" ")
        if key.lower().startswith("alias."):
            aliases[fold(key[len("alias."):])] = value
    return aliases


def guard_git(cmd, aliases):
    if cmd.prog >= len(cmd.words) or base(cmd.words[cmd.prog]) != "git":
        return
    words, start = cmd.words, cmd.prog + 1
    # GIT_* variables (GIT_DIR, GIT_SSH_COMMAND, GIT_CONFIG_PARAMETERS, …) change what git
    # runs or where it pushes; `-c` and `--config-env` set any setting for one command
    # (core.fsmonitor, core.sshCommand, alias.* run programs).
    if any(w.startswith("GIT_") for w in words[:cmd.prog]):
        ask("A GIT_* environment variable changes what git runs or where it pushes; a person approves it.")
    si = git_subcommand(words, start)
    if any(w == "-c" or w.startswith("--config-env") for w in words[start:si if si is not None else len(words)]):
        ask("`git -c`/`--config-env` sets git configuration (which can run commands) for this command; a person "
            "approves it.")
    if "config" in words[start:]:
        args = words[words.index("config", start) + 1:]
        names = [a for a in args if not a.startswith("-")]
        if not (CONFIG_READS & {a.split("=", 1)[0] for a in args} or names[:1] in (["get"], ["list"])):
            ask("This is a git setting change (settings can run commands or change where a push goes); a person "
                "approves it.")
    if si is not None and words[si] not in GIT_BUILTINS and fold(words[si]) in aliases():
        value = aliases()[fold(words[si])]
        if LOOSE.search(value) or PUSH_RAW.search(value) or value.lstrip().startswith("!"):
            deny(f"`git {words[si]}` runs the git alias `{value}`, which pushes, merges, or runs a shell; the guard "
                 "can't check it. " + PLAIN_HELP)
        ask(f"`git {words[si]}` runs the git alias `{value}`, which the guard can't check; a person approves it.")
    for w in words[start:]:
        if w != (words[si] if si is not None else None) and fold(w) in aliases():
            ask(f"`git … {w}` may run a git alias, which the guard can't read; a person approves it.")


ASK_COMMANDS = [
    # A token in a command bypasses the CLIs' own sign-in, and can leak into logs.
    (re.compile(r"\b(?:GH|GITHUB|GH_ENTERPRISE|GITHUB_ENTERPRISE|GITLAB|GITLAB_ACCESS|GL|OAUTH|CI_JOB)_TOKEN\b"
                r"|(?i:private-token)"),
     "use of a host token outside the host CLI"),
    # Git, gh, and glab configuration and the repository's own files (hooks, config) ask
    # whatever the command does: write forms are too many to list.
    (re.compile(r"(?<![\w.-])\.git(?![\w-])|\.gitconfig\b|\.config/(?:git|gh|glab-cli)\b"),
     "a command on git, gh, or glab configuration or the .git folder"),
]


# --- shell writes to protected paths ------------------------------------------------------------

# Programs whose every argument may be written, moved, or removed.
WRITE_ALL_ARGS = {"tee", "mv", "cp", "rm", "rmdir", "unlink", "shred", "truncate", "touch", "chmod", "chown", "chgrp",
                  "ln", "install", "rsync", "patch", "uniq", "split", "csplit", "mkdir", "mkfifo", "mknod", "ex", "ed",
                  "vi", "vim", "nvim", "nano", "emacs", "scp", "ditto", "gzip", "gunzip", "bzip2", "xz", "zip"}
# Any program's options that name an output file or folder.
OUTPUT_OPTION = re.compile(r"^--(?:output|out|output-file|output-document|outfile|out-file|outdir|output-dir|"
                           r"log-file|target-directory|directory-prefix|directory)(?:=(.*))?$")
# git subcommands that write the working tree; with no path, `git clean` works on the folder.
GIT_WRITERS = {"checkout", "restore", "reset", "clean", "apply", "am", "stash", "mv", "rm", "read-tree",
               "checkout-index", "update-index", "worktree"}
FIND_WRITES = {"-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprint0", "-fprintf", "-fls"}


def write_targets(cmd):
    """Words of a command that name files or folders it may write; "." stands for its working folder."""
    words, i = cmd.words, cmd.prog
    if i >= len(words):
        return []
    name, args = base(words[i]), words[i + 1:]
    positional = [a for a in args if a and not a.startswith("-")]
    out = []
    for j, a in enumerate(args):
        m = OUTPUT_OPTION.match(a)
        if m:
            out.append(m.group(1) if m.group(1) is not None else (args[j + 1] if j + 1 < len(args) else ""))
    short = [a for a in args if a.startswith("-") and not a.startswith("--")]
    if name in WRITE_ALL_ARGS:
        out += positional + [a.split("=", 1)[1] for a in args if a.startswith("--") and "=" in a]
    elif name == "dd":
        out += [a[3:] for a in args if a.startswith("of=")]
    elif name == "sed" and ("--in-place" in args or any(a.startswith("--in-place=") for a in args)
                            or any("i" in a[1:].split(".", 1)[0] for a in short)):
        out += positional  # -i, -Ei, -i.bak, -ni, --in-place: every file named is rewritten
    elif name == "perl" and any(re.match(r"-[A-Za-z0-9]*i", a) for a in short):
        out += positional  # -i, -pi, -0pi, -wi
    elif name == "sort":
        for j, a in enumerate(args):
            if a == "-o":
                out.append(args[j + 1] if j + 1 < len(args) else "")
            elif a.startswith("-o"):
                out.append(a[2:])
    elif name == "find" and FIND_WRITES & set(args):
        roots = []
        for a in args:
            if a.startswith(("-", "(", "!")):
                break
            roots.append(a)
        out += roots or ["."]
        out += [args[j + 1] for j, a in enumerate(args[:-1]) if a.startswith("-f") and a in FIND_WRITES]
    elif name in ("curl", "wget"):
        for j, a in enumerate(args):
            if a in ("-o", "-O", "-P") and name == "wget" or a == "-o" and name == "curl":
                out.append(args[j + 1] if j + 1 < len(args) else "")
            elif name == "curl" and re.fullmatch(r"-[A-Za-z]*o", a):
                out.append(args[j + 1] if j + 1 < len(args) else "")
            elif name == "curl" and re.fullmatch(r"-[A-Za-z]*o.+", a) and not a.startswith("--"):
                out.append(a.split("o", 1)[1])
            elif name == "curl" and (a in ("-O", "--remote-name", "--remote-name-all", "-J")
                                     or re.fullmatch(r"-[A-Za-z]*O[A-Za-z]*", a)):
                out.append(".")
        if name == "wget" and not any(a in ("-O", "--spider") or a.startswith("--output-document") for a in args):
            out.append(".")
    elif name in ("tar", "bsdtar", "unzip", "7z"):
        extract = name in ("unzip", "7z") or "--extract" in args or "--get" in args or any(
            "x" in a.lstrip("-") for a in args[:1] + short if not a.startswith("--"))
        for j, a in enumerate(args):
            if a in ("-C", "-d", "--directory") and j + 1 < len(args):
                out.append(args[j + 1])
            elif a.startswith("--directory="):
                out.append(a.split("=", 1)[1])
        if extract and not out:
            out.append(".")
        if not extract:
            out += positional  # creating an archive writes the file it names
    elif name == "git":
        si = git_subcommand(words, i + 1)
        if si is not None and words[si] in GIT_WRITERS:
            paths = [a for a in words[si + 1:] if a and not a.startswith("-")]
            out += paths or (["."] if words[si] == "clean" else [])
        elif si is not None and words[si] in ("archive", "format-patch", "bundle"):
            out += [words[k + 1] for k in range(si, len(words) - 1) if words[k] in ("-o", "--output-directory")]
    return out


# Protected paths named in free text (inline code, a script on stdin): asked about when an
# interpreter or shell runs that text. A leading `/` counts as a boundary so absolute paths
# match too. Matched on case-folded text: on macOS's default file system `DOCS/` is `docs/`.
PROTECTED_TEXT_FIXED = (
    r"(?:docs/(?!decision-log\.md(?![\w.-]))|\.claude/|\.github/|\.gitlab/|playbooks/"
    r"|(?:docs|\.claude|\.github|\.gitlab|playbooks)(?=$|[\s'\";&|)])"
    r"|(?:kitchen\.yml|kitchen\.lock|contributing\.md|agents\.md|claude\.md|\.gitlab-ci\.yml"
    r"|scripts/(?:kitchen_lib|hosts|backlog_check|deliver)\.py)(?![\w.-]))"
)
BOUNDARY = r"(?:^|(?<=[\s'\"=/<>(]))"


def protected_text(lock):
    # The lock lists the decision log too (init installs its skeleton); the exemption wins.
    extra = [re.escape(p) + r"(?![\w.-])" for p in sorted(lock.lower) if p != DECISION_LOG]
    if not lock.ok:
        extra.append(r"scripts/")
    return re.compile(BOUNDARY + "(?:" + "|".join([PROTECTED_TEXT_FIXED] + extra) + ")")


def guard_writes(cmds, cwd, root, lock):
    """Ask before a shell command writes a protected path.

    Targets are read from the command (redirects, and the files a writing program names) and
    resolved against the call's working folder, followed through `cd`. Code run by a shell or
    interpreter can write anywhere, so it asks when its text names a protected path or it
    runs inside a protected folder. Reading stays free.
    """
    here = Path(cwd) if Path(cwd).is_dir() else root
    text_re = None
    for cmd in cmds:
        i = cmd.prog
        name = base(cmd.words[i]) if i < len(cmd.words) else ""
        if name in ("cd", "pushd"):
            target = cmd.words[i + 1] if i + 1 < len(cmd.words) else "~"
            if i + 1 < len(cmd.words) and cmd.dynamic[i + 1]:
                here = None  # a folder known only at run time
            elif here is not None and target != "-":
                here = Path(os.path.normpath(os.path.join(str(here), os.path.expanduser(target))))
            continue
        targets = [t for _, t in cmd.redirects] + write_targets(cmd)
        if targets and here is None:
            ask(f"This command writes after `cd` to a folder known only at run time; {STOP}.")
            continue
        for t in targets:
            why = target_reason(t, here, root, lock)
            if why:
                ask(f"This command may write to {why}, which a person approves first.")
        if cmd.code:
            if here is not None and inside_protected(here, root, lock):
                ask(f"This runs code inside {here}, a protected folder; a person approves writes there first.")
            text_re = text_re or protected_text(lock)
            if text_re.search(fold(" ".join(cmd.words[i + 1:] + cmd.bodies))):
                ask("This runs code that names a protected path (docs/, .claude/, .github/, .gitlab/, playbooks/, "
                    "kitchen.yml, kitchen.lock, CONTRIBUTING.md, AGENTS.md, CLAUDE.md, or a framework file); a person "
                    "approves it first.")


def guard_bash(command, cwd, root, k, lock):
    cmds = analyze(command)
    if needs_plain(command, cmds):
        guard_plain(command, cwd, k)
    guard_dynamic(cmds)
    alias_cache = []

    def aliases():
        if not alias_cache:
            alias_cache.append(git_aliases(cwd if Path(cwd).is_dir() else root))
        return alias_cache[0]

    for cmd in cmds:
        guard_host(cmd)
        guard_git(cmd, aliases)
    words = " ".join(w for cmd in cmds for w in cmd.words)
    for pattern, what in ASK_COMMANDS:
        if pattern.search(command) or pattern.search(words):
            ask(f"This is {what}; {STOP}.")
    guard_writes(cmds, cwd, root, lock)


# --- file edits -----------------------------------------------------------------------------

def fold(text):
    """Text as a case-insensitive file system compares it: NFKC-normalized, then case-folded.

    macOS's default file system ignores case and Unicode compatibility forms, so `DOCS/`,
    `docſ/` (long s), and `Kitchen.yml` with a Kelvin sign all name the protected files.
    """
    return unicodedata.normalize("NFKC", text).casefold()


# Git, gh, and glab configuration, where aliases, hooks, credentials, and push settings
# live, wherever it is. `.git/` is matched on the path itself: inside it, git can't name
# the repository root, and a `.git` file (a worktree's or submodule's) redirects git.
CONFIG_FILES = re.compile(r"(?:^|/)\.gitconfig$|/\.config/(?:git|gh|glab-cli)/|(?:^|/)\.git(?:/|$)")
# Repository-relative paths (case-folded) a person approves before an edit: the project's
# definition (docs/), the guardrails and their configuration (.claude/, CI, kitchen.yml,
# kitchen.lock), the process (playbooks/, CONTRIBUTING.md), and the agents' instructions.
# The four framework scripts are named even without a lock: hosts.py defines the only
# merge, deliver.py the merge gate, and the guard imports both. `.claude/` and `.git/`
# count at any depth: both hold configuration that runs code.
PROTECTED_REL = re.compile(r"^(?:docs|\.github|\.gitlab|playbooks)/"
                           r"|^(?:kitchen\.yml|kitchen\.lock|contributing\.md|agents\.md|claude\.md|\.gitlab-ci\.yml)$"
                           r"|^scripts/(?:kitchen_lib|hosts|backlog_check|deliver)\.py$"
                           r"|(?:^|/)\.claude/|(?:^|/)\.git(?:/|$)")
# Folders and files a folder can hold that are protected: deleting or overwriting the
# folder (`rm -rf scripts`, `git clean -fdx` at the root) reaches them.
PROTECTED_PREFIXES = ("docs/", ".claude/", ".github/", ".gitlab/", "playbooks/", ".git/", "scripts/kitchen_lib.py",
                      "scripts/hosts.py", "scripts/backlog_check.py", "scripts/deliver.py")
# Appended to at every ticket's capture step; protecting it would stop every unattended
# delivery (docs/decision-log.md of Test Kitchen, 2026-11-24).
DECISION_LOG = "docs/decision-log.md"


def protected(rel, lock):
    """Why a repository-relative path is protected, or None."""
    low = fold(rel)
    if low == DECISION_LOG:
        return None
    if PROTECTED_REL.search(low):
        return "a definition, guardrail, process, or instruction file"
    if low in lock.lower:
        return "a framework file listed in kitchen.lock"
    if not lock.ok and low.startswith("scripts/"):
        return "under scripts/, and kitchen.lock cannot be read to tell framework scripts from the project's own"
    return None


def relative(path, base):
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return None


def path_reason(path, root, lock):
    """Why writing `path` (absolute, normalized) reaches a protected path, or None."""
    for p in (path, path.resolve()):
        if CONFIG_FILES.search(fold(p.as_posix())):
            return f"{p} (git, gh, or glab configuration)"
        rel = relative(p, root)
        if rel is None:
            if relative(root, p) is not None:
                return f"{p}, which holds the whole project"
            continue
        if rel in ("", "."):
            return "the project root, which holds protected paths"
        why = protected(rel, lock)
        if why:
            return f"{rel} ({why})"
        folder = fold(rel).rstrip("/") + "/"
        if any(x.startswith(folder) for x in PROTECTED_PREFIXES + tuple(lock.lower)) or (
                not lock.ok and folder == "scripts/"):
            return f"{rel}, a folder holding protected paths"
    return None


GLOB_LIMIT = 1000  # a glob's matches checked; a protected path sits near the top of a listing anyway


def target_reason(word, here, root, lock):
    """Why a write target (a shell word, relative to `here`) reaches a protected path, or None. Globs expand."""
    if not word or word == "-":
        return None
    w = os.path.expanduser(word)
    full = w if os.path.isabs(w) else os.path.join(str(here), w)
    paths = glob.glob(full)[:GLOB_LIMIT] if any(ch in w for ch in "*?[") else []
    for p in paths or [full]:
        why = path_reason(Path(os.path.normpath(p)), root, lock)
        if why:
            return why
    return None


def inside_protected(here, root, lock):
    """Is the folder `here` inside a protected folder (docs/, .claude/, …)?"""
    for p in (here, here.resolve()):
        rel = relative(p, root)
        if rel and rel != "." and protected(rel + "/x", lock):
            return True
    return False


def guard_edit(path, cwd, root, lock):
    if not path:
        return
    p = Path(path)
    if not p.is_absolute():
        p = Path(cwd) / p
    # Checked both as written (normalized) and resolved: a symbolic link into a protected
    # folder is that folder, and a protected path that links elsewhere is still named.
    candidates = [Path(os.path.normpath(str(p))), p.resolve()]
    for c in candidates:
        if CONFIG_FILES.search(fold(c.as_posix())):
            ask(f"{path} is git, gh, or glab configuration; a person approves changes to it first.")
    for c, b in ((candidates[0], Path(os.path.normpath(str(root)))), (candidates[1], root.resolve())):
        rel = relative(c, b)
        if rel is None:
            continue
        why = protected(rel, lock)
        if why:
            ask(f"{rel} is {why}; a person approves changes to it first.")


TOOLS = {"Bash", "Edit", "Write", "MultiEdit", "NotebookEdit"}


def main():
    call = json.load(sys.stdin)
    if not isinstance(call, dict):
        raise ValueError("the hook input is not a JSON object")
    global SUBAGENT
    SUBAGENT = is_subagent(call)
    tool = call.get("tool_name")
    if tool not in TOOLS:
        return
    args = call.get("tool_input") or {}
    if not isinstance(args, dict):
        raise ValueError("tool_input is not a JSON object")
    root = find_root()
    cwd = call.get("cwd") or str(root)
    lock = Lock(root)
    if tool == "Bash":
        guard_bash(str(args.get("command") or ""), cwd, root, Kitchen(root), lock)
    else:
        guard_edit(str(args.get("file_path") or args.get("notebook_path") or ""),
                   cwd if Path(cwd).is_dir() else str(root), root, lock)
    finish()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # fail closed: a broken guard must not let the call through
        emit("deny", f"The guard hook failed ({type(e).__name__}: {e}); fix .claude/hooks/guard.py before continuing.")
