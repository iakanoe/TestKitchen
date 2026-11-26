"""US-CONF-16: a `kitchen.yml` that is not UTF-8 is a configuration error (CONF-R26).

Each test builds a throwaway project (tests/helpers/kitchen_project.py), then overwrites
its `kitchen.yml` with raw bytes: a Latin-1 accent in a comment, which is not UTF-8.
This file carries no no-trace marker, so its test names are real tags of US-CONF-16.
"""
import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helpers.kitchen_project import Project, kitchen_yml  # noqa: E402

MESSAGE = "kitchen.yml: not valid UTF-8"


def load_kitchen_lib(project):
    """The project's own copy of kitchen_lib, imported under a unique name."""
    path = project.root / "scripts" / "kitchen_lib.py"
    name = f"kitchen_lib_{id(project)}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # Registered before running it: the module's dataclasses look themselves up by name.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class NotUtf8Test(unittest.TestCase):
    def project(self, raw=None):
        p = Project()
        self.addCleanup(p.close)
        if raw is not None:
            (p.root / "kitchen.yml").write_bytes(raw)
        return p

    def latin1(self):
        """A valid configuration whose first line is a comment saved as Latin-1."""
        return "# caf\xe9 settings\n".encode("latin-1") + kitchen_yml().encode("utf-8")

    def test_us_conf_16_ac1_loading_fails_with_one_configuration_error(self):
        p = self.project(self.latin1())
        kl = load_kitchen_lib(p)
        with self.assertRaises(kl.ConfigError) as caught:
            kl.load_config(p.root)
        self.assertEqual(str(caught.exception), MESSAGE)

    def test_us_conf_16_ac1_utf8_text_beyond_ascii_still_loads(self):
        """Limit: the check is about the encoding, not about non-ASCII text."""
        p = self.project("# café settings\n".encode("utf-8") + kitchen_yml().encode("utf-8"))
        kl = load_kitchen_lib(p)
        self.assertTrue(kl.load_config(p.root).tests)

    def test_us_conf_16_ac2_config_check_prints_an_error_line_and_exits_1(self):
        p = self.project(self.latin1())
        code, out = p.run("kitchen_lib.py", "--config")
        self.assertEqual(code, 1, out)
        self.assertTrue(any(line.startswith("ERROR") and MESSAGE in line for line in out.splitlines()), out)
        self.assertNotIn("Traceback", out)

    def test_us_conf_16_ac2_backlog_check_prints_an_error_line_and_exits_1(self):
        p = self.project(self.latin1())
        code, out = p.run("backlog_check.py")
        self.assertEqual(code, 1, out)
        self.assertIn(f"ERROR {MESSAGE}", out.splitlines(), out)
        self.assertNotIn("Traceback", out)


if __name__ == "__main__":
    unittest.main()
