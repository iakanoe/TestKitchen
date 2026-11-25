---
id: DEC-DLV-02
type: decision
title: Release notes include adopted stories
epic: EP-DLV
source_reqs: [DLV-R27]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: draft
---

## Question

Is this intended? `deliver.py release-notes` lists every done story and task when there is no git tag, and every done story and task of a slice when a slice is named, so stories written by `/define adopt` for behavior that existed before the backlog (`adopted: true`) appear in the release notes as if they were delivered changes.

## Context

- Current: `cmd_release_notes` chooses from all done stories and tasks with no regard to `adopted` (`template/scripts/deliver.py:953`); with a slice it keeps those in the slice (`:959`), and without a tag it keeps all of them (`:968`). Only the "since the last tag" path filters by delivery records added since the tag (`:961-966`), which adopted stories never have, so the same backlog gives different answers depending on whether a tag exists.
- `backlog/README.md` (Frontmatter) says `adopted: true` "marks behavior that existed before the backlog did"; `playbooks/define.md` (mode `adopt`) records existing behavior "as it is" and presents nothing as intended until a person confirms it.
- `docs/spec-v0.1.md` section 5 specifies "all done tickets when there is no tag" and done tickets in the slice; it predates any mention of adopted stories in release notes, and `tests/test_deliver.py` does not cover an adopted story in release notes.
- Likely intended: release notes describe what changed, so adopted stories stay out unless a person asks for them.

## Options

None recorded. Proposals, not decided anywhere:

- (a) Keep listing adopted stories.
- (b) Leave adopted stories out of every release-notes path.
- (c) List them under a separate heading such as "Recorded existing behavior".

## Recommendation

(b): adopted stories record behavior that shipped before the backlog existed, so listing them as a release's changes is misleading, and leaving them out makes the tag and no-tag paths agree.

## Decides

- US-DLV-21 (which done tickets the release notes choose).
