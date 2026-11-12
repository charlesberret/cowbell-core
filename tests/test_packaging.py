"""PyPI surface. 0.3.0's sdist shipped tests/ and house paths with it."""
import io
import re
import subprocess
import sys
import tomllib
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent


class Pack(unittest.TestCase):
    def test_sdist_does_not_include_tests(self):
        data = tomllib.loads((ROOT / "pyproject.toml").read_text())
        sdist = data["tool"]["hatch"]["build"]["targets"]["sdist"]["only-include"]
        self.assertNotIn("tests", sdist)
        self.assertEqual(data["project"]["name"], "cowbell")
        self.assertEqual(data["project"]["scripts"]["cowbell"], "cowbell_boot:cli")
        self.assertEqual(
            data["tool"]["hatch"]["build"]["targets"]["wheel"]["only-include"],
            ["cowbell.py", "cowbell_boot.py"],
        )
        self.assertEqual(
            data["tool"]["hatch"]["build"]["targets"]["wheel"]["shared-data"]["harnesses.toml"],
            "share/cowbell/harnesses.toml",
        )

    def test_project_urls(self):
        data = tomllib.loads((ROOT / "pyproject.toml").read_text())
        urls = data["project"]["urls"]
        self.assertEqual(urls["Homepage"], "https://github.com/charlesberret/cowbell-core")
        self.assertIn("issues", urls["Issues"].lower())

    def test_entry_guard_before_tomllib(self):
        text = (ROOT / "cowbell.py").read_text()
        guard = text.find("cowbell needs Python 3.11 or newer")
        tomllib_import = text.find("import tomllib")
        self.assertGreater(guard, 0)
        self.assertLess(guard, tomllib_import)

    def test_trap_old_python_stub(self):
        import cowbell_boot

        buf = io.StringIO()
        with mock.patch.object(sys, "version_info", (3, 9, 6, "final", 0)), redirect_stderr(
            buf
        ):
            with self.assertRaises(SystemExit) as ctx:
                cowbell_boot.trap_old_python()
        self.assertEqual(ctx.exception.code, 2)
        line = buf.getvalue().strip()
        self.assertRegex(
            line,
            r"^cowbell needs Python 3.11 or newer \(found 3\.9\.6 at .+\)\. "
            r"Install with pipx or Homebrew python\.$",
        )

    def test_boot_entry_on_old_python_stub(self):
        """Equivalent to invoking the console script under Python 3.9."""
        env = {**dict(__import__("os").environ), "PYTHONPATH": str(ROOT)}
        code = (
            "import sys\n"
            "sys.version_info = (3, 9, 6, 'final', 0)\n"
            "import cowbell_boot\n"
            "cowbell_boot.trap_old_python()\n"
        )
        proc = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 2, msg=proc.stderr + proc.stdout)
        self.assertIn("found 3.9.6", proc.stderr)
        self.assertIn("pipx or Homebrew python", proc.stderr)

    def test_readme_first_screen(self):
        lines = (ROOT / "README.md").read_text().splitlines()
        head = "\n".join(lines[:30])
        self.assertIn("pipx install git+", head)
        self.assertIn("Python 3.11", head)
        self.assertIn("MIT", head)
        self.assertIn("LICENSE", head)

    def test_public_surface_scan_exits_zero(self):
        proc = subprocess.run(
            ["/bin/bash", str(ROOT / "scripts/public-surface-scan.sh")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            proc.returncode,
            0,
            msg=proc.stdout + proc.stderr,
        )


if __name__ == "__main__":
    unittest.main()
