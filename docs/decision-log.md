# Decision log

Every decision about Test Kitchen, newest first. Each entry is a level-3 heading with the date, an em dash, and a short unique title, and says what was decided, why, who decided, and where it is recorded. Change requests cite entries by title ("Log: <title>"), so a title is never renamed; a replaced decision gets a "Superseded by: <new title>" line. Entries before the first release come from the planning conversation that produced `docs/spec-v0.1.md`; the project owner decided each one.

### 2026-11-27 — TASK-DLV-04, TASK-DLV-05, and TASK-DEF-08 are ready

- Decision: TASK-DLV-04, TASK-DLV-05, and TASK-DEF-08 passed refinement and are `ready`, refined 2026-11-27, owned by Ianick Noejovich. TASK-DLV-04 needed seven ticket-mode reviews; TASK-DLV-05 and TASK-DEF-08 three each. No review found a CRITICAL; every WARNING was settled with the owner (decision log, "How the refinement reviews of TASK-DLV-04, TASK-DLV-05, and TASK-DEF-08 were settled"), and the last reviews' suggestions are noted on the tickets for the delivering agent. TASK-DLV-04 waits for TASK-DEF-08 (`blocked_by`).
- Why: The owner asked to refine TASK-DLV-04 and TASK-DLV-05 once TASK-DEF-06 had written the questioning rules into define; TASK-DEF-08 was added because DEF-R52 widens define's rule, which TASK-DLV-04 points to, and a done ticket is never rewritten. The owner approved marking them ready once a review came back with no CRITICAL and no WARNING, and set the stop rule recorded on TASK-DLV-04.
- Decided by: Ianick Noejovich.
- Recorded in: TASK-DLV-04, TASK-DLV-05, TASK-DEF-08.

### 2026-11-27 — How the refinement reviews of TASK-DLV-04, TASK-DLV-05, and TASK-DEF-08 were settled

