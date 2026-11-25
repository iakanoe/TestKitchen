---
id: DEC-DLV-03
type: decision
title: Change-request skeleton wording for spikes and decisions
epic: EP-DLV
source_reqs: [DLV-R06, DLV-R37]
blocked_by: []
owner: Ianick Noejovich
assignee_type: human
status: draft
---

## Question

Is this intended? For a spike or a decision, `deliver.py pr-body` prints the Ticket line `None. Delivers <ID> <title>.`, while `playbooks/deliver.md` tells the agent to start that line `None. Spike <ID>: …` for a spike and `None. Decides <ID>…` for a decision; it also prints the same skeleton for an epic, which the playbook says is never delivered.

## Context

- Current: `cmd_pr_body` writes `None. Delivers {tid} {t.title}.` and a Plan of `None.` for every ticket type other than story and task (`template/scripts/deliver.py:305-308`).
- The playbook's spike variant says the change request's Ticket starts `None. Spike …` (`playbooks/deliver.md:308`); its decision variant says it starts `None. Decides …` (`playbooks/deliver.md:317`); its command table says an epic is not delivered (`playbooks/deliver.md:22`).
- Both wordings start with `None.`, so `gate pr` and `backlog_check.py --pr-body` treat either as a non-ticket change request; the difference is only in what the agent must edit and in what the delivery record says.
- `tests/test_deliver.py::CommandsTest::test_pr_body` asserts the `None. Delivers` line for a spike.

## Options

None recorded. Proposals, not decided anywhere:

- (a) Keep both as they are; the agent edits the skeleton.
- (b) Make `pr-body` print the playbook's wording per type (`None. Spike …`, `None. Decides …`) and refuse an epic.
- (c) Change the playbook to the skeleton's `None. Delivers …` wording.

## Recommendation

(b): the script is where facts should come from, so its skeleton should already say what the playbook asks for, and refusing an epic matches "an epic is not delivered".

## Decides

- US-DLV-04 (the skeleton's Ticket line for other ticket types).
- US-DLV-29 (the Ticket line the spike and decision variants ask for).
