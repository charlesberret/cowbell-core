import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cowbell as hm


class TestRcRedact(unittest.TestCase):
    def test_codex_config_dotted_instructions_value_is_masked(self):
        self.assertEqual(
            hm.redact_argv(["codex", "-c", "model.instructions=NOSHAPE1"]),
            ["codex", "-c", f"model.instructions={hm.REDACT}"],
        )

    def test_text_dotted_profile_instructions_value_is_masked(self):
        redacted = hm.redact_text("err: profile.instructions=NOSHAPE5")
        self.assertNotIn("NOSHAPE5", redacted)
        self.assertIn("profile.instructions=", redacted)

    def test_text_bare_instructions_value_is_masked(self):
        redacted = hm.redact_text("token instructions=NOSHAPE8 end")
        self.assertNotIn("NOSHAPE8", redacted)
        self.assertIn("instructions=", redacted)

    def test_long_instructions_flag_values_are_masked(self):
        self.assertEqual(
            hm.redact_argv(["agent", "--instructions", "NOSHAPE9"]),
            ["agent", "--instructions", hm.REDACT],
        )
        self.assertEqual(
            hm.redact_argv(["agent", "--instructions=NOSHAPE7"]),
            ["agent", f"--instructions={hm.REDACT}"],
        )

    def test_word_start_keywords_mask_in_free_text(self):
        redacted = hm.redact_text("err password=P1VAL token=T1VAL secret=S1VAL")
        for v in ("P1VAL", "T1VAL", "S1VAL"):
            self.assertNotIn(v, redacted)

    def test_instruction_in_prose_is_untouched(self):
        s = "no secrets here: instruction manual"
        self.assertEqual(hm.redact_text(s), s)


class TestRcRedactOverMatch(unittest.TestCase):
    """Pins intentional over-match: a NAME=value word is masked whenever NAME contains
    a keyword part anywhere, not just as a whole word. director-ruled safe-side."""

    def test_name_containing_auth_is_masked(self):
        redacted = hm.redact_text("author=NOSHAPE_A")
        self.assertNotIn("NOSHAPE_A", redacted)
        self.assertIn(hm.REDACT, redacted)

    def test_name_containing_key_is_masked(self):
        redacted = hm.redact_text("keyboard=NOSHAPE_K")
        self.assertNotIn("NOSHAPE_K", redacted)
        self.assertIn(hm.REDACT, redacted)

    def test_name_without_any_keyword_part_is_untouched(self):
        s = "slogan=NOSHAPE_Z"
        self.assertEqual(hm.redact_text(s), s)

    def test_plain_prose_is_untouched(self):
        s = "instructions and authors"
        self.assertEqual(hm.redact_text(s), s)

if __name__ == "__main__":
    unittest.main()
