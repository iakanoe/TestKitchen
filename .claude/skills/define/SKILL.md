---
name: define
description: Define the product in this repository with the person, following playbooks/define.md. Turn what they know into docs/product.md, requirements, ADRs, decisions (DEC), spikes (SPK), epics, stories, and tasks, asking about three questions per round with recommendations, never inventing answers, and writing only after a yes. Modes new, change, sweep, refine, adopt, slice, bug, hotfix, ask. Use for "/define", "/define change <topic>", "/define refine", "/define adopt", "let's decide the open questions", "split this into tickets", "what's not defined yet", "slice the releases", "triage this bug", "we need a hotfix", or questions about what the product must do.
argument-hint: "[mode] [topic]"
---

# Define

Follow `playbooks/define.md`. Read it in full first, together with `backlog/README.md` and `AGENTS.md`. It is the process; this file adds only what is specific to Claude Code.

## Arguments

- A mode (`new`, `change`, `sweep`, `refine`, `adopt`, `slice`, `bug`, `hotfix`, `ask`), optionally followed by a topic: run that mode.
- No mode: pick one as the playbook's "Without a mode" says.

## Claude Code mechanics

- **Decision rounds.** Write the decision brief (the playbook's decision format) in your message, then ask with AskUserQuestion: one question per decision, your recommendation as the first option marked "(recommended)". The person can always answer in their own words. Keep to about three questions per round.
- **Ticket reviews.** For `refine`, run the `ticket-reviewer` subagent (`.claude/agents/ticket-reviewer.md`) in `ticket` mode, with only the inputs `playbooks/review.md` lists.
- **Large repositories.** For `adopt` and for splitting many requirements, give each epic group to a subagent in parallel (with `backlog/README.md` and the group's requirement IDs), then de-duplicate the results yourself.
- **The guard.** `.claude/hooks/guard.py` asks the person before each edit under `docs/` and to `AGENTS.md` or `kitchen.yml`. That is expected after a checkpoint yes; a denial is final.
- **Model.** This skill and the reviewer set no model: they run on the model chosen for the session.
- **Headless:** AskUserQuestion is unavailable. Print the decision briefs and questions, write nothing that needs a yes, and stop.
