import re
import sys
import time
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


class TestRcRedactPerf(unittest.TestCase):
    """A launcher must not hang on a long argv: redact_text must stay linear on a long
    dotted name= run, even with no keyword and no '=' anywhere near the start of it."""

    def test_long_dotted_string_redacts_in_under_a_second(self):
        s = "a." * 10000 + "=x"
        start = time.perf_counter()
        hm.redact_text(s)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 1.0, f"redact_text took {elapsed:.2f}s on a 20000-char dotted string")


# A frozen copy of the old, superlinear _NAME_VALUE pattern (cowbell.py historical,
# pre fix for the 'a.'*50000+'=x' hang). Used only to differentially check that the
# new linear masking agrees with the old regex's masking decisions.
_OLD_NAME_VALUE = re.compile(
    r"\b((?:[A-Za-z_][\w.]*)?(?:key|token|secret|pass|auth|bearer|credential|prompt|instruction)[\w.]*)=[^\s'\"]*",
    re.I,
)


def _old_redact_name_value(s: str) -> str:
    return _OLD_NAME_VALUE.sub(lambda m: f"{m[1]}={hm.REDACT}", s)


class TestRcRedactDifferential(unittest.TestCase):
    """New linear masking must agree with the old backtracking regex on a corpus of
    name=value shapes: keywords, over-match cases, dots, digits, urls, and edge cases."""

    CORPUS = [
        "instructions=NOSHAPE1",
        "api_token=NOSHAPE2",
        "author=NOSHAPE3",
        "keyboard=NOSHAPE4",
        "slogan=NOSHAPE5",
        "model.instructions=NOSHAPE6",
        "profile.instructions=NOSHAPE7",
        "a.b.c.token=NOSHAPE8",
        "a.b.c.slogan=NOSHAPE9",
        "token=NOSHAPE10",
        "secret=NOSHAPE11",
        "password=NOSHAPE12",
        "passwd=NOSHAPE13",
        "passphrase=NOSHAPE14",
        "passcode=NOSHAPE15",
        "auth=NOSHAPE16",
        "oauth=NOSHAPE17",
        "authentication=NOSHAPE18",
        "authorization=NOSHAPE19",
        "bearer=NOSHAPE20",
        "credential=NOSHAPE21",
        "credentials=NOSHAPE22",
        "prompt=NOSHAPE23",
        "system_prompt=NOSHAPE24",
        "instruction=NOSHAPE25",
        "mykeyword=NOSHAPE26",
        "1secret=NOSHAPE27",
        "1.secret=NOSHAPE28",
        "123token=NOSHAPE29",
        "123.token=NOSHAPE30",
        "url=https://user:NOSHAPE31@example.com/",
        "https://example.com/path?token=NOSHAPE32",
        "=NOSHAPE33",
        "==NOSHAPE34",
        "name=",
        "token=",
        "token=a=b",
        "slogan=foo.token=NOSHAPE35",
        "instruction manual with no equals",
        "plain prose, no secrets, no equals signs at all",
        "_token=NOSHAPE36",
        "_secret_=NOSHAPE37",
        "multi token=NOSHAPE38 slogan=NOSHAPE39 author=NOSHAPE40",
        "ſecret=NOSHAPE41",        # re.I codepoints the old [A-Za-z_] matched
        "Ktoken=NOSHAPE42",
        "9.İtoken=NOSHAPE43",
    ]

    def test_new_masking_matches_old_regex_on_corpus(self):
        for s in self.CORPUS:
            with self.subTest(s=s):
                self.assertEqual(hm._mask_name_values(s), _old_redact_name_value(s))


if __name__ == "__main__":
    unittest.main()
