# test-kitchen: no-trace (the tickets, tags, and TODOs in this file are test data)
"""Tests for template/claude/hooks/guard.py: every command shape it must allow, ask about, or deny.

Each test builds a throwaway Test Kitchen project (tests/helpers/kitchen_project.py) with the
real `template/scripts/` copied in, the guard installed at `.claude/hooks/guard.py`, a
`kitchen.lock`, and a git repository with a bare local `origin`. The hook runs as Claude Code
runs it: a subprocess fed the PreToolUse JSON on stdin, with CLAUDE_PROJECT_DIR set (unless a
test checks the fallback). Fake `gh` and `glab` executables (tests/fakes/fake_cli.py) are first
on PATH, so the merge gate reads recorded host answers; nothing touches the network.

The shapes come from the guard of the project Test Kitchen was ported from, with neutral
branch names and numbers, plus the cases v0.1 adds: GitLab, the manual host, the autonomy
levels, the decision-log exemption, files listed in kitchen.lock, and failing closed.

Run: python3 -m unittest tests.test_guard -v
"""
import json
import os
import subprocess
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers.kitchen_project import ROOT, Project, kitchen_yml, ticket  # noqa: E402

GUARD = ROOT / "template" / "claude" / "hooks" / "guard.py"
SETTINGS = ROOT / "template" / "claude" / "settings.json"
# A local branch for the push cases. Its name has `source` and `eval` in it, which an
# earlier guard mistook for shell syntax.
B = "guard-test/source-eval-push"
SHA = "0123456789abcdef0123456789abcdef01234567"
# kitchen.lock as init.py writes it (JSON). The hashes are placeholders: the guard reads only
# the file list. `scripts/extra_tool.py` stands for a framework script a later version adds,
# protected only because the lock lists it; `docs/decision-log.md` is listed (init installs
# its skeleton) and must stay editable anyway.
LOCK = {
    "about": "Written by init.py.", "lock_format": 1, "version": "0.1.0", "source": "test",
    "options": {"host": "github", "no_claude": False, "toolchain": None},
    "files": {path: "0" * 64 for path in (
        ".claude/hooks/guard.py", ".claude/settings.json", ".github/workflows/check.yml", "AGENTS.md", "CLAUDE.md",
        "CONTRIBUTING.md", "backlog/README.md", "docs/decision-log.md", "playbooks/deliver.md",
        "scripts/backlog_check.py", "scripts/deliver.py", "scripts/extra_tool.py", "scripts/hosts.py",
        "scripts/kitchen_lib.py")},
    "side_by_side": [],
}


def guard_files(lock=True):
    files = {".claude/hooks/guard.py": GUARD.read_text(encoding="utf-8"),
             ".claude/settings.json": SETTINGS.read_text(encoding="utf-8")}
    if lock:
        files["kitchen.lock"] = json.dumps(LOCK, indent=2) + "\n"
    return files


def make_project(host="github", autonomy="merge", files=None, lock=True):
    """A project with the guard installed and the local branch B; the caller closes it."""
    all_files = guard_files(lock)
    all_files.update(files or {})
    p = Project(files=all_files, kitchen=kitchen_yml(host=host, autonomy=autonomy))
    p.git("branch", "-f", B, "HEAD")
    return p


def run_hook(p, value, tool="Bash", sandbox=False, cwd=None, project_dir=True, raw=None):
    """Feed one tool call to the installed guard; returns (decision, reason).

    "allow" when the guard prints nothing; "error" when it crashed (a test must never pass
    because the hook died silently).
    """
    key = {"Bash": "command", "NotebookEdit": "notebook_path"}.get(tool, "file_path")
    cwd = str(cwd or p.root)
    payload = raw if raw is not None else json.dumps({"tool_name": tool, "tool_input": {key: value}, "cwd": cwd})
    # The sandbox opt-in and the project folder are set per call, never inherited: a session
    # running these tests (itself perhaps a Claude Code session) must not leak its own.
    env = p.env()
    env.pop("CLAUDE_PROJECT_DIR", None)
    if project_dir:
        env["CLAUDE_PROJECT_DIR"] = str(p.root)
    if sandbox:
        env["KITCHEN_GUARD_SANDBOX"] = "1"
    r = subprocess.run([sys.executable, str(p.root / ".claude" / "hooks" / "guard.py")], input=payload,
                       capture_output=True, text=True, env=env, cwd=cwd)
    if r.returncode or r.stderr.strip():
        return "error", f"exit {r.returncode}: {r.stderr}"
    if not r.stdout.strip():
        return "allow", ""
    o = json.loads(r.stdout)["hookSpecificOutput"]
    return o["permissionDecision"], o["permissionDecisionReason"]


