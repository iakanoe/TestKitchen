---
id: TASK-DLV-03
type: task
title: Deliver each ticket of /deliver all in a fresh context
epic: EP-DLV
source_reqs: [DLV-R31, DLV-R36, DLV-R39, DLV-R52, DLV-R54, DLV-R55]
blocked_by: [SPK-DLV-02]
owner: Ianick Noejovich
assignee_type: either
status: draft
---

Change the delivery playbook and the `/deliver` skill, and add a `ticket-deliverer` agent, so that `/deliver all` delivers each ticket in a fresh context, and the skill and the agent read their files one per call. Later tickets then stop carrying earlier tickets' context and cost.

## Acceptance criteria

- AC1: `template/playbooks/deliver.md` tells the agent, under `/deliver all`, to pick each ticket, run the hand-off to define, and print the closing status in the main context, and to deliver each ticket, one at a time, in a fresh context where it can start one (a subagent or a new session), given only the ticket ID and the request to deliver it by following `playbooks/deliver.md`, never anything from earlier tickets.
- AC2: `template/playbooks/deliver.md` tells an agent that cannot start a fresh context to deliver the tickets one after another in the same session.
- AC3: `template/claude/skills/deliver/SKILL.md` tells the agent to read `playbooks/deliver.md` in full first, then `CONTRIBUTING.md`, `AGENTS.md`, and `backlog/README.md`, with the file-read tool, one file per call, never combined with other commands in one shell call; under `/deliver all`, to start one `ticket-deliverer` subagent per ticket, given only the ticket ID, starting the next only after the previous one returned; and, for `/deliver <ID>` and `/deliver next`, to deliver in the current session.
- AC4: `template/claude/agents/ticket-deliverer.md` sets no model and no tools list, and tells the subagent to read its files as AC3 says; to follow `playbooks/deliver.md` for the one ticket it was given; to keep the skill's Claude Code mechanics (the guard, a denial is final, plain push and merge commands); to run its reviews through the `ticket-reviewer` subagent; to switch to the up-to-date default branch before it returns at "ready to merge"; and, at a question or approval that needs the person, to commit and push the work it has, if any, and return the question.
- AC5: `template/claude/skills/deliver/SKILL.md` tells the main session to ask a returned question in one AskUserQuestion round and resume that same subagent with the answers; when it cannot be resumed, to start a new `ticket-deliverer` subagent for that ticket with the answers, which continues from the pushed branch or starts the ticket again; and, headless, to print the question and stop.
- AC6: `template/claude/skills/deliver/SKILL.md` tells the main session that a ticket is finished when its subagent finished it as `playbooks/deliver.md` says for its type (closed through step 14, or merged as the spike and decision variants say) or stopped at "ready to merge" as the autonomy level or the manual host requires, and then to pick the next ticket; and that a subagent returning otherwise without a question stops `/deliver all` with a report of what it returned.

## Notes

- Replaces US-DLV-42, retired and never reused (decision log, "The fresh-context story becomes a task"). An untestable task: the final review verifies each criterion by reading the files (DLV-R37). DEC-DEF-05 asks how such criteria should be accepted from now on.
- The worker is the dedicated `ticket-deliverer` agent, and a subagent that cannot be resumed is replaced by a new one (decision log, "TASK-DLV-03 names its worker agent and when a ticket is finished").
- The root copies (`.claude/skills/deliver/SKILL.md`, `.claude/agents/`, `playbooks/deliver.md`) are an installed release: they change only through `init.py update`, never by hand.
- Documents that name the Claude Code agents and need `ticket-deliverer` added (step 10): `template/CLAUDE.md.tmpl`, `template/CONTRIBUTING.md` (the Claude Code part of "Running it"), `guide/install.md` (the installed-files table), and `guide/agents.md`.
- The agent file sets no model, like the skills and the reviewer (DLV-R46), and no tools list, so it can start the `ticket-reviewer` subagent (decision log, "TASK-DLV-03 settles the checkout, the agent file, and DLV-R55").
- Measured on the US-DLV-38 delivery run (2026-11-26, desktop app): about 2.37M effective tokens; the context reached 254k tokens on that one ticket. A combined `cat playbooks/deliver.md && deliver.py next` call overflowed into a saved file that was then read a second time.
- Documented on code.claude.com (sub-agents and hooks pages, checked 2026-11-26): a subagent starts with a fresh context and may start subagents up to three levels deep; a returned subagent can be resumed by its ID through `SendMessage`, keeping its full history; `PreToolUse` hooks from project settings run on a subagent's tool calls; `AskUserQuestion` is always removed from subagents, so the main session asks and runs the hand-off to define. Not documented: resuming a subagent in a headless `claude -p` run (headless prints the question and stops, so it doesn't need to).
- AC6 follows step 14 and the autonomy rules (DLV-R36: change requests waiting for a person's merge don't block `/deliver all`) and applies DLV-R39 (stop and ask) to a subagent that stops for any other reason.
- Proposed direction for the fourth review's open points, not decided: a subagent that cannot be resumed stops `/deliver all` with a report (DLV-R55 superseded without the fallback); the switch to the default branch at "ready to merge" goes into the playbook for every agent (DLV-R36); DECs stay in the main context's hand-off; split into a playbook task, a skill task, and an agent-file task.
- Documented on code.claude.com (sub-agents page, checked 2026-11-26): background subagents surface every permission prompt in the main session, and foreground subagents pass prompts through; neither denies on its own.
- The `/define` half of DLV-R54 is TASK-DEF-05 (EP-DEF owns the define skill).
- US-DLV-37/AC1 and US-DLV-23/AC3 are not contradicted: `/deliver all` still repeats until nothing is ready, each ticket's subagent reads the playbooks in full, and tickets waiting for a person's merge still don't block it.

## Open questions

- Whether the guard runs on the tool calls of the reviewer a ticket's subagent starts, and what a guard "ask" does inside a subagent: SPK-DLV-02 (in `blocked_by`).
- The fourth ticket-mode review (2026-11-26) left these, to settle once SPK-DLV-02 (in `blocked_by`) is done, since its answer can change the design: (1) AC5's replacement subagent can neither continue nor start again as written: before the claim nothing is pushed, and step 1 stops on the old ticket's branch; (2) AC1 gives a fresh context "only the ticket ID" while AC5 also passes the answers; (3) the switch to the default branch at "ready to merge" is only in AC4, not in the playbook for every agent, and DLV-R46 is not in `source_reqs`; (4) DECs come only through the hand-off in the main context, so "decision" in AC6 cannot happen; (5) AC3's "returned" should say "finished (AC6)"; (6) the ticket may be split into the playbook, the skill, and the agent file.
