"""Public-surface scan: a clean tree passes, a dirty tree fails closed."""

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "public-surface-scan.sh"
FIX = Path(__file__).resolve().parent / "fixtures" / "public-surface"


def scan(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", str(SCRIPT), str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


class PublicSurface(unittest.TestCase):
    def test_clean_fixture_exits_0(self) -> None:
        proc = scan(FIX / "clean")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("clean", proc.stdout)

    def test_dirty_fixture_exits_1_and_names_every_planted_file(self) -> None:
        proc = scan(FIX / "dirty")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        dirty = FIX / "dirty"
        for path in sorted(dirty.iterdir()):
            if not path.is_file():
                continue
            if path.name == "ok-product.txt":
                self.assertNotIn(path.name, proc.stdout)
            else:
                self.assertIn(path.name, proc.stdout, proc.stdout)

    def test_repo_scan_skips_the_scanner_and_the_corpus(self) -> None:
        proc = scan(ROOT)
        self.assertIn(proc.returncode, (0, 1), proc.stderr)
        self.assertNotIn("public-surface-scan.sh", proc.stdout)
        self.assertNotIn("public-surface-allow.txt", proc.stdout)
        self.assertNotIn("fixtures/public-surface", proc.stdout)