ALLOW = [
    "npm run check",
    "python3 scripts/backlog_check.py docs/",
    "python3 scripts/deliver.py gate red US-PAY-02 2>&1 | tail",
    "git log --oneline origin/main..HEAD",
    "gh pr view 7 --json state",
    "gh pr list --state open",
    "echo $HOME && ls",
    "export PATH=\"$HOME/bin:$PATH\" && npm test",
    "git stash list",
    "H=$(gh pr view 31 --json headRefOid -q .headRefOid) && python3 scripts/deliver.py gate pr --body-file=b.md "
    "--branch=x --base=$(git merge-base origin/main $H) --head=$H",
    "git log --oneline $(git merge-base origin/main HEAD)..HEAD",
    "git commit -q -F - <<'EOF'\nfix: it isn't broken\nEOF",
    'git commit -m "$(cat <<\'EOF\'\nfix: don\'t break\nEOF\n)"',
    # Pushes: one existing local branch, by name.
    f"git push -u origin {B}",
    f"git push origin {B}",
    f"git push --set-upstream origin {B}",
    f"git commit -m \"fix: push the branch, don't merge\" && git push origin {B}",
    # The workflow's own command blocks (playbooks/deliver.md steps 5, 8, 11, 12, 13).
    f"# set status: in-progress in the ticket file, then:\ngit add backlog/ && git commit -m \"chore: start US-PAY-01\"\n"
    f"git push -u origin {B}\ngh pr create --draft --base main --head {B} --title \"feat: US-PAY-01 title\" "
    "--body-file body.md",
    "git fetch origin && git merge origin/main",
    "git fetch origin && git merge origin/main   # resolve conflicts before pushing",
    f"git push origin {B} && gh pr edit 5 --body-file body.md && gh pr ready 5",
    "gh pr checks 5 --watch --fail-fast",
    "gh pr view 5 --json headRefOid -q .headRefOid",
    "gh pr view 5 --json mergeCommit -q .mergeCommit.oid",
    "gh run list --branch main --commit abc --json databaseId,status -q '.[0].databaseId'",
    "gh run watch 123 --exit-status",
    f"python3 scripts/deliver.py gate merge 7 --head={SHA}",
    f"python3 scripts/deliver.py merge-command 7 --head={SHA}",
    "python3 scripts/deliver.py pr-body US-PAY-01 > /tmp/body.md",
    "git add backlog && git commit -m \"docs: delivery record\"",
    # Read-only commands that mention the words; `$` and `\\` are literal inside single quotes.
    "grep -nE 'push$|merge\\b' .claude/hooks/guard.py | head",
    "gh api repos/o/r/pulls/7",
    "gh api -X GET repos/o/r/pulls",
    # fetch and pull from origin by branch; git config reads; names that only contain `.git`.
    "git pull --ff-only origin main",
    f"git fetch -q origin main && git push origin {B}",
    "git config --get-regexp alias",
    "git config --list",
    "cat .gitignore && ls .github/workflows",
    "cat .gitlab-ci.yml",
    # GitLab's workflow steps, and its reads (allowed whatever host kitchen.yml names).
    f"git push -u origin {B}\nglab mr create --draft --source-branch {B} --target-branch main "
    "--title \"feat: US-PAY-01 title\" --description-file body.md --yes",
    "glab mr view 7 --output json",
    f"glab mr view {B} --output json --jq .iid",
    "glab mr list",
    f"git push origin {B} && glab mr update 7 --description-file body.md --yes && glab mr update 7 --ready --yes",
    "glab mr note 7 --message done",
    "glab mr diff 7",
    "glab mr checkout 7",
    "glab ci status --branch main --wait",
    "glab ci list",
    "glab ci trace 123",
    "glab api projects/:fullpath/pipelines/5/jobs",
    "glab api --paginate projects/:fullpath/merge_requests",
    "glab api -X GET projects/:fullpath/merge_requests",
    "glab mr create --fill --push=false --draft --yes",
    "gh --version",
    "glab --version",
    # The decision log takes entries without a person (decision log, 2026-11-24); reading
    # protected paths stays free.
    "echo '- entry' >> docs/decision-log.md",
    "cat docs/product.md kitchen.yml kitchen.lock CONTRIBUTING.md AGENTS.md CLAUDE.md",
    "grep -rn push playbooks/ scripts/deliver.py",
    # Push and merge as path parts or quoted search patterns are no push (review item 9).
    "rg -n 'push' src/",
    "rg -n push src/",
    "npx vitest run tests/push.test.ts",
    "python3 -m pytest tests/merge/",
    "sed -n 1,40p src/merge.py",
    "npx vitest run -t 'merge requests'",
    "grep -rn refund docs/requirements > /tmp/hits.txt",
    "cat docs/product.md 2>/dev/null",
    "ls docs >&2",
    # The documented workflow, step by step (playbooks/deliver.md).
    "git switch main\ngit pull --ff-only origin main\ngit switch -c us-pay-03-x\npython3 scripts/deliver.py context US-PAY-03",
    f"git add backlog\ngit commit -m \"chore: start US-PAY-03\"\ngit push -u origin {B}",
    "git commit -m \"test: US-PAY-03 failing tests\"",
    "git fetch origin\ngit merge origin/main",
    f"python3 scripts/deliver.py record --body-file=/tmp/US-PAY-03.md --branch={B} --cr=7\ngit add backlog\n"
    "git commit -m \"docs: delivery record\"\npython3 scripts/backlog_check.py --pr-body=/tmp/US-PAY-03.md\n"
    f"python3 scripts/deliver.py gate pr --body-file=/tmp/US-PAY-03.md --branch={B}\ngit push origin {B}",
    f"python3 scripts/deliver.py record --body-file=.kitchen/body.md --branch={B} --cr=7",
    f"gh pr create --draft --base main --head {B} --title \"feat: US-PAY-03 Push refunds\" --body-file /tmp/b.md",
    f"glab mr create --draft --source-branch {B} --target-branch main --title \"feat: US-PAY-03 merge refunds\" "
    "--description-file /tmp/b.md --yes",
    "glab mr view 7 --output json --jq .merge_commit_sha",
    f"git commit -F /tmp/msg.txt && git push origin {B}",
    f"git commit -m \"fix: US-PAY-03 handle merge of refunds\" && git push origin {B}",
    "gh pr checks 7 --watch --fail-fast && gh pr checks 7",
    "python3 scripts/deliver.py check",
    "git fetch origin\npython3 scripts/deliver.py next",
    "cat >> docs/decision-log.md <<'EOF'\n### 2026-11-24 \u2014 x\nRecorded in kitchen.yml.\nEOF",
    "git commit -q -F - <<'EOF'\nfix: update kitchen.yml and docs/product.md wording\nEOF",
]

ASK = [
    "sed -i '' s/a/b/ scripts/deliver.py",
    "sed -i '' s/a/b/ scripts/extra_tool.py",
    "sed -i '' s/a/b/ playbooks/deliver.md",
    "python3 - <<'EOF'\nopen('docs/x.md','w')\nEOF",
    "cat > docs/x.md <<'EOF'\nit's\nEOF",
    "tee playbooks/a.md <<EOF\nx\nEOF",
    "echo x >> .git/config",
    "echo x >> ~/.gitconfig",
    "gh api repos/x/y --method PUT -f a=b",
    "gh api -X put repos/o/r/pulls/7",
    "curl -X PUT -H \"Authorization: token $(gh auth token)\" https://api.github.com/repos/o/r",
    "gh alias set m 'pr view'",
    "git config remote.origin.pushurl x",
    "git config --global alias.p '!true'",
    "git config core.hooksPath /dev/null",
    # Write forms the shell check missed (found in review), and any command on .git or config.
    "git log -1 --output=.git/config",
    "sort -o .git/config x",
    "cd .git && ls",
    "git log -1 --out=docs/x.md",
    "sort -o docs/x.md x",
    # Every git config write: keys such as core.fsmonitor run commands.
    "git config core.fsmonitor ./x.sh",
    "git -C . config core.sshCommand x",
    "gh config set pager x",
    # git config values that contain the words get or list are still writes (found in review).
    "git config core.fsmonitor 'touch /tmp/x list'",
    "git config alias.st list",
    # gh commands outside the workflow's reads and change-request steps (found in review: repo sync --force).
    "gh repo sync",
    "gh workflow run check.yml",
    # Write forms on protected paths (found in review).
    "git checkout origin/main -- .claude/hooks/guard.py",
    "echo x | uniq - docs/x.md",
    # GitLab API writes, glab outside the workflow, tokens, and the CLIs' configuration.
    "glab api projects/:fullpath/merge_requests/7 -X PUT -f title=x",
    "glab api -X post projects/:fullpath/pipeline",
    "glab api graphql -f query='mutation { x }'",
    "glab api projects/:fullpath/variables --form key=x",
    "glab api projects/:fullpath/issues -F title=x",
    "glab mr approve 7",
    "glab mr close 7",
    "glab mr rebase 7",
    "glab ci run",
    "glab ci retry 5",
    "glab ci view",
    "glab repo mirror o/r --direction pull",
    "glab alias set m 'mr view'",
    "glab variable set X y",
    "glab release create v1",
    "glab config set editor vim",
    "glab -R o/r mr view 7",
    "glab mr create --create-source-branch --title x --yes",
    "GH_TOKEN=x gh pr view 7",
    "echo $GITHUB_TOKEN",
    "echo $GITLAB_TOKEN",
    "curl -H \"PRIVATE-TOKEN: $T\" https://gitlab.example.com/api/v4/projects",
    "cat ~/.config/glab-cli/config.yml",
    "ls ~/.config/gh",
    "cat ~/.config/git/config",
    # Shell writes to the rest of the protected paths, the framework scripts, and lock-listed files.
    "echo x > kitchen.yml",
    "echo '{}' > kitchen.lock",
    "echo x >> CONTRIBUTING.md",
    "cp a AGENTS.md",
    "mv x CLAUDE.md",
    "echo x > .gitlab-ci.yml",
    "rm .gitlab/merge_request_templates/Default.md",
    "echo x > .github/workflows/check.yml",
    "rm scripts/hosts.py",
    "cp x scripts/kitchen_lib.py",
    "echo x >> backlog/README.md",
    "echo x > docs/product.md",
    "echo x >> docs/decision-log.md.bak",
    "rm -rf docs",
    "rm -rf .claude",
    "echo x > Docs/x.md",
    "touch playbooks/new.md",
    # Redirect and write forms the review found (item 6), and Unicode folding (item 8).
    "echo x 1>kitchen.yml",
    "echo x 2> docs/product.md",
    "echo x &> CONTRIBUTING.md",
    "echo x 1>> .claude/settings.json",
    "echo x >| AGENTS.md",
    "echo x >&docs/product.md",
    "sed -E -i '' 's/a/b/' scripts/deliver.py",
    "sed -e s/merge/x/ -i '' scripts/hosts.py",
    "sed --in-place s/a/b/ kitchen.yml",
    "sed -i.bak s/a/b/ CLAUDE.md",
    "perl -0pi -e 's/a/b/' playbooks/deliver.md",
    "perl -w -i -pe 's/a/b/' AGENTS.md",
    "find docs -name '*.md' -delete",
    "find .claude -exec touch {} +",
    "curl -sL -o .github/workflows/check.yml https://example.invalid/x",
    "curl -sLo kitchen.yml https://example.invalid/x",
    "wget -O playbooks/deliver.md https://example.invalid/x",
    "tar -xf /tmp/a.tar -C .claude",
    "git clean -fdx docs/",
    "git clean -fdx",
    "rm -rf scripts",
    "rm -rf *",
    "dd if=/dev/zero of=kitchen.lock count=1",
    "cd docs && echo x > product.md",
    "bash -c 'echo x > docs/product.md'",
    "node -e \"require('fs').writeFileSync('kitchen.yml', '')\"",
    "echo x > doc\u017f/product.md",
    "\"git\" config core.fsmonitor ./x.sh",
    "git -c core.fsmonitor=./x.sh status",
    "GIT_SSH_COMMAND=./x.sh git fetch origin",
]

