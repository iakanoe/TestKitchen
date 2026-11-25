---
id: US-GRD-09
type: story
title: Ask before shell writes to protected paths
epic: EP-GRD
source_reqs: [GRD-R20, GRD-R22, GRD-R23]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a project owner, I want shell commands that may write a protected path to ask me first, as file edits do, while reading stays free, so that the shell is not a way around the protected paths.

## Acceptance criteria

- AC1: Given a redirect to a protected path (`>`, `>>`, `>|`, `&>`, `1>`, `2>`, `1>>`, `>&<file>`), when the command runs, then the guard asks a person; reading protected paths, `2>/dev/null`, and `>&2` go through.
- AC2: Given a writing program that names a protected path (`tee`, `cp`, `mv`, `rm`, `touch`, `uniq`, `sort -o`, `dd of=`, `sed -i` and its clustered and `--in-place` forms, `perl -i` and its clusters, `find … -delete` or `-exec`, `curl -o` and `-sLo`, `wget -O`, `tar -x -C`, `git checkout <ref> -- <path>`, `git clean <path>`, `git log --output=`/`--out=`), when it runs, then the guard asks a person.
- AC3: Given a command that removes or writes a folder or glob holding protected paths (`rm -rf docs`, `rm -rf .claude`, `rm -rf scripts`, `rm -rf *`, `git clean -fdx` with no path), when it runs, then the guard asks a person.
- AC4: Given a relative write target, when the command runs in a subfolder or after `cd` into one (`cd docs && echo x > product.md`, a call whose folder is `docs/` or `.claude/`), then the guard resolves the target from that folder and asks for protected ones; after a `cd` to a folder known only at run time, any write asks.
- AC5: Given a shell or interpreter running code inline or on stdin (`bash -c`, `node -e`, `python3 -c`, `python3 -` with a heredoc) whose text names a protected path, or run from inside a protected folder, when it runs, then the guard asks a person.
- AC6: Given a shell write to `docs/decision-log.md` (appending with `echo` or a `cat` heredoc from the root, or writing `decision-log.md` from inside `docs/`), when it runs, then the guard lets it through.

## Notes

- Adopted from `template/claude/hooks/guard.py` (`guard_writes`, `write_targets`, `target_reason`, `path_reason`, `inside_protected`, `protected_text`). Globs are expanded (up to 1000 matches) to find protected targets. Behavior observed in the code and its tests on 2026-11-25, not yet confirmed by a person.
- `python3 scripts/x.py … > file` is a write to `file`, not to the script (decision-log entry "Guard choices made while building v0.1").
- Out of reach by design: scripts written and then run, and files a program changes without naming them, such as the files a patch applied with `git apply` or `patch` touches.
- An open decision in this epic asks whether writes after `cd -`, `popd`, or a `cd` inside a subshell, which today resolve against the wrong folder and can reach protected paths without asking, are intended.

## Open questions

- None. The behavior is recorded as observed; the person confirms it when walking through the requirements.
