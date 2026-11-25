"""Release consistency: every pinned link and version string names the version
init.py installs, and the changelog has a section for it.

Installed projects and the README point at files pinned to a release tag
(`…/TestKitchen/v0.1.0/init.py`, `…/blob/v0.1.0/guide/…`). A release that bumps
`VERSION` in init.py but forgets one link would send people to an older (or
missing) tag, so this test fails until every link is bumped together.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# A link pinned to a tag: raw file URLs and blob/tree URLs of this repository.
PINNED = re.compile(r"iakanoe/TestKitchen/(?:(?:blob|tree)/)?v(\d+\.\d+\.\d+)/")
# Shipped text: what users, agents, and installed projects read.
SHIPPED = ["README.md", "AGENT-INSTALL.md", "CHANGELOG.md", "init.py", "guide", "template", "examples"]


def version():
    m = re.search(r'^VERSION = "(\d+\.\d+\.\d+)"$', (ROOT / "init.py").read_text(encoding="utf-8"), re.M)
    assert m, "init.py has no VERSION line"
    return m.group(1)


def shipped_files():
    for name in SHIPPED:
        path = ROOT / name
        yield from (sorted(p for p in path.rglob("*") if p.is_file()) if path.is_dir() else [path])


class ReleaseConsistency(unittest.TestCase):
    def test_pinned_links_name_this_version(self):
        want = version()
        wrong = []
        for path in shipped_files():
            for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                # guide/install.md shows updating to a later release on purpose.
                if path.name == "install.md" and "update" in line:
                    continue
                wrong += [f"{path.relative_to(ROOT)}:{n}: v{v}" for v in PINNED.findall(line) if v != want]
        self.assertEqual(wrong, [], f"links pinned to a version other than v{want}")

    def test_changelog_has_this_version(self):
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertRegex(text, rf"(?m)^## {re.escape(version())}\b")


if __name__ == "__main__":
    unittest.main()
