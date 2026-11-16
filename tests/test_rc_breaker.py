import sys
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cowbell as hm


class TestRcBreaker(unittest.TestCase):
    def test_long_timeout_does_not_arm_breaker(self):
        down = hm.subprocess.TimeoutExpired(cmd="herdr", timeout=35)
        with mock.patch.object(hm, "_HERDR_DOWN_UNTIL", 0.0), \
             mock.patch.object(hm.subprocess, "run", side_effect=down) as run:
            with self.assertRaises(hm.HerdrError):
                hm.herdr("agent", "start", "x", timeout=35)

            run.side_effect = None
            run.return_value = mock.Mock(
                stdout="{}", stderr="", returncode=0
            )
            hm.herdr("pane", "list")

        self.assertGreaterEqual(run.call_count, 2)

    def test_long_timeout_bypasses_armed_breaker(self):
        completed = mock.Mock(stdout="{}", stderr="", returncode=0)
        with mock.patch.object(hm, "_HERDR_DOWN_UNTIL", 0.0), \
             mock.patch.object(
                 hm.subprocess, "run", return_value=completed
             ) as run:
            with mock.patch.object(
                hm, "_HERDR_DOWN_UNTIL", time.monotonic() + 30
            ):
                hm.herdr(
                    "tab",
                    "close",
                    "t1",
                    timeout=hm.HERDR_TIMEOUT * 2,
                )

        self.assertEqual(run.call_count, 1)

    def test_default_timeout_still_arms_breaker(self):
        down = hm.subprocess.TimeoutExpired(cmd="herdr", timeout=5)
        with mock.patch.object(hm, "_HERDR_DOWN_UNTIL", 0.0), \
             mock.patch.object(hm.subprocess, "run", side_effect=down) as run:
            with self.assertRaises(hm.HerdrError):
                hm.herdr("pane", "list")
            with self.assertRaises(hm.HerdrError):
                hm.herdr("workspace", "list")

        self.assertEqual(run.call_count, 1)


if __name__ == "__main__":
    unittest.main()