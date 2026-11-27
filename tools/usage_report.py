#!/usr/bin/env python3
"""Report where a Claude Code session's tokens went, for measuring this repository's delivery runs.

A developer tool for working on Test Kitchen itself, not part of the product: it is not in
`template/`, `init.py` never installs it, and it sits outside `kitchen.yml`'s `code` globs
(decision log, "A cost report for this repository's delivery runs").

Usage:

    python3 tools/usage_report.py <session.jsonl> [--json]

It reads the session's transcript and every subagent transcript next to it
(`<session>/subagents/agent-*.jsonl`, with the `.meta.json` that names each one) and prints,
per transcript and in total:

- the raw token counts (input, cache reads, 5-minute and 1-hour cache writes, output);
- effective tokens: each count weighted by the model's price multiplier relative to its own
  base input price (see PRICES), so cache reads, cache writes, and output compare on one scale;
- the share of effective tokens per group (instructions, framework docs, code and ticket
  reading, writing, gates and tests, git and host, app tools, conversation);
- the number of model calls and the peak context.

Why the numbers are estimates, and where:

- The token counts and the weights are exact for what the transcript records.
- The groups are not. A model call only reports totals, so the tool splits each call's input
  by the share each kind of content holds in the context at that point, estimating content
  sizes at four characters per token. "Claude's instructions" is the context of the first
  call minus the content counted so far: the system prompt, the tool definitions, and the
  memory files, re-read on every call. Output is charged to the first tool the call used.
- The transcript format is internal to Claude Code and "can break on any release"
  (code.claude.com, sessions page, checked 2026-11-27). A record without the fields this tool
  needs stops it with a message rather than a wrong number.

Effective tokens are in units of each model's own input token, so a run that mixes models
(a subagent on another model) adds numbers of different prices; the report lists the models.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Price multipliers relative to the model's base input price, from
# https://platform.claude.com/docs/en/about-claude/pricing ("Prompt caching" and the model
# table), checked 2026-11-27. Output is not given as a multiplier there; it is the ratio of
# the listed output and input prices. Matched by prefix, longest first.
PRICES = {
    "claude-opus-5-5": {"read": 0.05, "write_5m": 1.25, "write_1h": 2.0, "output": 5.0},
    "claude-sonnet-5-5": {"read": 0.05, "write_5m": 1.25, "write_1h": 2.0, "output": 5.0},
    "claude-opus-5": {"read": 0.1, "write_5m": 1.25, "write_1h": 2.0, "output": 5.0},
    "claude-sonnet-5": {"read": 0.1, "write_5m": 1.25, "write_1h": 2.0, "output": 5.0},
    "claude-opus-4": {"read": 0.1, "write_5m": 1.25, "write_1h": 2.0, "output": 5.0},
    "claude-sonnet-4": {"read": 0.1, "write_5m": 1.25, "write_1h": 2.0, "output": 5.0},
}
# Used for a model the table does not list; the report names such models.
DEFAULT_PRICES = {"read": 0.1, "write_5m": 1.25, "write_1h": 2.0, "output": 5.0}

INSTRUCTIONS = "Claude's instructions"
FRAMEWORK = "Reading framework docs"
READING = "Reading code, tickets & docs"
WRITING = "Writing code, tests & docs"
GATES = "Gates, checks & test runs"
GIT = "Git & host"
APP = "App and connector tools"
CONVERSATION = "Conversation & notes"
HANDOFF = "Handing work to subagents"
OTHER = "Everything else"

# The files every Test Kitchen agent reads before it works: the playbooks, the rule files,
# and the Claude Code skills and agents.
FRAMEWORK_FILES = re.compile(
    r"playbooks/|AGENTS\.md|CONTRIBUTING\.md|CLAUDE\.md|backlog/README\.md|\.claude/(skills|agents)/"
)
# A shell call that runs a gate, the backlog check, or the tests (not one that only reads
# those scripts, which is reading code).
GATE_RUN = re.compile(r"python3? (-m (unittest|pytest)|scripts/(deliver|backlog_check)\.py)")
READ_FIRST = re.compile(r"^\s*(cat|sed|grep|head|tail|less)\b")
GIT_RUN = re.compile(r"(^|[;&|]\s*)(git|gh|glab)\s")
# A shell call that writes a file from a heredoc script (`python3 - <<EOF ... write(`).
SCRIPTED_WRITE = re.compile(r"<<.*(\.write\(|\.replace\()", re.S)
SAVED_OUTPUT = re.compile(r"tool-results/([\w.-]+)")


class FormatError(Exception):
    """The transcript lacks a field this tool needs: its format may have changed."""


def prices_for(model):
    for prefix in sorted(PRICES, key=len, reverse=True):
        if model and model.startswith(prefix):
            return PRICES[prefix], True
    return DEFAULT_PRICES, False


def classify(name, tool_input):
    """The group a tool call's content belongs to, from the tool name and its input."""
    text = json.dumps(tool_input)
    if name.startswith("mcp__"):
        return APP
    if name in ("Agent", "Task", "SendMessage"):
        return HANDOFF
    if name == "SubagentHandback":
        # A subagent's final report, written by the subagent: its own words, like a reply.
        return CONVERSATION
    if name in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        return WRITING
    if name == "Bash":
        command = tool_input.get("command", "")
        if SCRIPTED_WRITE.search(command):
            return WRITING
        if GATE_RUN.search(command) and not READ_FIRST.search(command):
            return GATES
        if FRAMEWORK_FILES.search(command):
            return FRAMEWORK
        if GIT_RUN.search(command):
            return GIT
        return READING
    if name in ("Read", "Grep", "Glob"):
        return FRAMEWORK if FRAMEWORK_FILES.search(text) else READING
    if name == "Skill":
        return FRAMEWORK
    return OTHER