# Force pushes ask, and keep asking in sandbox mode.
FORCE_ASK = [
    f"git push --force-with-lease origin {B}",
    f"git push origin +{B}",
    f"git push --force origin {B}",
    f"git push -f origin {B}",
]

DENY = [
    # Pushes to the default branch, and refspecs that reach it (found in review: heads/main, wildcards, `:`).
    "git push origin main",
    "git push origin MAIN",
    "git push origin feature:main",
    "git push origin HEAD:refs/heads/main",
    "git push origin :main",
    "git push origin heads/main",
    "git push origin HEAD:heads/main",
    "git push origin 'refs/heads/*:refs/heads/*'",
    "git push origin :",
    "git push origin HEAD",
    "git push",
    "git push origin",
    "git push --all",
    "git push --mirror origin",
    "git push origin --all",
    "git push origin no-such-branch-here",
    f"git push upstream {B}",
    f"git push origin {B} other",
    f"git push --no-verify origin {B}",
    "git push --force origin main",
    # Pushes after a switch or from elsewhere (found in review).
    "git switch main && git push",
    "git -C ../wt push origin HEAD",
    "cd x && git push",
    # Options and config before the subcommand (found in review).
    f"git -C . push origin {B}",
    "git --no-pager push origin main",
    "git -c remote.origin.push=HEAD:refs/heads/main push origin",
    "git -c push.default=matching push origin",
    "git -c alias.p=push p origin main",
    "git --git-dir=.git push origin main",
    "git config push.default matching",
    "git config remote.origin.push HEAD:refs/heads/main",
    "git config branch.x.merge refs/heads/main",
    # Programs and subcommands that push without `git push` (found in review).
    "git send-pack git@example.com:o/r.git feature:main",
    "/Library/Developer/CommandLineTools/usr/libexec/git-core/git-push origin main",
    "git subtree push --prefix=app origin main",
    # Wrappers, shells, and run-time construction.
    "/usr/bin/gh pr merge 7 --admin",
    "./gh pr merge 7 --auto",
    "env gh pr merge 7 --admin",
    "command git push origin main",
    "timeout 5 gh pr merge 7 --merge",
    "GIT_DIR=.git git push origin main",
    "(git push origin main)",
    "{ git push origin main; }",
    "f(){ git push origin main; }; f",
    "find . -maxdepth 0 -exec git push origin main ;",
    "python3 -c \"import os; os.system('git push origin main')\"",
    "G=gh; $G pr merge 7 --admin",
    "$(echo gh) pr merge 7 --admin",
    "g$()h pr merge 7 --admin",
    "gh pr $'merge' 7 --admin",
    "eval 'gh pr merge 7 --admin'",
    "eval \"git push origin main\"",
    "sh -c 'git push origin main'",
    "bash -c \"gh pr merge 7 --admin\"",
    "bash -e -c 'git push origin main'",
    "bash --norc -c 'gh pr merge 7 --admin'",
    "zsh -f -c 'git push origin main'",
    "fish -c 'git push origin main'",
    "echo 'git push origin main' | bash",
    "echo 'git push origin main' | sh",
    "bash <<< 'git push origin main'",
    "gh pr mer\\\nge 7 --admin",
    "git pu\\\nsh origin main",
    "B=main; git push origin $B",
    "echo main | xargs git push origin",
    "git push origin \"$B\"",
    f"git push -u origin {B} 2>&1 | tail",
    # Heredocs: a body with an odd quote hid the next line from the old parser (found in review).
    "cat <<'EOF'\nit's\nEOF\ngit push origin main # '",
    "cat <<'EOF'\nit\"\nEOF\ngh pr merge 7 --admin # \"",
    "git commit -m \"$(cat <<'EOF'\nfix: x\"\nEOF\n)\"; git push origin main # \"",
    "git commit -m \"$(cat <<'EOF'\nfix: push the branch\nEOF\n)\" && git push -u origin " + B,
    "cat <<EOF; gh pr merge 7 --admin\nbody\nEOF",
    "cat <<EOF && git push origin main\nbody\nEOF",
    "cat <<'EOF' | sh; gh pr merge 7 --auto\nit's\nEOF",
    "echo '<<X'\ngh pr merge 7 --admin\nX",
    "true # <<X\ngh pr merge 7 --admin\nX",
    "cat <<<X\ngh pr merge 7 --admin\nX",
    "echo $((1<<X))\ngit push origin main\nX",
    "git commit -F - <<'EOF'\nisn't\nEOF\ngit push origin main",
    "echo 'unterminated ; gh pr merge 5 --admin",
    # Comments that a shell without comments would run.
    "# x; git push origin main",
    "# it's\necho 'x\ngit push origin main\n'",
    # Merges: only the host adapter's exact command, alone.
    "gh pr merge 7 --merge",
    "gh pr merge --merge 7",
    "gh pr merge 7 --merge --admin",
    f"gh pr merge 7 --merge --admin=true --match-head-commit {SHA}",
    f"gh pr merge 7 --merge --auto=true --match-head-commit {SHA}",
    f"gh pr merge 7 --squash --match-head-commit {SHA}",
    f"gh pr merge 7 --rebase --match-head-commit {SHA}",
    f"gh pr merge 7 -s --match-head-commit {SHA}",
    f"gh pr merge 7 --merge --match-head-commit {SHA[:12]}",
    f"gh pr merge 7 --merge --match-head-commit {SHA.upper()}",
    f"gh pr merge https://github.com/other/repo/pull/5 --merge --match-head-commit {SHA}",
    f"gh pr merge us-pay-01-x --merge --match-head-commit {SHA}",
    f"gh pr merge 007 --merge --match-head-commit {SHA}",
    f"gh pr merge 7 -R someone/else --merge --match-head-commit {SHA}",
    # Exactly the printed command: no reordering, no `=` forms, no extra options (the source
    # project let these reach its gate; v0.1 compares with hosts.merge_argv word for word).
    f"gh pr merge 7 --match-head-commit={SHA} --merge --delete-branch",
    f"gh pr merge 7 --merge --match-head-commit {SHA} --delete-branch",
    f"gh pr merge 7 --match-head-commit {SHA} --merge",
    "gh pr -R o/r merge 7 --admin",
    "gh --repo o/r pr merge 7 --admin",
    "gh pr merge $(gh pr list -q x)",
    "gh api -X PUT repos/o/r/pulls/7/merge",
    "gh alias set m 'pr merge'",
    # The merge race: commits pushed in the same call would merge unreviewed (found in review).
    f"git commit --allow-empty -m late && git push origin {B} && gh pr merge 7 --merge --match-head-commit {SHA}",
    f"gh pr merge 7 --merge --match-head-commit {SHA} & git push origin {B}",
    f"gh pr merge 7 --merge --match-head-commit {SHA}; true",
    # The GitLab merge is not this (github) project's merge, and bypasses are refused on it too.
    f"glab mr merge 7 --sha {SHA} --auto-merge=false --yes",
    "/usr/bin/glab mr merge 7 --yes",
    "env glab mr merge 7",
    f"glab mr merge 7 --auto-merge --sha {SHA} --yes",
    f"glab mr merge 7 --squash --sha {SHA} --auto-merge=false --yes",
    f"glab mr merge {B} --sha {SHA} --auto-merge=false --yes",
    "glab api -X PUT projects/:fullpath/merge_requests/7/merge",
    "glab repo mirror o/r --direction push",
    "glab alias set m 'mr merge'",
    f"git push origin {B} && glab mr merge 7 --sha {SHA} --auto-merge=false --yes",
    # `glab mr create` pushes with --push or --fill, and merges later with --auto-merge (glab docs).
    "glab mr create --fill --yes",
    "glab mr create -f -y",
    "glab mr create -fy",
    "glab mr create --push --title x --yes",
    "glab mr create --push=true --title x --yes",
    "glab mr create --auto-merge --title x --yes",
    "glab -R o/r mr create --fill --yes",
    # A carriage return is a word character to bash and zsh, so `#` after it is no comment (found in review).
    "echo push\r#`git push origin HEAD:main`",
    "echo merge\r#`gh pr merge 7 --admin`",
    # Comments hold only plain words.
    "true # `git push origin HEAD:main`",
    "git status # ${x} `git push origin HEAD:main`",
    # fetch and pull options that run commands (found in review), abbreviated too, and other remotes.
    "git fetch --upload-pack='git push origin HEAD:main;:' .",
    "git pull --upload-pack='gh pr merge 7 --admin;:' .",
    f"git fetch --upload='true;:' . && git push origin {B}",
    f"git fetch . && git push origin {B}",
    # Characters outside the word list: subshells, background, braces, tilde, non-ASCII.
    f"(git push origin {B})",
    f"git push origin {B} & gh pr view 1",
    f"git push origin {B} |& cat",
    f"git push origin {{{B},main}}",
    f"git push origin {B}; ls ~",
    f"git push origin {B} ",
    # A comment ending in a backslash doesn't continue in bash or zsh (found in review).
    "# note\\\ngit push origin main",
    "git status # x\\\ngh pr merge 5 --admin",
    # Programs that write files or run others (found in review: rg --pre, sort -o).
    "echo git push origin main | sort -o /tmp/s.sh; rg --pre sh x /tmp/s.sh",
    # git options outside the workflow's list (merge -s runs git-merge-<name>), and http-push.
    f"git merge -s evil origin/main && git push origin {B}",
    f"git log --output=x && git push origin {B}",
    "git http-push https://example.com/r.git main",
    # An ask on one part of a call never hides a denial of another part.
    f"git push --force origin {B} && git push origin main",
    f"git push -f origin {B}; git push origin feature:main",
    # Words spliced at run time (review item 1): the shell runs these as push and merge.
    "git pu$'\\x73'h origin main",
    "git $'\\x70'ush origin HEAD:main",
    "git pu$()sh origin main",
    "git pu`true`sh origin main",
    "git pu${x}sh origin main",
    "git pu\\sh origin main",
    "gh pr mer$'\\x67'e 7 --admin",
    "gh pr mer$()ge 7 --admin",
    "g$()it push origin main",
    "$(echo git) pu$()sh origin main",
    "sh -c 'git pu$()sh origin main'",
    "git co$()nfig core.fsmonitor ./x.sh",
    "gh a$()pi repos/o/r/merges -f base=main",
    # Host API merges and branch writes are denied, not asked (review items 2 and 3).
    "gh api repos/o/r/merges -f base=main -f head=x",
    f"gh api repos/o/r/merges -fbase=main -fhead={B}",
    f"gh api repos/o/r/merges -Fbase=main -Fhead={B}",
    "gh api graphql -f query='mutation { mergePullRequest(input: {}) { clientMutationId } }'",
    "gh api graphql -f query='mutation { enablePullRequestAutoMerge(input: {}) { clientMutationId } }'",
    "gh api -XPUT repos/o/r/pulls/7/merge",
    "gh api repos/o/r/git/refs/heads/main -X PATCH -f sha=x",
    "gh api repos/o/r/contents/README.md -X PUT -f message=x -f content=eA== -f branch=main",
    "\"gh\" api repos/o/r/merges -f base=main -f head=x",
    "g''h api repos/o/r/merges -f base=main -f head=x",
    "glab api projects/:fullpath/repository/commits -fbranch=main -fcommit_message=x",
    "glab api -X PUT projects/:fullpath/merge_requests/7/merge",
    "glab api -X PUT projects/:fullpath/merge_requests/7/merge_when_pipeline_succeeds",
    # glab's other names for merge and create (review item 3).
    "glab mr accept 7 --yes",
    "glab mr new --fill --yes",
    "glab mr new --fill --auto-merge --yes",
    # gh aliases and extensions can't be read, and a remote repo sync moves a branch.
    "gh m 7 --admin",
    "gh repo sync o/r --source f/r --branch main --force",
    "\"gh\" repo sync o/r --source f/r --branch main --force",
    "\"git\" config alias.ship push",
]

