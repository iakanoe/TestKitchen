"""US-CONF-17: a glob that starts with `/` is refused when the configuration loads (CONF-R28).

Paths are compared relative to the repository root, so `/vendor/**` would load and then
match nothing. Each test calls the project copy's `parse_config` (the loading entry point)
with a configuration mapping. This file carries no no-trace marker, so its test names are
real tags of US-CONF-17.
"""
import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers.kitchen_project import Project  # noqa: E402

ROOTED = "globs are relative to the repository root and never start with `/`"


def base():
    return {"tests": ["tests/**"], "code": ["src/**"], "test_command": "run {files} {report}"}


class RootedGlobsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project = Project(git=False)
        path = cls.project.root / "scripts" / "kitchen_lib.py"
        name = "kitchen_lib_rooted_globs"
        spec = importlib.util.spec_from_file_location(name, path)
        cls.kl = importlib.util.module_from_spec(spec)
        sys.modules[name] = cls.kl  # its dataclasses look themselves up by module name
        spec.loader.exec_module(cls.kl)

    @classmethod
    def tearDownClass(cls):
        cls.project.close()

    def errors(self, **overrides):
        """The ConfigError lines for the base config with `overrides`, or [] when it loads."""
        data = dict(base(), **overrides)
        try:
            self.kl.parse_config(data)
        except self.kl.ConfigError as e:
            return str(e).splitlines()
        return []

    def test_us_conf_17_ac1_a_glob_starting_with_a_slash_is_one_error(self):
        for key in ("tests", "code", "ignore"):
            with self.subTest(key=key):
                lines = self.errors(**{key: ["/vendor/**"]})
                self.assertEqual(len(lines), 1, lines)
                self.assertTrue(lines[0].startswith("kitchen.yml:"), lines)
                self.assertIn(f"`{key}` {ROOTED}", lines[0])
                self.assertIn("'/vendor/**'", lines[0])

    def test_us_conf_17_ac1_every_offending_glob_is_listed_in_the_one_line(self):
        lines = self.errors(code=["/a/**", "src/**", "/b/**"])
        self.assertEqual(len(lines), 1, lines)
        self.assertIn("'/a/**'", lines[0])
        self.assertIn("'/b/**'", lines[0])
        self.assertNotIn("'src/**'", lines[0])

    def test_us_conf_17_ac1_relative_globs_still_load(self):
        """Limit: folder names, `./`, and hidden folders are not refused."""
        self.assertEqual(self.errors(code=["src/**", "./src/**", ".github/**"], ignore=["./vendor/**"]), [])

    def test_us_conf_17_ac2_whitespace_and_a_leading_dot_slash_are_removed_first(self):
        for glob in (" /vendor/**", ".//vendor/**"):
            with self.subTest(glob=glob):
                lines = self.errors(ignore=[glob])
                self.assertEqual(len(lines), 1, lines)
                self.assertIn(f"`ignore` {ROOTED}", lines[0])
                self.assertIn(repr(glob), lines[0])  # listed as written

    def test_us_conf_17_ac3_a_backslash_and_a_leading_slash_are_both_reported(self):
        lines = self.errors(tests=["a\\b", "/vendor/**"])
        self.assertEqual(len(lines), 2, lines)
        backslash = [line for line in lines if "never a backslash" in line]
        rooted = [line for line in lines if ROOTED in line]
        self.assertEqual(len(backslash), 1, lines)
        self.assertEqual(len(rooted), 1, lines)
        self.assertIn(repr("a\\b"), backslash[0])
        self.assertIn("'/vendor/**'", rooted[0])
        self.assertNotIn("'/vendor/**'", backslash[0])


if __name__ == "__main__":
    unittest.main()