def tokens(text):
    return len(text) // 4


def load(path):
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as err:
        raise FormatError(f"cannot read {path}: {err.strerror}") from err
    records = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as err:
            raise FormatError(f"{path}:{number}: not a JSON line ({err.msg})") from err
    return records


def analyze(path):
    """Walk one transcript in order: content enters the context, and each model call pays
    for the context it reads, split by the share each group holds at that point."""
    events = []  # ("content", tokens, group) or ("call", usage, model, [groups of tools used])
    calls = {}
    tool_group = {}  # tool_use id -> group
    saved_group = {}  # name of a saved tool output -> group of the call that produced it
    for record in load(path):
        message = record.get("message") or {}
        content = message.get("content")
        if record.get("type") == "assistant":
            used = []
            for block in content if isinstance(content, list) else []:
                if block.get("type") == "tool_use":
                    group = classify(block.get("name", ""), block.get("input") or {})
                    saved = SAVED_OUTPUT.search(json.dumps(block.get("input") or {}))
                    if block.get("name") == "Read" and saved and saved.group(1) in saved_group:
                        # Reading back an output that was too long to show: it belongs to
                        # whatever produced it (a playbook printed by `cat` is still a playbook).
                        group = saved_group[saved.group(1)]
                    tool_group[block.get("id")] = group
                    used.append(group)
                    events.append(("content", tokens(json.dumps(block.get("input"))), group))
                elif block.get("type") == "text":
                    events.append(("content", tokens(block.get("text", "")), CONVERSATION))
            usage = message.get("usage")
            if usage is None:
                continue
            missing = [k for k in ("input_tokens", "output_tokens") if k not in usage]
            if missing:
                raise FormatError(f"{path}: usage without {', '.join(missing)}")
            key = message.get("id") or id(record)
            if key in calls:
                # One response is stored as several records with the same id and usage.
                calls[key][3].extend(used)
                continue
            call = ["call", usage, message.get("model", ""), used]
            calls[key] = call
            events.append(call)
        elif record.get("type") == "user":
            blocks = content if isinstance(content, list) else [{"type": "text", "text": content or ""}]
            for block in blocks:
                if block.get("type") == "tool_result":
                    group = tool_group.get(block.get("tool_use_id"), OTHER)
                    body = json.dumps(block.get("content"))
                    for name in SAVED_OUTPUT.findall(body):
                        saved_group.setdefault(name, group)
                    events.append(("content", tokens(body), group))
                elif block.get("type") == "text":
                    events.append(("content", tokens(block.get("text", "")), CONVERSATION))
    if not calls:
        raise FormatError(f"{path}: no model call with usage found; the transcript format may have changed")
    return summarize(events)


