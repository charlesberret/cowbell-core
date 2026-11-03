"""Public-surface scan: generic patterns only, unless an env file adds terms."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "public-surface-scan.sh"
FIX = Path(__file__).resolve().parent / "fixtures" / "public-surface"


def scan(root: Path, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    run_env = os.environ.copy()
    run_env.pop("PUBLIC_SURFACE_TERMS", None)
    if env:
        run_env.update(env)
    return subprocess.run(
        ["sh", str(SCRIPT), str(root)],
        capture_output=True,
        text=True,
        check=False,
        env=run_env,
    )


class PublicSurface(unittest.TestCase):
    def test_clean_fixture_exits_0(self) -> None:
        proc = scan(FIX / "clean")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("clean", proc.stdout)

    def test_dirty_fixture_exits_1_and_names_every_planted_file(self) -> None:
        proc = scan(FIX / "dirty")
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        for path in sorted((FIX / "dirty").iterdir()):
            if path.is_file():
                self.assertIn(path.name, proc.stdout, proc.stdout)

    def test_repo_scans_clean(self) -> None:
        proc = scan(ROOT)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("clean", proc.stdout)
        self.assertNotIn("public-surface-scan.sh", proc.stdout)

    def test_extra_terms_are_off_until_the_env_is_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "tree"
            root.mkdir()
            (root / "note.txt").write_text("alpha-marker\n")
            self.assertEqual(scan(root).returncode, 0)
            secret = scan(root, {"PUBLIC_SURFACE_TERMS": "alpha-marker"})
            self.assertEqual(secret.returncode, 1, secret.stdout + secret.stderr)
            self.assertIn("note.txt", secret.stdout)
            terms = Path(tmp) / "terms.txt"
            terms.write_text("# comment\n\nalpha-marker\n")
            from_file = scan(root, {"PUBLIC_SURFACE_TERMS": str(terms)})
            self.assertEqual(from_file.returncode, 1, from_file.stdout + from_file.stderr)
            self.assertIn("note.txt", from_file.stdout)
