"""Tests for US-GRD-17 (GRD-R36): in a subagent, the guard denies what it would ask.

A call made in a subagent carries `agent_id` in the PreToolUse hook input. In Claude Code's
auto permission mode an ask from a subagent is approved by the classifier instead of the
person (SPK-DLV-02), so the guard turns every ask into a deny that hands the step back to the
main session. An `agent_id` that is absent, null, or an empty string means a main-session call
(decision log, "How the guard reads agent_id"); `agent_type` alone does not count.

The hook runs as in tests/test_guard.py: the installed guard as a subprocess fed the hook JSON,
in a throwaway project with fake host CLIs. The call lists come from tests/test_guard.py, so
every ask shape the guard has is covered here too.

Run: python3 -m unittest tests.test_guard_subagent -v
"""
import json
import subprocess
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_guard  # noqa: E402  (a module import, so the runner doesn't collect test_guard's classes twice)
from test_guard import (  # noqa: E402
    ALLOW, ASK, B, DENY, EDIT_ALLOW, EDIT_ASK, FORCE_ASK, HOME_CONFIG_ASK, REACHES_GATE, make_project, run_hook)

# The line every subagent deny ends with (the wording is logged in docs/decision-log.md,
# "The guard's hand-back line for subagent calls").
HAND_BACK = ("This call came from a subagent, where the guard can't ask the person; hand this step back to the main "
             "session, which runs it and the person is asked there.")
AGENT = "a1b2c3"
# Values that count as a subagent's id although they are not strings, are falsy, or are blank.
OTHER_IDS = [7, {}, [], False, " "]
# Hook-input extras that mean a main-session call.
MAIN_SESSION = [{}, {"agent_id": None}, {"agent_id": ""}, {"agent_type": "general-purpose"}]
SHELL_ASK = "echo x > kitchen.yml"
# Three different ask reasons in one call (a force push joined with anything else is denied by
# the push-shape rules, so it cannot be part of a multi-reason ask).
MIXED_ASK = "git config core.x y && gh repo sync && echo x > kitchen.yml"
KEYS = {"Bash": "command", "NotebookEdit": "notebook_path"}


def call(p, value, tool="Bash", extra=None, sandbox=False, env_value=None):
    """Run the guard on one call whose hook input carries `extra` (agent_id, agent_type)."""
    payload = {"tool_name": tool, "tool_input": {KEYS.get(tool, "file_path"): value}, "cwd": str(p.root)}
    payload.update(extra or {})
    if env_value is not None:
        return run_with_env(p, payload, env_value)
    return run_hook(p, value, tool, sandbox=sandbox, raw=json.dumps(payload))


def run_with_env(p, payload, env_value):
    """The guard with KITCHEN_GUARD_SANDBOX set to a value other than the opt-in's `1`."""
    env = p.env()
    env["CLAUDE_PROJECT_DIR"] = str(p.root)
    env["KITCHEN_GUARD_SANDBOX"] = env_value
    r = subprocess.run([sys.executable, str(p.root / ".claude" / "hooks" / "guard.py")], input=json.dumps(payload),
                       capture_output=True, text=True, env=env, cwd=str(p.root))
    if r.returncode or r.stderr.strip():
        return "error", f"exit {r.returncode}: {r.stderr}"
    if not r.stdout.strip():
        return "allow", ""
    o = json.loads(r.stdout)["hookSpecificOutput"]
    return o["permissionDecision"], o["permissionDecisionReason"]


class SubagentCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = make_project()
        cls.addClassCleanup(cls.p.close)

    def path(self, rel):
        return str(self.p.root / rel)

    def run_all(self, cases, tool="Bash", **kw):
        with ThreadPoolExecutor(max_workers=8) as pool:
            return list(pool.map(lambda value: call(self.p, value, tool, **kw), cases))

    def expect(self, cases, want, tool="Bash", **kw):
        for value, (got, reason) in zip(cases, self.run_all(cases, tool, **kw)):
            with self.subTest(value=value, tool=tool, extra=kw.get("extra")):
                self.assertEqual(got, want, reason)

    def edit_asks(self):
        return [self.path(rel) for rel in EDIT_ASK] + HOME_CONFIG_ASK


