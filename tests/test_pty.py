"""Menu and prompt behaviour in a real pseudo-terminal: keys, SGR mouse, Esc. Unix only."""
import fcntl
import json
import os
import pty
import select
import struct
import sys
import tempfile
import termios
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import cowbell as hm  # noqa: E402

ESC = "\x1b"
UP, DOWN = "\x1b[A", "\x1b[B"
BODY = ["", "  header", "", "  LIVE"] + [f"  {i + 1}  row{i + 1}" for i in range(3)] \
       + ["", "  RAISE"] + [f"  {i + 4}  raise{i + 4}" for i in range(2)]
ROWS = [4, 5, 6, 9, 10]  # body line of each choice; screen row = line + 1
HINTS = [("⏎", "open", "enter"), ("w", "wizard", "w"), ("esc", "close", "esc")]  # bar row 24: x 3-8, 12-19, 23-31


def mouse(code, x, y, down=True):
    return f"{ESC}[<{code};{x};{y}{'M' if down else 'm'}"


def in_pty(child, steps, rows=24, cols=80, settle=0.35, gap=0.08):
    """Run child() in a pty, type steps, return its JSON result (or 'HUNG') and the screen bytes."""
    out = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    out.close()
    pid, fd = pty.fork()
    if pid == 0:  # child
        try:
            os.environ["TERM"] = "xterm-256color"
            # a test runner may have swapped these for capture objects; the child talks to the pty
            sys.stdin = open(0, "r", closefd=False)
            sys.stdout = open(1, "w", buffering=1, closefd=False)
            sys.stderr = open(2, "w", buffering=1, closefd=False)
            res = child()
        except BaseException as e:  # noqa: BLE001 — report, never hang the parent
            res = ["error", type(e).__name__, str(e)]
        with open(out.name, "w") as fh:
            json.dump(res, fh)
        os._exit(0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    screen = b""

    def pump(t):
        nonlocal screen
        end = time.time() + t
        while time.time() < end:
            if select.select([fd], [], [], 0.02)[0]:
                try:
                    screen += os.read(fd, 65536)
                except OSError:
                    return
    pump(settle)
    for st in steps:
        try:
            os.write(fd, st.encode())
        except OSError:
            break
        pump(gap)
    for _ in range(40):
        if os.waitpid(pid, os.WNOHANG)[0]:
            break
        pump(0.05)
    else:
        os.kill(pid, 9)
        os.waitpid(pid, 0)
        return "HUNG", screen
    os.close(fd)
    res = json.loads(Path(out.name).read_text() or "null")
    os.unlink(out.name)
    return res, screen


def run_menu(steps, rows=ROWS):
    return in_pty(lambda: list(hm.menu(BODY, rows, HINTS, hotkeys="w")), steps)


def run_ask(steps):
    def child():
        try:
            return ["ok", hm.ask("  name [d]: ", "d")]
        except KeyboardInterrupt:
            return ["cancelled"]
    return in_pty(child, steps)


@unittest.skipUnless(hasattr(os, "fork") and sys.platform != "win32", "needs a unix pty")
class Menu(unittest.TestCase):
    cases = [
        ("arrows then enter", [DOWN, DOWN, "\r"], ["pick", 2]),
        ("up at the top stays", [UP, "\r"], ["pick", 0]),
        ("esc cancels", [ESC], ["cancel"]),
        ("q cancels", ["q"], ["cancel"]),
        ("a digit picks when unambiguous", ["4"], ["pick", 3]),
        ("hotkey", ["w"], ["key", "w", 0]),
        ("arrows then hotkey keep the selection", [DOWN, DOWN, "w"], ["key", "w", 2]),
        ("click selects only", [mouse(0, 8, 11), mouse(0, 8, 11, False), ESC], ["cancel"]),
        ("click then enter", [mouse(0, 8, 11), mouse(0, 8, 11, False), "\r"], ["pick", 4]),
        ("a press alone selects", [mouse(0, 8, 6), "\r"], ["pick", 1]),
        ("hover does nothing", [mouse(35, 8, 6), "\r"], ["pick", 0]),
        ("wheel moves", [mouse(65, 8, 6), mouse(65, 8, 6), "\r"], ["pick", 2]),
        ("the enter button confirms", [mouse(0, 8, 11), mouse(0, 5, 24)], ["pick", 4]),
        ("a hint button fires on press", [mouse(0, 14, 24)], ["key", "w", 0]),
        ("the esc button closes", [mouse(0, 25, 24), mouse(0, 25, 24, False)], ["cancel"]),
        ("a lone release is ignored", [mouse(0, 14, 24, False), ESC], ["cancel"]),
    ]

    def test_cases(self):
        for label, steps, want in self.cases:
            with self.subTest(label):
                res, screen = run_menu(steps)
                self.assertEqual(res, want)
                self.assertIn(b"?1006h", screen)   # mouse reporting was on
                self.assertIn(b"?1049l", screen)   # and the terminal was restored

    def test_empty_list_ignores_enter(self):
        res, _ = in_pty(lambda: list(hm.menu(["", "  nothing"], [], HINTS, hotkeys="w")), ["\r", ESC])
        self.assertEqual(res, ["cancel"])


@unittest.skipUnless(hasattr(os, "fork") and sys.platform != "win32", "needs a unix pty")
class Prompt(unittest.TestCase):
    def test_typing_with_backspace(self):
        self.assertEqual(run_ask(["bob", "\x7f", "x", "\r"])[0], ["ok", "box"])

    def test_empty_takes_default(self):
        self.assertEqual(run_ask(["\r"])[0], ["ok", "d"])

    def test_esc_cancels(self):
        self.assertEqual(run_ask(["ab", ESC])[0], ["cancelled"])


@unittest.skipUnless(hasattr(os, "fork") and sys.platform != "win32", "needs a unix pty")
class PickerHere(unittest.TestCase):
    """The whole picker, standalone, no herdr server: opens, moves, closes; herdr is never run."""

    def test_picker_opens_and_closes_without_herdr(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            log = base / "calls.log"
            stub = base / "herdr"
            stub.write_text(f"#!/bin/sh\necho \"$@\" >> {log}\nexit 1\n")
            stub.chmod(0o755)
            (base / "cfg").mkdir()
            (base / "cfg" / "harnesses.toml").write_text(
                'schema = 1\n[[harness]]\nid = "fake"\nkind = "pi"\ncommand = "/bin/echo"\ntitle = "stand-in"\n')
            env = {"HERDR_BIN_PATH": str(stub), "HERDR_SOCKET_PATH": str(base / "no.sock"), "COWBELL_MODE": "here",
                   "COWBELL_CONFIG_DIR": str(base / "cfg"), "COWBELL_STATE_DIR": str(base / "state")}

            def child():
                os.environ.update(env)
                for k in ("COWBELL_PLAIN", "HERDR_PLUGIN_CONTEXT_JSON", "COWBELL_CTX", "NO_COLOR"):
                    os.environ.pop(k, None)
                os.chdir(tmp)
                return hm.main(["picker"])

            res, screen = in_pty(child, [DOWN, ESC], settle=1.0, gap=0.3)
            self.assertEqual(res, 0)
            self.assertIn(b"New", screen)
            self.assertIn(b"stand-in", screen)
            self.assertFalse(log.exists(), log.read_text() if log.exists() else "")

    def _here(self, tmp):
        base = Path(tmp)
        log = base / "calls.log"
        stub = base / "herdr"
        stub.write_text(f"#!/bin/sh\necho \"$@\" >> {log}\nexit 1\n")
        stub.chmod(0o755)
        (base / "cfg").mkdir()
        (base / "cfg" / "harnesses.toml").write_text(
            'schema = 1\n[[harness]]\nid = "fake"\nkind = "pi"\ncommand = "/bin/echo"\n'
            'title = "stand-in"\n# keep-me\n')
        env = {"HERDR_BIN_PATH": str(stub), "HERDR_SOCKET_PATH": str(base / "no.sock"), "COWBELL_MODE": "here",
               "COWBELL_CONFIG_DIR": str(base / "cfg"), "COWBELL_STATE_DIR": str(base / "state")}

        def child():
            os.environ.update(env)
            for k in ("COWBELL_PLAIN", "HERDR_PLUGIN_CONTEXT_JSON", "COWBELL_CTX", "NO_COLOR"):
                os.environ.pop(k, None)
            os.chdir(tmp)
            return hm.main(["picker"])

        return child, env, log

    def test_plus_minus_edit_hotkeys(self):
        res, _ = in_pty(lambda: list(hm.menu(BODY, ROWS, HINTS, hotkeys=hm.PICKER_HOTKEYS)), ["+"])
        self.assertEqual(res, ["key", "+", 0])
        res, _ = in_pty(lambda: list(hm.menu(BODY, ROWS, HINTS, hotkeys=hm.PICKER_HOTKEYS)), ["-"])
        self.assertEqual(res, ["key", "-", 0])
        res, _ = in_pty(lambda: list(hm.menu(BODY, ROWS, HINTS, hotkeys=hm.PICKER_HOTKEYS)), ["e"])
        self.assertEqual(res, ["key", "e", 0])
        res, _ = in_pty(lambda: list(hm.menu(BODY, ROWS, HINTS, hotkeys=hm.PICKER_HOTKEYS)), ["p"])
        self.assertEqual(res, ["key", "p", 0])

    def test_callable_hints_follow_selection(self):
        def hints(sel):
            return [("⏎", "open", "enter"), ("e", "edit", "e")] if sel else \
                   [("⏎", "open", "enter"), ("esc", "close", "esc")]
        res, _ = in_pty(lambda: list(hm.menu(BODY, ROWS, hints, hotkeys="e")), [DOWN, "e"])
        self.assertEqual(res, ["key", "e", 1])

    def test_start_row_hint_click_is_plus(self):
        hints = hm.picker_hints(False, True)
        _, spans = hm.hint_bar(hints)
        plus = next(s for s in spans if s[2] == "+")
        x = (plus[0] + plus[1]) // 2
        res, _ = in_pty(lambda: list(hm.menu(BODY, ROWS, hints, hotkeys=hm.PICKER_HOTKEYS)),
                        [mouse(0, x, 24)])
        self.assertEqual(res, ["key", "+", 0])
        edit = next(s for s in spans if s[2] == "e")
        res, _ = in_pty(lambda: list(hm.menu(BODY, ROWS, hints, hotkeys=hm.PICKER_HOTKEYS)),
                        [mouse(0, (edit[0] + edit[1]) // 2, 24)])
        self.assertEqual(res, ["key", "e", 0])

    def test_pin_and_hide_keys_stay_in_picker(self):
        with tempfile.TemporaryDirectory() as tmp:
            child, env, log = self._here(tmp)
            res, screen = in_pty(child, ["p", ESC], settle=1.0, gap=0.3)
            self.assertEqual(res, 0)
            pins = json.loads((Path(env["COWBELL_STATE_DIR"]) / "pins.json").read_text())
            root = os.path.realpath(tmp)
            self.assertEqual(pins["dirs"][root]["fake"], "pin")
            self.assertIn(b"stand-in", screen)
            self.assertFalse(log.exists())

        with tempfile.TemporaryDirectory() as tmp:
            child, env, log = self._here(tmp)
            res, _ = in_pty(child, ["h", ESC], settle=1.0, gap=0.3)
            self.assertEqual(res, 0)
            pins = json.loads((Path(env["COWBELL_STATE_DIR"]) / "pins.json").read_text())
            root = os.path.realpath(tmp)
            self.assertEqual(pins["dirs"][root]["fake"], "hide")
            self.assertEqual((Path(env["COWBELL_CONFIG_DIR"]) / "harnesses.toml").read_text().count("keep-me"), 1)

    def test_edit_add_remove_esc_write_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            child, env, _ = self._here(tmp)
            catalog = Path(env["COWBELL_CONFIG_DIR"]) / "harnesses.toml"
            before = catalog.read_bytes()
            for steps in (["e", ESC, ESC], ["+", ESC, ESC], ["-", ESC, ESC], ["n", ESC, ESC]):
                with self.subTest(steps=steps[0]):
                    catalog.write_bytes(before)
                    res, _ = in_pty(child, steps, settle=1.0, gap=0.35)
                    self.assertEqual(res, 0)
                    self.assertEqual(catalog.read_bytes(), before)
                    self.assertFalse((Path(env["COWBELL_STATE_DIR"]) / "pins.json").exists())


if __name__ == "__main__":
    unittest.main()
