# Using Test Kitchen from an agent

The process does not depend on one agent. It lives in plain markdown and scripts:

- `AGENTS.md`: what Test Kitchen is, where everything lives, the rules, the commands, and a `## This project` section for the project's own notes.
- `CONTRIBUTING.md`: the principles, what is enforced where, and when an agent stops and asks.
- `playbooks/deliver.md`, `playbooks/define.md`, `playbooks/review.md`: the single source of each process.
- `scripts/deliver.py` and `scripts/backlog_check.py`: the facts and the gates.

Any agent that reads files and runs shell commands can follow them. What differs between agents is how commands are started, how a fresh-context review is obtained, and whether anything enforces the merge rules.

## Claude Code (recommended)

Test Kitchen was developed and tested in Claude Code, and it is the only agent where the merge guard is enforced.

- **Commands.** `/define [mode]` runs `playbooks/define.md`. `/deliver <ID>` delivers one ticket, `/deliver next` picks one, `/deliver all` keeps going until nothing is ready or a question needs a person. The skills in `.claude/skills/` are thin wrappers that point at the playbooks.
- **Reviews.** The reviewer is a subagent (`.claude/agents/ticket-reviewer.md`, read-only tools) that follows `playbooks/review.md`, so each review starts with fresh context.
- **Questions.** Decision rounds use Claude Code's question prompts.
- **Model.** The skills and the reviewer set no model; they run on the model you pick for the session.
- **The guard.** `.claude/hooks/guard.py`, registered in `.claude/settings.json` as a hook that runs before every shell command and file edit, in every session and subagent:
  - a push must be exactly `git push [-u] origin <branch>`, never the default branch; force pushes ask, even in sandbox mode;
  - a merge must be exactly the command the host adapter allows, and the guard runs `deliver.py gate merge` first; on the manual host, and with `autonomy: pr` or `supervised`, every agent merge is refused;
  - editing `docs/` (except `docs/decision-log.md`, which every delivery appends to), `.claude/`, `.github/`, `.gitlab/`, `.gitlab-ci.yml`, `.git/`, `playbooks/`, the framework scripts listed in `kitchen.lock`, `kitchen.yml`, `kitchen.lock`, `CONTRIBUTING.md`, `AGENTS.md`, or `CLAUDE.md` asks a person (reading stays free);
  - git configuration writes, tokens in commands, and host API writes ask a person;
  - if the guard itself fails, the call is refused;
  - in a subagent, whatever the guard would ask about is refused instead, with the same reasons and a line telling the subagent to hand the step back to the main session, where you are asked. In auto permission mode a subagent's asks are approved by a classifier rather than by you.
- **Unattended machines.** Setting `KITCHEN_GUARD_SANDBOX=1` in the git-ignored `.claude/settings.local.json` lets the guard's "ask" cases through without a prompt on a machine you chose to run unattended, in subagents too. Refusals (the push and merge rules, the merge gate) are unchanged, and a force push from a subagent is refused.
- **Headless runs** (`claude -p "/deliver all"`): the guard's questions become refusals, and the agent prints decision briefs and stops when a person is needed.

The installer's `doctor` mode (`curl -fsSL https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.1.0/init.py | python3 - doctor`) checks that the guard is registered and not switched off.

The guard reads commands literally. Text assembled at run time (variables, an interpreter one-liner, a script written and then run) is out of its reach. It is a guardrail against mistakes, not a sandbox against an agent trying to evade it. Host branch protection is what holds against everything; turn it on where your plan offers it.

## Codex, Cursor, and other agents

Many agents read `AGENTS.md` automatically; otherwise, point the agent at it at the start of a session.

- **Commands.** Ask in plain words: "Follow `playbooks/deliver.md` for the next ticket", "Follow `playbooks/define.md` in mode refine". `/define` and `/deliver` are Claude Code names; the playbooks define the same steps.
- **Reviews.** At each review (plan, tests, final diff, and ticket refinement), start a fresh session or agent, give it `playbooks/review.md` and only the inputs that playbook lists for the mode, and paste its report back. A reviewer that saw the implementation being written is not a fresh-context reviewer.
- **Questions.** The agent asks decision rounds in chat, in the format `playbooks/define.md` gives.
- **Merging.** Nothing local enforces the merge rules. Before every merge, run from a clean checkout of the change request's head:

  ```sh
  python3 scripts/deliver.py gate merge <n> --head=<sha>
  python3 scripts/deliver.py merge-command <n> --head=<sha>   # prints the one allowed merge command
  ```

  and merge only with that command, only if the gate passed. CI still runs `gate pr` on every change request, so a skipped step shows up as a failing `check`; but a failing check does not stop a merge unless your host's branch protection requires it.
- **Recommended:** set `autonomy: pr` in `kitchen.yml` so agents without the guard stop at a ready change request and a person merges. Use `--no-claude` at install time if nobody uses Claude Code; the Claude Code files are harmless otherwise.

## People

A person can run the same workflow by hand: the playbooks are written as steps, and the scripts print what to do next. A person running it approves the plan and the tests themselves instead of the reviewer.
