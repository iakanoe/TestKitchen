"""`tools/usage_report.py`: the repository's cost report for Claude Code sessions.

A developer tool, not part of the product, so these tests prove no ticket criterion and carry
no tags (decision log, "A cost report for this repository's delivery runs"). Every transcript
here is synthetic and built in a temporary folder: a real one holds a whole conversation and
is never committed.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import usage_report as ur  # noqa: E402

OPUS = "claude-opus-5-5"


def call(msg_id, model, usage, content=()):
    return {"type": "assistant", "message": {"id": msg_id, "model": model, "usage": usage, "content": list(content)}}


def tool_use(tool_id, name, tool_input):
    return {"type": "tool_use", "id": tool_id, "name": name, "input": tool_input}


def result(tool_id, text):
    return {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": tool_id, "content": text}]}}


def usage(fresh, read=0, write_5m=0, write_1h=0, output=0):
    return {
        "input_tokens": fresh,
        "cache_read_input_tokens": read,
        "cache_creation_input_tokens": write_5m + write_1h,
        "cache_creation": {"ephemeral_5m_input_tokens": write_5m, "ephemeral_1h_input_tokens": write_1h},
        "output_tokens": output,
    }


def session():
    """Three model calls on Opus 5.5: a playbook read, a test run, and a closing reply.
    The first response is stored twice, as Claude Code does when it streams one response."""
    first = call("m1", OPUS, usage(10, write_1h=1000, output=20),
                 [tool_use("t1", "Read", {"file_path": "playbooks/deliver.md"})])
    return [
        {"type": "user", "message": {"content": "go"}},
        first,
        first,
        result("t1", "x" * 4000),
        call("m2", OPUS, usage(5, read=1010, write_5m=200, output=10),
             [tool_use("t2", "Bash", {"command": "python3 -m pytest tests -q"})]),
        result("t2", "y" * 400),
        call("m3", OPUS, usage(1, read=1300, output=4), [{"type": "text", "text": "done"}]),
    ]


# Opus 5.5 multipliers: cache reads 0.05, 5-minute writes 1.25, 1-hour writes 2, output 5.
MAIN_EFFECTIVE = (10 + 2 * 1000 + 5 * 20) + (5 + 0.05 * 1010 + 1.25 * 200 + 5 * 10) + (1 + 0.05 * 1300 + 5 * 4)


class Transcripts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write(self, name, records):
        path = self.dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        return path

    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "tools" / "usage_report.py"), *args],
                              capture_output=True, text=True)


class CountingTest(Transcripts):
    def test_counts_each_response_once_and_weights_it_by_its_model(self):
        main = ur.analyze(self.write("s.jsonl", session()))
        self.assertEqual(main["steps"], 3)
        self.assertEqual(main["raw"], {"input": 16, "cache_read": 2310, "cache_write_5m": 200,
                                       "cache_write_1h": 1000, "output": 34})
        self.assertEqual(main["peak_context"], 1301)
        self.assertAlmostEqual(main["effective"], MAIN_EFFECTIVE, delta=len(main["groups"]))
        self.assertEqual(main["models"], [OPUS])
        self.assertEqual(main["unpriced_models"], [])

    def test_splits_the_context_into_groups(self):
        groups = ur.analyze(self.write("s.jsonl", session()))["groups"]
        self.assertGreater(groups[ur.INSTRUCTIONS], 0)
        self.assertGreater(groups[ur.FRAMEWORK], 0)  # the playbook read
        # The test run's output tokens (5 x 10) are charged to the gates and tests group.
        self.assertGreaterEqual(groups[ur.GATES], 50)

    def test_a_call_is_not_charged_for_what_it_writes(self):
        # The first call writes a 10k-token file; it read only its instructions, so all of
        # its input is instructions and only its output is charged to writing.
        records = [
            {"type": "user", "message": {"content": "go"}},
            call("m1", OPUS, usage(0, write_1h=1000, output=7),
                 [tool_use("t1", "Write", {"file_path": "a.py", "content": "w" * 40000})]),
        ]
        groups = ur.analyze(self.write("s.jsonl", records))["groups"]
        self.assertEqual(groups[ur.INSTRUCTIONS], 2 * 1000)
        self.assertEqual(groups[ur.WRITING], 5 * 7)

    def test_a_saved_output_read_back_keeps_the_group_that_produced_it(self):
        records = [
            call("m1", OPUS, usage(10, write_1h=500, output=5),
                 [tool_use("t1", "Bash", {"command": "cat playbooks/deliver.md"})]),
            result("t1", "Output too large. Saved to /tmp/s/tool-results/abc123.txt"),
            call("m2", OPUS, usage(5, read=510, output=5),
                 [tool_use("t2", "Read", {"file_path": "/tmp/s/tool-results/abc123.txt"})]),
            result("t2", "z" * 8000),
            call("m3", OPUS, usage(1, read=2600, output=1)),
        ]
        groups = ur.analyze(self.write("s.jsonl", records))["groups"]
        self.assertNotIn(ur.READING, groups)
        self.assertGreater(groups[ur.FRAMEWORK], groups[ur.CONVERSATION])


class SubagentTest(Transcripts):
    def test_reads_each_subagent_with_its_label_and_flags_an_unpriced_model(self):
        main_path = self.write("s.jsonl", session())
        self.write("s/subagents/agent-a1.jsonl", [call("r1", "claude-unlisted-1", usage(100, output=10))])
        (self.dir / "s/subagents/agent-a1.meta.json").write_text(
            json.dumps({"agentType": "ticket-reviewer", "description": "Plan review"}), encoding="utf-8")
        data = ur.report(main_path)
        self.assertEqual(len(data["subagents"]), 1)
        sub = data["subagents"][0]
        self.assertEqual((sub["label"], sub["agent_type"]), ("Plan review", "ticket-reviewer"))
        self.assertEqual(sub["effective"], 100 + 5 * 10)  # default multipliers
        self.assertEqual(sub["unpriced_models"], ["claude-unlisted-1"])
        self.assertEqual(data["total_effective"], data["main"]["effective"] + 150)
        text = ur.render(data)
        self.assertIn("Subagent: Plan review (ticket-reviewer)", text)
        self.assertIn("not in the price table", text)

    def test_skips_a_subagent_with_no_model_call_and_reports_the_rest(self):
        main_path = self.write("s.jsonl", session())
        self.write("s/subagents/agent-a2.jsonl", [{"type": "user", "message": {"content": "start"}}])
        data = ur.report(main_path)
        self.assertEqual(data["subagents"], [])
        self.assertEqual(data["skipped_subagents"], [{"label": "agent-a2", "file": "agent-a2.jsonl"}])
        self.assertEqual(data["total_effective"], data["main"]["effective"])
        self.assertIn("Subagent skipped, no model call", ur.render(data))


class CommandLineTest(Transcripts):
    def test_json_output_holds_the_same_report(self):
        path = self.write("s.jsonl", session())
        done = self.run_tool(str(path), "--json")
        self.assertEqual(done.returncode, 0, done.stderr)
        data = json.loads(done.stdout)
        self.assertEqual(data["main"]["steps"], 3)
        self.assertIn("estimates", data["note"])

    def test_text_output_names_the_totals_and_the_estimate(self):
        done = self.run_tool(str(self.write("s.jsonl", session())))
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("effective tokens in all", done.stdout)
        self.assertIn("Groups are estimates", done.stdout)

    def test_stops_when_a_usage_record_lacks_a_field(self):
        path = self.write("s.jsonl", [call("m1", OPUS, {"input_tokens": 3})])
        done = self.run_tool(str(path))
        self.assertEqual(done.returncode, 1)
        self.assertIn("usage without output_tokens", done.stderr)

    def test_stops_when_a_usage_record_lacks_a_cache_field(self):
        broken = usage(3, read=100, output=1)
        del broken["cache_read_input_tokens"]
        done = self.run_tool(str(self.write("s.jsonl", [call("m1", OPUS, broken)])))
        self.assertEqual(done.returncode, 1)
        self.assertIn("usage without cache_read_input_tokens", done.stderr)

    def test_stops_when_no_call_has_usage(self):
        done = self.run_tool(str(self.write("s.jsonl", [{"type": "user", "message": {"content": "hi"}}])))
        self.assertEqual(done.returncode, 1)
        self.assertIn("format may have changed", done.stderr)

    def test_stops_on_a_line_that_is_not_json(self):
        path = self.dir / "s.jsonl"
        path.write_text("{not json\n", encoding="utf-8")
        done = self.run_tool(str(path))
        self.assertEqual(done.returncode, 1)
        self.assertIn("not a JSON line", done.stderr)


class ClassifyTest(unittest.TestCase):
    def test_groups_tool_calls_by_what_they_do(self):
        cases = [
            ("Read", {"file_path": "playbooks/review.md"}, ur.FRAMEWORK),
            ("Read", {"file_path": "template/scripts/deliver.py"}, ur.READING),
            ("Bash", {"command": "sed -n 1,40p template/scripts/deliver.py"}, ur.READING),
            ("Bash", {"command": "python3 scripts/deliver.py gate red X"}, ur.GATES),
            ("Bash", {"command": "python3 - <<'EOF'\nopen(p,'w').write(s)\nEOF"}, ur.WRITING),
            ("Bash", {"command": "git push -u origin chore/x"}, ur.GIT),
            ("Edit", {"file_path": "template/scripts/deliver.py"}, ur.WRITING),
            ("Agent", {"prompt": "review"}, ur.HANDOFF),
            ("SubagentHandback", {"report": "CRITICAL: 0"}, ur.CONVERSATION),
            ("mcp__app__wrap_up", {}, ur.APP),
        ]
        for name, tool_input, expected in cases:
            with self.subTest(name=name, tool_input=tool_input):
                self.assertEqual(ur.classify(name, tool_input), expected)


if __name__ == "__main__":
    unittest.main()
