# Why each rule exists

Every rule in Test Kitchen answers one question: how can a person trust work they did not watch being done? An agent is fast and confident whether it is right or wrong. The rules below replace "trust me" with something a person or a script can check later.

## Definition

- **Requirements are numbered lines in the repository.** A requirement that lives in a chat or a meeting cannot be cited, checked, or found again. A line with a stable ID (`PAY-R03`) can be cited by a ticket, covered by a test, and superseded on a known date.
- **IDs are never renumbered or reused.** Records, commits, and test names point at IDs. Renumbering would silently make old records point at the wrong thing.
- **`(observed in code)` until a person confirms.** When requirements are read off existing code, the code may be wrong. The marker keeps "this is what it does" apart from "this is what it should do" until someone with the authority says so.
- **Superseded requirements stay, marked.** Deleting them would erase why the old code and tickets look the way they do.
- **Accepted ADRs bind every ticket.** Architecture decided once should not be re-decided by each agent that touches the code.
- **The decision log, newest first, with who and why.** Decisions made in passing are forgotten, then re-made differently. A log entry says what was decided, why, by whom, and where it is written, so the next person can follow the reasoning instead of guessing it.
- **Agents never decide.** Choosing between options, changing a criterion, and changing `docs/` need a person. An agent that fills a gap with its own guess produces code that looks finished and is wrong in a way nobody noticed. What cannot be decided now becomes a DEC or SPK ticket, visible to everyone.
- **About three questions per round, each with a recommendation.** Long questionnaires get skimmed; bare questions push the work back onto the person. A short round with a recommended answer gets real answers.
- **Writes only after a yes.** The person sees exactly what will be written before it is written, so the definition stays theirs.

## Tickets

- **Acceptance criteria are numbered for good; removed ones stay as placeholders.** Tests and records refer to `US-PAY-03/AC2`. If numbers moved, an old test would silently start "proving" a different criterion.
- **A change of meaning is a removal plus a new criterion.** Editing a criterion in place would leave its old tests claiming to prove a statement they were never written for.
- **Open questions name a ticket and state the interim behavior.** "TBD" in a ticket becomes whatever the agent felt like. Naming the DEC makes the question trackable; "Until decided: …" makes today's behavior explicit and tested.
- **Code that meets an open decision fails closed.** Refusing is easy to change later; a permissive default ships the undecided behavior to users.
- **Readiness needs an owner.** Work nobody is accountable for drifts; someone must be able to answer questions about the ticket.
- **`blocked_by` means "can start, can't finish".** Preparation can begin before a blocker lands, but the scripts never pick a ticket whose blocker is unfinished, so nothing ships on top of missing work.
- **Done tickets are never rewritten.** A done ticket is a record of what was delivered. A change becomes a new ticket, so history stays true.
- **Stories above the split threshold are flagged.** Large stories hide unreviewed behavior inside them; small ones get proper tests and reviews.

## Tests

- **Tests come first, and must be seen failing.** A test written after the code tends to describe the code, bugs included. A test that never failed may test nothing at all. `gate red` proves each criterion's test fails while the behavior is missing.
- **The freeze commit.** Committing the tests alone, before any product code, makes "tests first" checkable from the history rather than a promise.
- **Frozen tests change only when they contradict the ticket, and every change is listed.** The easiest way to make a failing test pass is to change the test. Listing every change puts that in front of the reviewer.
- **No criterion may lose its tagged tests.** Otherwise a criterion can quietly stop being proven.
- **No skipped or focused tests after the freeze.** A skipped test reports nothing; a focused one silently disables the rest of the suite.
- **Tags live in test names.** The name is what every runner reports in JUnit XML, so one rule works for every language. Two forms exist because some languages cannot put brackets in a function name.
- **JUnit XML as the only result format.** One format every mainstream runner can write keeps Test Kitchen independent of any language or framework.
- **Test debt for adopted code is reported, not blocking.** Existing code without tests should not stop new work, but the missing proof should stay visible.

## Delivery

- **One ticket per branch and change request.** A change that mixes tickets cannot be reviewed against any one of them.
- **Facts come from scripts, not memory.** Which ticket is next, what its criteria say, and whether it may merge are computed the same way every time. Agents do the judgment work in between, where judgment is needed.
- **A fresh-context reviewer, three times.** An agent reviewing its own work sees what it meant to write. A reviewer with only the ticket, the plan, and the diff sees what is actually there. It checks the plan, the tests, and the final diff because each catches a different mistake early.
- **`Reviewed commit:` and nothing changed after it.** A review only covers the code it read. Any later change to code or tests needs another look.
- **`CRITICAL: 0` before a change request passes.** Findings are sorted by severity so a critical problem cannot be lost in a list of style notes.
- **Nothing found stays only in chat.** Every gap becomes a ticket, every decision and platform change a log entry, and the change request lists them. Chat is gone tomorrow; the repository is not.
- **The description is committed as a delivery record.** Hosts change, accounts close, and change requests get hard to find. A record in the repository keeps the plan, the review, and the decisions next to the code they explain.
- **Nothing merges on a failing or pending check.** A merge "because it is probably fine" is exactly the trust problem this exists to remove.
- **Merges are pinned to the commit the checks passed on.** Otherwise something pushed between the check and the merge would ride along unchecked.
- **The guard fails closed, and pushes go only to the ticket branch.** If the guard errors, refusing is the safe answer. The default branch only changes through a merge that passed the gate.
- **Editing the framework, `docs/`, and CI asks a person.** An agent could otherwise make a gate pass by changing the gate.
- **Autonomy levels.** Teams differ in how much they trust an agent; `merge`, `pr`, and `supervised` let them choose without changing the process.
- **The hotfix lane still writes tests first.** Urgency is when mistakes happen. The lane skips planning rounds, not proof, and logs why it was used.
- **Every TODO names a ticket.** An unnamed TODO is a gap nobody owns.

## The framework itself

- **"Change request" in shared text.** Test Kitchen works with several hosts; neutral words keep the process the same on each.
- **Playbooks are the single source; agent files are thin wrappers.** One process, many agents: a rule changed in the playbook changes for everyone.
- **The installer never overwrites.** Your files are yours. A side-by-side `.kitchen-new` copy lets you merge on your terms.
- **The lock records hashes.** Updates can then tell your edits from the framework's without guessing, and never discard your work.
- **Template files are stored inertly.** Instruction files in `template/` are named so tools never load them while Test Kitchen itself is developed, and the project can run Test Kitchen on itself.
- **Releases are pinned.** The one-line install names a version, so what you install is what you reviewed.
