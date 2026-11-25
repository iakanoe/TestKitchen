---
id: DEC-GRD-02
type: decision
title: A file named config in a git command
epic: EP-GRD
source_reqs: [GRD-R16]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

Is this intended? Any git command with a word `config` among its arguments asks as a git setting change, even when `config` is a file or folder name and the subcommand is not `git config`.

## Context

- Current behavior (verified on 2026-11-25 by feeding the hook JSON in a scratch project built like `tests/test_guard.py` does): `git add config`, `git diff -- config`, and `git log -- config` each ask with "This is a git setting change (settings can run commands or change where a push goes); a person approves it."
- Evidence: `template/claude/hooks/guard.py:1161-1166` (`guard_git`) checks `if "config" in words[start:]`, any word after `git`, rather than the subcommand that `git_subcommand()` (`guard.py:1123-1134`) already finds.
- Likely intended: GRD-R16 and the docstring (`guard.py:51`) speak of "every `git config` that is not a read", that is the `config` subcommand, including after global options such as `git -C . config …` (an ask case in the tests).
- The effect is an extra prompt (fail-safe), not a hole; in an unattended run without the sandbox opt-in it stops the run. Projects with a `config/` folder (common in web frameworks) would hit it on every `git add config`.

## Options

None recorded. Proposals:

- (a) Ask only when git's subcommand (after global options) is `config`.
- (b) Keep asking on any `config` word, as a cautious default.

## Recommendation

(a): it matches the stated rule and the docstring, keeps every `git config` write asking, and removes prompts on ordinary file names.

## Decides

US-GRD-07 (its git configuration criterion and notes). A change to the guard would be a new story in this epic.

## Outcome

- Date: 2026-11-25.
- Answer: Option (a): `git config` asks only when git's subcommand, after the global options, is `config`.
- Decided by: Ianick Noejovich.
- Recorded in: requirements GRD-R27; confirmed GRD-R16; US-GRD-12; decision log, "git config asks only for the config subcommand".
