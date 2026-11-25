"""A fake `gh` / `glab` for the tests: answers from a JSON rule file and logs every call.

The tests put two tiny wrappers named `gh` and `glab` first on PATH (see
tests/helpers/kitchen_project.py, `fake_bin`); each runs this file with its own name first.
Nothing here touches the network or a real account.

Environment:
    FAKE_CLI_RULES  path of a JSON list of rules: {"cli": "gh", "args": [...], "stdout": "...",
                    "stderr": "...", "exit": 0}. The first rule whose `cli` matches and whose
                    `args` are a prefix of the call's arguments answers it.
    FAKE_CLI_LOG    path of a file that gets one JSON line per call: {"cli": ..., "args": [...]}.

A call no rule answers exits 97 with a message, so a test never passes by accident.
"""
import json
import os
import sys


def main():
    name, args = sys.argv[1], sys.argv[2:]
    log = os.environ.get("FAKE_CLI_LOG")
    if log:
        with open(log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"cli": name, "args": args}) + "\n")
    rules_path = os.environ.get("FAKE_CLI_RULES")
    rules = json.load(open(rules_path, encoding="utf-8")) if rules_path and os.path.exists(rules_path) else []
    for rule in rules:
        if rule.get("cli", name) == name and args[:len(rule["args"])] == rule["args"]:
            sys.stdout.write(rule.get("stdout", ""))
            sys.stderr.write(rule.get("stderr", ""))
            return rule.get("exit", 0)
    sys.stderr.write(f"fake {name}: no rule for {args}\n")
    return 97


if __name__ == "__main__":
    sys.exit(main())
