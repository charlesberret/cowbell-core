"""Seed harnesses.toml: parse, catalog --check, launch argv, and public-surface hygiene."""
import contextlib
import io
import os
import re
import sys
import tomllib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import cowbell as hm  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SEED_PATH = REPO_ROOT / "harnesses.toml"

# Fields cmd_catalog_check treats as required on every harness row.
HARNESS_REQUIRED = ("id", "kind")

_USER_ABS = re.compile(
    r"(?:^|[\s\"'=])"
    r"(?P<path>"
    r"/Users/[A-Za-z0-9._-]+(?:/|$)"
    r"|/home/[a-z][a-z0-9._-]{0,31}(?:/|$)"
    r"|[A-Za-z]:\\Users\\[^\\]+\\"
    r")",
)
_HOSTNAME = re.compile(
    r"(?i)(?:"
    r"https?://[a-z0-9][-a-z0-9.]*[a-z0-9](?::\d+)?(?:/|$)"
    r"|\b[a-z0-9][-a-z0-9.]*\.(?:local|lan|internal|corp|home)\b"
    r"|\blocalhost\b"
    r")",
)


def _walk_strings(value, out: list[str]) -> None:
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, list):
        for item in value:
            _walk_strings(item, out)
    elif isinstance(value, dict):
        for item in value.values():
            _walk_strings(item, out)


def load_seed_catalog() -> dict:
    """Parse the shipped seed the way load_catalog normalises harness rows."""
    with open(SEED_PATH, "rb") as fh:
        cat = tomllib.load(fh)
    cat.setdefault("schema", 1)
    cat.setdefault("defaults", {})
    cat.setdefault("lanes", {})
    hm.apply_ext(cat)
    for h in cat.get("harness", []):
        h.setdefault("kind", h["id"])
        h.setdefault("family", h["kind"])
        h.setdefault("egress", "vendor")
        h.setdefault("trust_tool", h["id"])
        h.setdefault("models", [])
        h.setdefault("resume", [])
        if "command" in h:
            h["command"] = os.path.expanduser(h["command"])
    return cat


class SeedCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cat = load_seed_catalog()
        cls.rows = list(cls.cat.get("harness") or [])

    def test_seed_harnesses_toml_parses(self):
        self.assertTrue(SEED_PATH.is_file())
        self.assertGreaterEqual(self.cat.get("schema", 0), 1)
        self.assertIsInstance(self.cat.get("harness"), list)
        self.assertGreater(len(self.rows), 0)
        self.assertIn("defaults", self.cat)
        self.assertIn("lanes", self.cat)

    def test_seed_harness_ids_are_unique(self):
        ids = [h["id"] for h in self.rows if h.get("id")]
        self.assertEqual(len(ids), len(set(ids)), f"duplicate ids: {ids}")

    def test_seed_harness_required_fields_on_every_row(self):
        missing = []
        for h in self.rows:
            hid = h.get("id") or "(no id)"
            for key in HARNESS_REQUIRED:
                if not h.get(key):
                    missing.append(f"{hid}: missing {key}")
        self.assertEqual(missing, [], "\n".join(missing))

    def test_seed_catalog_check_exits_zero(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = hm.cmd_catalog_check(self.cat)
        self.assertEqual(rc, 0, buf.getvalue())
        self.assertIn("ok:", buf.getvalue())

    def test_each_seed_row_builds_launch_argv_without_running(self):
        root = "/tmp/cowbell-seed-catalog"
        for h in self.rows:
            with self.subTest(harness=h.get("id")):
                spec = hm.spec_default(self.cat, h, root, f"dry-{h['id']}")
                cmd = hm.spec_command(self.cat, h, spec, root, mode="tab")
                self.assertIsInstance(cmd, list)
                self.assertGreater(len(cmd), 0, h.get("id"))
                head = cmd[0]
                if hm.is_wrapper(h):
                    self.assertTrue(os.path.isabs(head) or head == h.get("command"), head)
                else:
                    self.assertEqual(head, h["kind"])

    def test_seed_rows_have_no_user_paths_or_hostnames(self):
        offenders = []
        for h in self.rows:
            hid = h.get("id") or "(no id)"
            strings: list[str] = []
            _walk_strings(h, strings)
            blob = "\n".join(strings)
            for pat, label in ((_USER_ABS, "user-specific path"), (_HOSTNAME, "hostname")):
                if pat.search(blob):
                    offenders.append(f"{hid}: {label} in {strings!r}")
        self.assertEqual(offenders, [], "\n".join(offenders))


if __name__ == "__main__":
    unittest.main()