def summarize(events):
    raw = {"input": 0, "cache_read": 0, "cache_write_5m": 0, "cache_write_1h": 0, "output": 0}
    groups, context = {}, {}
    base, peak, steps, models, unpriced = None, 0, 0, set(), set()
    for event in events:
        if event[0] == "content":
            context[event[2]] = context.get(event[2], 0) + event[1]
            continue
        _, usage, model, used = event
        steps += 1
        models.add(model)
        price, known = prices_for(model)
        if not known:
            unpriced.add(model or "(none)")
        fresh = usage.get("input_tokens", 0)
        read = usage.get("cache_read_input_tokens", 0)
        written = usage.get("cache_creation_input_tokens", 0)
        split = usage.get("cache_creation") or {}
        write_1h = split.get("ephemeral_1h_input_tokens", 0)
        write_5m = split.get("ephemeral_5m_input_tokens", written - write_1h)
        output = usage.get("output_tokens", 0)
        raw["input"] += fresh
        raw["cache_read"] += read
        raw["cache_write_5m"] += write_5m
        raw["cache_write_1h"] += write_1h
        raw["output"] += output
        full = fresh + read + write_5m + write_1h
        peak = max(peak, full)
        if base is None:
            base = max(full - sum(context.values()), 0)
        weighted = fresh + price["read"] * read + price["write_5m"] * write_5m + price["write_1h"] * write_1h
        rate = weighted / full if full else 0.0
        groups[INSTRUCTIONS] = groups.get(INSTRUCTIONS, 0) + min(base, full) * rate
        rest = max(full - base, 0)
        counted = sum(context.values())
        if counted:
            # Content sizes are estimates, so scale them to the context the call reported.
            for group, size in context.items():
                groups[group] = groups.get(group, 0) + size * rest / counted * rate
        elif rest:
            groups[OTHER] = groups.get(OTHER, 0) + rest * rate
        charged = used[0] if used else CONVERSATION
        groups[charged] = groups.get(charged, 0) + price["output"] * output
    return {
        "steps": steps,
        "peak_context": peak,
        "models": sorted(models),
        "unpriced_models": sorted(unpriced),
        "raw": raw,
        "effective": round(sum(groups.values())),
        "groups": {k: round(v) for k, v in sorted(groups.items(), key=lambda kv: -kv[1])},
    }


def subagents(session_path):
    folder = session_path.with_suffix("") / "subagents"
    found = []
    for path in sorted(folder.glob("agent-*.jsonl")) if folder.is_dir() else []:
        meta = {}
        meta_path = path.with_name(path.stem + ".meta.json")
        if meta_path.is_file():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                meta = {}
        label = meta.get("description") or meta.get("agentType") or path.stem
        found.append((label, meta.get("agentType", ""), path))
    return found


def report(session_path):
    session_path = Path(session_path)
    main = analyze(session_path)
    subs = []
    for label, agent_type, path in subagents(session_path):
        result = analyze(path)
        result.update({"label": label, "agent_type": agent_type, "file": path.name})
        subs.append(result)
    return {
        "session": session_path.name,
        "main": main,
        "subagents": subs,
        "total_effective": main["effective"] + sum(s["effective"] for s in subs),
        "note": "Groups are estimates: each call's input is split by the estimated share of each kind of content in its context.",
    }


def share(part, whole):
    return f"{100 * part / whole:.0f}%" if whole else "-"


def render(data):
    out = []
    total = data["total_effective"]
    out.append(f"Session {data['session']}: {total:,} effective tokens in all")
    for title, part in [("Main session", data["main"])] + [
        (f"Subagent: {s['label']}" + (f" ({s['agent_type']})" if s["agent_type"] else ""), s) for s in data["subagents"]
    ]:
        out.append("")
        out.append(f"{title}: {part['effective']:,} effective ({share(part['effective'], total)} of all), "
                   f"{part['steps']} calls, peak context {part['peak_context']:,}, models {', '.join(part['models'])}")
        raw = part["raw"]
        out.append(f"  raw: input {raw['input']:,}, cache reads {raw['cache_read']:,}, "
                   f"cache writes {raw['cache_write_5m']:,} (5m) + {raw['cache_write_1h']:,} (1h), output {raw['output']:,}")
        for group, value in part["groups"].items():
            out.append(f"  {group:<30} {value:>12,}  {share(value, part['effective']):>4}")
        if part["unpriced_models"]:
            out.append(f"  not in the price table, default multipliers used: {', '.join(part['unpriced_models'])}")
    out.append("")
    out.append(data["note"])
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Report where a Claude Code session's tokens went.")
    parser.add_argument("transcript", help="the session's .jsonl file")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    args = parser.parse_args(argv)
    try:
        data = report(args.transcript)
    except FormatError as err:
        print(f"usage_report: {err}", file=sys.stderr)
        return 1
    print(json.dumps(data, indent=2) if args.json else render(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