class DenyInSubagentTest(SubagentCase):
    def test_us_grd_17_ac1_every_shell_ask_and_force_push_is_denied(self):
        self.expect(ASK + FORCE_ASK, "deny", extra={"agent_id": AGENT})

    def test_us_grd_17_ac1_protected_edits_are_denied_with_every_edit_tool(self):
        self.expect(self.edit_asks(), "deny", tool="Write", extra={"agent_id": AGENT})
        for tool in ("Edit", "MultiEdit"):
            self.expect([self.path(r) for r in ("docs/x.md", "kitchen.yml", "scripts/extra_tool.py")], "deny",
                        tool=tool, extra={"agent_id": AGENT})
        self.expect([self.path("docs/n.ipynb")], "deny", tool="NotebookEdit", extra={"agent_id": AGENT})

    def test_us_grd_17_ac1_non_string_falsy_and_blank_ids_count(self):
        for agent_id in OTHER_IDS:
            extra = {"agent_id": agent_id}
            self.expect([SHELL_ASK, FORCE_ASK[0]], "deny", extra=extra)
            self.expect([self.path("docs/x.md")], "deny", tool="Write", extra=extra)

    def test_us_grd_17_ac1_an_alias_that_asks_is_denied(self):
        self.p.git("config", "alias.st", "status")
        self.addCleanup(self.p.git, "config", "--unset", "alias.st")
        self.assertEqual(call(self.p, "git st")[0], "ask")
        got, reason = call(self.p, "git st", extra={"agent_id": AGENT})
        self.assertEqual(got, "deny", reason)

    def test_us_grd_17_ac1_a_sandbox_value_other_than_1_is_off(self):
        got, reason = call(self.p, SHELL_ASK, extra={"agent_id": AGENT}, env_value="true")
        self.assertEqual(got, "deny", reason)


class ReasonTest(SubagentCase):
    def assert_keeps_the_ask(self, value, tool="Bash", sandbox=False):
        got, ask_reason = call(self.p, value, tool)
        self.assertEqual(got, "ask", ask_reason)
        got, reason = call(self.p, value, tool, extra={"agent_id": AGENT}, sandbox=sandbox)
        self.assertEqual(got, "deny", reason)
        self.assertTrue(reason.startswith(ask_reason), reason)
        self.assertTrue(reason.endswith(HAND_BACK), reason)
        for line in ask_reason.splitlines():
            self.assertEqual(reason.splitlines().count(line), 1, line)
        return ask_reason

    def test_us_grd_17_ac2_the_deny_keeps_every_ask_reason_in_order(self):
        self.assert_keeps_the_ask(SHELL_ASK)
        self.assertIn("listed in kitchen.lock", self.assert_keeps_the_ask(self.path("scripts/extra_tool.py"), "Edit"))
        self.assertGreaterEqual(len(self.assert_keeps_the_ask(MIXED_ASK).splitlines()), 3)

    def test_us_grd_17_ac2_a_repeated_reason_appears_once(self):
        ask_reason = self.assert_keeps_the_ask("echo x > kitchen.yml && echo y > kitchen.yml")
        self.assertEqual(len(ask_reason.splitlines()), 1)

    def test_us_grd_17_ac2_the_sandbox_force_push_deny_keeps_its_reason(self):
        self.assert_keeps_the_ask(FORCE_ASK[0], sandbox=True)

    def test_us_grd_17_ac2_every_ac1_deny_hands_the_step_back(self):
        runs = [(ASK + FORCE_ASK, "Bash"), (self.edit_asks(), "Write")]
        runs += [([self.path("docs/x.md")], tool) for tool in ("Edit", "MultiEdit")]
        runs += [([self.path("docs/n.ipynb")], "NotebookEdit")]
        for cases, tool in runs:
            for value, (got, reason) in zip(cases, self.run_all(cases, tool, extra={"agent_id": AGENT})):
                with self.subTest(value=value, tool=tool):
                    self.assertEqual(got, "deny", reason)
                    self.assertTrue(reason.endswith("\n" + HAND_BACK), reason)


class MainSessionTest(SubagentCase):
    def test_us_grd_17_ac3_calls_without_an_agent_id_still_ask(self):
        plain = self.run_all(ASK + FORCE_ASK)
        plain_edits = self.run_all(self.edit_asks(), "Write")
        for extra in MAIN_SESSION:
            self.assertEqual(self.run_all(ASK + FORCE_ASK, extra=extra), plain, extra)
            self.assertEqual(self.run_all(self.edit_asks(), "Write", extra=extra), plain_edits, extra)
        self.assertEqual({got for got, _ in plain + plain_edits}, {"ask"})

    # The boundary of AC3 against its contrast: these criteria describe behavior that must not
    # change, so the tests above already pass; this one proves the main-session forms are told
    # apart from a subagent's id, which only holds once the rule exists (gate red needs a failing
    # test per criterion; decision log, "Unchanged-behavior criteria get a boundary test").
    def test_us_grd_17_ac3_only_a_present_non_empty_agent_id_turns_an_ask_into_a_deny(self):
        for value, tool in ((SHELL_ASK, "Bash"), (FORCE_ASK[0], "Bash"), (self.path("docs/x.md"), "Write")):
            for extra in MAIN_SESSION:
                with self.subTest(value=value, extra=extra):
                    self.assertEqual(call(self.p, value, tool, extra=extra)[0], "ask")
            with self.subTest(value=value, extra="subagent"):
                self.assertEqual(call(self.p, value, tool, extra={"agent_id": AGENT})[0], "deny")