- Decision: The ticket-mode reviews found no CRITICAL. TASK-DLV-04's two warnings: AC6 is replaced by AC11 (the rules apply to every option a "Stop and ask" question offers; a question with no options, such as a location, a credential, or an approval, needs only the open-DEC check), and AC9 makes the "Hotfix stories" variant keep the open-DEC check for self-decided items, a match being a stop. Suggestions taken: TASK-DLV-04/AC5 names "each option lettered, with one For and one Against line" (a wording fix); AC10 adds an answer to an open DEC's question to the "Stop and ask" list; TASK-DEF-08/AC1 also keeps the search before recommending, so DEF-R52 is covered in full (a wording fix); TASK-DLV-05/AC3 brings step 6's "Done when" row in line with DLV-R64. AC5 keeps excluding define's round size. TASK-DLV-05's suggestions to define "read-only checks" and to forbid drafts outside the repository are left out, since they would change DLV-R61. At the re-review, two more warnings on TASK-DLV-04 were settled: AC9 is replaced by AC12, which puts the open-DEC check for self-decided items in "Ground rules" for every variant (hotfix stories, spikes, decisions, other changes), a match outside step 3 being a stop; and AC5 says only the bullet, the lettered option with its For and Against lines, and the three rules under the template apply, not the Defer option or the brief's headings. Also taken: AC11 keeps the re-evaluation rule for a stop question with no options (edited in place, never committed); TASK-DEF-08/AC1 keeps the bullet's name, which TASK-DLV-04/AC5 points to; TASK-DLV-05/AC2 ends the rerun before the supervised tests approval too; Notes say why US-DLV-24/AC3 and US-DLV-25/AC3 (done) need no `replaces:`. Left as it is: `--refine` keeps listing TASK-DEF-06 for citing DEF-R49, the existing behavior for done tickets citing superseded requirements. At the third review, AC5 says a question that only confirms how to read a criterion lists each reasonable reading as a lettered option with For and Against lines (the no-options case stays for stops only, keeping "Delivery's questions and self-decided items follow define's rules"), and names define's three rules by their titles; AC12 is limited to the kinds of item step 3 lists, as DLV-R63 says; AC8 puts the agent's proposals in the same format; AC7 keeps only the step-3 part and points to "Ground rules". AC5, AC7, AC8, and AC12 were edited in place, never having been committed. At the fourth review, AC12 makes a match a stop only after step 3 or in a variant that skips step 3, as AC7 and DLV-R63 say (a match found while planning waits for the questions round); AC5 gives a question that is an open DEC that DEC's full decision round, Defer included, so a DEC is decided the same way wherever it comes up, keeps the recommended option first, and counts the template's "**Recommendation:**" line among the headings that do not apply; AC10 puts the wider case in the same bullet. These edits were made in place, never having been committed. At the fifth review, AC11 makes a stop question follow step 3's questions-round rules as a whole (readings as options, an open DEC's full round), limits the no-options case to questions with nothing to choose between, and names define's bullet so the decision-log search is included; the Notes say the final review checks AC5's parts one by one. AC11 was edited in place, never having been committed. At the sixth review, AC5 says define's round size never applies in delivery, while the rest of the template applies only to a question that is an open DEC; DLV-R65 and AC8 also cover the DECs a spike files as follow-ups (edited in place, never committed); AC11 says a yes on a drafted change to `docs/`, criteria, or open questions is a choice between the draft and leaving things as they are, an approval being only the supervised approval of a reviewed plan or tests. The owner also set a stop rule: after the next review, new readings of the same wording raised without a CRITICAL are noted on TASK-DLV-04 for the delivering agent and its diff review, while anything new in substance still goes to the owner.
- Why: Forcing options onto a question that has none would make the agent invent them; a hotfix skips step 3, where the check lives, so without a rule every lane reads (first AC9 for hotfixes, then AC12 for all variants) a lane that skips it could decide a DEC silently; restating the whole template would put a Defer option on every one-line question, against "Delivery points to define's named questioning rules".
- Decided by: Ianick Noejovich.
- Recorded in: TASK-DLV-04, TASK-DLV-05, TASK-DEF-08.

### 2026-11-27 — The tests review reruns until no CRITICAL is left

- Decision: In delivery step 6, after fixing what the tests review finds, the agent runs `gate red` and the tests review again until no CRITICAL finding is left, before the freeze commit (DLV-R64, added to TASK-DLV-05 as AC2).
- Why: In the US-GRD-17 delivery (2026-11-27) the tests review found 2 CRITICAL issues, which were fixed and frozen without a second review; steps 4 and 9 already rerun their reviews until no CRITICAL is left, and a wrong fix to a test is hard to undo once frozen. It joins TASK-DLV-05, which already covers review discipline in the same file, rather than a ticket of its own.
- Decided by: Ianick Noejovich.
- Recorded in: DLV-R64; TASK-DLV-05.

### 2026-11-27 — Delivery opens new DECs in the DEC format

- Decision: Wherever delivery files a new DEC (step 10's gaps, and a spike's follow-ups), each option is in the DEC format DEF-R51 checks (`- (x) …` with a For and an Against line), its options still coming only from what `docs/` records, otherwise "None recorded" (DLV-R65, TASK-DLV-04/AC8; the spike's follow-ups were added at the sixth refinement review).
- Why: TASK-DEF-06's final review found that step 10 never mentions the format, so a DEC delivery opens with recorded options would fail the check US-DEF-35 added. The owner chose to state it in step 10 over relying on `backlog_check.py` at the end of the same step, which was the recommendation, so the agent gets it right the first time instead of by failing.
- Decided by: Ianick Noejovich (over the recommendation to leave it to the check).
- Recorded in: DLV-R65; TASK-DLV-04.

### 2026-11-27 — Stop-and-ask questions follow the questioning rules

- Decision: Every question delivery asks the person under "Stop and ask", not only in step 3's questions round, follows the rules on open DECs and on evaluating options (DLV-R62, superseding DLV-R59; TASK-DLV-04/AC11, which replaced AC6 at the refinement review: every option a stop offers is evaluated, and a stop with no options needs only the open-DEC check). A hotfix still skips step 3 (DLV-R37), but its stops follow the rules.
- Why: Stops are where DEC options and unsettled behavior reach the person in the middle of a delivery; leaving them out would present those choices without For and Against lines or a compared recommendation, against the aim that every option in a decision round is evaluated.
- Decided by: Ianick Noejovich.
- Recorded in: DLV-R62; TASK-DLV-04.

### 2026-11-27 — An answer to an open DEC's question counts as that DEC

- Decision: An option that matches an open DEC's option, or otherwise answers an open DEC's question, is presented as that DEC, in define's decision rounds (DEF-R52, superseding DEF-R49; new task TASK-DEF-08) and in delivery's self-decided items (DLV-R63, superseding DLV-R60; TASK-DLV-04/AC7). TASK-DEF-06/AC3 (done) stays true under the wider rule, so nothing is replaced.
- Why: The last review of TASK-DLV-04 asked whether "matches an open DEC's option" covers an answer the DEC does not list. Accepting such an answer as an ordinary choice settles the DEC silently, the failure DEF-R49 was written to prevent. The owner chose to widen the rule over the recommendation to keep the literal reading and note the gap.
- Decided by: Ianick Noejovich (over the recommendation to keep the literal reading).
- Recorded in: DEF-R52, DLV-R63; TASK-DEF-08, TASK-DLV-04.

### 2026-11-27 — Self-decided items are checked whenever they come up

- Decision: The open-DEC check before the agent decides an item itself applies whenever such an item comes up, not only at step 3; a match found after step 3 is a stop under "Stop and ask", which already lists "a DEC option to choose" (DLV-R63; TASK-DLV-04/AC7).
- Why: Names, plumbing, and wording are mostly decided during implementation, after step 3; checking only at step 3 would leave the 2026-11-26 failure open through a later door.
- Decided by: Ianick Noejovich.
- Recorded in: DLV-R63; TASK-DLV-04.

### 2026-11-27 — Delivery points to define's named questioning rules

- Decision: Delivery step 3 points to define's "Check open decisions before recommending" and to "Decision format"'s option shape with the three rules under its template, says they apply to every question, and says define's round size and its table of small sub-questions do not apply (TASK-DLV-04/AC5, replacing AC3, which pointed to whole sections).
- Why: The last review of TASK-DLV-04 found that pointing to whole sections pulled in rules that conflict with step 3 (about three questions per round; a table with no options). The first recommendation was to restate the rules in step 3; re-evaluated when the owner asked what was wrong with pointing, it lost to naming the rules: `deliver.md` already points to define's decision format in its hand-off, and DEF-R52 changes define's text again, which a copy would have to follow in two files.
- Decided by: Ianick Noejovich.
- Recorded in: TASK-DLV-04.

### 2026-11-27 — How backlog_check.py reads and reports the DEC format

- Decision: US-DEF-35 checks DEF-R51 in `backlog_check.py` (`_dec_format`, run as each DEC is read). Readings within the criteria's words: every status but `done` and `deferred` counts as open, an invalid one included (it is also reported on its own), so a bad status never skips the check; "exactly `## Outcome`" ignores trailing spaces and Windows line endings, as `kitchen_lib.section` does, while `### Outcome` and `## Outcomes` do not count; an option is `- (<a-z>)` at the start of a line followed by a space or the end of the line. The error texts: "`<DEC>`: option (`<x>`) under ## Options has no `` `For:` `` [or `` `Against:` ``] line (DEF-R51)", "`<DEC>`: an open decision records an outcome: remove `## Outcome`, or set status done or deferred once decided (DEF-R51)", and "`<DEC>`: the decision has no outcome (status `<status>`): add `## Outcome` (DEF-R51)". `template/CONTRIBUTING.md`'s enforcement table and `CHANGELOG.md` (Added, and a migration note) name the check. AC3 forced an `## Outcome` onto five done or deferred DEC fixtures, four in `tests/test_backlog_check.py` and one in `tests/test_deliver.py`, in the freeze commit; no assertion changed. Fenced code blocks inside a DEC are not skipped (final review suggestion): no DEC quotes one today, so it was noted, not filed.
- Why: The criteria fix the rules; these choices fill only what they leave to the implementation, and failing closed on an unknown status matches "not `done` or `deferred`". Reviews added tests for the end of `## Options`, near-miss headings on decided DECs, the one-letter marker, and the line-start rule.
- Decided by: the delivering agent.
- Recorded in: `template/scripts/backlog_check.py`; `tests/test_def_dec_format.py`; US-DEF-35's delivery record.

### 2026-11-27 — How the define skill words its one-file-per-call reading

- Decision: TASK-DEF-05 rewrites the define skill's opening (`template/claude/skills/define/SKILL.md`, and its installed copy through `init.py update`) to "Read it in full first, then `backlog/README.md` and `AGENTS.md`, with the file-read tool, one file per call, never combined with other commands in one shell call", followed by the reason: a combined call can overflow into a saved file that is then read a second time (DLV-R54). The two files keep the order DLV-R54 lists them in; no order between them is required. `CHANGELOG.md` gets a line under Unreleased, Changed. The `/deliver` skill's half of DLV-R54 stays with TASK-DLV-03.
- Why: The criterion's words are used as they are so the skill and DLV-R54 read the same; the reason is the overflow measured on the US-DLV-38 run (TASK-DLV-03, Notes), so the next reader knows why the rule exists. The plan review's suggestion not to require an order between the two files was applied.
- Decided by: the delivering agent (wording left to the implementation).
- Recorded in: `template/claude/skills/define/SKILL.md`; `CHANGELOG.md`; TASK-DEF-05's delivery record.

### 2026-11-27 — The guard's hand-back line for subagent calls

- Decision: A subagent's deny (GRD-R36, US-GRD-17) is the ask's reasons, deduplicated and in the ask's order (force-push reasons first), followed by one last line: "This call came from a subagent, where the guard can't ask the person; hand this step back to the main session, which runs it and the person is asked there." The rule sits in `finish()` after the sandbox opt-in, read from `agent_id` by `is_subagent()` as "How the guard reads agent_id" says. Documented in the guard's docstring, `template/CONTRIBUTING.md` (the root copy through `init.py update`), `guide/agents.md`, and `CHANGELOG.md` (a change and a migration note).
- Why: AC2 requires the deny to keep every reason the ask gives and tell the subagent to hand the step back; putting the reasons first keeps them identical to what the main session's ask shows, and a fixed last line lets the subagent and the tests find the hand-back. The wording names the subagent, the reason (the guard can't ask the person there), and the action.
- Decided by: the delivering agent (wording left open by the ticket; plan review WARNING 1).
- Recorded in: `template/claude/hooks/guard.py`; `tests/test_guard_subagent.py`; US-GRD-17's delivery record.

### 2026-11-27 — Unchanged-behavior criteria get a boundary test

- Decision: US-GRD-17/AC3, AC4, and AC6 describe behavior that must stay as it is (main-session calls still ask, the sandbox still lets asks through, allows and denies stay), so their direct tests passed before the change and `gate red` refused them. Each also got a boundary test that pairs the unchanged case with its contrast under the new rule: main-session forms ask while a present `agent_id` denies (AC3), the same subagent call is denied without the opt-in and allowed with it (AC4), and over allowed, asked, and denied calls a subagent's decisions are the main session's with only the asks turned into denies (AC6). These fail on the old code only for the missing behavior; the direct tests stay too.
- Why: `gate red` needs a failing tagged test per live criterion and a gate's FAIL is final; the boundary is what each criterion adds once the rule exists, so the test proves the criterion rather than working around the gate. No earlier delivery recorded a way to handle this.
- Decided by: the delivering agent.
- Recorded in: `tests/test_guard_subagent.py`; US-GRD-17's delivery record.

### 2026-11-27 — Delivery waits for each review's report

- Decision: After running a plan, tests, or diff review, the delivering agent waits for its report before the next step; meanwhile it may read files and run read-only checks, but does not edit repository files, run `init.py update`, claim, or commit (DLV-R61, built by TASK-DLV-05). Define's refine reviews are left out.
- Why: In the TASK-DEF-06 delivery the plan review ran in the background and the agent drafted its edits and refreshed the root copies before the report arrived, then judged the review's suggestions against its draft. The playbook ordered the steps but never said to wait, and no gate can see uncommitted drafting. Waiting avoids anchoring on a draft and wasted work when a review is critical, and matters more once TASK-DLV-03 runs tickets in unattended subagents. Define's refine reviews were left out because the changes they lead to need the person's yes at a checkpoint anyway.
- Decided by: Ianick Noejovich.
- Recorded in: DLV-R61; TASK-DLV-05.

### 2026-11-27 — How define's playbook and the backlog README word the questioning rules

- Decision: TASK-DEF-06 writes DEF-R49 into define's "Questioning" as a new bullet, "Check open decisions before recommending" (open DECs are those not `done` or `deferred`; a matching option is presented as that DEC and its decision round is run). "Decision format" now writes each option, Defer included, as `- (x) …` with indented `- For:` and `- Against:` sub-bullets, the same shape the backlog README sets for DEC files, so an option copied from a brief into a DEC passes the US-DEF-35 check; it adds a `**Recommendation:**` line (why it beats each other option, then "Strongest reason against it") and three rules below the template (one For and one Against line per option, "conflicts with nothing recorded" when a search found nothing; the recommendation compares; when questioned, re-evaluate and say what was missed or that nothing changed, never switch or defend without re-checking). The README's Decision body says "None recorded" may be followed by "Proposals:", that a decided DEC is `done` (or `deferred`), and states the DEF-R51 format as three bullets with an example; it says a plain `For:` or `Against:` line "is also accepted" rather than naming the check, which US-DEF-35 has not built yet.
- Why: The wording is the delivering agent's, within DEF-R49, DEF-R50, and DEF-R51. The final review's suggestion that Defer's Against placeholder name conflicts too was noted, not applied: the rule under the template binds every option. Its other suggestion, that `deliver.md` step 10 opens DECs without the new format, is filed on TASK-DLV-04.
- Decided by: the delivering agent, within "Agents check open decisions and evaluate options before recommending" and "Open DECs carry evaluated options; outcomes match status".
- Recorded in: `template/playbooks/define.md`, `template/backlog/README.md` (and their installed copies); TASK-DEF-06; TASK-DLV-04 (note).

### 2026-11-27 — How the guard reads agent_id

- Decision: For GRD-R36, an `agent_id` that is absent, null, or an empty string means a main-session call; any other value, including a number, an object, or whitespace, counts as a subagent's call, so its asks are denied. US-GRD-17's criteria now cover every ask the guard gives (not only protected edits and shell writes), give one rule for the deny's reason (every reason the ask would have given, plus the hand-back), and test that `agent_type` alone does not trigger the rule.
- Why: The ticket-mode review of US-GRD-17 found its criteria covered only part of GRD-R36 and left unusual `agent_id` values open. Treating null as a main-session call fails closed for asks without blocking every main-session call should Claude Code ever send a null `agent_id` there, which has not been verified; denying every call on a malformed value was the stricter option, rejected for that risk.
- Decided by: Ianick Noejovich.
- Recorded in: GRD-R36 (the null and empty reading); US-GRD-17.

### 2026-11-27 — The guard denies in a subagent what it would ask

- Decision: When a call carries a non-empty `agent_id` (it was made in a subagent), every ask the guard would give becomes a deny that tells the subagent to hand the step back to the main session (GRD-R36, built by US-GRD-17). Sandbox mode applies first and is unchanged, so its asks still pass; a force push, which asks even in sandbox mode, is denied in a subagent. Closes DEC-GRD-05 with option (a). GRD-R36 narrows, without contradicting, the done criteria US-GRD-08/AC1, AC4, AC5, US-GRD-09/AC1 to AC4, and US-GRD-10/AC4: they describe calls without an `agent_id`, which their tests send none of, so no `replaces:` is needed.
- Why: SPK-DLV-02 found that in auto mode the guard's asks from subagents are approved by the classifier instead of the person. Run by hand on the normal delivery steps (`init.py update`, commits, plain pushes of the ticket's branch, the `gh pr` steps, every gate and `record`, edits to `template/`, `tests/`, `backlog/`, `guide/`, `CHANGELOG.md`, and the decision log), the guard asks about none of them, so the deny falls only on steps that need the person anyway. Listing the eight criteria under `replaces:` would restate behavior that does not change and push US-GRD-17 past the split threshold.
- Decided by: Ianick Noejovich (option (a), sandbox unchanged, and the narrowing reading of the done criteria).
- Recorded in: GRD-R36; DEC-GRD-05 (outcome); US-GRD-17; TASK-DLV-03 (now blocked by US-GRD-17); US-GRD-16 (note).

### 2026-11-27 — TASK-DLV-04 is refined after TASK-DEF-06

- Decision: US-DEF-35 and TASK-DEF-06 passed refinement and are `ready`. TASK-DLV-04 stays `draft` and is refined right after TASK-DEF-06 is delivered; the five points its last ticket-mode review left are recorded in its Notes.
- Why: TASK-DLV-04 points to rules TASK-DEF-06 has not written into `define.md` yet, so each review reasoned about text that does not exist and found new readings; it cannot be delivered before TASK-DEF-06 anyway, and refining it against the real text avoids rounds that would be redone.
- Decided by: Ianick Noejovich.
- Recorded in: US-DEF-35, TASK-DEF-06, TASK-DLV-04.