# A well-formed merge reaches the merge gate, which refuses: the fake gh has no answer for it.
REACHES_GATE = [
    f"gh pr merge 7 --merge --match-head-commit {SHA}",
    f"gh pr merge '7' --merge --match-head-commit \"{SHA}\"",
]

# Paths relative to the project root that a file edit asks about.
EDIT_ASK = [
    "docs/x.md",
    "docs/requirements/PAY-payments.md",
    "docs/architecture/ADR-001-storage.md",
    ".git/config",
    ".git/hooks/pre-push",
    ".git",
    ".claude/settings.json",
    ".claude/settings.local.json",
    ".claude/hooks/guard.py",
    "src/.claude/settings.json",
    ".github/workflows/check.yml",
    ".gitlab/merge_request_templates/Default.md",
    ".gitlab-ci.yml",
    "playbooks/deliver.md",
    "playbooks/new.md",
    "kitchen.yml",
    "kitchen.lock",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "CLAUDE.md",
    "scripts/deliver.py",
    "scripts/hosts.py",
    "scripts/kitchen_lib.py",
    "scripts/backlog_check.py",
    "scripts/extra_tool.py",
    "scripts/extra_tool.py.kitchen-new",
    "backlog/README.md",
    "DOCS/x.md",
    "Kitchen.yml",
    "docs/decision-log.md.bak",
    "src/../docs/x.md",
    "doc\u017f/product.md",
    "\u017fcripts/hosts.py",
    ".claude/\u017fettings.json",
    "\u212aitchen.yml",
]