class SandboxSubagentTest(SubagentCase):
    def test_us_grd_17_ac4_sandbox_lets_asks_through_in_a_subagent(self):
        self.expect(ASK, "allow", extra={"agent_id": AGENT}, sandbox=True)
        self.expect(self.edit_asks(), "allow", tool="Write", extra={"agent_id": AGENT}, sandbox=True)
        for tool in ("Edit", "MultiEdit"):
            self.expect([self.path("docs/x.md")], "allow", tool=tool, extra={"agent_id": AGENT}, sandbox=True)
        self.expect([self.path("docs/n.ipynb")], "allow", tool="NotebookEdit", extra={"agent_id": AGENT}, sandbox=True)
        for agent_id in OTHER_IDS:
            self.expect([SHELL_ASK], "allow", extra={"agent_id": agent_id}, sandbox=True)

    def test_us_grd_17_ac4_sandbox_applies_before_the_subagent_rule(self):
        # The boundary of AC4 against its contrast: the same subagent call is denied without the
        # opt-in and let through with it.
        for value, tool in ((SHELL_ASK, "Bash"), (self.path("docs/x.md"), "Write")):
            with self.subTest(value=value):
                self.assertEqual(call(self.p, value, tool, extra={"agent_id": AGENT})[0], "deny")
                self.assertEqual(call(self.p, value, tool, extra={"agent_id": AGENT}, sandbox=True), ("allow", ""))

    def test_us_grd_17_ac5_sandbox_force_pushes_are_denied_in_a_subagent(self):
        cases = FORCE_ASK
        self.expect(cases, "deny", extra={"agent_id": AGENT}, sandbox=True)
        self.expect(cases, "deny", extra={"agent_id": 7}, sandbox=True)
        self.expect(cases, "ask", sandbox=True)


class UnchangedTest(SubagentCase):
    def test_us_grd_17_ac6_allowed_calls_stay_allowed(self):
        for sandbox in (False, True):
            self.expect(ALLOW, "allow", extra={"agent_id": AGENT}, sandbox=sandbox)
            self.expect([self.path(rel) for rel in EDIT_ALLOW], "allow", tool="Write", extra={"agent_id": AGENT},
                        sandbox=sandbox)
        got, _ = run_hook(self.p, None, raw=json.dumps(
            {"tool_name": "Read", "tool_input": {"file_path": "docs/x.md"}, "agent_id": AGENT}))
        self.assertEqual(got, "allow")

    def test_us_grd_17_ac6_denied_calls_keep_the_same_deny(self):
        cases = DENY + REACHES_GATE + [f"git push --force origin {B} && git push origin main",
                                       f"git push --force origin {B} && echo x > kitchen.yml"]
        for sandbox in (False, True):
            plain = self.run_all(cases, sandbox=sandbox)
            self.assertEqual({got for got, _ in plain}, {"deny"})
            self.assertEqual(self.run_all(cases, extra={"agent_id": AGENT}, sandbox=sandbox), plain)

    def test_us_grd_17_ac6_a_subagent_changes_only_the_asks(self):
        # The boundary of AC6 against its contrast: over allowed, asked, and denied calls, a
        # subagent's decisions are the main session's with each ask, and only each ask, a deny.
        cases = ALLOW[:10] + ASK[:10] + FORCE_ASK + DENY[:10]
        plain = [got for got, _ in self.run_all(cases)]
        self.assertEqual({"allow", "ask", "deny"}, set(plain))
        sub = [got for got, _ in self.run_all(cases, extra={"agent_id": AGENT})]
        self.assertEqual(sub, ["deny" if got == "ask" else got for got in plain])


class SubagentMergeTest(unittest.TestCase):
    """The merge fixture of tests/test_guard.py, where the real merge gate passes."""
    M = test_guard.MergeTest
    BRANCH, STORY, TESTS, TAGGED = M.BRANCH, M.STORY, M.TESTS, M.TAGGED
    setUp = M.setUp
    github = M.github
    del M

    def test_us_grd_17_ac6_a_merge_that_passes_the_gate_stays_allowed(self):
        self.github()
        command = f"gh pr merge 7 --merge --match-head-commit {self.head}"
        self.p.log_file.write_text("")
        self.assertEqual(call(self.p, command), ("allow", ""))
        self.p.log_file.write_text("")
        self.assertEqual(call(self.p, command, extra={"agent_id": AGENT}), ("allow", ""))


if __name__ == "__main__":
    unittest.main()
