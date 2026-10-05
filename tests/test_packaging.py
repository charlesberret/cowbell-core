"""PyPI surface. 0.3.0's sdist shipped tests/ and house paths with it."""
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Pack(unittest.TestCase):
    def test_sdist_does_not_include_tests(self):
        data = tomllib.loads((ROOT / "pyproject.toml").read_text())
        sdist = data["tool"]["hatch"]["build"]["targets"]["sdist"]["only-include"]
        self.assertNotIn("tests", sdist)
        self.assertEqual(data["project"]["name"], "cowbell")
        self.assertEqual(data["project"]["scripts"]["cowbell"], "cowbell:cli")
        self.assertEqual(
            data["tool"]["hatch"]["build"]["targets"]["wheel"]["only-include"],
            ["cowbell.py"],
        )
        self.assertEqual(
            data["tool"]["hatch"]["build"]["targets"]["wheel"]["shared-data"]["harnesses.toml"],
            "share/cowbell/harnesses.toml",
        )