# Git, gh, and glab configuration outside the project (never written: the hook only judges).
HOME_CONFIG_ASK = [
    str(Path.home() / ".gitconfig"),
    str(Path.home() / ".config" / "git" / "config"),
    str(Path.home() / ".config" / "gh" / "config.yml"),
    str(Path.home() / ".config" / "glab-cli" / "config.yml"),
]

EDIT_ALLOW = [
    "src/pay.py",
    "tests/test_pay.py",
    "backlog/PAY-payments/US-PAY-01-refunds.md",
    "backlog/PAY-payments/delivery/US-PAY-01.md",
    "docs/decision-log.md",
    "Docs/Decision-Log.md",
    "README.md",
    "scripts/my_tool.py",
    "app/docs/x.md",
    ".gitignore",
    ".github-notes.md",
    "playbooks.md",
]


class GuardCase(unittest.TestCase):
    """One project for the whole class (host github, autonomy merge); tests only read it."""
    HOST = "github"
    AUTONOMY = "merge"

    @classmethod
    def setUpClass(cls):
        cls.p = make_project(cls.HOST, cls.AUTONOMY)
        cls.addClassCleanup(cls.p.close)

    def hook(self, value, tool="Bash", **kw):
        return run_hook(self.p, value, tool, **kw)

    def check(self, cases, want, tool="Bash", **kw):
        # The calls only read the project, so they run side by side; results are asserted in order.
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda value: self.hook(value, tool, **kw), cases))
        for value, (got, reason) in zip(cases, results):
            with self.subTest(value=value):
                self.assertEqual(got, want, reason)

    def path(self, rel):
        return str(self.p.root / rel)


class ShapesTest(GuardCase):
    def test_allows(self):
        self.check(ALLOW, "allow")

    def test_asks(self):
        self.check(ASK, "ask")

    def test_force_pushes_ask(self):
        self.check(FORCE_ASK, "ask")

    def test_denies(self):
        self.check(DENY, "deny")

    def test_a_well_formed_merge_runs_the_merge_gate(self):
        for command in REACHES_GATE:
            with self.subTest(command=command):
                got, reason = self.hook(command)
                self.assertEqual(got, "deny", reason)
                self.assertIn("Merge gate failed", reason)
                self.assertIn("cannot read pull request 7", reason)

    def test_a_merge_names_the_exact_printed_command(self):
        got, reason = self.hook(f"gh pr merge 7 --merge --match-head-commit {SHA} --delete-branch")
        self.assertEqual(got, "deny")
        self.assertIn(f"`gh pr merge 7 --merge --match-head-commit {SHA}`", reason)
        got, reason = self.hook(f"glab mr merge 7 --sha {SHA} --auto-merge=false --yes")
        self.assertIn("the host is github", reason)
        got, reason = self.hook(f"gh pr merge 7 --merge --admin --match-head-commit {SHA}")
        self.assertIn("never bypass", reason)

    def test_merges_and_pushes_must_be_plain_and_say_why(self):
        got, reason = self.hook("git push origin $B")
        self.assertEqual(got, "deny")
        self.assertIn("plain commands", reason)
        got, reason = self.hook(f"git push origin {B} && gh pr merge 7 --merge --match-head-commit {SHA}")
        self.assertIn("alone in its call", reason)

    def test_a_push_to_the_default_branch_names_it(self):
        got, reason = self.hook("git push origin main")
        self.assertEqual(got, "deny")
        self.assertIn("default branch (main)", reason)

    def test_an_ask_never_hides_a_denial_even_in_sandbox(self):
        for command in (f"git push --force origin {B} && git push origin main", "glab -R o/r mr create --fill --yes",
                        "gh repo view && git push origin main"):
            with self.subTest(command=command):
                self.assertEqual(self.hook(command, sandbox=True)[0], "deny")

    def test_git_aliases(self):
        # git reads alias names in any case; an alias that pushes, merges, or runs a shell is
        # denied (review item 4), any other asks, and a built-in name runs the built-in.
        for key, value in (("alias.ship", "push"), ("alias.land", "merge origin/main"), ("alias.sh", "!git push"),
                           ("alias.st", "status"), ("alias.log", "push")):
            self.p.git("config", key, value)
            self.addCleanup(self.p.git, "config", "--unset", key)
        for command in (f"git ship origin {B}", "git Ship origin main", "git SHIP origin main", "git land",
                        "git Sh"):
            with self.subTest(command=command):
                got, reason = self.hook(command)
                self.assertEqual(got, "deny", reason)
                self.assertIn("git alias", reason)
                self.assertEqual(self.hook(command, sandbox=True)[0], "deny")
        got, reason = self.hook("git st")
        self.assertEqual(got, "ask", reason)
        self.assertEqual(self.hook("git log --oneline")[0], "allow")
        self.assertEqual(self.hook("git Log origin main")[0], "deny")

    def test_writes_resolve_against_the_call_cwd(self):
        # Review item 7: a relative target is read from the folder the command runs in.
        self.assertEqual(self.hook("sed -i '' s/a/b/ product.md", cwd=self.p.root / "docs")[0], "ask")
        self.assertEqual(self.hook("echo '{}' > settings.json", cwd=self.p.root / ".claude")[0], "ask")
        self.assertEqual(self.hook("python3 -c \"open('x', 'w')\"", cwd=self.p.root / "docs")[0], "ask")
        self.assertEqual(self.hook("echo x > decision-log.md", cwd=self.p.root / "docs")[0], "allow")
        self.assertEqual(self.hook("echo x > notes.txt", cwd=self.p.root / "backlog")[0], "allow")

    def test_unguarded_tools_and_empty_input_pass(self):
        self.assertEqual(run_hook(self.p, None, raw=json.dumps({"tool_name": "Read", "tool_input": {"file_path": "x"}}))[0],
                         "allow")
        self.assertEqual(self.hook(""), ("allow", ""))


class EditTest(GuardCase):
    def test_edits_to_protected_paths_ask(self):
        self.check([self.path(rel) for rel in EDIT_ASK] + HOME_CONFIG_ASK, "ask", tool="Write")
        for tool in ("Edit", "MultiEdit"):
            self.check([self.path(rel) for rel in ("docs/x.md", "kitchen.yml", "scripts/extra_tool.py")], "ask", tool=tool)

    def test_other_edits_pass(self):
        self.check([self.path(rel) for rel in EDIT_ALLOW] + [str(self.p.tmp / "outside.txt")], "allow", tool="Write")

    def test_the_decision_log_is_exempt_though_the_lock_lists_it(self):
        self.assertIn("docs/decision-log.md", LOCK["files"])
        self.assertEqual(self.hook(self.path("docs/decision-log.md"), "Edit"), ("allow", ""))
        got, reason = self.hook(self.path("docs/product.md"), "Edit")
        self.assertEqual(got, "ask", reason)

    def test_a_lock_listed_file_says_so(self):
        got, reason = self.hook(self.path("scripts/extra_tool.py"), "Edit")
        self.assertEqual(got, "ask")
        self.assertIn("listed in kitchen.lock", reason)

    def test_notebooks(self):
        self.assertEqual(self.hook(self.path("docs/n.ipynb"), "NotebookEdit")[0], "ask")
        self.assertEqual(self.hook(self.path("src/n.ipynb"), "NotebookEdit")[0], "allow")

    def test_relative_paths_resolve_against_the_call_cwd(self):
        (self.p.root / "src").mkdir(exist_ok=True)
        self.assertEqual(self.hook("docs/x.md", "Write")[0], "ask")
        self.assertEqual(self.hook("x.md", "Write", cwd=self.p.root / "docs")[0], "ask")
        self.assertEqual(self.hook("../kitchen.yml", "Write", cwd=self.p.root / "src")[0], "ask")
        self.assertEqual(self.hook("pay.py", "Write", cwd=self.p.root / "src")[0], "allow")

    def test_a_symbolic_link_into_a_protected_folder_asks(self):
        link = self.p.root / "notes"
        link.symlink_to(self.p.root / "docs", target_is_directory=True)
        self.addCleanup(link.unlink)
        got, reason = self.hook(str(link / "x.md"), "Write")
        self.assertEqual(got, "ask", reason)