### 2026-11-27 — Delivery's questions and self-decided items follow define's rules

- Decision: Every question of delivery's step-3 questions round, including one that only confirms how to read a criterion, follows define's rules on open DECs and on evaluating options (DLV-R59, as TASK-DLV-04/AC3 states). Before deciding an item of "You decide, then log" itself, the agent checks the open DECs, and an item that matches an open DEC's option is asked, not decided (DLV-R60, TASK-DLV-04/AC4).
- Why: The re-review of TASK-DLV-04 found that DLV-R59 could be read as covering only questions with real alternatives, which would let an agent frame a choice as a yes/no question to skip the evaluation, and that the items the agent decides itself could still pick an open DEC's option without any check, the 2026-11-26 failure through another door.
- Decided by: Ianick Noejovich (every question, over the recommendation to limit it to real choices; the self-decided check as recommended).
- Recorded in: DLV-R60; TASK-DLV-04.

### 2026-11-27 — Review-only work stays in untestable tasks

- Decision: The outcome of DEC-DEF-05, option (b) (the `(review)` marker), is reversed to its option (a): review-only work stays in untestable tasks, confirmed by the final review (DLV-R37). DEF-R47 and DEF-R48 are superseded by DEF-R14, and DLV-R56, DLV-R57, and DLV-R58 by DLV-R08: DEF-R14 and DLV-R08 are live again (the superseded markers added to them earlier the same day are removed), so the done stories that test them, US-DEF-10 and US-DLV-06, cover them again. Restoring them, rather than restating their rules under new IDs, is a step the playbook does not name; the owner chose it because new IDs would stay uncovered for good, since done tickets are never edited to cite them. US-DEF-34, US-DLV-43, and TASK-DEF-07 are deferred and retired (their IDs are never reused); the marker criteria of TASK-DEF-06 (AC1, AC2) and TASK-DLV-04 (AC1, AC2) are removed. DEC-DEF-05's file stays as it is: a done ticket is never rewritten, and this entry records the reversal. The questioning rules and the DEC check (DEF-R49, DEF-R50, DEF-R51, DLV-R59) stand.
- Why: The ticket-mode reviews of the marker tickets found it would also change the criterion format check (DEF-R08), the freeze check in `gate pr` (DLV-R18), `gate red` and the freeze for stories whose criteria are all review-only, the plan and tests reviews and delivery steps 2 and 6, and the define playbook's "one allowed edit": about six requirements and four done criteria across two epics, several times the "2 or 3 tickets" estimated when DEC-DEF-05 was decided. The untestable-task route already works.
- Decided by: Ianick Noejovich.
- Recorded in: DEF-R14, DLV-R08 (restored); DEF-R47, DEF-R48, DLV-R56, DLV-R57, DLV-R58 (superseded); US-DEF-34, US-DLV-43, TASK-DEF-07 (deferred); TASK-DEF-06, TASK-DLV-04.

### 2026-11-27 — Open DECs carry evaluated options; outcomes match status

