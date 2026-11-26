---
id: DEC-DEF-03
type: decision
title: Playbook done condition differs from what --gaps checks
epic: EP-DEF
source_reqs: [DEF-R03, DEF-R18, DEF-R39]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: done
---

## Question

Is this intended? The playbook's "Done" paragraph describes a fully defined product differently from what `backlog_check.py --gaps` reports.

## Context

- Current behavior: `--gaps` lists unconfirmed `(observed in code)` requirements, and treats a requirement as covered when any story or task that is not deferred cites it (draft and in-progress included; drafts are listed as their own gap). The playbook's "Done" paragraph does not list unconfirmed observed requirements and says "every requirement covered by ready or done tickets". `guide/define.md`, "Done means no gaps", does list the unconfirmed observed requirements.
- Likely intended behavior: the playbook's paragraph matches `--gaps` (the script is what decides "fully defined"); the difference looks like wording that was not updated, not a different rule.
- Evidence: `playbooks/define.md:255`; `template/scripts/backlog_check.py:452-460` (coverage) and `544-546` (observed gaps); `guide/define.md:60-72`.

## Options

- (a) Reword the playbook's "Done" paragraph to match `--gaps`: add unconfirmed observed requirements, and say "cited by a story or task that is not deferred".
- (b) Change `--gaps` to count only ready, in-progress, or done tickets as coverage.

None of these is recorded in `docs/`; both are proposals.

## Recommendation

(a), proposed: the script's rule is tested and drafts already show as their own gap, so only the text is out of step.

## Decides

The DEF-R39 wording, and a playbook wording change if (a). No ticket is blocked by it.

## Outcome

- Date: 2026-11-25.
- Answer: Option (a): the "Done" paragraph of `playbooks/define.md` is reworded to match `--gaps`: it adds unconfirmed observed requirements and says "cited by a story or task that is not deferred".
- Decided by: Ianick Noejovich.
- Recorded in: requirements DEF-R42; confirmed DEF-R03, DEF-R18, DEF-R39; US-DEF-32, now TASK-DEF-03 (decision log, "Review-only stories become tasks"); decision log, "The playbook's Done paragraph follows --gaps". Widened 2026-11-26: DEF-R44 supersedes DEF-R42 (decision log, "Refinement widens ten requirements of the adopt decisions").
