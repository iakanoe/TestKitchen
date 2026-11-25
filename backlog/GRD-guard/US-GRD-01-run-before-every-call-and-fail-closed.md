---
id: US-GRD-01
type: story
title: Run before every guarded call and fail closed
epic: EP-GRD
source_reqs: [GRD-R01, GRD-R02, GRD-R03]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project owner, I want the guard to run before every shell command and file edit and to refuse when it cannot decide, so that a broken guard or install never lets a push or merge through unchecked.

## Acceptance criteria

- AC1: Given the installed `.claude/settings.json`, when Claude Code reads it, then it registers one PreToolUse hook with the matcher `Bash|Edit|Write|MultiEdit|NotebookEdit` and the command `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/guard.py" || exit 2`.
- AC2: Given a call of another tool (such as Read) or an empty shell command, when the guard runs, then it prints nothing and the call goes through.
- AC3: Given hook input that is not JSON, is not a JSON object, or carries a tool input that is not an object, when the guard runs, then it denies the call with a message that the guard hook failed.
- AC4: Given a guard file with a syntax error, or no guard file, when the registered hook command runs, then it exits 2 with no output, which blocks the call; given a working guard, the same command exits 0 with the guard's decision.
- AC5: Given an invalid or missing `kitchen.yml`, a missing or broken framework script, an unreadable `kitchen.lock`, or a `CLAUDE_PROJECT_DIR` without the framework, when a push or a merge runs, then it is denied with a message naming the load error, while `ls`, `git status`, `gh pr view`, edits outside protected paths, and decision-log edits go through and protected edits still ask.
- AC6: Given `CLAUDE_PROJECT_DIR` is not set, when a call runs from the project or one of its subfolders, then the guard uses the git checkout that holds the guard file as the project root.

## Notes

- Adopted from `template/claude/hooks/guard.py` (`main`, `find_root`, `Kitchen`, the `__main__` handler) and `template/claude/settings.json`. Behavior observed in the code and its tests on 2026-11-25, not yet confirmed by a person.
- `docs/spec-v0.1.md` section 6 says the hook is registered "exactly as the original does"; the code adds `|| exit 2`, decided in the decision-log entry "Guard hardening after the adversarial review".
- The 300-second limit on each git or gate subprocess also fails closed: a timeout raises, and raising denies.

## Open questions

- None. The behavior is recorded as observed; the person confirms it when walking through the requirements.