- Decision: `backlog_check.py` reports an error for an option of an open DEC (not `done` or `deferred`) without a `For:` and an `Against:` line, for an open DEC with an `## Outcome`, and for a `done` or `deferred` DEC without one (DEF-R51, built by US-DEF-35; the README's DEC format by TASK-DEF-06/AC5). DEC-DEF-06 and DEC-DEF-07 get For and Against lines now.
- Why: It moves the DEC-file half of DEF-R50 from judgment into a check, catches a DEC decided in its file while still open, and costs nothing today: all 20 done DECs already have an Outcome. Chat briefs stay with the playbook rules of TASK-DEF-06.
- Decided by: Ianick Noejovich.
- Recorded in: DEF-R51; US-DEF-35, TASK-DEF-06; DEC-DEF-06, DEC-DEF-07.

### 2026-11-27 — How the cost report groups and checks a transcript

- Decision: Besides the eight groups "A cost report for this repository's delivery runs" lists, `tools/usage_report.py` reports "Handing work to subagents" (prompts given to the Agent, Task, and SendMessage tools) and "Everything else" (tools it does not recognize, so an unknown tool shows up instead of hiding in another group). A subagent's final report (`SubagentHandback`) counts as conversation. Only `deliver.py gate` and `check`, `backlog_check.py`, and the tests run as `python3 -m unittest` or `python3 -m pytest` (how this repository runs them) count as gates and tests, unless the command starts with a read such as `cat` or `grep`; a bare `pytest` counts as reading; `deliver.py context`, `next`, `status`, and `pr-body` print tickets and count as ticket reading; a git command counts as git even when it names a framework file. A call is charged for what it read, not for what it wrote, and a block repeated across the records of one response is counted once. The tool stops with a message when a usage record lacks a token field or splits no cache writes into 5-minute and 1-hour ones, and on a file that is not UTF-8 JSON lines; a subagent with no model call is listed as skipped.
- Why: Two fresh-context reviews of the change found that the first version would have counted ticket reading as gates (skewing the comparison SPK-DLV-01 needs), charged calls for their own output, and silently priced missing fields at 0 or as 5-minute writes.
- Decided by: the delivering agent, within the decision "A cost report for this repository's delivery runs".
- Recorded in: `tools/usage_report.py`, `tools/README.md`, `tests/test_usage_report.py`.

### 2026-11-27 — A cost report for this repository's delivery runs

- Decision: This repository gets `tools/usage_report.py`, a developer tool that is not part of the product (not in `template/`, not installed, outside `kitchen.yml`'s `code` globs), built as a `chore/` change. It reads a Claude Code session transcript and its subagents' transcripts and prints, per session and per subagent: raw token counts (input, cache reads, 5-minute and 1-hour cache writes, output); effective tokens weighted by a per-model table of multipliers taken from the Anthropic pricing page, with the page's URL and the date checked; the share of effective tokens per group (instructions, framework docs, code and ticket reading, writing, gates and tests, git and host, app tools, conversation); the number of steps; and the peak context. `--json` prints the same for before-and-after comparisons. The groups and the split of carried context between them are heuristic, and the report says so. Its tests use small synthetic transcripts, never a real one.
- Why: SPK-DLV-01 and every later cost change need measurements made the same way each time. The transcript format is internal to Claude Code and "can break on any release" (code.claude.com, sessions page, checked 2026-11-27), and it works only with Claude Code, so it is not a product feature; the tool fails with a clear message when a field it needs is missing.
- Decided by: Ianick Noejovich.
- Recorded in: this entry; SPK-DLV-01.

### 2026-11-27 — The US-DLV-38 run cost about 1.61M effective tokens, not 2.37M

- Decision: The measured cost of the US-DLV-38 delivery run is corrected to about 1.61M effective tokens (1.28M in the main session, 0.32M in the three reviews). The 2.37M figure used a flat 0.1× weight for cache reads; the pricing page gives 0.05× for Claude Opus 5.5, the model that ran (1-hour cache writes 2× and output 5× were right). The shares barely change (instructions about 30%, code and ticket reading 20%, reviews 20%, writing 13%, framework docs 8%), so the conclusions of "Fresh context per ticket under /deliver all" stand.
- Why: The figure is cited in later tickets and must be right.
- Decided by: Ianick Noejovich.
- Recorded in: SPK-DLV-01, TASK-DLV-03. The entry "Fresh context per ticket under /deliver all" keeps the old figure as history.

### 2026-11-27 — Agents check open decisions and evaluate options before recommending

- Decision: Before recommending in a decision round, the agent searches the decision log and the open DECs for the same kind of question, and presents an option that matches an open DEC's option as that DEC, never as an ordinary choice (DEF-R49). Each option in a decision brief has one "For" and one "Against" line naming its cost and what in `docs/`, the backlog, or the decision log it conflicts with; the recommendation says why it beats each other option and the strongest reason against it; when the person questions a recommendation, the agent re-evaluates and says what it missed, or that nothing changed (DEF-R50). Delivery's questions round follows both (DLV-R59).
- Why: On 2026-11-26 an agent refining US-DLV-42 recommended text tests, an option of the then-open DEC-DEF-05, as an ordinary ticket choice, which would have decided the DEC silently; and it presented a recommendation (keep refining TASK-DLV-03) that it reversed as soon as the owner asked why, because it had not weighed the open spike. Both reached the owner before any check caught them.
- Decided by: Ianick Noejovich.
- Recorded in: DEF-R49, DEF-R50, DLV-R59; TASK-DEF-06, TASK-DLV-04.

### 2026-11-27 — Review-only criteria carry a (review) marker

- Decision: A criterion whose text starts with `(review)` is one only reading can check (the wording of a playbook, a guide, or an instruction file). A `done` story needs no tagged test for it, it is never test debt, and a test tag naming it is an error (DEF-R47, superseding DEF-R14; DEF-R48). `gate red` skips it and names it (DLV-R56, superseding DLV-R08); `gate pr` requires the final review to write `Checked by review: <ID>/AC<n>` for each one (DLV-R57); the reviewer checks each one by name and challenges markers a test could check (DLV-R58). Only a person adds the marker, at a define checkpoint; adding it to a live criterion of an adopted `done` story, with the person's yes, is the second allowed edit to a done ticket. Closes DEC-DEF-05 with option (b). The new tickets replace US-DEF-10/AC4, AC5, AC6 and US-DLV-06/AC2, AC4 (shown to the owner and approved).
- Why: It keeps review-only criteria in the tickets they belong to instead of splitting them into tasks late (as US-DLV-42 had to be), it clears the test debt no test can pay (about 150 of 636 lines, the owner's estimate), and it checks each such criterion by name, which the untestable-task route does not. Text tests (option (c)) were rejected: they prove only that words exist, as "Review-only stories become tasks" recorded. Until US-DEF-34 and US-DLV-43 are delivered, review-only work still uses untestable tasks.
- Decided by: Ianick Noejovich.
- Recorded in: DEF-R47, DEF-R48, DLV-R56, DLV-R57, DLV-R58; DEC-DEF-05 (outcome); US-DEF-34, US-DLV-43, TASK-DLV-04, TASK-DEF-06, TASK-DEF-07.
- Superseded by: Review-only work stays in untestable tasks

### 2026-11-26 — TASK-DLV-03 waits for SPK-DLV-02; TASK-DEF-05 is ready

- Decision: Refinement of TASK-DLV-03 pauses until SPK-DLV-02 is done; the fourth ticket-mode review's open points are its open questions, with a proposed direction in its Notes. SPK-DLV-02 also checks what a guard "ask" does inside a subagent. TASK-DEF-05 passed refinement and is `ready`.
- Why: Four ticket-mode reviews each found new edge cases of a design that SPK-DLV-02 can still change (if the guard does not cover the reviewer a ticket's subagent starts, the reviews move to the main session); TASK-DLV-03 cannot finish before the spike anyway, and each further round costs tokens for a change meant to save them.
- Decided by: Ianick Noejovich.
- Recorded in: TASK-DLV-03, SPK-DLV-02, TASK-DEF-05.

### 2026-11-26 — TASK-DLV-03 settles the checkout, the agent file, and DLV-R55

- Decision: A `ticket-deliverer` subagent that stops at "ready to merge" switches to the up-to-date default branch before it returns, so the next ticket's step 1 does not stop on an unmerged branch. The agent file sets no model and no tools list, and carries the skill's guard rules (a denial is final, plain push and merge commands), since the subagent runs the merge. DLV-R53 is superseded by DLV-R55, which adds the replacement subagent when one cannot be resumed. Under `/deliver all` the ticket subagents run one at a time, each given only the ticket ID and the request to follow `playbooks/deliver.md`; a spike or decision is finished when it is merged as its variant says.
- Why: The third ticket-mode review found that "per-ticket instructions" could carry what earlier tickets learned, that a merged spike never reaches step 14, that subagents could run together in one checkout, that every ticket after a "ready to merge" would stop at step 1, and that the fallback had no requirement behind it.
- Decided by: Ianick Noejovich.
- Recorded in: DLV-R55 (supersedes DLV-R53); TASK-DLV-03.

### 2026-11-26 — TASK-DLV-03 names its worker agent and when a ticket is finished

- Decision: Under `/deliver all`, each ticket runs in a dedicated `ticket-deliverer` subagent (a new `template/claude/agents/ticket-deliverer.md`), given only the ticket ID; the main session picks, runs the hand-off to define, and prints the closing status. A ticket is finished when its subagent closed it through step 14 or stopped at "ready to merge" as the autonomy level or the manual host requires; a supervised approval is a question; a subagent that returns otherwise stops `/deliver all`. When a subagent cannot be resumed, a new `ticket-deliverer` for that ticket gets the answers and continues from the pushed branch or starts again. The skill and the agent read the playbook in full first, one file per call (TASK-DEF-05 says the same for `/define`).
- Why: The second ticket-mode review found that "without finishing" would stop `/deliver all` at every ticket waiting for a person's merge, which step 14 and US-DLV-23/AC3 forbid; that a subagent given only the ID would never see the skill's instructions; and that picking and the hand-off need AskUserQuestion, which subagents lack. TASK-DLV-03's criteria were rewritten in place rather than retired as placeholders: it is a draft that no test, plan, or record cites.
- Decided by: Ianick Noejovich.
- Recorded in: TASK-DLV-03, TASK-DEF-05.

### 2026-11-26 — The fresh-context story becomes a task

- Decision: US-DLV-42 becomes TASK-DLV-03, an untestable task, and its ID is retired, never reused; its criteria now say what the playbook and the `/deliver` skill tell the agent. A ticket's subagent that has a question commits and pushes the work it has, if any, and the main session resumes that same subagent with the answers. A subagent that returns unfinished with no question stops `/deliver all` (DLV-R39). The `/define` half of DLV-R54 moves to TASK-DEF-05 in EP-DEF. DLV-R54 names its files (a wording fix).
- Why: The ticket-mode review found that no test can check the playbook's or skill's wording, which the entry "Review-only stories become tasks" already settles; resuming keeps the plan, which before the claim lives only outside the repository; EP-DLV's Boundaries give the define skill to EP-DEF.
- Decided by: Ianick Noejovich.
- Recorded in: DLV-R54; TASK-DLV-03, TASK-DEF-05, SPK-DLV-02. The entry "Fresh context per ticket under /deliver all" names the old ID.

### 2026-11-26 — Fresh context per ticket under /deliver all

- Decision: `/deliver all` delivers each ticket in a fresh context where the agent can start one (DLV-R52); in Claude Code, a subagent per ticket that commits, pushes, and hands its questions back to the main session, which asks them, since `AskUserQuestion` is not available inside subagents (DLV-R53); the `/deliver` and `/define` skills read the playbooks and rule files one file per call (DLV-R54). Advice on lean sessions waits for a measurement (SPK-DLV-01). Reviews and what agents read stay unchanged.
- Why: measured on the US-DLV-38 run (about 2.37M effective tokens; the context reached 254k tokens on one ticket), the context carried from one ticket into the next is the largest cost that can be removed without reducing what agents read. Trimming the playbooks would save about 4% and shortening script output about 2%, each at a cost to reliability; merging or skipping reviews would break the product's promise of fresh-context review of the plan, the tests, and the diff.
- Decided by: Ianick Noejovich.
- Recorded in: DLV-R52, DLV-R53, DLV-R54; US-DLV-42 (blocked by SPK-DLV-02, whether the guard covers the reviewer a ticket's subagent starts); SPK-DLV-01.

### 2026-11-26 — US-DLV-38: gate pr reads kitchen.lock at --head too

- Decision: `deliver.py gate pr` resolves `--head` and judges everything through a view of the repository read at that revision (`Project.at`): the ticket files (`Backlog(root, cfg, rev)`, committed files only, read in one `git cat-file --batch` call through the new `kitchen_lib.blobs_at`), `kitchen.yml` (`load_config(root, rev)`), and `kitchen.lock` (`framework_files(root, rev)`). `Project` now loads the configuration on first use, so `gate pr` never reads the checkout's `kitchen.yml`: a missing or invalid one there changes nothing. A `kitchen.yml` missing at `--head` prints `FAIL kitchen.yml: not found at <sha>` (exit 1). `gate merge` is unchanged; its comment now says its own backlog and description checks read the checkout. Delivers US-DLV-38 (DLV-R48; "gate pr reads tickets and kitchen.yml at --head").
- Why `kitchen.lock` too: it decides which files are framework files, excluded from every scan and so never code or tests; read from the checkout, it would change the verdict between checkouts, which AC4 forbids. The ticket's notes name only the ticket files and `kitchen.yml`, so this is recorded here.
- Also: `read_at` now goes through `blobs_at`, which skips the content of a non-file object (a path naming a folder) instead of losing its place in git's output.
- Decided by: the delivering agent, within US-DLV-38's criteria.
- Recorded in: `template/scripts/deliver.py`, `kitchen_lib.py`, `backlog_check.py`, `tests/test_dlv_gate_pr_at_head.py`, `guide/concepts.md`; this repository's installed copy refreshed through `init.py update`.
- Review suggestion noted, not taken: `playbooks/deliver.md`, "One checkout", says "the gates read this checkout"; it stays true for `gate red`, `gate merge`, and `backlog_check.py`, and the rule it supports is unchanged.
- Tooling note: pytest is not installed on this machine's Python; `gate red` and `check` ran with a throwaway virtualenv (pytest, PyYAML) first on PATH, as CI installs them.

### 2026-11-26 — US-DEF-30: summary counts and a frozen-test fix

- Decision: `backlog_check.py` computes the uncovered requirements before the summary and adds them to the error count with `--strict` and to the warning count without it; output order and exit codes are unchanged. Delivers US-DEF-30 (DEF-R40, DEC-DEF-01).
- Frozen-test change: after the freeze, `tests/test_def_summary.py` held the literal to-do marker word as fixture text, which this repository's own trace scan reported as an unowned marker (`doctor` failed). The word is now assembled from parts; the test asserts exactly the same thing. Allowed because it contradicted a project rule (every such marker names a ticket); listed under the change request's "Test changes".
- Lesson for the next deliveries here: run `python3 scripts/backlog_check.py` on this repository before the freeze commit, since test fixtures are traced here too.
- Decided by: the delivering agent, within US-DEF-30's criteria.
- Recorded in: `template/scripts/backlog_check.py`, `tests/test_def_summary.py`; this repository's installed copy refreshed through `init.py update`.

### 2026-11-26 — US-CONF-17: globs that start with a slash

- Decision: `_globs` in `kitchen_lib.py` refuses a glob that starts with `/` after trimming and removing one leading `./`, listing the globs as written, with the message "`<key>` globs are relative to the repository root and never start with `/`: [...]". The backslash check no longer returns before it, so a key with both problems reports both, one line each. Delivers US-CONF-17 (CONF-R28, DEC-CONF-02 as widened).
- Why: one normalization for checking and matching; every problem at once (CONF-R05).
- Decided by: the delivering agent, within US-CONF-17's criteria.
- Recorded in: `template/scripts/kitchen_lib.py`, `tests/test_conf_rooted_globs.py`; this repository's installed copy refreshed through `init.py update`.
- Review suggestion noted, not taken: a test for `"./ /vendor/**"` (whitespace after `./`), which CONF-R28 does not name.

### 2026-11-26 — US-CONF-16: a kitchen.yml that is not UTF-8

- Decision: `load_config` reads `kitchen.yml` in its own `try` and turns a `UnicodeDecodeError` into `ConfigError("kitchen.yml: not valid UTF-8")`; YAML errors keep their separate handling. The existing callers already print a `ConfigError` as `ERROR` lines and exit 1, so `--config` and `backlog_check.py` needed no change. The docstring now lists the failure modes. Delivers US-CONF-16 (CONF-R26, DEC-CONF-01).
- Why: catching only around the read keeps an encoding problem from being reported as a YAML one.
- Decided by: the delivering agent, within US-CONF-16's criteria.
- Recorded in: `template/scripts/kitchen_lib.py`, `tests/test_conf_utf8.py`; this repository's installed copy refreshed through `init.py update`.
- Review suggestion noted, not taken: `raise … from None` on the new raise (cosmetic; callers catch the error).

### 2026-11-26 — TASK-INST-03: terminal wording

- Decision: `AGENT-INSTALL.md` now says the agent's shell may have no terminal, tells it to always pass `--yes`, and says that without `--yes` the installer stops before writing only when there is no terminal (and asks on one when there is), keeping the exit-code-2 clause for a missing answer. `guide/install.md`, "Answering without a terminal", now reads "(CI; an agent's shell may have none)"; its existing sentence already limits the stop to "without a terminal and without `--yes`". Delivers TASK-INST-03 (DEC-INST-03, option (a), as widened on 2026-11-26).
- Why: neither file may state as fact what was checked in only one agent.
- Decided by: the delivering agent, within TASK-INST-03's criteria.
- Recorded in: the two files.

### 2026-11-26 — TASK-INST-02: the Python version comment

- Decision: the comment at `init.py`'s version check now says Python 3.7 and later get the sentence, and that 3.6 and older stop earlier with a syntax error on the `__future__` import (accepted; it points to the decision log rather than naming the closed DEC, so the checker does not flag a "decided" seam). The check itself is unchanged. Delivers TASK-INST-02 (DEC-INST-02, option (b)).
- Why: the old comment promised a sentence to every old interpreter.
- Decided by: the delivering agent, within TASK-INST-02's criteria.
- Recorded in: `init.py`.

### 2026-11-26 — TASK-DLV-02: crossing out at capture

- Decision: `template/playbooks/deliver.md`, step 10 (Capture), gains a "Replaced criteria" bullet before "Status": when the ticket lists `replaces:`, each named criterion becomes `- AC<n>: (removed YYYY-MM-DD, replaced by <ID>)` in its done ticket within the same change request (today's date, this ticket's ID, only that line changes), stated as the one edit a done ticket allows and the one exception to asking before editing criteria, since the person approved it when `replaces:` was written. It names `backlog_check.py`'s existing check; `gate pr`'s check is US-DLV-41's and is not described before it exists. Delivers TASK-DLV-02 (DEC-DEF-04).
- Why: the plan review asked for the exception to be explicit and the edit to be exact.
- Decided by: the delivering agent, within TASK-DLV-02's criterion.
- Recorded in: the playbook; this repository's installed copy refreshed through `init.py update`.

### 2026-11-26 — TASK-DEF-04: replaces in the playbook and README

- Decision: `template/playbooks/define.md` gains a Checkpoints bullet "Contradicting a done criterion" (warn, show the criterion, list it under `replaces:` on a yes; without the yes, a DEC), and each of its three "never rewritten" places (Applying a decision, Checkpoints, `change` step 4) names the one allowed edit, crossing out as `- AC<n>: (removed YYYY-MM-DD, replaced by <ID>)` when the replacing ticket is delivered. `template/backlog/README.md` documents `replaces:` in its frontmatter example and field list next to `fixes:`, and its "never rewritten" rule names the same edit. Delivers TASK-DEF-04 (DEC-DEF-04).
- Why: one wording of the cross-out everywhere, matching the checker's message (US-DEF-33).
- Decided by: the delivering agent, within TASK-DEF-04's criteria.
- Recorded in: the two files; this repository's installed copies refreshed through `init.py update`.
- Gap filed: the guides (`guide/define.md`, `guide/why.md`) still say done tickets are never rewritten: DEC-DEF-07.

### 2026-11-26 — TASK-DEF-03: Done wording follows --gaps

- Decision: the "Done" paragraph of `template/playbooks/define.md` and `guide/define.md`, "Done means no gaps", now list unconfirmed `(observed in code)` requirements and draft stories and tasks as gaps, and define coverage as "not superseded and not in a deferred epic … cited by a story or task that is not deferred", as `--gaps` checks (the deferred-epic exception confirmed in `uncovered()`). The "refined" item was left as it is: changing it to ready or in-progress tickets is beyond the criteria, so it is filed as DEC-DEF-06. Delivers TASK-DEF-03 (DEC-DEF-03, option (a), as widened on 2026-11-26).
- Why: the plan review held the refined change outside DEF-R44.
- Decided by: the delivering agent, within TASK-DEF-03's criteria; DEC-DEF-06 is for a person.
- Recorded in: the two files; this repository's installed `playbooks/define.md` refreshed through `init.py update`.

### 2026-11-26 — TASK-DEF-02: readiness wording

- Decision: both "Readiness" texts now begin "A ticket other than an epic …" (`template/backlog/README.md`, `guide/concepts.md`), with no added rationale, the smallest wording that meets DEF-R43. Delivers TASK-DEF-02 (DEC-DEF-02, option (b), as widened on 2026-11-26).
- Why: the plan review advised against adding a reason neither the criterion nor the requirement asks for.
- Decided by: the delivering agent, within TASK-DEF-02's criteria.
- Recorded in: the two files; this repository's installed `backlog/README.md` refreshed through `init.py update`.

### 2026-11-26 — US-DEF-33: how backlog_check reads replaces

- Decision: `backlog_check.py` checks each `replaces:` entry in order: its form (a `<ticket>/AC<n>` reference), then that the criterion exists (a `(removed …)` placeholder exists, so it is no broken reference), then that its ticket is `done` (also for a placeholder, since the field only ever names done tickets), and, only once the replacing ticket is `done`, that the criterion is crossed out. Messages: "replaces `<entry>` is not a criterion reference", "… names a criterion that does not exist", "… names a criterion of a `<status>` ticket: only criteria of done tickets are replaced", and "replaces `<entry>`, which is still live: cross it out as `- AC<n>: (removed YYYY-MM-DD, replaced by <ID>)`"; a value that is not a list gets the existing "`replaces` is a list" message only. Delivers US-DEF-33 (DEF-R45, DEC-DEF-04).
- Why: the order gives one precise message per entry; the done-only rule keeps an open replacing ticket from failing while the old behavior is still the code's.
- Decided by: the delivering agent, within US-DEF-33's criteria; not a person's choice beyond DEC-DEF-04.
- Recorded in: `template/scripts/backlog_check.py` (`_replaces`), `tests/test_def_replaces.py`.
- Gap filed: `deliver.py context` does not list `replaces:` targets among related tickets (noted on US-DLV-41). Review suggestion noted, not taken: a no-op line keeping two imports used in `tests/test_def_replaces.py`.

### 2026-11-26 — The adopt fix tickets are refined and ready

- Decision: The 24 tickets of the adopt fixes are refined after two fresh-context reviews and set to `ready` with `refined: 2026-11-26`. The owner approved eight precision fixes: US-DEF-33 names the replacing ticket as the one that must be `done` and treats a `replaces:` entry naming a removed criterion as valid; US-DLV-41/AC1 states the exact `PASS pr: <ID>` output and that `<ID>` is the delivered ticket's; US-DLV-38 gains a criterion that the verdict follows `--head` for a ticket present at only one revision; TASK-INST-03 splits its criteria so each claim stands alone; US-GRD-11 names the shells and command substitution; US-GRD-15 notes that US-GRD-06/AC5's "branches" is GitLab's `/repository/branches` and gains a criterion that every spelling of the listed addresses counts; US-GRD-16, US-DLV-39, and US-DLV-40 wait on US-DEF-33 (`blocked_by`) so the `replaces:` field exists first.
- Why: Two independent reviews found criteria that a reviewer could read two ways or that left a case open; each fix makes the criterion observable, and the blocker order keeps the tickets that replace criteria from being delivered before the checker accepts `replaces:`.
- Decided by: Ianick Noejovich.
- Recorded in: the tickets.

### 2026-11-26 — A new definition retires a done ticket's criterion through replaces

- Decision: When a new definition contradicts a criterion of a `done` ticket (adopted or not), `/define` warns the person and shows the affected criterion; on a yes, the new ticket records it in a `replaces: [<ticket>/AC<n>]` frontmatter list (like `fixes:`); when that new ticket is delivered, the replaced criterion becomes `- AC<n>: (removed YYYY-MM-DD, replaced by <ticket>)` in the done ticket (the one allowed edit of a done ticket), and the checker refuses a done ticket whose `replaces:` criteria are still live. Until `backlog_check.py` accepts the field, the tickets that replace criteria list them in their Notes ("Replaces (to become a `replaces:` field once US-DEF-33 is delivered)"): US-DLV-39 (US-DLV-21/AC1, AC3, AC4), US-DLV-40 (US-DLV-04/AC2, AC3, AC4), and US-GRD-16 (US-GRD-08/AC3, US-GRD-09/AC6). Closes DEC-DEF-04.
- Why: A done ticket is never rewritten, so without this the backlog keeps two live criteria that disagree, and nothing says which one binds.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DEF-R45, DEF-R46, DLV-R51; DEC-DEF-04; US-DEF-33, TASK-DEF-04, US-DLV-41, TASK-DLV-02.

### 2026-11-26 — Review-only stories become tasks

- Decision: The three documentation-only stories become tasks with new IDs: US-DEF-31 becomes TASK-DEF-02, US-DEF-32 becomes TASK-DEF-03, and US-INST-26 becomes TASK-INST-03; the old IDs are retired, never reused. Their criteria are checkable statements, and the final review verifies them. DEC-DEF-05 asks how such criteria should be accepted from now on.
- Why: A done story needs a tagged test for every live criterion (DEF-R14), and no test can check the wording of a playbook, a guide, or an instruction file; an untestable task is confirmed by the final reviewer instead (DLV-R37).
- Decided by: Ianick Noejovich.
- Recorded in: TASK-DEF-02, TASK-DEF-03, TASK-INST-03; DEC-DEF-02, DEC-DEF-03, DEC-INST-03 (their outcomes); DEC-DEF-05 (open). The entries "Epics stay exempt from readiness", "The playbook's Done paragraph follows --gaps", and "AGENT-INSTALL.md says the shell may have no terminal" name the old IDs.

### 2026-11-26 — Refinement widens ten requirements of the adopt decisions

- Decision: Refining the tickets of the 2026-11-25 decisions, the owner made ten requirements wider or exact, each superseded by a new one: CONF-R28 (a glob is refused when it starts with `/` after surrounding whitespace is trimmed and a leading `./` is removed); DEF-R43 and DEF-R44 (`guide/concepts.md` and `guide/define.md` are fixed in the same tickets, and the Done paragraph also says draft stories and tasks are gaps); GRD-R32 (a `cd` inside a shell's `-c` script or a pipeline stage also makes the folder unknown); GRD-R33 (`git apply`, `patch`, and `git reset --hard` ask in every project, while `git apply --check`, `--stat`, `--numstat`, and `patch --dry-run` stay allowed); GRD-R34 (appending to the decision log stays free through `>>`, `tee -a`, Edit, and MultiEdit, while replacing or removing it asks, a Write call included); GRD-R35 (the branch-protection writes denied are listed, as GitHub's and GitLab's documentation confirm them on 2026-11-26); INST-R35 (`guide/install.md` drops the claim that an agent's shell has no terminal); INST-R36 (a missing lock `version`, or an `options` value that is not a table, is a broken lock, and the accepted version form is `X.Y.Z` with an optional leading `v`); INST-R37 (the line telling the person to set `host:` prints in the plan, on `--dry-run` too, and after a real run). US-GRD-14 is split: the decision-log part becomes US-GRD-16. US-HOST-13 gets an open question naming SPK-HOST-01: until it runs, empty output from a list command counts as no open change requests. It widens, and does not replace, the entries "Globs never start with a slash", "Epics stay exempt from readiness", "The playbook's Done paragraph follows --gaps", "The guard treats the folder as unknown after cd -, popd, or a subshell cd", "The guard asks before writes it cannot see", "AGENT-INSTALL.md says the shell may have no terminal", "A lock version that is not a number is a broken lock", and "Host switch on update tells the person to set kitchen.yml's host".
- Why: The ticket review found cases the 2026-11-25 wording left open (whitespace and `./` before a slash, other folder changes, which writes append and which replace, which endpoints protect a branch, other broken lock fields, the guides that repeat the same text), and each answer fails toward the stricter or clearer reading.
- Decided by: Ianick Noejovich.
- Recorded in: requirements CONF-R28, DEF-R43, DEF-R44, GRD-R32, GRD-R33, GRD-R34, GRD-R35, INST-R35, INST-R36, INST-R37; superseded CONF-R27, DEF-R41, DEF-R42, GRD-R26, GRD-R29, GRD-R30, GRD-R31, INST-R33, INST-R34, INST-R30; US-CONF-17, TASK-DEF-02, TASK-DEF-03, US-GRD-11, US-GRD-14, US-GRD-15, US-GRD-16, US-HOST-13, TASK-INST-03, US-INST-25, US-INST-27; the outcomes of DEC-CONF-02, DEC-DEF-02, DEC-DEF-03, DEC-GRD-01, DEC-GRD-04, DEC-INST-01, DEC-INST-03, DEC-INST-04.

### 2026-11-26 — New tickets leave out criteria that are already true

- Decision: A new ticket's criteria state only what changes. A criterion that restates behavior already true today (other checks unchanged, GET reads stay allowed, a full sha still builds the command) is left out, and a Notes line names the existing criterion that holds it. Draft tickets were never referenced by tests, so their criteria are renumbered from AC1. When a new ticket replaces a criterion of a done ticket, it keeps the part of that criterion that stays true, since that part would otherwise lose its criterion once the old one is crossed out.
- Why: A criterion that is already true passes before any code changes, so it proves nothing about the change and duplicates a criterion that lives in another story.
- Decided by: Ianick Noejovich.
- Recorded in: US-CONF-17, US-DEF-30, TASK-DEF-02, US-GRD-11, US-GRD-12, US-GRD-13, US-GRD-15, US-HOST-13, US-HOST-14, US-INST-25, US-INST-27.

### 2026-11-25 — The guard asks before writes it cannot see

- Decision: Option (a): `git apply`, `patch`, and `git reset --hard` ask whenever the project has protected files; deleting or truncating `docs/decision-log.md` asks while appending stays free; branch-protection API writes are denied. Closes DEC-GRD-04.
- Why: As the DEC recommended, each one is a plain command an agent might run by mistake, which is the guard's job; `git reset --hard` asking may slow some recoveries, an accepted cost.
- Decided by: Ianick Noejovich.
- Recorded in: requirements GRD-R29, GRD-R30, GRD-R31; superseded GRD-R20 (by GRD-R30); confirmed GRD-R22; US-GRD-14, US-GRD-15. It narrows "The guard does not ask before decision-log edits": appending and edits stay free.

### 2026-11-25 — The guard denies GraphQL deleteRef

- Decision: Option (a): the GraphQL `deleteRef` mutation is denied like REST ref writes; `updatePullRequestBranch` is not denied (option (b) was not chosen) and still asks. Closes DEC-GRD-03.
- Why: It brings the GraphQL path in line with the REST path and with "Guard hardening after the adversarial review" (host API calls that write refs are refused); GitHub's GraphQL reference lists `deleteRef` ("Delete a Git Ref."), https://docs.github.com/en/graphql/reference/git, checked 2026-11-25.
- Decided by: Ianick Noejovich.
- Recorded in: requirements GRD-R28; confirmed GRD-R14; US-GRD-13.

### 2026-11-25 — git config asks only for the config subcommand

- Decision: Option (a): `git config` asks only when git's subcommand, after the global options, is `config`. Closes DEC-GRD-02.
- Why: As the DEC recommended, it matches the stated rule and the guard's docstring, keeps every `git config` write asking, and removes prompts on ordinary file names.
- Decided by: Ianick Noejovich.
- Recorded in: requirements GRD-R27; confirmed GRD-R16; US-GRD-12.

### 2026-11-25 — The guard treats the folder as unknown after cd -, popd, or a subshell cd

- Decision: Option (a): after `cd -`, `popd`, or a `cd` inside a subshell or group, the guard treats the folder as unknown, so every later write in the call asks. Closes DEC-GRD-01.
- Why: As the DEC recommended, it fails toward asking, matches how the guard already treats a folder known only at run time, and is small.
- Decided by: Ianick Noejovich.
- Recorded in: requirements GRD-R26; confirmed GRD-R22; US-GRD-11.

### 2026-11-25 — The merge sha check matches the whole value

- Decision: Fix: the merge sha check matches the whole value, so a trailing newline is refused. Closes DEC-HOST-02.
- Why: As the DEC proposed, it closes a gap in the fail-closed validation of the one function that defines the allowed merge command; HOST-R14 already says only the full 40-character sha is accepted.
- Decided by: Ianick Noejovich.
- Recorded in: requirements HOST-R27; confirmed HOST-R14; US-HOST-14.

### 2026-11-25 — Unreadable host CLI output is a host error

- Decision: Fix: host CLI output that is not JSON, when listing the branches of open change requests or reading a change request, is a HostError naming the command. Closes DEC-HOST-01.
- Why: As the DEC proposed, an unreadable answer is treated like a failing CLI, so `next` stops with its own message and `status` uses its offline fallback instead of a traceback.
- Decided by: Ianick Noejovich.
- Recorded in: requirements HOST-R26; confirmed HOST-R04, HOST-R06; US-HOST-13. HOST-R05 stays marked as observed in code until SPK-HOST-01 runs.

### 2026-11-25 — pr-body prints the playbook's Ticket line per type

- Decision: Option (b): `deliver.py pr-body` prints the playbook's wording per type (`None. Spike <ID>: …` for a spike, `None. Decides <ID> …` for a decision) and refuses an epic. Closes DEC-DLV-03.
- Why: As the DEC recommended, the script is where facts come from, so its skeleton should already say what the playbook asks for, and refusing an epic matches "an epic is not delivered".
- Decided by: Ianick Noejovich.
- Recorded in: requirements DLV-R50; superseded DLV-R06 (by DLV-R50); confirmed DLV-R37; US-DLV-40.

### 2026-11-25 — Release notes leave out adopted tickets

- Decision: Option (b): release notes leave adopted tickets out on every path. Closes DEC-DLV-02.
- Why: As the DEC recommended, adopted tickets record behavior that shipped before the backlog existed, so listing them as a release's changes misleads, and the tag and no-tag paths then agree.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DLV-R49; superseded DLV-R27 (by DLV-R49); US-DLV-39.

### 2026-11-25 — gate pr reads tickets and kitchen.yml at --head

- Decision: Option (b): `deliver.py gate pr` reads the ticket files and `kitchen.yml` at `--head` too, so it judges exactly the revision it names. Closes DEC-DLV-01.
- Why: The gate then judges one revision consistently even when CI checks out another commit than the one it names.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DLV-R48; confirmed DLV-R14, DLV-R16, DLV-R20; US-DLV-38.

### 2026-11-25 — The playbook's Done paragraph follows --gaps

- Decision: Option (a): the "Done" paragraph of `playbooks/define.md` is reworded to match `--gaps`: it adds unconfirmed observed requirements and says "cited by a story or task that is not deferred". Closes DEC-DEF-03.
- Why: As the DEC recommended, the script's rule is tested and drafts already show as their own gap, so only the text was out of step.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DEF-R42; confirmed DEF-R03, DEF-R18, DEF-R39; US-DEF-32.

### 2026-11-25 — Epics stay exempt from readiness

- Decision: Option (b): epics stay exempt from the readiness rules, and `backlog/README.md`, "Readiness", says that it applies to tickets other than epics. Closes DEC-DEF-02.
- Why: As the DEC recommended, it matches the recorded choice that epics need only their fields ("Script choices made while building v0.1"), and requiring owners could fail installed projects whose epics use `TBD`.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DEF-R41; confirmed DEF-R09; US-DEF-31.

### 2026-11-25 — The strict summary counts uncovered requirements

- Decision: Option (a): the `backlog_check.py` summary counts uncovered requirements, as errors with `--strict` and as warnings without it; exit codes are unchanged. Closes DEC-DEF-01.
- Why: As the DEC recommended, a summary that disagrees with the lines under it misleads people and CI logs, and no exit code changes.
- Decided by: Ianick Noejovich.
- Recorded in: requirements DEF-R40; confirmed DEF-R17, DEF-R18; US-DEF-30.

### 2026-11-25 — Globs never start with a slash

- Decision: Option (a): a glob with a leading `/` is rejected with a message like the backslash one. Closes DEC-CONF-02.
- Why: As the DEC recommended, it keeps one meaning per pattern, and the reason backslashes are rejected (they would silently match nothing) applies equally.
- Decided by: Ianick Noejovich.
- Recorded in: requirements CONF-R27; confirmed CONF-R11, CONF-R12; US-CONF-17.

### 2026-11-25 — A kitchen.yml that is not UTF-8 is a configuration error

- Decision: Option (a): a `kitchen.yml` that is not valid UTF-8 is the configuration error `kitchen.yml: not valid UTF-8`, with no traceback. Closes DEC-CONF-01.
- Why: As the DEC recommended, it matches CONF-R05 and the configuration guide's promise of one clear message per invalid value.
- Decided by: Ianick Noejovich.
- Recorded in: requirements CONF-R26; confirmed CONF-R01, CONF-R05; US-CONF-16.

### 2026-11-25 — A lock version that is not a number is a broken lock

- Decision: Option (a): a `kitchen.lock` whose `version` is not a dotted number gives the same `error: kitchen.lock … Restore it from git history.` failure (exit 1) as other broken locks. Closes DEC-INST-04.
- Why: As the DEC recommended, one check makes every lock problem read the same way.
- Decided by: Ianick Noejovich.
- Recorded in: requirements INST-R34; superseded INST-R27 (by INST-R34); confirmed INST-R17; US-INST-27.

### 2026-11-25 — AGENT-INSTALL.md says the shell may have no terminal

- Decision: Option (a): `AGENT-INSTALL.md` is reworded to "Your shell may have no terminal …; always pass `--yes`". Closes DEC-INST-03.
- Why: As the DEC recommended, it keeps the instruction to always pass `--yes` and drops a claim nobody has checked across agents.
- Decided by: Ianick Noejovich.
- Recorded in: requirements INST-R33; confirmed INST-R07, INST-R29; US-INST-26.

### 2026-11-25 — Python 3.6 and older may fail with a syntax error

- Decision: Option (b): Python 3.6 and older getting a syntax error before the version check is accepted, and the code comment in `init.py` is corrected to say that Python 3.7 and later get the sentence. Closes DEC-INST-02.
- Why: As the DEC recommended, Python 3.6 is long out of support, and keeping it parseable would need a style exception in `init.py`.
- Decided by: Ianick Noejovich.
- Recorded in: requirements INST-R32; confirmed INST-R03; TASK-INST-02. INST-R03 also lost its reference to this DEC (a wording fix).

### 2026-11-25 — Host switch on update tells the person to set kitchen.yml's host

- Decision: Option (a): `kitchen.yml` stays untouched; an `update --host <new host>` that changes the host prints that `host:` in `kitchen.yml` must be set to the new host, and `doctor`'s host-mismatch fix offers both directions (set `host:` in `kitchen.yml` to the installed host, or run `update --host <other host>`). Closes DEC-INST-01.
- Why: As the DEC recommended, it keeps the recorded rule that `update` never edits the project's configuration ("Installer choices made while building v0.1") and stops `doctor` from pointing the person back to the host they just left.
- Decided by: Ianick Noejovich.
- Recorded in: requirements INST-R30, INST-R31; confirmed INST-R20, INST-R25; US-INST-25.

### 2026-11-25 — Adopt progress: all six epics written

- Decision: the six epics are adopted and written: `INST` (29 requirements, 24 stories), `CONF` (25, 15 stories and 2 tasks), `DEF` (39, 29 stories), `DLV` (47, 37 stories), `HOST` (25, 12 stories), `GRD` (25, 10 stories); every story and adopted task is `done` with `adopted: true`; each epic has one draft "Pay test debt" task. Each epic's checkpoint was approved as shown. 18 DECs ask "Is this intended?" about behavior found while reading the code (DEC-GRD-03's GraphQL claim was checked in GitHub's GraphQL reference; DEC-GRD-04 collects the writes the guard does not see), and SPK-HOST-01 verifies the GitLab adapter on a real GitLab project.
- Why: adopt mode, step 2 of `playbooks/define.md`.
- Decided by: Ianick Noejovich (each epic's checkpoint).
- Recorded in: `docs/requirements/*.md`; `backlog/*/`.
- Not done yet (for the next session): step 4, confirming the 190 `(observed in code)` requirements (the person chose to do it after all epics were written); the 18 DECs and SPK-HOST-01; the six test-debt tasks (636 criteria on `--test-debt`, about 150 of them review-only).

### 2026-11-25 — Adopt: test debt and review-only behavior

- Decision: Test Kitchen's adopted criteria are recorded as test debt, with one draft task per epic ("Pay test debt: tagged tests for EP-<CODE>") that adds tagged tests in new test files without the no-trace marker. Behavior only a review can check (playbooks, docs, agent instructions) stays in adopted stories, and its criteria stay on the test-debt list, read as "review only".
- Why: this repository's test files carry `test-kitchen: no-trace` because they hold example tickets, so tags there can never prove a criterion; paying the debt in separate files needs no framework change. Keeping review-only behavior in stories keeps its requirements covered without stretching what a task is.
- Decided by: Ianick Noejovich.
- Recorded in: the epics' test-debt tasks; `backlog_check.py --test-debt`.

### 2026-11-25 — Adopt: product, epics, and owner

- Decision: `docs/product.md` is written as confirmed (vision, three roles, six capabilities, boundaries). The existing code is split into six epics, each owning one code file: `INST` (`init.py`), `CONF` (`template/scripts/kitchen_lib.py`), `DEF` (`template/scripts/backlog_check.py`), `DLV` (`template/scripts/deliver.py`), `HOST` (`template/scripts/hosts.py`), `GRD` (`template/claude/hooks/guard.py`). Ianick Noejovich owns the epics and every adopted ticket. The six epics were drafted in parallel and de-duplicated before their checkpoints.
- Why: one epic per capability gives every code file exactly one owner, so `--gaps` reports no unclaimed code.
- Decided by: Ianick Noejovich.
- Recorded in: `docs/product.md`; `backlog/<CODE>-*/epic.md`.

### 2026-11-25 — CI runs Python 3.9 on Ubuntu 24.04

The product-test job on Python 3.9 failed before running anything: `actions/setup-python` publishes 3.9 builds only for Ubuntu 22.04 and 24.04, and `ubuntu-latest` is now 26.04. The 3.9 job pins `ubuntu-24.04`; the current-Python job stays on `ubuntu-latest`. 3.9 stays the supported minimum because it is the `python3` macOS ships. When GitHub retires the 24.04 image, the minimum has to move or 3.9 has to run another way. Recorded in `.github/workflows/ci.yml`. Decided while fixing CI on the first change request.

### 2026-11-25 — An empty project is not fully defined

Right after installing Test Kitchen on itself, `backlog_check.py --gaps` printed nothing although nothing was defined: with no requirements, coverage passed trivially, and the unmapped-code check only ran once some epic declared `code:`. `--gaps` now also lists a missing `docs/product.md`, a `docs/product.md` with only the skeleton's headings and comments, a project with no requirements, and, while no epic declares `code:`, existing code as one gap in all (one line per file once any epic declares `code:`, as before). This amends `docs/spec-v0.1.md` section 5. Decided by the project owner ("fix the hole first").

### 2026-11-25 — Test Kitchen installed on its own repository

The root now runs Test Kitchen 0.1.0, installed from the local `template/` (the bootstrap case of "Dogfooding layout"): `tests: ["tests/**"]`, `code: ["init.py", "template/scripts/**", "template/claude/hooks/**"]` (the product code that needs tests first; playbooks and docs don't), `ignore: ["examples/**", "tests/fixtures/**"]`, host github. The test command runs the stdlib unittest suite through pytest, because unittest writes no JUnit XML; pytest is a development dependency only, installed in CI's toolchain step. The CI is two workflows rather than one with two jobs: `check.yml` (the installed framework file, changed only through `init.py update`) and `ci.yml` (the product tests on Python 3.9 and a current Python). The template's decision-log header was merged into this log's introduction. Next step for the owner: `/define adopt` on this repository, after which all work goes through `/define` and `/deliver`.

### 2026-11-25 — Guard hardening after the adversarial review

A fresh-context adversarial review reproduced five ways around the guard: push/merge words built at run time (`git pu$'\x73'h`), host-API merges (`gh api …/merges -fbase=main`), glab's `accept`/`new` aliases, git aliases in another case (`git Ship`), and a guard that fails to compile letting every call through. The shell side now uses a lexer that splits commands the way bash and zsh do, decodes `$'…'`, flags anything built at run time, and reads inside `$()`, backticks, `sh -c`, `eval`, `xargs`, and `find -exec`. Choices:
- A git/gh/glab program or subcommand built at run time is refused. Unknown gh/glab top-level commands (possible aliases or extensions) are refused. Host API calls that merge, write refs, or commit to a branch are refused, sandbox mode included, as is `gh repo sync <repository>`. A git alias that pushes, merges, or runs a shell is refused; other aliases ask. `git -c`, `--config-env`, and `GIT_*` variables ask.
- The hook command is `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/guard.py" || exit 2`: a guard that can't start exits 2, which blocks the call, instead of 1, which Claude Code treats as non-blocking.
- Shell writes to protected paths are read from every redirect form and from the files writing programs name (`sed -i`, `perl -i`, `find -delete`, `curl -o`, `tar -C`, `git clean`, `dd of=`, …), resolved against the call's working folder; archive extraction, `wget`, `curl -O`, and `git clean` without a path count as writes to the current folder. Paths are compared after NFKC normalization and case folding.
- An unquoted bare `push` or `merge` word still triggers the strict checks, so `make push` or `pytest -k merge` is refused; quoting the word avoids it. Path parts (`tests/push.test.ts`) and quoted search patterns don't count. Heredoc bodies fed to `cat` are data; fed to a shell or interpreter, they are code.

### 2026-11-24 — The `test-kitchen: no-trace` marker

Test Kitchen's own tests are full of example tickets, tags, and TODOs, which the trace scans read as real references, so the repository could not install Test Kitchen on itself. A file whose first ten lines contain `test-kitchen: no-trace` is now treated as data: it is not scanned for tags, TODOs, or DEC mentions, and its tags never prove a criterion. The gates still classify it as a test or code file, so changes to it still count for the freeze and review checks. Only the first lines count, so the marker can't hide in the middle of a file. Any project whose tests handle ticket-like text can use it. Decided while installing Test Kitchen on its own repository; recorded in `template/backlog/README.md` and `guide/concepts.md`.

### 2026-11-24 — History checks see merge commits

The fresh-context review found that code written inside a merge commit (a conflict resolution after the review, or an implementation slipped in before the freeze) was invisible to `gate pr`. Now a merge commit changes a file when git's combined diff (`--cc`) shows a hunk for it; a conflict resolved by taking one side counts as no change, so a clean merge of the default branch still passes. In a merge, a skip marker counts only when its line is new against every parent. Every git call whose output is parsed runs with `core.quotePath=false`, no color, no external diff, and explicit prefixes, so user git config and unusual file names can't hide changes. Other fixes from the same review: `gate merge` also fails on backlog errors; a task whose tests carry its tags needs a freeze commit; "Test changes" matches whole paths or file names, not substrings; `status` leaves claimed tickets out of READY; `gate pr` falls back to the local default branch when `origin/<default>` is missing; globs with backslashes are rejected; a `kitchen.lock` that isn't valid JSON is a config error (the guard then refuses pushes and merges).

### 2026-11-24 — Guard choices made while building v0.1

Made by the builder of `template/claude/hooks/guard.py`, within `docs/spec-v0.1.md` section 6:
- The project root is `CLAUDE_PROJECT_DIR`, else the git checkout the guard file sits in (never the command's working directory). Pushes and merges are refused unless they run from that checkout, so other worktrees and clones are refused.
- A merge must equal `merge_argv` word for word: no `--delete-branch`, `=` forms, or reordered options (the source project let some reach the gate). A merge through the other host's CLI is refused, and the message shows the right command.
- Every check runs before any ask is returned, and a refusal always wins, so an ask (a force push) can't hide a later refused command (a push to the default branch) in the same call. This closes a hole in the source project's hook.
- Protected paths match case-insensitively (macOS); `.claude/` and `.git/` count at any depth; the decision-log exemption wins even if `kitchen.lock` lists the file. The four framework scripts are always protected, as is every `.kitchen-new` copy of a locked file, and all of `scripts/` when the lock can't be read. `python3 scripts/x.py … > file` is not a write to the script.
- glab rules (checked against the glab docs): `mr create` with `--push`, `--fill`/`-f` (which push unless `--push=false`), or `--auto-merge` is refused; `--create-source-branch` asks; `ci view` asks; `glab api --form` is a write. The token list covers GitHub, GitLab (including `CI_JOB_TOKEN` and the `PRIVATE-TOKEN` header), and OAuth names. `touch`, `chmod`, `unlink`, and bare folder names (`rm -rf docs`) are writes. The default branch is compared without case.
- The merge gate runs with the hook's own interpreter. If the scripts, `kitchen.yml`, or `kitchen.lock` fail to load, only pushes and merges are refused; other work continues.

### 2026-11-24 — A change request with no ticket that touches code needs a review

`gate pr` used to check only the delivery record for a change request whose `## Ticket` starts `None. …`, so code could reach the default branch with no review at all. Now, when the branch's own changes touch a `code` or `tests` file, such a change request must also pass the review checks: a tally with `CRITICAL: 0`, a `Reviewed commit:` on the branch, and nothing in code or tests changed after it. It still needs no plan or freeze, because it has no criteria. Decided while fixing the fresh-context review of v0.1; recorded in `template/playbooks/deliver.md` and `template/CONTRIBUTING.md`.

### 2026-11-24 — Test Kitchen's own files are excluded from project scans

A project whose `code` or `tests` globs are broad (`**/*.py`) would otherwise scan the installed framework scripts, whose comments hold example TODOs and DEC IDs, and fail its first `check` right after install. Every file listed in `kitchen.lock` is left out of the code trace, tag scans, and gate classification. Decided while fixing the fresh-context review of v0.1.

### 2026-11-24 — Required host settings

Merges must be merge commits (the gates and records point at the freeze and reviewed commits, which squash and rebase rewrite), and on GitLab merged results pipelines must be off (the adapter reads the branch's own head pipeline and fails closed on a merged results one). Documented in `guide/hosts.md` and `template/CONTRIBUTING.md`. Decided while fixing the fresh-context review of v0.1.

### 2026-11-24 — Script choices made while building v0.1

Made by the builder of `kitchen_lib.py`, `hosts.py`, `backlog_check.py`, and `deliver.py`, within `docs/spec-v0.1.md` section 5:
- Unknown ticket fields warn, not fail. Epics need only id, type, title, owner, assignee_type, status. Stories must cite a requirement once `ready` or later; decisions may cite none. Slugs are lowercase kebab-case.
- A `done` ticket with an unfinished blocker is an error. A deferred ticket with a release must be in the last slice; a `release` while slices are off only warns. `priority` is a ticket field only, not a `kitchen.yml` key.
- TODO and DEC tracing scans test files as well as code; scans include untracked files that git does not ignore.
- Globs support `**`, `*`, `?` only (no `[...]` or `{a,b}`). Identifier tags also accept a camel-case left boundary (`TestUS_PAY_03_AC2`).
- `next` always prints a `NEXT` line first (`NEXT none: …` when nothing is ready); DECIDE includes decisions that block indirectly; REFINE lists draft stories, tasks, and spikes; IDs sort naturally.
- `gate red`: skipped tests don't count as run; a task without tags passes. Plan rows match exactly (`AC10` never counts as `AC1`). Skip/focus markers are checked in test files only.
- Hotfix: `## Gaps found` must name another existing ticket; under `supervised`, hotfixes also need the approvals.
- Records carry `- Change request: #N url`; the marker is `<!-- change-request-description -->` (`<!-- pr-description -->` is read too). `gate pr --from-record` uses the record committed on the branch for this branch's name. `--pr-body` accepts a record file and checks the text after the marker.
- GitLab: a failed job that may fail counts as skipped; a manual job is skipped if it may fail, else pending; GitLab's "still checking" merge states mean unknown; merged-results pipelines fail closed. The glab commands follow the official docs cited in `hosts.py`, but were not run (glab is not installed on the build machine).
- `merge-command` exits 0 under `pr`/`supervised` with a note on stderr, and 1 on the manual host. `status` reads local copies of origin's branches and works offline. Release notes cover done tickets only.

### 2026-11-24 — Installer choices made while building v0.1

Made by the builder of `init.py`, within `docs/spec-v0.1.md` section 8:
- `kitchen.lock` is JSON (any reader, including the guard, can read it without PyYAML): `about`, `lock_format: 1`, `version`, `source`, `options {host, no_claude, toolchain}`, `files {path: sha256}`, `side_by_side`. `kitchen.yml` is not in `files`; `update` never touches it.
- A local source is recorded as `local checkout (commit <sha>)`, never an absolute path. Run from a clone, `init.py` installs from its own `template/`; it downloads only with `--version`. The default version is the running file's `VERSION`; there is no "latest" lookup.
- `--no-claude` also skips `CLAUDE.md`. `--host` can switch hosts on update; `--no-claude` can be turned on by an update, never off.
- Without a terminal and without `--yes`, anything needing confirmation stops with exit 2 and writes nothing; a dry run never asks. Installing into a subfolder of a repository is refused; `git init` happens only after the plan is confirmed. Install exits 0 once files are written even if the doctor run after it reports failures.
- Update conflicts only when both sides changed a file; a deleted framework file is restored.
- `.tmpl` is dropped anywhere in `template/`; only known `{{key}}` tokens are replaced.
- CI toolchain fill: only npm and pip are recognized (yarn, pnpm, bun, Poetry, uv, Pipenv leave the placeholder). The Python fill installs `pyyaml` (plus `pytest` when the test command uses it). Node on GitLab installs `nodejs npm` with apt when missing (image `python:3`). The marker becomes `# TEST-KITCHEN: toolchain setup (filled by init.py: …)`.
- Doctor is read-only, fails when Claude Code's `disableAllHooks` is on, and treats globs that match nothing and a signed-out host CLI as warnings.
- Guessed test commands: pytest as `python3 -m pytest`; Go as `gotestsum … ./...` (a full run, since `go test` takes packages); JUnit 5 needs a small merge script shown in the guide.

### 2026-11-24 — Process-doc choices made while building v0.1

Made by the builder of the playbooks and CI templates, within `docs/spec-v0.1.md` sections 7 and 9:
- `/define` commits on a `docs/define-<topic>` branch through a non-ticket change request, merged according to the autonomy level. Spike and DEC change requests start `## Ticket` with `None. …`.
- A task that is only partly testable is a reason to stop and propose a split, since `gate red` needs a test per criterion.
- A hotfix skips only the questions round and the plan review; the tests review still runs.
- A bug-fix test may carry both its own tag and the broken criterion's tag.
- A person merges with a merge commit (no squash or rebase), so the freeze and reviewed commits survive on the default branch.
- Each ticket's decision-log entries are written at the capture step; a replaced entry gets a `Superseded by:` line and titles are never renamed.
- A deferred DEC has `status: deferred` and is not open; a decided DEC gets an `## Outcome` section.
- The full stop-and-ask list lives only in `playbooks/deliver.md`; `CONTRIBUTING.md` summarizes it.
- GitHub CI: push trigger `[main, master]`; GitLab CI: no duplicate pipelines, `GIT_DEPTH: "0"`, drafts detected by `CI_MERGE_REQUEST_DRAFT` or a "Draft:" title, and `--pr-body` reads the committed record because the description variable is truncated at 2700 characters. GitLab starts no pipeline when a draft is marked ready, so the playbook marks the merge request ready before the final push.

### 2026-11-24 — The guard does not ask before decision-log edits

`docs/decision-log.md` is appended to at every ticket's capture step. Protecting it like the rest of `docs/` would make every delivery ask a person and stop unattended runs. The source project kept its decision log outside the protected folders too. Every other `docs/` file stays protected. Decided while building v0.1 (raised by the process-doc builder).

### 2026-11-24 — GitHub home: iakanoe/TestKitchen

The repository lives at github.com/iakanoe/TestKitchen (public, empty when chosen); `origin` is `git@github.com:iakanoe/TestKitchen.git`. The installer clones over HTTPS (`https://github.com/iakanoe/TestKitchen.git`) so installing needs no SSH key, and the pinned one-liner is `https://raw.githubusercontent.com/iakanoe/TestKitchen/v0.1.0/init.py`. Nothing is pushed until the owner says so. Decided by the project owner.

### 2026-11-24 — Build v0.1 from the approved plan

The planning is done and v0.1 is built from `docs/spec-v0.1.md`. Nothing is pushed or published until the owner says so. Decided by the project owner.

### 2026-11-24 — `blocked_by` means "can start, can't finish"

A ticket can be `ready` while a blocker is unfinished, and `deliver.py next` still never picks it. Readiness covers what the ticket itself needs (owner, answered questions, live criteria); blockers only control picking and finishing. This differs from the source project, where `ready` also required finished blockers. Recorded in `docs/spec-v0.1.md` section 3.

### 2026-11-24 — Two tag forms for tests

Tests prove criteria by tag in the test name, either `[US-PAY-03/AC2]` or the identifier form `us_pay_03_ac2`. The identifier form exists because many languages (Python, Go, Java) report function names that cannot hold brackets. Recorded in `docs/spec-v0.1.md` section 3.

### 2026-11-24 — Scope of v0.1

In: the delivery workflow (`/deliver`), the definition workflow (`/define` with modes new, change, sweep, refine, adopt, slice, bug, hotfix, ask), task tickets, the autonomy setting, `deliver.py status`, release notes, optional release slices, optional priority, host adapters (github, gitlab, manual), the installer with update and doctor, and the agent install prompt. Later: traceability report, learning from reviews (`/define retro`), richer delivery-record data. Decided by the project owner.

### 2026-11-24 — Platform-agnostic by design

No language, framework, or platform is assumed: three required config keys (`tests`, `code`, `test_command`) plus optional ones, and JUnit XML as the one test-result format. Hosts are adapters; the neutral term is "change request". Any AI agent can run it from `AGENTS.md` and the plain-markdown playbooks; Claude Code is recommended because it was developed and tested there and is the only agent where the merge guard is enforced. Decided by the project owner.

### 2026-11-24 — Name, license, language

Name "Test Kitchen", tagline "Let the agents cook (then taste the food) AKA vibecoding for devs with trust issues"; no kitchen metaphors anywhere else. License Apache-2.0. Docs in English only. Decided by the project owner.

### 2026-11-24 — Dogfooding layout

The product lives in `template/`, with instruction files stored inertly (`AGENTS.md.tmpl`, `claude/`, `github/`, `gitlab/`) and renamed on install, so Test Kitchen can later be installed on its own repository without the two interfering. The root runs the previous release and is changed only through `init.py update`. Decided by the project owner (the safer of the two options offered).
