"""Every user-facing subcommand answers --help with exit 0 and a cowbell usage line."""
from __future__ import annotations

import argparse
import contextlib
import difflib
import io
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = Path(__file__).resolve().parent / "snapshots"
TOP_SNAPSHOT = SNAPSHOT_DIR / "help-top.txt"
REGEN_CMD = (
    "python3 -c \"import sys; sys.path.insert(0,'.'); import cowbell as hm; "
    "import io, contextlib; o=io.StringIO(); "
    "exec('with contextlib.redirect_stdout(o): hm.main([\\\"--help\\\"])'); "
    "open('tests/snapshots/help-top.txt','w').write(o.getvalue())\""
)

sys.path.insert(0, str(ROOT))
import cowbell as hm  # noqa: E402

PLACEHOLDER_RE = re.compile(r"\bTODO\b", re.IGNORECASE)
_TOP_LEVEL_TRAP = re.compile(
    r"^\s*if\s+sys\.version_info\s*<\s*\(\s*3\s*,\s*11\s*\)",
    re.MULTILINE,
)


def build_parser() -> argparse.ArgumentParser:
    """Discover subcommands from the module's argparse tree."""
    return hm.build_parser()


def iter_subcommand_argv(parser: argparse.ArgumentParser) -> list[list[str]]:
    """Walk subparsers; yield argv prefixes for each command level (not including --help)."""
    out: list[list[str]] = []

    def walk(sub: argparse.ArgumentParser, prefix: list[str]) -> None:
        for action in sub._actions:
            if not isinstance(action, argparse._SubParsersAction):
                continue
            for name, child in action.choices.items():
                path = prefix + [name]
                out.append(path)
                if any(isinstance(a, argparse._SubParsersAction) for a in child._actions):
                    walk(child, path)

    walk(parser, [])
    return out


def usage_prefix(argv: list[str]) -> str:
    return "cowbell " + " ".join(argv)


def normalize_help(text: str) -> str:
    return text.replace("\r\n", "\n").rstrip("\n") + "\n"


class HelpEnv:
    """Isolated config/state and no live herdr calls."""

    _td: tempfile.TemporaryDirectory | None = None
    _env: dict[str, str] = {}

    @classmethod
    def setup(cls) -> None:
        if cls._td is not None:
            return
        cls._td = tempfile.TemporaryDirectory()
        base = Path(cls._td.name)
        stub = base / "herdr"
        stub.write_text("#!/bin/sh\nexit 1\n")
        stub.chmod(0o755)
        cls._env = os.environ.copy()
        cfg = base / "cfg"
        cfg.mkdir()
        os.environ["HERDR_BIN_PATH"] = str(stub)
        os.environ["HERDR_SOCKET_PATH"] = str(base / "no.sock")
        os.environ["COWBELL_CONFIG_DIR"] = str(cfg)
        os.environ["COWBELL_STATE_DIR"] = str(cfg)
        seed = ROOT / "harnesses.toml"
        if seed.is_file():
            (cfg / "catalog.toml").write_bytes(seed.read_bytes())
        cls._saved_server_up = hm.server_up
        cls._saved_tui_ok = hm.tui_ok
        hm.server_up = lambda: False  # type: ignore[method-assign]
        hm.tui_ok = lambda: False  # type: ignore[method-assign]

    @classmethod
    def teardown(cls) -> None:
        if cls._td is None:
            return
        hm.server_up = cls._saved_server_up  # type: ignore[method-assign]
        hm.tui_ok = cls._saved_tui_ok  # type: ignore[method-assign]
        cls._td.cleanup()
        cls._td = None
        os.environ.clear()
        os.environ.update(cls._env)

    @classmethod
    def run_help(cls, argv: list[str]) -> tuple[int, str]:
        cls.setup()
        out, err = io.StringIO(), io.StringIO()
        args = [*argv, "--help"]
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = hm.main(args)
        except SystemExit as exc:
            rc = exc.code if isinstance(exc.code, int) else 1
            if exc.args and not err.getvalue():
                err.write(str(exc.args[0]))
        return rc, out.getvalue() + err.getvalue()

    @classmethod
    def help_ok(cls, argv: list[str]) -> tuple[bool, str]:
        rc, text = cls.run_help(argv)
        lines = [ln for ln in text.splitlines() if ln.strip()]
        prefix = usage_prefix(argv)
        if rc != 0:
            return False, f"exit {rc}: {text[:200]}"
        if not lines:
            return False, "empty help"
        first = lines[0].strip()
        if not first.startswith(prefix):
            return False, f"first line {first!r} does not start with {prefix!r}"
        if PLACEHOLDER_RE.search(text):
            return False, "placeholder TODO in help"
        return True, text


