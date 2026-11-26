---
id: US-GRD-16
type: story
title: Ask before the decision log is replaced or removed
epic: EP-GRD
source_reqs: [GRD-R34]
blocked_by: [US-DEF-33]
owner: Ianick Noejovich
assignee_type: either
status: ready
refined: 2026-11-26
---

As a project owner, I want the guard to keep appends to the decision log free and ask before it is replaced or removed, so that entries are added without a prompt but never lost unasked.

## Acceptance criteria

- AC1: Given a shell append to `docs/decision-log.md` (`echo … >> docs/decision-log.md`, a `cat >> docs/decision-log.md` heredoc, `… | tee -a docs/decision-log.md`, or `echo … >> decision-log.md` run from inside `docs/`), when the guard checks it, then it lets it through.
- AC2: Given an Edit or MultiEdit call on `docs/decision-log.md` (also written `Docs/Decision-Log.md`), when the guard checks it, then it lets it through.
- AC3: Given a Write call on `docs/decision-log.md`, when the guard checks it, then it asks.
- AC4: Given a shell command that replaces `docs/decision-log.md` (a `>` redirect to it, also `echo x > decision-log.md` run from inside `docs/`; `cp` or `mv` of another file onto it; `truncate` of it; `sed -i` or `perl -i` on it), when the guard checks it, then it asks.
- AC5: Given a shell command that removes `docs/decision-log.md` or restores it from git (`rm` of it, `mv` of it elsewhere, `git checkout -- docs/decision-log.md`, `git restore docs/decision-log.md`), when the guard checks it, then it asks.

## Notes

- Implements DEC-GRD-04, option (a), decided 2026-11-25 by Ianick Noejovich (its second part), as made exact on 2026-11-26 (GRD-R34 supersedes GRD-R30). Split from US-GRD-14 on 2026-11-26. It changes the behavior recorded by US-GRD-08 (protected edits) and US-GRD-09 (shell writes), which stay as the record of the earlier behavior.
- Replaces (to become a `replaces:` field once US-DEF-33 is delivered): US-GRD-08/AC3, which lets every edit of the decision log through (a Write call included), and US-GRD-09/AC6, which lets `echo x > decision-log.md` from inside `docs/` through. AC1 and AC2 restate what those criteria say about appends and Edit and MultiEdit calls, because that part stays true and must not lose its criterion when they are crossed out. A lookalike such as `docs/decision-log.md.bak` keeps asking as a file under `docs/` (US-GRD-08/AC1).
- Reading of the decided list: the other truncating redirect forms GRD-R22 names (`>|`, `&>`, a numbered descriptor) replace the file as `>` does, and so does `tee` without `-a`.

## Open questions

- None. The decision log records this decision, and the decision of 2026-11-26 listed which writes append and which replace.
