---
name: deliver
description: Deliver backlog tickets end to end in this repository, following playbooks/deliver.md. Pick deterministically, plan from the acceptance criteria, write failing tests and gate them, implement, check, get fresh-context reviews, record every gap and decision, open the change request, merge on green through the merge gate (as the autonomy setting allows), and verify. When nothing is ready, hand off to /define. Use for "/deliver US-PAY-03", "/deliver next", "/deliver all", or any request to work through the backlog, take the next ticket, or build a ticket.
argument-hint: "[ticket ID | next | all]"
---

# Deliver

Follow `playbooks/deliver.md`. Read it in full before the first ticket, together with `CONTRIBUTING.md`, `AGENTS.md`, and `backlog/README.md`. It is the process; this file adds only what is specific to Claude Code.

## Arguments

- A ticket ID (`US-PAY-03`, `TASK-CI-01`, `SPK-PAY-01`, `DEC-PAY-02`): deliver that ticket.
- `next`, or no argument: deliver the ticket `python3 scripts/deliver.py next` names.
- `all`: repeat until nothing is ready and the hand-off to define leaves nothing to do, or a question needs the person.

Keep a task list of the playbook's steps for the current ticket.

## Claude Code mechanics

- **Reviews.** Run the `ticket-reviewer` subagent (`.claude/agents/ticket-reviewer.md`) for each review: a fresh context on the session's model. Give it only the inputs `playbooks/review.md` lists for the mode, never your reasoning or conclusions.
- **Questions.** Ask every open question in one round with AskUserQuestion, one question per decision, your recommendation as the first option marked "(recommended)". Put context the options can't hold (what is already fixed, what each option costs) in your message before the call.
- **Hand-off.** When `deliver.py next` prints `NEXT none`, follow the playbook's hand-off using `/define` (`.claude/skills/define/SKILL.md`): the `DECIDE` list, then the `REFINE` list, then ask what to build next.
- **The guard.** `.claude/hooks/guard.py` checks every shell command and edit. Pushes and merges must be plain commands; the only merge is what `deliver.py merge-command` prints, alone in its call, and the guard runs `deliver.py gate merge` before it. Edits to protected paths ask the person (`docs/decision-log.md` is the one `docs/` file that does not). A denial is final: fix the cause, never work around it.
- **Model.** This skill and the reviewer set no model: they run on the model chosen for the session.
- **Headless** (`claude -p "/deliver all"`): AskUserQuestion is unavailable and the guard's asks become refusals. Print the questions or decision briefs and stop, as the playbook says.