class SandboxTest(GuardCase):
    """KITCHEN_GUARD_SANDBOX=1 is a per-machine opt-in: asks pass, denials and force pushes don't."""

    def test_sandbox_lets_asks_through(self):
        self.check(ASK, "allow", sandbox=True)
        self.check([self.path(rel) for rel in EDIT_ASK] + HOME_CONFIG_ASK, "allow", tool="Write", sandbox=True)

    def test_sandbox_still_denies(self):
        self.check(DENY, "deny", sandbox=True)

    def test_sandbox_still_asks_on_a_force_push(self):
        self.check(FORCE_ASK, "ask", sandbox=True)

    def test_sandbox_still_runs_the_merge_gate(self):
        got, reason = self.hook(REACHES_GATE[0], sandbox=True)
        self.assertEqual(got, "deny")
        self.assertIn("Merge gate failed", reason)

    def test_other_values_are_not_the_opt_in(self):
        env_value = "true"
        p = self.p
        env = p.env()
        env["CLAUDE_PROJECT_DIR"] = str(p.root)
        env["KITCHEN_GUARD_SANDBOX"] = env_value
        r = subprocess.run([sys.executable, str(p.root / ".claude" / "hooks" / "guard.py")],
                           input=json.dumps({"tool_name": "Bash", "tool_input": {"command": "echo x > kitchen.yml"},
                                             "cwd": str(p.root)}), capture_output=True, text=True, env=env)
        self.assertEqual(json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"], "ask")


class GitLabShapesTest(GuardCase):
    """The same rules on a GitLab project; gh commands keep their rules there too."""
    HOST = "gitlab"

    def test_pushes_and_both_clis(self):
        self.check([f"git push -u origin {B}", "gh pr view 7", "gh pr list", "glab mr view 7 --output json",
                    "glab ci status --branch main --wait", "glab api projects/:fullpath/pipelines/5/jobs"], "allow")
        self.check(["gh repo sync", "glab ci run", "glab api -X POST projects/:fullpath/pipeline",
                    "GITLAB_TOKEN=x glab mr view 7"], "ask")
        self.check(["git push origin main", "glab mr create --fill --yes", "glab mr merge 7 --yes",
                    "gh repo sync o/r --force", "glab mr accept 7 --yes",
                    f"glab mr merge 7 --sha {SHA} --yes",
                    f"glab mr merge 7 --sha {SHA} --auto-merge=true --yes",
                    f"glab mr merge 7 --sha {SHA} --auto-merge=false --yes --squash",
                    f"glab mr merge 7 --sha {SHA} --auto-merge=false --yes --remove-source-branch"], "deny")

    def test_a_well_formed_gitlab_merge_runs_the_gate_and_the_github_one_is_refused(self):
        got, reason = self.hook(f"glab mr merge 7 --sha {SHA} --auto-merge=false --yes")
        self.assertEqual(got, "deny")
        self.assertIn("Merge gate failed", reason)
        self.assertIn("cannot read merge request 7", reason)
        got, reason = self.hook(f"gh pr merge 7 --merge --match-head-commit {SHA}")
        self.assertEqual(got, "deny")
        self.assertIn("(the host is gitlab): the only merge is `glab mr merge <number> --sha <sha> --auto-merge=false "
                      "--yes`", reason)


class ManualShapesTest(GuardCase):
    HOST = "manual"

    def test_pushes_work_and_every_merge_is_a_persons(self):
        self.check([f"git push -u origin {B}"], "allow")
        self.check(["git push origin main"], "deny")
        for command in (f"gh pr merge 7 --merge --match-head-commit {SHA}",
                        f"glab mr merge 7 --sha {SHA} --auto-merge=false --yes", "gh pr merge 7 --merge"):
            with self.subTest(command=command):
                got, reason = self.hook(command)
                self.assertEqual(got, "deny")
                self.assertIn("a person merges this change request", reason)
                self.assertIn("the host is manual", reason)


class HostAutonomyTest(unittest.TestCase):
    """Every host and autonomy level, with the merge command deliver.py merge-command prints."""

    def setUp(self):
        self.p = make_project()
        self.addCleanup(self.p.close)

    def merge_command(self, host):
        code, out = self.p.run("deliver.py", "merge-command", "7", f"--head={SHA}")
        if host == "manual":
            self.assertEqual(code, 1, out)
            self.assertIn("a person merges", out)
            return [f"gh pr merge 7 --merge --match-head-commit {SHA}", f"glab mr merge 7 --sha {SHA} --auto-merge=false --yes"]
        self.assertEqual(code, 0, out)
        return [out.splitlines()[0]]

    def test_every_host_and_autonomy_level(self):
        for host in ("github", "gitlab", "manual"):
            for autonomy in ("merge", "pr", "supervised"):
                self.p.write("kitchen.yml", kitchen_yml(host=host, autonomy=autonomy), add=False)
                for command in self.merge_command(host):
                    with self.subTest(host=host, autonomy=autonomy, command=command):
                        self.p.log_file.write_text("")
                        got, reason = run_hook(self.p, command)
                        self.assertEqual(got, "deny", reason)
                        if host != "manual" and autonomy == "merge":
                            self.assertIn("Merge gate failed", reason)
                            self.assertTrue(self.p.calls(), "the gate asks the host")
                        else:
                            self.assertIn("a person merges this change request", reason)
                            self.assertIn("manual" if host == "manual" else f"autonomy: {autonomy}", reason)
                            self.assertEqual(self.p.calls(), [], "no gate and no host call")
                        pushed = run_hook(self.p, f"git push -u origin {B}")
                        self.assertEqual(pushed, ("allow", ""))


class MergeTest(unittest.TestCase):
    """A change request that follows the workflow, so the real merge gate passes, on fake host CLIs."""
    BRANCH = "us-pay-99-fixture"
    STORY = "backlog/PAY-payments/US-PAY-99-fixture.md"
    TESTS = "tests/fixture.txt"
    TAGGED = "us_pay_99_ac1_a fail\nus_pay_99_ac2_b fail\n"

    def setUp(self):
        self.p = p = make_project()
        self.addCleanup(p.close)
        p.git("checkout", "-q", "-b", self.BRANCH)
        story = lambda status: ticket("US-PAY-99", title="Fixture story", status=status)  # noqa: E731
        p.write(self.STORY, story("in-progress"))
        p.commit("chore: start US-PAY-99")
        p.write(self.TESTS, self.TAGGED)
        p.commit("test: US-PAY-99 failing tests")
        p.write("src/fixture.py", "# implementation\n")
        p.write(self.TESTS, self.TAGGED.replace("fail", "pass"))
        p.write(self.STORY, story("done"))
        reviewed = p.commit("feat: US-PAY-99")
        self.description = (
            "## Ticket\n\nUS-PAY-99 Fixture.\n\n## Plan\n\n| US-PAY-99/AC1 | t |\n| US-PAY-99/AC2 | t |\n\n"
            "## Gaps found\n\n- None\n\n## Decisions\n\n- None\n\n## Platform changes\n\n- None\n\n"
            f"## Test changes\n\n- {self.TESTS}: flipped\n\n## Review report\n\nReviewed commit: {reviewed}\n"
            "CRITICAL: 0, WARNING: 0, SUGGESTION: 0\n")
        body = p.tmp / "body.md"
        body.write_text(self.description)
        code, out = p.run("deliver.py", "record", f"--body-file={body}", f"--branch={self.BRANCH}", "--cr=7")
        self.assertEqual(code, 0, out)
        p.commit("docs: delivery record")
        p.git("push", "-q", "origin", self.BRANCH)
        self.head = p.head()

    def github(self, **change):
        pr = {"number": 7, "state": "OPEN", "isDraft": False, "baseRefName": "main", "headRefName": self.BRANCH,
              "headRefOid": self.head, "mergeable": "MERGEABLE", "body": self.description, "url": "https://h/pr/7",
              "statusCheckRollup": [{"name": "check", "status": "COMPLETED", "conclusion": "SUCCESS"}]}
        pr.update(change)
        self.p.rules([{"cli": "gh", "args": ["pr", "view", "7"], "stdout": json.dumps(pr)}])

    def gitlab(self, job_status="success"):
        self.p.write("kitchen.yml", kitchen_yml(host="gitlab"))
        self.head = self.p.commit("chore: gitlab")
        self.p.git("push", "-q", "origin", self.BRANCH)
        mr = {"iid": 7, "state": "opened", "draft": False, "target_branch": "main", "source_branch": self.BRANCH,
              "sha": self.head, "detailed_merge_status": "mergeable", "description": self.description,
              "web_url": "https://h/mr/7", "head_pipeline": {"id": 55, "sha": self.head, "status": "success"}}
        jobs = [{"id": 1, "name": "check", "status": job_status}]
        self.p.rules([{"cli": "glab", "args": ["mr", "view", "7"], "stdout": json.dumps(mr)},
                      {"cli": "glab", "args": ["api", "--paginate"], "stdout": json.dumps(jobs)}])

    def merge(self, command, **kw):
        self.p.log_file.write_text("")
        return run_hook(self.p, command, **kw)

    def test_the_printed_merge_passes_after_the_gate(self):
        self.github()
        code, out = self.p.run("deliver.py", "merge-command", "7", f"--head={self.head}")
        self.assertEqual(code, 0, out)
        command = out.strip()
        self.assertEqual(command, f"gh pr merge 7 --merge --match-head-commit {self.head}")
        self.assertEqual(self.merge(command), ("allow", ""))
        self.assertIn({"cli": "gh", "args": ["pr", "view", "7", "--json", self.p.calls()[0]["args"][4]]},
                      self.p.calls())
        # From a subfolder of the same checkout too.
        (self.p.root / "src").mkdir(exist_ok=True)
        self.assertEqual(self.merge(command, cwd=self.p.root / "src"), ("allow", ""))

    def test_a_failing_gate_denies_with_its_output(self):
        self.github(statusCheckRollup=[{"name": "check", "status": "COMPLETED", "conclusion": "FAILURE"}])
        got, reason = self.merge(f"gh pr merge 7 --merge --match-head-commit {self.head}")
        self.assertEqual(got, "deny")
        self.assertIn("Merge gate failed", reason)
        self.assertIn("check `check` is failing", reason)
        self.github()
        got, reason = self.merge(f"gh pr merge 7 --merge --match-head-commit {'c' * 40}")
        self.assertEqual(got, "deny")
        self.assertIn("the merge pins cccccccc", reason)

    def test_an_altered_merge_never_reaches_the_gate(self):
        self.github()
        for command in (f"gh pr merge 7 --merge --match-head-commit {self.head} --admin",
                        f"gh pr merge 7 --merge --match-head-commit {self.head} --delete-branch",
                        f"gh pr merge {self.BRANCH} --merge --match-head-commit {self.head}"):
            with self.subTest(command=command):
                got, reason = self.merge(command)
                self.assertEqual(got, "deny", reason)
                self.assertEqual(self.p.calls(), [])

    def test_autonomy_pr_and_supervised_leave_the_merge_to_a_person(self):
        self.github()
        for autonomy in ("pr", "supervised"):
            with self.subTest(autonomy=autonomy):
                self.p.write("kitchen.yml", kitchen_yml(host="github", autonomy=autonomy), add=False)
                got, reason = self.merge(f"gh pr merge 7 --merge --match-head-commit {self.head}")
                self.assertEqual(got, "deny")
                self.assertIn("a person merges this change request", reason)
                self.assertEqual(self.p.calls(), [])

    def test_a_merge_from_another_checkout_is_refused(self):
        self.github()
        other = self.p.tmp / "other"
        subprocess.run(["git", "init", "-q", str(other)], check=True, env=self.p.env())
        got, reason = self.merge(f"gh pr merge 7 --merge --match-head-commit {self.head}", cwd=other)
        self.assertEqual(got, "deny")
        self.assertIn("this project's checkout", reason)
        self.assertEqual(self.p.calls(), [])

    def test_gitlab(self):
        self.gitlab()
        code, out = self.p.run("deliver.py", "merge-command", "7", f"--head={self.head}")
        self.assertEqual(code, 0, out)
        command = out.strip()
        self.assertEqual(command, f"glab mr merge 7 --sha {self.head} --auto-merge=false --yes")
        self.assertEqual(self.merge(command), ("allow", ""))
        self.assertTrue(any(c["cli"] == "glab" and c["args"][:3] == ["mr", "view", "7"] for c in self.p.calls()))
        for wrong in (f"gh pr merge 7 --merge --match-head-commit {self.head}",
                      f"glab mr merge 7 --sha {self.head} --yes",
                      f"glab mr merge 7 --sha {self.head} --auto-merge=false --yes --squash"):
            with self.subTest(command=wrong):
                self.assertEqual(self.merge(wrong)[0], "deny")
                self.assertEqual(self.p.calls(), [])

    def test_gitlab_pending_job_fails_the_gate(self):
        self.gitlab(job_status="running")
        got, reason = self.merge(f"glab mr merge 7 --sha {self.head} --auto-merge=false --yes")
        self.assertEqual(got, "deny")
        self.assertIn("check `check` is pending", reason)


class PushTest(unittest.TestCase):
    def setUp(self):
        self.p = make_project()
        self.addCleanup(self.p.close)

    def test_the_detected_default_branch_is_never_pushed(self):
        p = self.p
        p.git("branch", "trunk")
        p.git("push", "-q", "origin", "trunk")
        p.git("fetch", "-q", "origin")
        p.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
        for command in ("git push origin trunk", "git push origin TRUNK", "git push -u origin +trunk"):
            with self.subTest(command=command):
                got, reason = run_hook(p, command)
                self.assertEqual(got, "deny", reason)
                self.assertIn("default branch (trunk)", reason)
        self.assertEqual(run_hook(p, "git push origin main"), ("allow", ""))

    def test_push_and_mirror_settings_block_every_push(self):
        for key, value in (("remote.origin.push", "HEAD:refs/heads/main"), ("remote.origin.mirror", "true")):
            with self.subTest(key=key):
                self.p.git("config", key, value)
                got, reason = run_hook(self.p, f"git push origin {B}")
                self.assertEqual(got, "deny")
                self.assertIn("remote.origin.push or remote.origin.mirror", reason)
                self.p.git("config", "--unset", key)
        self.assertEqual(run_hook(self.p, f"git push origin {B}"), ("allow", ""))

    def test_the_root_comes_from_git_without_claude_project_dir(self):
        self.assertEqual(run_hook(self.p, f"git push origin {B}", project_dir=False), ("allow", ""))
        self.assertEqual(run_hook(self.p, str(self.p.root / "docs" / "x.md"), "Write", project_dir=False)[0], "ask")
        (self.p.root / "src").mkdir(exist_ok=True)
        self.assertEqual(run_hook(self.p, f"git push origin {B}", cwd=self.p.root / "src"), ("allow", ""))

    def test_a_push_from_another_checkout_is_refused(self):
        other = self.p.tmp / "other"
        subprocess.run(["git", "init", "-q", str(other)], check=True, env=self.p.env())
        subprocess.run(["git", "-C", str(other), "commit", "-q", "--allow-empty", "-m", "x"], check=True, env=self.p.env())
        subprocess.run(["git", "-C", str(other), "branch", B], check=True, env=self.p.env())
        got, reason = run_hook(self.p, f"git push origin {B}", cwd=other)
        self.assertEqual(got, "deny")
        self.assertIn("this project's checkout", reason)


class FailClosedTest(unittest.TestCase):
    """A broken install refuses pushes and merges, and only them; a broken guard refuses everything."""

    def setUp(self):
        self.p = make_project()
        self.addCleanup(self.p.close)

    def assertPushAndMergeDenied(self, why):
        for command in (f"git push origin {B}", f"gh pr merge 7 --merge --match-head-commit {SHA}"):
            with self.subTest(command=command):
                got, reason = run_hook(self.p, command)
                self.assertEqual(got, "deny", reason)
                self.assertIn("do not load", reason)
                self.assertIn(why, reason)

    def assertOrdinaryWorkPasses(self):
        for value, tool in (("ls", "Bash"), ("git status", "Bash"), ("gh pr view 7", "Bash"),
                            (str(self.p.root / "src" / "x.py"), "Write"),
                            (str(self.p.root / "docs" / "decision-log.md"), "Edit")):
            with self.subTest(value=value):
                self.assertEqual(run_hook(self.p, value, tool), ("allow", ""))
        self.assertEqual(run_hook(self.p, str(self.p.root / "docs" / "x.md"), "Edit")[0], "ask")
        self.assertEqual(run_hook(self.p, str(self.p.root / "scripts" / "hosts.py"), "Edit")[0], "ask")

    def test_an_invalid_kitchen_yml(self):
        self.p.write("kitchen.yml", "colour: red\n", append=True, add=False)
        self.assertPushAndMergeDenied("unknown key `colour`")
        self.assertOrdinaryWorkPasses()

    def test_a_missing_kitchen_yml(self):
        (self.p.root / "kitchen.yml").unlink()
        self.assertPushAndMergeDenied("not found")
        self.assertOrdinaryWorkPasses()

    def test_a_missing_script(self):
        (self.p.root / "scripts" / "hosts.py").unlink()
        self.assertPushAndMergeDenied("No module named 'hosts'")
        self.assertOrdinaryWorkPasses()

    def test_a_broken_script(self):
        self.p.write("scripts/kitchen_lib.py", "def broken(:\n", add=False)
        self.assertPushAndMergeDenied("SyntaxError")
        self.assertOrdinaryWorkPasses()

    def test_a_project_dir_without_the_framework(self):
        empty = self.p.tmp / "empty"
        empty.mkdir()
        env = self.p.env()
        env["CLAUDE_PROJECT_DIR"] = str(empty)
        r = subprocess.run([sys.executable, str(self.p.root / ".claude" / "hooks" / "guard.py")],
                           input=json.dumps({"tool_name": "Bash", "tool_input": {"command": f"git push origin {B}"},
                                             "cwd": str(self.p.root)}), capture_output=True, text=True, env=env)
        self.assertEqual(json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_an_unreadable_lock_protects_every_script(self):
        self.p.write("kitchen.lock", "{not json", add=False)
        for value, tool in ((str(self.p.root / "scripts" / "my_tool.py"), "Write"), ("rm scripts/my_tool.py", "Bash")):
            with self.subTest(value=value):
                self.assertEqual(run_hook(self.p, value, tool)[0], "ask")
        # kitchen_lib reads the lock too and refuses to load without it, so pushes stop as well.
        self.assertPushAndMergeDenied("kitchen.lock")
        self.assertEqual(run_hook(self.p, "git status"), ("allow", ""))

    def test_without_a_lock_the_fixed_paths_and_framework_scripts_stay_protected(self):
        (self.p.root / "kitchen.lock").unlink()
        self.assertEqual(run_hook(self.p, str(self.p.root / "scripts" / "deliver.py"), "Write")[0], "ask")
        self.assertEqual(run_hook(self.p, str(self.p.root / "scripts" / "extra_tool.py"), "Write")[0], "allow")
        self.assertEqual(run_hook(self.p, str(self.p.root / "playbooks" / "deliver.md"), "Write")[0], "ask")

    def test_malformed_hook_input_is_denied(self):
        for raw in ("not json", "[1, 2]", json.dumps({"tool_name": "Bash", "tool_input": ["git push"]})):
            with self.subTest(raw=raw):
                got, reason = run_hook(self.p, None, raw=raw)
                self.assertEqual(got, "deny")
                self.assertIn("The guard hook failed", reason)


HOOK_COMMAND = "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/guard.py\" || exit 2"


class SettingsTest(unittest.TestCase):
    def test_the_hook_is_registered_like_the_original_and_blocks_on_a_crash(self):
        settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
        self.assertEqual(settings, {"hooks": {"PreToolUse": [{
            "matcher": "Bash|Edit|Write|MultiEdit|NotebookEdit",
            "hooks": [{"type": "command", "command": HOOK_COMMAND}],
        }]}})

    def registered(self, p, command):
        """Run the registered hook command through the shell, as Claude Code does."""
        env = p.env()
        env["CLAUDE_PROJECT_DIR"] = str(p.root)
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(p.root)})
        return subprocess.run(["/bin/sh", "-c", HOOK_COMMAND], input=payload, capture_output=True, text=True, env=env)

    def test_a_guard_that_does_not_run_blocks_the_call(self):
        # Review item 5: a guard that can't even start (a syntax error, python3 missing)
        # exits non-zero without a decision; `|| exit 2` turns that into Claude Code's
        # blocking exit code, while the guard's own decisions exit 0 with JSON.
        p = make_project()
        self.addCleanup(p.close)
        r = self.registered(p, "git push origin main")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(self.registered(p, "ls").returncode, 0)
        p.write(".claude/hooks/guard.py", "def broken(:\n", add=False)
        r = self.registered(p, "ls")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertEqual(r.stdout, "")
        (p.root / ".claude" / "hooks" / "guard.py").unlink()
        self.assertEqual(self.registered(p, "ls").returncode, 2)

    def test_the_guard_compiles_on_its_own(self):
        r = subprocess.run([sys.executable, "-c", "import ast,sys; ast.parse(open(sys.argv[1]).read())", str(GUARD)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
