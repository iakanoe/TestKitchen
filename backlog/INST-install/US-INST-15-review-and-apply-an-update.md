---
id: US-INST-15
type: story
title: Review and apply an update
epic: EP-INST
source_reqs: [INST-R19]
blocked_by: []
owner: Ianick Noejovich
assignee_type: either
status: done
adopted: true
---

As a maintainer of a project using Test Kitchen, I want to see what an update changes and what the release asks of me before it writes anything, so that I can update safely.

## Acceptance criteria

- AC1: Given an installed version and a new one, when `update` runs, then it prints "Test Kitchen update <old> → <new>", the source, the host and the Claude Code choice, one row per added, restored, replaced, kept, conflicting, or removed file, and the number of unchanged files.
- AC2: Given the new release's CHANGELOG, when `update` runs, then it prints the `### Migration notes` of every `## x.y.z` section after the installed version up to the new one, oldest first, "none." for a release without notes, and nothing from sections that are not versioned.
- AC3: Given a new version older than the installed one, when `update` runs, then it warns and continues.
- AC4: Given `--dry-run`, when the plan has been shown, then nothing is written and the run exits 0; otherwise it asks "Apply this update?" (default yes), and a no stops with exit code 1.
- AC5: Given an applied update, when it finishes, then `kitchen.lock` holds the new version and the hashes of the new version's files (kept conflicts included), and it prints "Updated Test Kitchen to <version>." with the files no longer shipped and a commit hint, runs `doctor`, and exits 0.

## Notes

Observed in `init.py` on 2026-11-25 by `/define adopt`; not yet confirmed by a person. `## Unreleased` sections are skipped, as `CHANGELOG.md` describes. Without a terminal and without `--yes`, the confirmation follows US-INST-04/AC5.

## Open questions

- None. Behavior recorded as observed; the person confirms it.