class TopLevelHelp(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        HelpEnv.setup()

    @classmethod
    def tearDownClass(cls) -> None:
        HelpEnv.teardown()

    def test_top_level_help_matches_snapshot(self) -> None:
        rc, text = HelpEnv.run_help([])
        self.assertEqual(rc, 0)
        self.assertTrue(text.strip().startswith("cowbell"))

        got = normalize_help(text)
        if not TOP_SNAPSHOT.is_file():
            SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
            TOP_SNAPSHOT.write_text(got, encoding="utf-8")
            self.fail(
                f"missing snapshot; wrote {TOP_SNAPSHOT.relative_to(ROOT)}\n"
                f"regenerate: {REGEN_CMD}"
            )
        want = normalize_help(TOP_SNAPSHOT.read_text(encoding="utf-8"))
        if got != want:
            diff = "".join(difflib.unified_diff(
                want.splitlines(keepends=True),
                got.splitlines(keepends=True),
                fromfile=str(TOP_SNAPSHOT),
                tofile="current",
            ))
            self.fail(
                f"top-level --help differs from {TOP_SNAPSHOT.relative_to(ROOT)}\n"
                f"{diff}\nregenerate: {REGEN_CMD}"
            )
        self.assertIsNone(PLACEHOLDER_RE.search(text))


class SubcommandHelp(unittest.TestCase):
    argv: list[str] = []

    @classmethod
    def setUpClass(cls) -> None:
        HelpEnv.setup()

    @classmethod
    def tearDownClass(cls) -> None:
        HelpEnv.teardown()

    def test_help_exits_zero_with_usage_line(self) -> None:
        ok, detail = HelpEnv.help_ok(self.argv)
        self.assertTrue(ok, detail)


def _make_subcommand_test(argv: list[str]) -> type[SubcommandHelp]:
    def test_help(self: SubcommandHelp) -> None:
        ok, detail = HelpEnv.help_ok(self.argv)
        self.assertTrue(ok, detail)

    name = "Help_" + "_".join(argv)
    test_help.__doc__ = f"cowbell {' '.join(argv)} --help"
    return type(
        name,
        (SubcommandHelp,),
        {"argv": argv, "test_help_exits_zero_with_usage_line": test_help},
    )


class PythonVersionTrap(unittest.TestCase):
    def test_module_level_trap_if_present(self) -> None:
        source = (ROOT / "cowbell.py").read_text(encoding="utf-8")
        if not _TOP_LEVEL_TRAP.search(source):
            raise unittest.SkipTest("no module-level Python 3.11 trap on main")

        snippet = (
            "import sys\n"
            "sys.version_info = (3, 9, 0, 'final', 0)\n"
            f"with open({str(ROOT / 'cowbell.py')!r}) as fh:\n"
            "    src = fh.read()\n"
            "ns = {'__name__': 'cowbell', '__file__': 'cowbell.py'}\n"
            "try:\n"
            "    exec(compile(src, 'cowbell.py', 'exec'), ns)\n"
            "except SystemExit as e:\n"
            "  import sys as _s\n"
            "  _s.stderr.write(getattr(e, 'args', [''])[0] if e.args else '')\n"
            "  _s.exit(e.code if isinstance(e.code, int) else 1)\n"
        )
        proc = subprocess.run(
            [sys.executable, "-c", snippet],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(proc.returncode, 2)
        msg = proc.stderr.strip()
        self.assertEqual(len(msg.splitlines()), 1, proc.stderr)
        self.assertIn("3.11", msg)


def load_tests(loader: unittest.TestLoader, tests: unittest.TestSuite, pattern: str | None):
    HelpEnv.setup()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TopLevelHelp))
    suite.addTests(loader.loadTestsFromTestCase(PythonVersionTrap))
    for argv in iter_subcommand_argv(build_parser()):
        suite.addTest(loader.loadTestsFromTestCase(_make_subcommand_test(argv)))
    return suite


if __name__ == "__main__":
    unittest.main()
