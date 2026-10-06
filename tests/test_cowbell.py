import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import tomllib
import unittest
import warnings
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import cowbell as hm  # noqa: E402


CAT = {
    "defaults": {"lane": "yellow"},
    "lanes": {"claude": {"green": ["--permission-mode", "plan"], "yellow": ["--permission-mode", "acceptEdits"]},
              "grok": {"green": ["--permission-mode", "plan"], "yellow": ["--permission-mode", "acceptEdits"],
                       "red": ["--always-approve"]},
              "codex": {"green": ["--sandbox", "read-only"], "yellow": ["--sandbox", "workspace-write"],
                        "red": ["--dangerously-bypass-approvals-and-sandbox"]},
              "pi": {"green": ["--tools", "read"]}},
    "harness": [
        {"id": "claude", "kind": "claude", "family": "claude", "egress": "vendor", "trust_tool": "claude",
         "models": ["claude-sonnet-5", "claude-opus-5"], "model_flag": ["--model"], "resume": ["--resume"],
         "tools_allow_flag": "--allowedTools", "tools_deny_flag": "--disallowedTools",
         "seat_flag": "--append-system-prompt-file"},
        {"id": "grok", "kind": "grok", "family": "grok", "egress": "vendor", "trust_tool": "grok",
         "models": [], "model_flag": ["-m"], "resume": ["--resume"], "claim_flag": "--agent",
         "tools_allow_flag": "--allowedTools", "tools_deny_flag": "--disallowed-tools"},
        {"id": "codex", "kind": "codex", "family": "codex", "egress": "vendor", "trust_tool": "codex",
         "models": [], "resume": ["resume"]},
        {"id": "omp", "kind": "omp", "family": "omp", "egress": "vendor", "trust_tool": "omp",
         "models": [], "resume": ["--resume="]},
        {"id": "oll-mid", "kind": "pi", "family": "oll", "egress": "vendor", "trust_tool": "oll-mid",
         "models": [], "command": "/nonexistent/oll-mid", "resume": ["--continue"]},
        {"id": "oll-memo", "kind": "pi", "family": "oll", "egress": "vendor", "trust_tool": "oll-memo",
         "models": [], "command": "/nonexistent/oll-memo", "resume": ["--continue"]},
        {"id": "lobby", "kind": "pi", "family": "oll", "egress": "vendor", "trust_tool": "lobby",
         "models": [], "command": "/nonexistent/lobby", "resume": ["--continue"]},
        {"id": "local-ornith", "kind": "pi", "family": "local", "egress": "local", "trust_tool": "local-ornith",
         "models": [], "command": "/nonexistent/local-ornith", "resume": ["--continue"]},
    ],
}
ROOT = "/Users/x/code/projects/acme"


def agent(pane, kind, cwd, status="idle", title="", sid="s1"):
    return {"pane_id": pane, "agent": kind, "cwd": cwd, "agent_status": status, "tab_id": "w1:t1",
            "workspace_id": "w1", "terminal_title_stripped": title, "agent_session": {"value": sid}}


class Scope(unittest.TestCase):
    def test_at_or_beneath(self):
        self.assertTrue(hm.at_or_beneath(ROOT, ROOT))
        self.assertTrue(hm.at_or_beneath(ROOT + "/ballots", ROOT))
        self.assertFalse(hm.at_or_beneath("/Users/x", ROOT))            # above never counts
        self.assertFalse(hm.at_or_beneath(ROOT + "-core", ROOT))        # sibling with prefix
        self.assertFalse(hm.at_or_beneath("/Users/x/code/projects", ROOT))

    def test_same_tree_and_occupant(self):
        self.assertTrue(hm.same_tree(ROOT, ROOT + "/src"))
        self.assertTrue(hm.same_tree(ROOT + "/src", ROOT))
        self.assertFalse(hm.same_tree(ROOT, "/Users/x/mise"))
        row = {"name": "herdr-dev", "cwd": ROOT}
        here = agent("w1A:pD", "grok", ROOT)
        other = agent("w19:p3", "grok", "/Users/x/mise", sid="stolen")
        self.assertTrue(hm.occupant_same(row, here, "herdr-dev"))
        self.assertFalse(hm.occupant_same(row, other, "mise"))
        moved = {"name": "scholar", "cwd": ROOT + "/old"}
        self.assertTrue(hm.occupant_same(moved, agent("wM:pE", "grok", ROOT + "/new"), "scholar"))
        self.assertFalse(hm.occupant_same(moved, agent("wM:pE", "grok", ROOT + "/new"), "metawork"))

    def test_seat_file_walks_up_and_stops_at_home(self):
        # Same semantics as code/bin/lib/pi-project-seat.sh: check each dir up to and
        # including $HOME, never above it.
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            proj = home / "cloud" / "proj" / "deep"
            proj.mkdir(parents=True)
            (Path(tmp) / "SEAT.md").write_text("above home: never")
            self.assertIsNone(hm.seat_file(str(proj), home=str(home)))
            (home / "SEAT.md").write_text("home seat")
            self.assertTrue(str(hm.seat_file(str(proj), home=str(home))).endswith("home/SEAT.md"))
            (home / "cloud" / "proj" / "SEAT.md").write_text("nearer wins")
            self.assertTrue(str(hm.seat_file(str(proj), home=str(home))).endswith("proj/SEAT.md"))

    def test_slug_and_unique(self):
        self.assertEqual(hm.slug("Claude Code"), "claude-code")
        self.assertEqual(hm.slug("9lives"), "h-9lives")
        self.assertTrue(hm.NAME_RE.match(hm.slug("x" * 60)))
        self.assertEqual(hm.unique_name("a", {"a", "a-2"}), "a-3")


class Flags(unittest.TestCase):
    def test_json_flag(self):
        opts, pos = hm.parse_flags(["--json", "--place", "lobby"])
        self.assertTrue(opts.get("json"))
        self.assertEqual(opts.get("place"), "lobby")
        self.assertEqual(pos, [])


class Argv(unittest.TestCase):
    def test_claude_full(self):
        h = hm.harness_by_id(CAT, "claude")
        with tempfile.TemporaryDirectory() as tmp:
            seat = Path(tmp) / "SEAT.md"; seat.write_text("s")
            argv = hm.build_argv(CAT, h, "claude-opus-5", "green", "Read,Grep", "Bash", seat)
        self.assertEqual(argv, ["--model", "claude-opus-5", "--permission-mode", "plan",
                                "--allowedTools", "Read,Grep", "--disallowedTools", "Bash",
                                "--append-system-prompt-file", str(seat)])

    def test_resume_shapes(self):
        self.assertEqual(hm.build_argv(CAT, hm.harness_by_id(CAT, "claude"), resume_id="abc"), ["--resume", "abc"])
        self.assertEqual(hm.build_argv(CAT, hm.harness_by_id(CAT, "codex"), resume_id="abc"), ["resume", "abc"])
        self.assertEqual(hm.build_argv(CAT, hm.harness_by_id(CAT, "omp"), resume_id="abc"), ["--resume=abc"])

    def test_wrapper_ignores_lane_and_model(self):
        h = hm.harness_by_id(CAT, "oll-mid")
        self.assertEqual(hm.build_argv(CAT, h, "whatever", "red", "x", "y"), [])
        self.assertEqual(hm.build_argv(CAT, h, resume_id="any"), ["--continue"])
        self.assertEqual(hm.build_argv(CAT, h, extra=["--memo"]), ["--memo"])

    def test_unknown_lane_adds_nothing(self):
        self.assertEqual(hm.build_argv(CAT, hm.harness_by_id(CAT, "claude"), lane="red"), [])

    def test_codex_lanes(self):
        h = hm.harness_by_id(CAT, "codex")
        self.assertEqual(hm.build_argv(CAT, h, lane="green"), ["--sandbox", "read-only"])
        self.assertEqual(hm.build_argv(CAT, h, lane="yellow"), ["--sandbox", "workspace-write"])
        self.assertEqual(hm.build_argv(CAT, h, lane="red"),
                         ["--dangerously-bypass-approvals-and-sandbox"])


class Registry(unittest.TestCase):
    def setUp(self):
        self.agents = [
            agent("w1:p1", "claude", ROOT, "working", "majordomo"),
            agent("w1:p2", "grok", "/Users/x", "idle", "sysadmin"),          # above root: excluded
            agent("w1:p3", "claude", ROOT + "/ballots", "idle", "ballots"),
        ]
        self.panes = [{"pane_id": p} for p in ("w1:p1", "w1:p2", "w1:p3", "w1:p9")]
        self.roster = [
            {"name": "majordomo", "cwd": ROOT, "harness": "claude", "kind": "claude", "pane_id": "w1:p1", "model": "claude-opus-5"},
            {"name": "kimi-notes", "cwd": ROOT, "harness": "oll-mid", "kind": "pi", "pane_id": "w1:p9", "session_id": "k1"},
            {"name": "old-codex", "cwd": ROOT + "/sub", "harness": "codex", "kind": "codex", "pane_id": "gone", "session_id": "c1"},
            {"name": "elsewhere", "cwd": "/Users/x/other", "harness": "claude", "kind": "claude", "pane_id": "w1:p5"},
        ]
        self.matcher = lambda tool: {"verdict": "blocked" if tool == "local-ornith" else "ok", "flag": ""}

    def test_partition(self):
        reg = hm.build_registry(CAT, ROOT, self.agents, self.panes, self.roster, matcher=self.matcher, subject="internal")
        self.assertEqual([r["name"] for r in reg["live"]], ["majordomo", "ballots"])
        self.assertEqual(reg["live"][0]["model"], "claude-opus-5")
        self.assertTrue(reg["live"][0]["on_roster"]); self.assertFalse(reg["live"][1]["on_roster"])
        cold = {r["name"]: r for r in reg["cold"]}
        self.assertEqual(set(cold), {"kimi-notes", "old-codex"})
        self.assertEqual(cold["kimi-notes"]["status"], "unknown")   # pane exists, no detected agent
        self.assertEqual(cold["old-codex"]["status"], "cold")
        absent = {a["harness"]: a for a in reg["absent"]}
        self.assertEqual(set(absent), {"omp", "local-ornith", "grok", "lobby", "oll-memo"})
        self.assertEqual(absent["local-ornith"]["trust"]["verdict"], "blocked")
        self.assertFalse(absent["local-ornith"]["installed"])

    def test_render_mentions_sections(self):
        reg = hm.build_registry(CAT, ROOT, self.agents, self.panes, self.roster, matcher=self.matcher, subject="internal")
        text = hm.render_registry(reg, git_top="/Users/x/code/projects", wider=3)
        for needle in ("LIVE HERE", "COLD HERE", "ABSENT HERE", "majordomo", "kimi-notes", "local-ornith ⌂⊘",
                       "omp ↑ok", "[g] widen", "subject: internal"):
            self.assertIn(needle, text)
        self.assertNotIn("sysadmin", text)

    def test_live_name_prefers_tab_label(self):
        agents = [agent("w1:p1", "grok", ROOT, "idle", "- Inspect flags - Grok 4.6 - grok")]
        agents[0]["tab_id"] = "w1:t9"
        reg = hm.build_registry(CAT, ROOT, agents, [{"pane_id": "w1:p1"}], [],
                                matcher=self.matcher, tab_label={"w1:t9": "coord-cowbell"})
        self.assertEqual(reg["live"][0]["name"], "coord-cowbell")

    def test_empty_root(self):
        reg = hm.build_registry(CAT, "/nowhere", [], [], [], matcher=self.matcher)
        self.assertIn("nothing raised here yet", hm.render_registry(reg))

    def test_status_json_keys(self):
        # Fake live source: the same agents/panes/roster the partition test uses.
        reg = hm.build_registry(CAT, ROOT, self.agents, self.panes, self.roster, matcher=self.matcher)
        place = {"name": "nomogenesis", "cwd": ROOT}
        payload = hm.registry_json(reg, place)
        json.dumps(payload)  # must be serializable
        self.assertEqual(payload["root"], ROOT)
        self.assertEqual(payload["place"], "nomogenesis")
        self.assertEqual({k for k in payload}, {"root", "place", "running", "resume", "new"})
        keys = {"name", "harness", "place", "cwd", "host", "state"}
        for row in payload["running"]:
            self.assertTrue(keys <= set(row))
            self.assertTrue(row["harness"])
            self.assertTrue(row["cwd"])
            self.assertEqual(row["place"], "nomogenesis")
            self.assertEqual(row["host"], "herdr pane")
        self.assertEqual([r["name"] for r in payload["running"]], ["majordomo", "ballots"])
        resume = {r["name"]: r for r in payload["resume"]}
        self.assertEqual(resume["old-codex"]["host"], "none")
        self.assertEqual(resume["kimi-notes"]["host"], "herdr pane")
        self.assertTrue(payload["new"])
        self.assertTrue(all(n["state"] == "new" and n["host"] == "none" for n in payload["new"]))

    def test_row_host_tty_from_process_scan(self):
        self.assertEqual(hm.row_host({"pane_id": "pid:412", "tty": "ttys002"}), "tty")
        self.assertEqual(hm.row_host({"pane_id": "wK:p1"}), "herdr pane")
        self.assertEqual(hm.row_host({}), "none")


class Trust(unittest.TestCase):
    def test_parse_match(self):
        text = "tool:      claude\nverdict:   blocked  (H2 subject personal exceeds ceiling project-ip)\nflag:      ⊘H2\n"
        v = hm.parse_match(text, 4)
        self.assertEqual(v["verdict"], "blocked"); self.assertEqual(v["flag"], "⊘H2")
        v = hm.parse_match("verdict:   ok\nflag:      (none)\n", 0)
        self.assertEqual((v["verdict"], v["flag"]), ("ok", ""))
        self.assertEqual(hm.parse_match("", 3)["verdict"], "overprivilege")
        v = hm.parse_match("verdict:   overprivilege  (W1 mutate tools on internal work)  [W1 -- reported here]\n"
                           "flag:      (none)\n", 3)
        self.assertEqual(v["flag"], "W1 mutate tools on internal work")


class PickerList(unittest.TestCase):
    def reg(self):
        return {
            "root": ROOT, "subject": "internal",
            "live": [{"name": "majordomo", "harness": "claude", "kind": "claude", "status": "idle",
                      "pane_id": "w1:p1", "workspace_id": "w1", "on_roster": True, "since": ""},
                     {"name": "scholar", "harness": "grok", "kind": "grok", "status": "done",
                      "pane_id": "w2:p1", "workspace_id": "w2", "on_roster": True, "since": "4m"}],
            "cold": [{"name": "kimi-notes", "harness": "oll-mid", "status": "cold", "pane_id": None, "kind": "pi",
                      "last_seen": "2026-09-11", "session_id": "k1"},
                     {"name": "no-session", "harness": "grok", "status": "cold", "pane_id": None, "kind": "grok",
                      "last_seen": "2026-09-12"}],
            "startable": [
                {"harness": "claude", "kind": "claude", "title": "Claude Code", "installed": True, "trust": {"verdict": "ok"}},
                {"harness": "grok", "kind": "grok", "title": "Grok CLI", "installed": True, "trust": {"verdict": "overprivilege"}},
                {"harness": "omp", "kind": "omp", "title": "omp", "installed": False, "trust": {"verdict": "ok"}},
                {"harness": "local-ornith", "kind": "local-ornith", "title": "ornith", "installed": True, "trust": {"verdict": "blocked"}},
                {"harness": "pi", "kind": "pi", "title": "pi (bare)", "installed": True, "trust": {"verdict": "unknown"}},
            ],
            "absent": [],
        }

    def test_sections_and_what_is_left_off(self):
        reg = self.reg()
        choices = hm.picker_choices(reg, [], here_ws="w1", ws_labels={"w2": "sys:clubhouse"})
        self.assertEqual([c["section"] for c in choices], ["running", "running", "resume", "start", "start", "start"])
        self.assertEqual([c["target"]["harness"] for c in choices if c["action"] == "raise"], ["claude", "grok", "pi"])
        self.assertEqual([hm.picker_selectable(c) for c in choices], [False, False, True, True, True, True])
        text = hm.render_picker(reg, choices)
        for needle in ("┌─ Active ", "  Resume\n", "  New Session\n", "majordomo", "in sys:clubhouse", "4m",
                       "Claude Code", "! more reach than needed"):
            self.assertIn(needle, text)
        self.assertNotIn("  1  majordomo", text)
        self.assertTrue(any(c.get("idx") == 1 and c["action"] == "enter" for c in choices))
        for gone in ("LIVE", "RAISE", "subject", "omp", "local-ornith", "⊘", "?", "w1:p1", "cold", "no-session"):
            self.assertNotIn(gone, text)

    def test_picker_rows_use_the_lobe_mark(self):
        reg = self.reg()
        choices = hm.picker_choices(reg, [], here_ws="w1", ws_labels={"w2": "sys:clubhouse"})

        def plain(c):
            return hm.ANSI_RE.sub("", c["line"])

        live = next(c for c in choices if c["target"].get("name") == "majordomo")
        resume = next(c for c in choices if c["action"] == "enter")
        start = next(c for c in choices if c.get("action") == "raise" and c["target"]["harness"] == "claude")
        for row, kind in ((live, "claude"), (resume, "pi"), (start, "claude")):
            g = hm.LOBE_GLYPH[kind]
            self.assertEqual(ord(g) >> 16, 15)
            self.assertIn(g, plain(row))
        self.assertNotIn("claude", plain(live))
        self.assertNotIn("oll-mid", plain(resume))
        self.assertNotIn("pi", plain(resume))
        self.assertGreater(plain(live).index(hm.LOBE_GLYPH["claude"]), plain(live).index("majordomo"))
        self.assertGreater(plain(resume).index(hm.LOBE_GLYPH["pi"]), plain(resume).index("kimi-notes"))
        self.assertGreater(plain(start).index(hm.LOBE_GLYPH["claude"]), plain(start).index("claude"))
        self.assertTrue(plain(live).split(hm.LOBE_GLYPH["claude"], 1)[1].startswith("  "))
        self.assertTrue(plain(resume).split(hm.LOBE_GLYPH["pi"], 1)[1].startswith("  "))
        self.assertTrue(plain(start).split(hm.LOBE_GLYPH["claude"], 1)[1].startswith("  "))
        census = hm.render_registry({
            "root": ROOT, "subject": "internal",
            "live": [{"name": "majordomo", "harness": "claude", "kind": "claude", "status": "idle",
                      "pane_id": "w1:p1", "on_roster": True, "cwd": ROOT, "session_id": ""}],
            "cold": [{"name": "kimi-notes", "harness": "oll-mid", "kind": "pi", "status": "cold",
                      "pane_id": None, "cwd": ROOT, "session_id": "k1"}],
            "absent": [{"harness": "local-ornith", "egress": "local", "installed": True,
                        "trust": {"verdict": "blocked"}}],
        })
        self.assertIn(hm.LOBE_GLYPH["claude"], census)
        self.assertIn(hm.LOBE_GLYPH["pi"], census)
        self.assertNotIn("oll-mid", census)
        self.assertIn("⌂", census)

    def test_active_sits_in_a_box(self):
        reg = self.reg()
        choices = hm.picker_choices(reg, [], here_ws="w1", ws_labels={"w2": "sys:clubhouse"})
        lines = hm.render_picker(reg, choices).split("\n")
        top = next(i for i, ln in enumerate(lines) if "┌─ Active" in ln)
        bot = next(i for i, ln in enumerate(lines) if ln.strip().startswith("└"))
        inner = "\n".join(lines[top:bot + 1])
        self.assertIn("majordomo", inner)
        self.assertIn("scholar", inner)
        self.assertNotIn("Resume", inner)
        self.assertGreater(next(i for i, ln in enumerate(lines) if ln == "  Resume"), bot)
        name = next(ln for ln in lines[top + 1:bot] if "majordomo" in ln)
        self.assertTrue(name.lstrip().startswith("│"))
        self.assertTrue(name.rstrip().endswith("│"))
        self.assertEqual(hm.visible_len(lines[top]), hm.visible_len(name))
        self.assertEqual(hm.visible_len(lines[top]), hm.visible_len(lines[bot]))

    def test_active_more_row_stays_inside_the_box(self):
        reg = self.reg()
        reg["live"] = [{"name": f"a{i}", "harness": "claude", "kind": "claude", "status": "idle",
                        "pane_id": f"w1:p{i}", "workspace_id": "w1", "on_roster": True, "since": ""}
                       for i in range(8)]
        choices = hm.picker_choices(reg, [])
        running = [c for c in choices if c["section"] == "running"]
        self.assertEqual(running[-1]["action"], "more")
        self.assertTrue(hm.picker_selectable(running[-1]))
        body = hm.render_picker(reg, choices).split("\n")
        more = running[-1]
        self.assertIsNone(more["idx"])
        self.assertIn("+ 4 more", body[more["row"]])
        self.assertIn("│", body[more["row"]])
        self.assertTrue(any("┌─ Active" in ln for ln in body[:more["row"]]))
        self.assertTrue(any(ln.strip().startswith("└") for ln in body[more["row"] + 1:]))

    def test_long_clock_does_not_run_into_the_workspace(self):
        reg = self.reg()
        reg["live"][1]["since"] = "26h55m"
        line = next(c for c in hm.picker_choices(reg, [], here_ws="w1", ws_labels={"w2": "proj:fonts"})
                    if c["target"].get("name") == "scholar")["line"]
        self.assertIn("26h55m  in proj:fonts", hm.ANSI_RE.sub("", line))

    def test_widen_only_when_it_shows_more(self):
        reg = self.reg()
        choices = hm.picker_choices(reg, [])
        self.assertNotIn("widen", hm.render_picker(reg, choices, "/Users/x/code/projects", wider=2))
        self.assertIn("g widen to projects · 5 running",
                      hm.render_picker(reg, choices, "/Users/x/code/projects", wider=5))

    def test_fold_and_numbers_skip_more_row(self):
        reg = self.reg()
        reg["startable"] = [{"harness": f"h{i}", "title": "", "installed": True, "trust": {"verdict": "ok"}}
                            for i in range(8)]
        choices = hm.picker_choices(reg, [])
        start = [c for c in choices if c["section"] == "start"]
        self.assertEqual(len(start), hm.FOLD)
        self.assertEqual(start[-1]["action"], "more")
        self.assertIn("+ 4 more", start[-1]["line"])
        hm.render_picker(reg, choices)
        self.assertIsNone(start[-1]["idx"])
        self.assertEqual([c["idx"] for c in choices if c["action"] != "more"],
                         [None, None, 1, 2, 3, 4, 5])
        self.assertEqual(len([c for c in hm.picker_choices(reg, [], expanded={"start"}) if c["section"] == "start"]), 8)

    def test_rank_here_beats_elsewhere_beats_catalog_order(self):
        roster = [{"harness": "grok", "cwd": "/Users/x/other", "last_seen": "2026-09-12"},
                  {"harness": "grok", "cwd": "/Users/x/other2", "last_seen": "2026-09-12"},
                  {"harness": "pi", "cwd": ROOT + "/sub", "last_seen": "2026-09-01"}]
        self.assertEqual(hm.rank_harnesses(["claude", "grok", "pi", "agy"], roster, ROOT),
                         ["pi", "grok", "claude", "agy"])

    def test_ago(self):
        import datetime as dt
        today = dt.date(2026, 9, 13)
        self.assertEqual(hm.ago("2026-09-13T10:00:00", today), "today")
        self.assertEqual(hm.ago("2026-09-12", today), "yesterday")
        self.assertEqual(hm.ago("2026-09-11", today), "2 days ago")
        self.assertEqual(hm.ago("2026-06-01", today), "Jun 1")
        self.assertEqual(hm.ago("", today), "")

    def test_remember_live_records_unseen_agents_once(self):
        reg = {"live": [{"name": "ballots", "harness": "claude", "kind": "claude", "cwd": ROOT, "pane_id": "w1:p3",
                         "session_id": "s9", "on_roster": False},
                        {"name": "nosession", "harness": "grok", "kind": "grok", "cwd": ROOT, "pane_id": "w1:p4",
                         "session_id": "", "on_roster": False}]}
        rows = [{"name": "ballots", "cwd": "/elsewhere"}]
        saved = []
        orig, hm.save_roster = hm.save_roster, saved.append
        try:
            self.assertEqual(hm.remember_live(reg, rows), 1)
            self.assertEqual(hm.remember_live(reg, rows), 0)
        finally:
            hm.save_roster = orig
        self.assertEqual(rows[-1]["name"], "ballots-2")
        self.assertEqual(rows[-1]["session_id"], "s9")
        self.assertEqual(len(saved), 1)

    def test_refresh_unbinds_when_pane_holds_another_project(self):
        rows = [{"name": "herdr-dev", "cwd": ROOT, "kind": "grok", "harness": "grok",
                 "pane_id": "w19:p3", "session_id": "stolen", "tab_id": "w19:t3", "workspace_id": "w19"}]
        agents = [agent("w19:p3", "grok", "/Users/x/mise", sid="stolen")]
        saved = []
        orig, hm.save_roster = hm.save_roster, saved.append
        try:
            hm.refresh_sessions(rows, agents=agents, tab_labels={"w19:t3": "mise"})
        finally:
            hm.save_roster = orig
        self.assertEqual(rows[0]["pane_id"], "")
        self.assertEqual(rows[0]["session_id"], "")
        self.assertEqual(rows[0]["cwd"], ROOT)  # sitting's home stays; the pane does not
        self.assertEqual(len(saved), 1)

    def test_refresh_updates_kind_when_the_sitting_is_still_there(self):
        rows = [{"name": "cowbell", "cwd": ROOT, "kind": "claude", "harness": "claude",
                 "pane_id": "w1A:p3", "session_id": "s1", "tab_id": "w1A:t3"}]
        agents = [agent("w1A:p3", "grok", ROOT, sid="s1")]
        agents[0]["tab_id"] = "w1A:t3"
        saved = []
        orig, hm.save_roster = hm.save_roster, saved.append
        try:
            hm.refresh_sessions(rows, agents=agents, tab_labels={"w1A:t3": "herdr-cowbell"})
        finally:
            hm.save_roster = orig
        self.assertEqual(rows[0]["pane_id"], "w1A:p3")
        self.assertEqual(rows[0]["kind"], "grok")
        self.assertEqual(rows[0]["harness"], "grok")

    def test_refresh_keeps_a_sitting_that_moved_directories_when_the_tab_matches(self):
        rows = [{"name": "scholar", "cwd": ROOT + "/old", "kind": "claude", "harness": "claude",
                 "pane_id": "wM:pE", "session_id": "s1", "tab_id": "wM:tE"}]
        agents = [agent("wM:pE", "grok", ROOT + "/new", sid="s1")]
        agents[0]["tab_id"] = "wM:tE"
        orig, hm.save_roster = hm.save_roster, lambda rows: None
        try:
            hm.refresh_sessions(rows, agents=agents, tab_labels={"wM:tE": "scholar"})
        finally:
            hm.save_roster = orig
        self.assertEqual(rows[0]["pane_id"], "wM:pE")
        self.assertEqual(rows[0]["kind"], "grok")
        self.assertEqual(rows[0]["cwd"], ROOT + "/new")

    def test_bind_sitting_keeps_sonnet_model_from_quota_token(self):
        row = {"name": "blender", "kind": "claude", "harness": "claude", "model": ""}
        live = agent("w13:p8", "claude", ROOT)
        live["tokens"] = {"quota_model": "Sonnet 5"}
        hm.bind_sitting(row, live)
        self.assertEqual(row["model"], "Sonnet 5")
        self.assertEqual(hm.glyph_for(row["kind"], row["model"]), hm.LOBE_GLYPH["claude"])

    def test_remember_live_reclaims_cold_sitting_by_name_and_cwd(self):
        reg = {"live": [{"name": "herdr-dev", "harness": "grok", "kind": "grok", "cwd": ROOT,
                         "pane_id": "w1A:pD", "session_id": "s-new", "tab_id": "w1A:tA",
                         "workspace_id": "w1A", "on_roster": False}]}
        rows = [{"name": "herdr-dev", "cwd": ROOT, "kind": "grok", "harness": "grok",
                 "pane_id": "", "session_id": ""}]
        saved = []
        orig, hm.save_roster = hm.save_roster, saved.append
        try:
            self.assertEqual(hm.remember_live(reg, rows), 0)
        finally:
            hm.save_roster = orig
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["pane_id"], "w1A:pD")
        self.assertEqual(rows[0]["session_id"], "s-new")
        self.assertTrue(reg["live"][0]["on_roster"])
        self.assertEqual(len(saved), 1)


class Input(unittest.TestCase):
    def test_keys_and_mouse(self):
        evs, tail = hm.parse_input(b"\x1b[A\x1b[Bj\r\x1b[<0;8;11M\x1b[<0;8;11m\x1b[<65;1;2M\x1b[5~")
        self.assertEqual(evs, [("key", "up"), ("key", "down"), ("char", "j"), ("key", "enter"),
                               ("mouse", 0, 8, 11, True), ("mouse", 0, 8, 11, False),
                               ("mouse", 65, 1, 2, True), ("key", "pgup")])
        self.assertEqual(tail, b"")

    def test_lone_esc_waits_and_partial_sequence_is_kept(self):
        self.assertEqual(hm.parse_input(b"\x1b"), ([], b"\x1b"))
        self.assertEqual(hm.parse_input(b"a\x1b[<0;8"), ([("char", "a")], b"\x1b[<0;8"))
        self.assertEqual(hm.parse_input(b"\x1bx")[0], [("key", "esc"), ("char", "x")])

    def test_hint_bar_spans_are_plain_columns(self):
        line, spans = hm.hint_bar([("⏎", "open", "enter"), ("w", "wizard", "w"), ("esc", "close", "esc")])
        self.assertEqual(spans, [(3, 9, "enter"), (12, 20, "w"), (23, 32, "esc")])
        self.assertEqual(hm.visible_len(line), 31)


class Paths(unittest.TestCase):
    """XDG config/state shared by both doors; one-time copy off herdr's plugin dirs (LAB-248)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.cfg, self.state = base / "cfg" / "cowbell", base / "state" / "cowbell"
        self.old_cfg, self.old_state = base / "old-cfg", base / "old-state"
        self.seed_root = base / "seed"
        self.seed_root.mkdir()
        (self.seed_root / "harnesses.toml").write_text('schema = 1\n[[harness]]\nid = "claude"\n')
        self.env = {"COWBELL_CONFIG_DIR": str(self.cfg), "COWBELL_STATE_DIR": str(self.state),
                    "HERDR_PLUGIN_CONFIG_DIR": str(self.old_cfg), "HERDR_PLUGIN_STATE_DIR": str(self.old_state),
                    "HERDR_PLUGIN_ROOT": str(self.seed_root)}
        self.saved = {k: os.environ.get(k) for k in self.env}
        os.environ.update(self.env)

    def tearDown(self):
        for k, v in self.saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()

    def legacy(self):
        self.old_cfg.mkdir()
        self.old_state.mkdir()
        catalog = b'# house catalog\n[defaults]\nlane = "yellow"  # kept\n\n[[harness]]\nid = "grok"\n'
        (self.old_cfg / "harnesses.toml").write_bytes(catalog)
        rows = [{"name": "butler", "cwd": "/x", "harness": "grok", "session_id": "s1"}]
        (self.old_state / "roster.json").write_text(json.dumps({"harnesses": rows}))
        return catalog, rows

    def test_fresh_run_seeds_new_dirs(self):
        p = hm.catalog_path()
        self.assertEqual(p, self.cfg / "harnesses.toml")
        self.assertEqual(p.read_text(), (self.seed_root / "harnesses.toml").read_text())
        self.assertEqual(hm.load_roster(), [])
        self.assertFalse((self.cfg / ".migrated_from").exists())

    def test_migrates_byte_faithful_once(self):
        catalog, rows = self.legacy()
        self.assertEqual(hm.catalog_path().read_bytes(), catalog)
        self.assertEqual(hm.load_roster(), rows)
        backups = sorted(p.name for p in (self.cfg / "migration-backup").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertTrue((self.old_cfg / "harnesses.toml").exists())            # copy, not move
        marker = (self.cfg / ".migrated_from").read_text().splitlines()
        self.assertEqual(json.loads(marker[0])["from"], str(self.old_cfg / "harnesses.toml"))
        (self.old_cfg / "harnesses.toml").write_text("# changed later in the old dir\n")
        hm.catalog_path(); hm.load_roster()                                     # second run
        self.assertEqual(hm.catalog_path().read_bytes(), catalog)
        self.assertEqual(sorted(p.name for p in (self.cfg / "migration-backup").iterdir()), backups)
        self.assertEqual(len((self.cfg / ".migrated_from").read_text().splitlines()), 1)

    def test_installed_seed_is_found_under_share(self):
        (self.seed_root / "harnesses.toml").unlink()
        saved = sys.prefix
        prefix = Path(self.tmp.name) / "venv"
        (prefix / "share" / "cowbell").mkdir(parents=True)
        (prefix / "share" / "cowbell" / "harnesses.toml").write_text('schema = 1\n[[harness]]\nid = "pi"\n')
        sys.prefix = str(prefix)
        try:
            self.assertEqual(hm.catalog_path().read_text(), 'schema = 1\n[[harness]]\nid = "pi"\n')
        finally:
            sys.prefix = saved

    def test_missing_seed_and_legacy_means_no_catalog(self):
        (self.seed_root / "harnesses.toml").unlink()
        with self.assertRaises(SystemExit):
            hm.load_catalog()

    def test_xdg_homes_when_no_override(self):
        for k in ("COWBELL_CONFIG_DIR", "COWBELL_STATE_DIR"):
            os.environ.pop(k)
        base = Path(self.tmp.name)
        os.environ["XDG_CONFIG_HOME"], os.environ["XDG_STATE_HOME"] = str(base / "xc"), str(base / "xs")
        try:
            self.assertEqual(hm.config_dir(), base / "xc" / "cowbell")
            self.assertEqual(hm.state_dir(), base / "xs" / "cowbell")
        finally:
            os.environ.pop("XDG_CONFIG_HOME"); os.environ.pop("XDG_STATE_HOME")

    def test_roster_without_schema_is_accepted_and_rewritten(self):
        _, rows = self.legacy()
        hm.save_roster(hm.load_roster())
        data = json.loads((self.state / "roster.json").read_text())
        self.assertEqual(data["schema"], hm.SCHEMA)
        self.assertEqual(data["harnesses"], rows)

    def test_newer_roster_is_read_but_never_written(self):
        self.state.mkdir(parents=True)
        body = json.dumps({"schema": hm.SCHEMA + 1, "harnesses": [{"name": "a", "cwd": "/x"}], "future": True})
        (self.state / "roster.json").write_text(body)
        self.assertEqual([r["name"] for r in hm.load_roster()], ["a"])
        with self.assertRaises(hm.SchemaError):
            hm.save_roster([])
        self.assertEqual((self.state / "roster.json").read_text(), body)

    def test_newer_catalog_loads_and_refuses_writes(self):
        self.cfg.mkdir(parents=True)
        (self.cfg / "harnesses.toml").write_text(f'schema = {hm.SCHEMA + 1}\n[[harness]]\nid = "claude"\n')
        cat = hm.load_catalog()
        self.assertEqual(cat["harness"][0]["id"], "claude")
        with self.assertRaises(hm.SchemaError):
            hm.check_writable(cat["schema"], "harnesses.toml")


class CtxCwd(unittest.TestCase):
    def test_command_in_a_pane_uses_its_own_cwd(self):
        orig = hm.herdr
        hm.herdr = lambda *a, **k: (_ for _ in ()).throw(AssertionError("asked herdr for the pane cwd"))
        try:
            ctx = hm.Ctx.from_env({"HERDR_PANE_ID": "w1:p1", "HERDR_WORKSPACE_ID": "w1"})
        finally:
            hm.herdr = orig
        self.assertEqual(ctx.cwd, os.path.realpath(os.getcwd()))

    def test_plugin_action_asks_herdr_for_the_caller_pane(self):
        orig = hm.herdr
        hm.herdr = lambda *a, **k: {"pane": {"cwd": "/"}}
        try:
            ctx = hm.Ctx.from_env({"HERDR_PANE_ID": "w1:p1", "HERDR_PLUGIN_ROOT": "/plugin"})
        finally:
            hm.herdr = orig
        self.assertEqual(ctx.cwd, "/")


class Places(unittest.TestCase):
    """[places]: a directory's pen, allowed harnesses and lane; ~ goes to the untitled place (LAB-262)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = os.path.realpath(self.tmp.name)
        self.pad = os.path.join(self.home, "cloud", "git-projects", "agent-lobby")
        os.makedirs(self.pad)
        self.cat = {**CAT, "defaults": {"lane": "yellow", "untitled_place": "lobby"},
                    "places": {"lobby": {"cwd": self.pad, "workspace_label": "lobby",
                                         "allow_harness": ["lobby", "claude", "grok"],
                                         "default_harness": "lobby", "lane": "green"}}}

    def tearDown(self):
        self.tmp.cleanup()

    def test_home_remaps_to_untitled_place(self):
        root, place, remapped = hm.resolve_root(self.cat, self.home, home=self.home)
        self.assertEqual((root, place["name"], remapped), (self.pad, "lobby", True))

    def test_no_untitled_place_means_no_remap(self):
        cat = {**self.cat, "defaults": {"lane": "yellow"}}
        self.assertEqual(hm.resolve_root(cat, self.home, home=self.home), (self.home, None, False))

    def test_place_holds_its_subdirectories_only(self):
        self.assertEqual(hm.resolve_root(self.cat, os.path.join(self.pad, "visitors"), home=self.home)[1]["name"],
                         "lobby")
        self.assertIsNone(hm.resolve_root(self.cat, os.path.join(self.home, "cloud"), home=self.home)[1])

    def test_scoped_catalog_filters_harnesses_and_sets_lane(self):
        scoped = hm.scoped_catalog(self.cat, hm.places(self.cat)["lobby"])
        self.assertEqual([h["id"] for h in scoped["harness"]], ["lobby", "claude", "grok"])
        self.assertEqual(scoped["defaults"]["lane"], "green")
        self.assertEqual(scoped["defaults"]["default_harness"], "lobby")
        self.assertEqual(len(self.cat["harness"]), len(CAT["harness"]))          # original untouched
        reg = hm.build_registry(scoped, self.pad, [], [], [], matcher=lambda t: {"verdict": "ok"})
        self.assertEqual([a["harness"] for a in reg["startable"]], ["lobby", "claude", "grok"])
        self.assertEqual(reg["default_harness"], "lobby")

    def test_resume_omits_harnesses_the_place_does_not_allow(self):
        scoped = hm.scoped_catalog(self.cat, hm.places(self.cat)["lobby"])
        roster = [
            {"name": "kimi-notes", "harness": "oll-memo", "cwd": self.pad, "session_id": "s1", "pane_id": None},
            {"name": "house-grok", "harness": "grok", "cwd": self.pad, "session_id": "s2", "pane_id": None},
        ]
        reg = hm.build_registry(scoped, self.pad, [], [], roster, matcher=lambda t: {"verdict": "ok"})
        self.assertEqual({r["name"] for r in reg["cold"]}, {"house-grok"})

    def test_default_harness_ranks_first_despite_house_usage(self):
        ids = ["claude", "grok", "lobby"]
        roster = [{"harness": "grok", "cwd": self.pad, "last_seen": "2026-09-15"}] * 5
        ranked = hm.rank_harnesses(ids, roster, self.pad, default="lobby")
        self.assertEqual(ranked[0], "lobby")
        self.assertIn("grok", ranked)

    def test_new_without_harness_uses_place_default(self):
        with self.assertRaises(SystemExit) as e:
            hm.cmd_new(hm.Ctx(cwd=self.pad), self.cat, "", place="lobby")
        self.assertIn("lobby", str(e.exception))  # default, then not-installed

    def test_new_refuses_a_harness_the_place_does_not_allow(self):
        with self.assertRaises(SystemExit) as e:
            hm.cmd_new(hm.Ctx(cwd=self.pad), self.cat, "codex", place="lobby")
        self.assertIn("may not start in place lobby", str(e.exception))
        with self.assertRaises(SystemExit):
            hm.cmd_new(hm.Ctx(cwd=self.pad), self.cat, "grok", place="nowhere")

    # --- LAB-295: nested cwds resolve to exactly one place ---

    def _nested_cat(self):
        """An inner place inside the lobby place: the inner one wins beneath its cwd."""
        inner = os.path.join(self.pad, "visitors", "inner-pad")
        os.makedirs(inner)
        cat = {**self.cat, "places": {
            **self.cat["places"],
            "inner": {"cwd": inner, "workspace_label": "lobby", "allow_harness": ["grok"],
                      "default_harness": "grok", "lane": "yellow"}}}
        return cat, inner

    def test_nested_places_resolve_to_the_inner_place(self):
        cat, inner = self._nested_cat()
        self.assertEqual(hm.resolve_root(cat, inner, home=self.home)[1]["name"], "inner")
        self.assertEqual(hm.resolve_root(cat, os.path.join(inner, "deeper"), home=self.home)[1]["name"], "inner")
        # a cwd under the parent but outside the inner place still names the parent
        self.assertEqual(hm.resolve_root(cat, os.path.join(self.pad, "visitors"), home=self.home)[1]["name"],
                         "lobby")

    def test_status_names_the_place(self):
        cat, inner = self._nested_cat()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            hm.cmd_registry(hm.Ctx(cwd=inner, mode="here"), cat)
        self.assertIn("inner", buf.getvalue())

    def test_status_json_names_the_place(self):
        cat, inner = self._nested_cat()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            hm.cmd_registry(hm.Ctx(cwd=inner, mode="here"), cat, as_json=True)
        self.assertEqual(json.loads(buf.getvalue())["place"], "inner")

    def test_new_without_place_uses_the_nested_place(self):
        cat, inner = self._nested_cat()
        with self.assertRaises(SystemExit) as e:
            hm.cmd_new(hm.Ctx(cwd=inner), cat, "codex")
        self.assertIn("may not start in place inner", str(e.exception))

    def test_place_flag_still_overrides_the_cwd_place(self):
        cat, inner = self._nested_cat()
        # codex is allowed at the parent (add it), refused at the inner cwd:
        cat["places"]["lobby"]["allow_harness"] = ["lobby", "claude", "grok", "codex"]
        with self.assertRaises(SystemExit) as e:
            hm.cmd_new(hm.Ctx(cwd=inner), cat, "codex", place="lobby")
        self.assertNotIn("may not start", str(e.exception))   # the parent's rules apply instead
        self.assertIn("not installed", str(e.exception))      # codex is allowed there, just not installed

    def _raise(self, existing):
        calls = []

        def fake_herdr(*args, expect_json=True):
            calls.append(args)
            if args[:2] == ("workspace", "list"):
                return {"workspaces": existing}
            if args[:2] == ("workspace", "create"):
                return {"tab": {"tab_id": "wL:t1", "label": "lobby"},
                        "root_pane": {"pane_id": "wL:p1", "tab_id": "wL:t1", "workspace_id": "wL"}}
            if args[:2] == ("tab", "create"):
                return {"root_pane": {"pane_id": "wL:p2", "tab_id": "wL:t2", "workspace_id": args[3]}}
            return {}
        saved = (hm.herdr, hm.start_native, hm.save_roster, hm.load_roster)
        hm.herdr = fake_herdr
        hm.start_native = lambda *a, **k: {}
        hm.save_roster = lambda rows: None
        hm.load_roster = lambda: []
        try:
            pane = hm.raise_harness(self.cat, hm.harness_by_id(self.cat, "grok"), "grok-3", self.pad,
                                    hm.Ctx(workspace_id="wK", cwd=self.home), pen=True)
        finally:
            hm.herdr, hm.start_native, hm.save_roster, hm.load_roster = saved
        return pane, calls

    def test_pen_is_created_when_missing(self):
        pane, calls = self._raise([{"workspace_id": "wK", "label": "home ~"}])
        create = next(c for c in calls if c[:2] == ("workspace", "create"))
        self.assertEqual(create[create.index("--label") + 1], "lobby")
        self.assertEqual(create[create.index("--cwd") + 1], self.pad)
        self.assertEqual(pane["workspace_id"], "wL")
        self.assertFalse(any(c[:2] == ("tab", "create") and "wK" in c for c in calls))   # not the caller's home ~

    def test_pen_is_reused_when_present(self):
        pane, calls = self._raise([{"workspace_id": "wK", "label": "home ~"},
                                   {"workspace_id": "w1B", "label": "proj:agent-lobby"},
                                   {"workspace_id": "wL", "label": "lobby"}])
        tab = next(c for c in calls if c[:2] == ("tab", "create"))
        self.assertEqual(tab[tab.index("--workspace") + 1], "wL")
        self.assertFalse(any(c[:2] == ("workspace", "create") for c in calls))

    def test_without_pen_stays_on_the_caller_line(self):
        pane, calls = self._raise([{"workspace_id": "wK", "label": "home ~"},
                                   {"workspace_id": "wL", "label": "lobby"}])
        # _raise passes pen=True. Call again without it.
        calls.clear()
        saved = (hm.herdr, hm.start_native, hm.save_roster, hm.load_roster)
        def fake_herdr(*args, expect_json=True):
            calls.append(args)
            if args[:2] == ("workspace", "list"):
                return {"workspaces": [{"workspace_id": "wK", "label": "home ~"},
                                       {"workspace_id": "wL", "label": "lobby"}]}
            if args[:2] == ("tab", "create"):
                return {"root_pane": {"pane_id": "wK:p9", "tab_id": "wK:t9", "workspace_id": args[3]}}
            return {}
        hm.herdr = fake_herdr
        hm.start_native = lambda *a, **k: {}
        hm.save_roster = lambda rows: None
        hm.load_roster = lambda: []
        try:
            pane = hm.raise_harness(self.cat, hm.harness_by_id(self.cat, "grok"), "grok-4", self.pad,
                                    hm.Ctx(workspace_id="wK", cwd=self.home))
        finally:
            hm.herdr, hm.start_native, hm.save_roster, hm.load_roster = saved
        tab = next(c for c in calls if c[:2] == ("tab", "create"))
        self.assertEqual(tab[tab.index("--workspace") + 1], "wK")
        self.assertEqual(pane["workspace_id"], "wK")
        self.assertFalse(any(c[:2] == ("workspace", "create") for c in calls))

    def test_without_pen_creates_a_tab_in_proj_workspace(self):
        calls = []

        def fake_herdr(*args, expect_json=True):
            calls.append(args)
            if args[:2] == ("workspace", "list"):
                return {"workspaces": [
                    {"workspace_id": "w1B", "label": "proj:agent-lobby"},
                    {"workspace_id": "wL", "label": "lobby"},
                ]}
            if args[:2] == ("pane", "list"):
                return {"panes": [{"pane_id": "w1B:p1", "workspace_id": "w1B", "tab_id": "w1B:t1",
                                   "cwd": self.pad}]}
            if args[:2] == ("tab", "create"):
                return {"tab": {"tab_id": "w1B:t2", "workspace_id": "w1B"}, "root_pane": {"pane_id": "w1B:p9", "tab_id": "w1B:t2", "workspace_id": "w1B"}}
            return {}

        saved = (hm.herdr, hm.start_native, hm.save_roster, hm.load_roster)
        hm.herdr = fake_herdr
        hm.start_native = lambda *a, **k: {}
        hm.save_roster = lambda rows: None
        hm.load_roster = lambda: []
        try:
            pane = hm.raise_harness(self.cat, hm.harness_by_id(self.cat, "grok"), "grok-5", self.pad,
                                    hm.Ctx(workspace_id="wL", cwd=self.pad))
        finally:
            hm.herdr, hm.start_native, hm.save_roster, hm.load_roster = saved
        tab_create = next(c for c in calls if c[:2] == ("tab", "create"))
        self.assertEqual(tab_create[2], "--workspace")
        self.assertEqual(tab_create[3], "w1B")
        self.assertEqual(pane["pane_id"], "w1B:p9")
        self.assertEqual(pane["workspace_id"], "w1B")
        self.assertFalse(any(c[:2] == ("workspace", "create") for c in calls))
        self.assertFalse(any(c[:2] == ("pane", "split") for c in calls))


class Hosts(unittest.TestCase):
    """LiveSource / HostLaunch seams (LAB-249)."""

    SRC = Path(__file__).resolve().parent.parent / "cowbell.py"

    def test_every_herdr_call_is_inside_the_adapter(self):
        lines = self.SRC.read_text().splitlines()
        start = next(i for i, ln in enumerate(lines) if ln.startswith("# --- herdr adapter"))
        end = next(i for i, ln in enumerate(lines) if i > start and ln.startswith("# --- "))
        outside = [f"{i + 1}: {ln.strip()}" for i, ln in enumerate(lines)
                   if re.search(r"\bherdr\(", ln) and not start < i < end]
        self.assertEqual(outside, [])

    def test_server_up_probes_the_socket_not_the_cli(self):
        orig, env = hm.herdr, os.environ.get("HERDR_SOCKET_PATH")
        hm.herdr = lambda *a, **k: (_ for _ in ()).throw(AssertionError("ran herdr"))
        os.environ["HERDR_SOCKET_PATH"] = "/nonexistent/herdr.sock"
        try:
            self.assertFalse(hm.server_up())
        finally:
            hm.herdr = orig
            if env is None:
                os.environ.pop("HERDR_SOCKET_PATH")
            else:
                os.environ["HERDR_SOCKET_PATH"] = env

    def test_host_is_chosen_once(self):
        pane = {"HERDR_PANE_ID": "w1:p1", "HERDR_WORKSPACE_ID": "w1"}
        inside = hm.choose_host(True, pane)
        self.assertEqual(inside.mode, "here")
        self.assertIsInstance(inside.launch, hm.HereLaunch)
        self.assertIsInstance(inside.live, hm.CombinedLive)
        forced = hm.choose_host(True, {**pane, "COWBELL_MODE": "here"})
        self.assertEqual(forced.mode, "here")
        self.assertIsInstance(forced.launch, hm.HereLaunch)
        self.assertTrue(forced.live.herdr)
        offline = hm.choose_host(False, pane)
        self.assertEqual(offline.mode, "here")
        self.assertFalse(offline.live.herdr)
        self.assertEqual([type(x) for x in offline.live.sources], [hm.ProcessScan])
        agent = hm.choose_host(True, {**pane, "GROK_AGENT": "1"})
        self.assertEqual(agent.mode, "tab")
        self.assertIsInstance(agent.launch, hm.HerdrLaunch)
        self.assertIsInstance(agent.live, hm.HerdrLive)
        person = hm.choose_host(True, {**pane, "GROK_AGENT": "1", "COWBELL_CALLER": "person"})
        self.assertEqual(person.mode, "here")
        tabbed_person = hm.choose_host(True, {**pane, "COWBELL_MODE": "tab"})
        self.assertEqual(tabbed_person.mode, "tab")

    def test_here_never_creates_a_tab(self):
        calls = []
        saved = (hm.herdr, hm.exec_here)
        hm.herdr = lambda *a, **k: calls.append(a) or {}
        hm.exec_here = lambda *a, **k: {"pane_id": None}
        try:
            hm.launch(CAT, CAT["harness"][0], "n", ROOT, hm.Ctx(cwd="/", mode="here"))
        finally:
            hm.herdr, hm.exec_here = saved
        self.assertEqual(calls, [])

    def test_combined_focus_routes_by_row(self):
        focused = []
        orig = hm.focus_agent
        hm.focus_agent = focused.append
        try:
            live = hm.CombinedLive(hm.HerdrLive(), hm.ProcessScan())
            self.assertIn("focused", live.focus({"name": "a", "pane_id": "w1:p2"}))
            with self.assertRaises(SystemExit) as e:
                live.focus({"name": "b", "pane_id": "pid:42", "pid": 42, "tty": "ttys003"})
            self.assertIn("ttys003", str(e.exception))
            with self.assertRaises(SystemExit):
                hm.CombinedLive(hm.ProcessScan()).focus({"name": "c", "pane_id": "w1:p9"})
        finally:
            hm.focus_agent = orig
        self.assertEqual(focused, ["w1:p2"])


class NoHerdrCalls(unittest.TestCase):
    """COWBELL_MODE=here, no server: a herdr binary that logs and fails is never run (LAB-249)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.log = base / "herdr-calls.log"
        stub = base / "herdr"
        stub.write_text(f"#!/bin/sh\necho \"$@\" >> {self.log}\nexit 1\n")
        stub.chmod(0o755)
        agent = base / "fake-agent"
        agent.write_text("#!/bin/sh\necho FAKE-AGENT \"$@\"\n")
        agent.chmod(0o755)
        (base / "cfg").mkdir()
        (base / "cfg" / "harnesses.toml").write_text(
            f'schema = 1\n[[harness]]\nid = "fake"\nkind = "pi"\ncommand = "{agent}"\nresume = ["--continue"]\n')
        (base / "state").mkdir()
        (base / "state" / "roster.json").write_text(json.dumps({"schema": 1, "harnesses": [
            {"name": "sitting", "cwd": str(base), "harness": "fake", "kind": "pi", "session_id": "s1", "pane_id": "w1:p1"}]}))
        self.env = {**os.environ, "HERDR_BIN_PATH": str(stub), "HERDR_SOCKET_PATH": str(base / "no.sock"),
                    "COWBELL_MODE": "here", "COWBELL_PLAIN": "1", "COWBELL_CONFIG_DIR": str(base / "cfg"),
                    "COWBELL_STATE_DIR": str(base / "state"), "HERDR_PANE_ID": "w1:p1",
                    "PATH": "/usr/sbin:/usr/bin:/bin"}
        self.env.pop("HERDR_PLUGIN_CONTEXT_JSON", None)
        self.env.pop("COWBELL_CTX", None)
        self.base = base

    def tearDown(self):
        self.tmp.cleanup()

    def run_cowbell(self, *args, stdin=""):
        import subprocess
        return subprocess.run([sys.executable, str(Hosts.SRC), *args], input=stdin, capture_output=True, text=True,
                              env=self.env, cwd=self.base, timeout=30)

    def test_status_picker_enter_never_run_herdr(self):
        status = self.run_cowbell("status")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertIn("sitting", status.stdout)
        picker = self.run_cowbell("picker", stdin="q\n")
        self.assertEqual(picker.returncode, 0, picker.stderr)
        self.assertIn("  New Session\n", picker.stdout)
        enter = self.run_cowbell("enter", "sitting")
        self.assertIn("FAKE-AGENT --continue", enter.stdout, enter.stderr)
        self.assertFalse(self.log.exists(), self.log.read_text() if self.log.exists() else "")

    def test_new_never_runs_herdr(self):
        res = self.run_cowbell("new", "--harness", "fake", "--name", "test1")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertFalse(self.log.exists(), self.log.read_text() if self.log.exists() else "")

    def test_list_never_runs_herdr(self):
        res = self.run_cowbell("list")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertFalse(self.log.exists(), self.log.read_text() if self.log.exists() else "")

    def test_dispatch_never_runs_herdr(self):
        res = self.run_cowbell("fake", "--name", "test2")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertFalse(self.log.exists(), self.log.read_text() if self.log.exists() else "")

    def test_server_socket_listening_but_no_herdr_bin(self):
        import socket, subprocess
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(self.env["HERDR_SOCKET_PATH"])
        sock.listen(1)
        try:
            env = {**self.env}
            env.pop("HERDR_BIN_PATH", None)
            env["PATH"] = "/usr/sbin:/usr/bin:/bin"
            res = subprocess.run([sys.executable, str(Hosts.SRC), "status"], env=env, cwd=self.base, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("sitting", res.stdout)
        finally:
            sock.close()


class Standalone(unittest.TestCase):
    PS = """\
    1     0 ??       /sbin/launchd
  500     1 ??       /Applications/Herdr.app/Contents/MacOS/herdr server
  510   500 ttys001  -zsh
  511   510 ttys001  claude --model claude-opus-5
  600     1 ??       tmux -u new-session -d -s agentdeck_x
  601   600 ttys004  pi
  602   600 ttys005  /Users/x/.local/bin/grok --resume 019f
  603   602 ttys005  node /opt/mcp/server.js
  604   602 ttys005  grok helper
  700     1 ttys009  node /opt/homebrew/bin/gemini
  800     1 ??       /Applications/ChatGPT.app/Contents/Resources/codex app-server
  900     1 ??       claude --print hello
"""

    def test_exe_kind(self):
        self.assertEqual(hm.exe_kind(["claude", "--model", "x"]), "claude")
        self.assertEqual(hm.exe_kind(["/Users/x/.local/bin/grok"]), "grok")
        self.assertEqual(hm.exe_kind(["node", "--no-warnings", "/opt/homebrew/bin/gemini"]), "gemini")
        self.assertEqual(hm.exe_kind(["/Applications/ChatGPT.app/Contents/Resources/codex"]), "")
        self.assertEqual(hm.exe_kind(["-zsh"]), "")

    def test_agent_processes_skip_herdr_nested_and_ttyless(self):
        table = hm.ps_table(self.PS)
        rows = hm.agent_processes(table, cwds=lambda pids: {p: f"/work/{p}" for p in pids})
        self.assertEqual(sorted((r["pid"], r["agent"], r["tty"]) for r in rows),
                         [(601, "pi", "ttys004"), (602, "grok", "ttys005"), (700, "gemini", "ttys009")])
        self.assertEqual(rows[0]["pane_id"], f"pid:{rows[0]['pid']}")

    def test_here_command_session_and_name(self):
        claude = dict(CAT["harness"][0], session_id_flag="--session-id", name_flag="--name")
        cmd, sid = hm.here_command(CAT, claude, "butler", model="claude-opus-5", lane="yellow")
        self.assertEqual(cmd[:3], ["claude", "--session-id", sid])
        self.assertEqual(len(sid), 36)
        self.assertIn("--permission-mode", cmd)
        self.assertEqual(cmd[-2:], ["--name", "butler"])
        cmd, sid = hm.here_command(CAT, claude, "butler", resume_id="abc")
        self.assertEqual(sid, "abc")
        self.assertNotIn("--session-id", cmd)
        self.assertEqual(cmd[cmd.index("--resume") + 1], "abc")

    def test_launch_routes_by_mode(self):
        calls = []
        orig = hm.exec_here, hm.raise_harness
        hm.exec_here = lambda *a, **k: calls.append("here")
        hm.raise_harness = lambda *a, **k: calls.append("tab")
        try:
            hm.launch(CAT, CAT["harness"][0], "n", ROOT, hm.Ctx(cwd="/", mode="here"))
            hm.launch(CAT, CAT["harness"][0], "n", ROOT, hm.Ctx(cwd="/", mode="tab"))
        finally:
            hm.exec_here, hm.raise_harness = orig
        self.assertEqual(calls, ["here", "tab"])

    def test_in_herdr_pane(self):
        self.assertTrue(hm.in_herdr_pane({"HERDR_PANE_ID": "w1:p1"}))
        self.assertFalse(hm.in_herdr_pane({"TERM": "xterm"}))


class SidebarTokens(unittest.TestCase):
    """LAB-297: herdr identity tokens on raise/adopt/state-change only — never a loop."""

    def test_glyph_table_matches_the_sidebar(self):
        self.assertEqual(hm.glyph_for("grok"), hm.LOBE_GLYPH["grok"])
        self.assertEqual(hm.glyph_for("pi"), hm.LOBE_GLYPH["pi"])
        self.assertEqual(hm.glyph_for("gemini"), hm.LOBE_GLYPH["gemini"])
        self.assertEqual(hm.glyph_for("codex"), hm.LOBE_GLYPH["codex"])
        self.assertEqual(hm.glyph_for("claude", "claude-sonnet-5"), hm.LOBE_GLYPH["claude"])
        self.assertEqual(hm.glyph_for("claude", "claude-opus-5"), hm.LOBE_GLYPH["claude"])
        self.assertEqual(hm.glyph_for("claude"), hm.LOBE_GLYPH["claude"])
        self.assertEqual(hm.glyph_for("devin"), hm.LOBE_GLYPH["devin"])
        self.assertEqual(hm.glyph_for("agy"), hm.LOBE_GLYPH["antigravity"])
        self.assertEqual(hm.glyph_for("droid"), "·")
        for ch in hm.LOBE_GLYPH.values():
            self.assertEqual(ord(ch) >> 16, 15)   # plane 15, one cell in Menlo+lobe-icons

    def test_report_identity_one_publish_source_cowbell(self):
        calls = []
        orig = hm.herdr
        hm.herdr = lambda *a, **k: calls.append(a) or {}
        try:
            self.assertTrue(hm.report_identity("w1B:p5", "droid", "grok", ""))
        finally:
            hm.herdr = orig
        self.assertEqual(len(calls), 1)
        args = calls[0]
        self.assertEqual(args[:2], ("pane", "report-metadata"))
        self.assertIn("w1B:p5", args)
        self.assertEqual(args[args.index("--source") + 1], "cowbell")
        g = hm.LOBE_GLYPH["grok"]
        self.assertEqual(args[args.index("--display-agent") + 1], g)
        self.assertNotIn("--ttl-ms", args)
        tokens = [args[i + 1] for i, a in enumerate(args) if a == "--token"]
        self.assertIn(f"glyph={g}", tokens)
        self.assertIn(f"line1={g} droid", tokens)
        self.assertFalse(hm.report_identity("pid:42", "n", "grok"))   # no herdr pane: no publish

    def test_clear_identity_drops_cowbell_tokens(self):
        calls = []
        orig = hm.herdr
        hm.herdr = lambda *a, **k: calls.append(a) or {}
        try:
            self.assertTrue(hm.clear_identity("w19:p3"))
        finally:
            hm.herdr = orig
        args = calls[0]
        self.assertEqual(args[:2], ("pane", "report-metadata"))
        self.assertIn("--clear-display-agent", args)
        self.assertIn("glyph", args)
        self.assertIn("line1", args)
        self.assertFalse(hm.clear_identity("pid:9"))

    def test_identity_events_publish_once_per_change(self):
        seen = {}
        row = {"pane_id": "w1:p1", "name": "butler", "kind": "grok", "status": "working", "on_roster": True}
        self.assertEqual(len(hm.identity_events(seen, [row])), 1)     # first seen: one event
        self.assertEqual(hm.identity_events(seen, [row]), [])         # unchanged: no event
        row2 = {**row, "status": "idle"}
        self.assertEqual(len(hm.identity_events(seen, [row2])), 1)     # state change: one event
        self.assertEqual(hm.identity_events(seen, [row2]), [])
        unknown = {"pane_id": "w1:p2", "name": "stray", "kind": "grok", "status": "idle", "on_roster": False}
        self.assertEqual(hm.identity_events(seen, [unknown]), [])     # not known: stays unbadged
        proc = {"pane_id": "pid:9", "name": "term", "kind": "grok", "status": "idle", "on_roster": True}
        self.assertEqual(hm.identity_events(seen, [proc]), [])        # a process is not a pane
        self.assertEqual(hm.identity_events(seen, []), [])            # gone: forgotten, no event
        self.assertEqual(seen, {})

    def test_raise_publishes_once_and_adopt_publishes_once(self):
        published = []
        orig = hm.report_identity
        hm.report_identity = lambda pane, name, kind, model="": published.append((pane, name, kind)) or True
        try:
            # adopt: a process-scan row has no herdr pane, so no publish even here
            row = agent("pid:42", "grok", ROOT, "running", "majordomo")
            row["pid"], row["tty"], row["tab_id"] = 42, "ttys002", "w1:t1"
            ctx = hm.Ctx(cwd=ROOT, mode="here", live=OneLive(row), launch=hm.HereLaunch())
            os.environ["COWBELL_STATE_DIR"] = tempfile.mkdtemp()
            hm.cmd_adopt(ctx, CAT, name="majordomo")
            self.assertEqual(published, [])
            # adopt of a herdr pane publishes once
            row = agent("w1B:p5", "grok", ROOT, "idle", "grok-seat")
            ctx = hm.Ctx(cwd=ROOT, mode="here", live=OneLive(row), launch=hm.HereLaunch())
            hm.cmd_adopt(ctx, CAT, name="grok-seat")
            self.assertEqual(published, [("w1B:p5", "grok-seat", "grok")])
            # a raise publishes once with the sitting and harness
            saved = (hm.start_native, hm.save_roster, hm.load_roster, hm.create_tab, hm.pick_workspace)
            hm.create_tab = lambda *a, **k: {"pane_id": "w1C:p1", "tab_id": "w1C:t1", "workspace_id": "w1C"}
            hm.pick_workspace = lambda *a, **k: "w1C"
            hm.start_native = lambda *a, **k: {}
            hm.save_roster = lambda rows: None
            hm.load_roster = lambda: []
            try:
                hm.raise_harness(CAT, hm.harness_by_id(CAT, "grok"), "probe-seat", ROOT,
                                 hm.Ctx(workspace_id="w1C", cwd=ROOT), model="", lane="")
            finally:
                (hm.start_native, hm.save_roster, hm.load_roster, hm.create_tab, hm.pick_workspace) = saved
        finally:
            hm.report_identity = orig
            os.environ.pop("COWBELL_STATE_DIR", None)
        self.assertEqual(published[-1], ("w1C:p1", "probe-seat", "grok"))

    def test_plugin_has_no_reporter(self):
        # LAB-297: no report-metadata clock. keys ensure may run at startup (prefix+c claim).
        plugin = Path(__file__).resolve().parent.parent.parent / "herdr-cowbell" / "herdr-plugin.toml"
        if not plugin.exists():
            self.skipTest("plugin tree not present")
        text = plugin.read_text()
        self.assertNotIn("bt-reporter", text)
        code = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
        self.assertNotIn("report-metadata", code)
        if "[[startup]]" in code:
            self.assertIn('command = ["./bin/cowbell", "keys", "ensure"]', code)


class ResumeOutside(unittest.TestCase):
    """LAB-298: recall in a plain terminal — the session-flag table, honestly filled."""

    def test_claude_resume_with_herdr_down_uses_the_session_flag(self):
        claude = dict(CAT["harness"][0], session_id_flag="--session-id", name_flag="--name")
        cat = {**CAT, "harness": [claude] + [h for h in CAT["harness"] if h["id"] != "claude"]}
        roster = [{"name": "butler", "cwd": ROOT, "harness": "claude", "kind": "claude",
                   "session_id": "abc", "pane_id": None}]
        captured = []
        orig_exec, orig_roster = hm.exec_here, hm.load_roster
        hm.exec_here = lambda *a, **k: captured.append((a, k)) or {"pane_id": "here"}
        hm.load_roster = lambda: roster
        try:
            ctx = hm.Ctx(cwd=ROOT, mode="here", live=hm.LiveSource())   # no herdr anywhere
            hm.cmd_enter(ctx, cat, "butler")
        finally:
            hm.exec_here, hm.load_roster = orig_exec, orig_roster
        self.assertEqual(len(captured), 1)
        args, kwargs = captured[0]
        self.assertEqual(kwargs.get("resume_id"), "abc")               # the roster's session id
        cmd, session = hm.here_command(cat, claude, "butler", resume_id="abc")
        self.assertEqual(session, "abc")
        self.assertIn("--resume", cmd) and self.assertIn("abc", cmd)
        self.assertNotIn("--session-id", cmd)                           # resuming, not starting fresh

    def test_harness_without_a_session_never_appears_in_resume(self):
        roster = [
            {"name": "butler", "cwd": ROOT, "harness": "claude", "kind": "claude",
             "session_id": "abc", "pane_id": None},
            {"name": "grok-seat", "cwd": ROOT, "harness": "grok", "kind": "grok", "pane_id": None},
        ]
        reg = hm.build_registry(CAT, ROOT, [], [], roster, matcher=lambda t: {"verdict": "ok"})
        self.assertEqual([r["name"] for r in reg["cold"]], ["butler", "grok-seat"])   # cold holds both
        payload = hm.registry_json(reg)
        self.assertEqual([r["name"] for r in payload["resume"]], ["butler"])          # Resume: only the flag
        text = hm.render_registry(reg)
        self.assertIn("butler", text)
        self.assertNotIn("grok-seat", text)                        # honestly absent from the resumable list

    def test_seed_documents_the_resume_table(self):
        import tomllib
        seed = Path(__file__).resolve().parent.parent / "harnesses.toml"
        text = seed.read_text()
        cat = tomllib.loads(text)
        self.assertIn("Resuming outside herdr", text)             # the table is documented in the seed
        self.assertIn("honestly absent from Resume", text)
        claude = next(h for h in cat["harness"] if h["id"] == "claude")
        self.assertEqual(claude.get("session_id_flag"), "--session-id")
        # only claude claims a cowbell-chosen session id; the others are honestly absent
        self.assertEqual([h["id"] for h in cat["harness"] if h.get("session_id_flag")], ["claude"])

    def test_seed_documents_unix_user_and_ships_no_place(self):
        import tomllib
        seed = Path(__file__).resolve().parent.parent / "harnesses.toml"
        text = seed.read_text()
        cat = tomllib.loads(text)
        self.assertIn("unix_user", text)
        self.assertIn("require_uid", text)
        self.assertIn("sudo -u", text)
        self.assertNotIn("places", cat)

    def test_cmd_enter_with_target_resumes_directly(self):
        claude = dict(CAT["harness"][0], session_id_flag="--session-id", name_flag="--name")
        cat = {**CAT, "harness": [claude] + [h for h in CAT["harness"] if h["id"] != "claude"]}
        captured = []
        orig_exec, orig_roster = hm.exec_here, hm.load_roster
        hm.exec_here = lambda *a, **k: captured.append((a, k)) or {"pane_id": "here"}
        hm.load_roster = lambda: []  # empty roster
        try:
            ctx = hm.Ctx(cwd=ROOT, mode="here", live=hm.LiveSource())
            target = {"name": "target-sess", "cwd": ROOT, "harness": "claude", "kind": "claude",
                      "session_id": "target-sid", "pane_id": None}
            hm.cmd_enter(ctx, cat, "target-sess", target=target)
        finally:
            hm.exec_here, hm.load_roster = orig_exec, orig_roster
        self.assertEqual(len(captured), 1)
        args, kwargs = captured[0]
        self.assertEqual(kwargs.get("resume_id"), "target-sid")

    def test_cmd_enter_finds_history_session_when_absent_from_roster(self):
        claude = dict(CAT["harness"][0], session_id_flag="--session-id", name_flag="--name")
        cat = {**CAT, "harness": [claude] + [h for h in CAT["harness"] if h["id"] != "claude"]}
        hist_session = {"name": "metawork-history", "cwd": ROOT, "harness": "claude", "kind": "claude",
                        "session_id": "sess-hist-123", "title": "fix parser", "pane_id": None}
        captured = []
        orig_exec, orig_roster, orig_discover = hm.exec_here, hm.load_roster, hm.discover_sessions
        hm.exec_here = lambda *a, **k: captured.append((a, k)) or {"pane_id": "here"}
        hm.load_roster = lambda: []  # empty roster
        hm.discover_sessions = lambda root, cat, home=None: [hist_session]
        try:
            ctx = hm.Ctx(cwd=ROOT, mode="here", live=hm.LiveSource())
            # Find by name
            hm.cmd_enter(ctx, cat, "metawork-history")
            self.assertEqual(captured[-1][1].get("resume_id"), "sess-hist-123")

            # Find by session_id prefix
            hm.cmd_enter(ctx, cat, "sess-hist")
            self.assertEqual(captured[-1][1].get("resume_id"), "sess-hist-123")

            # Find by title
            hm.cmd_enter(ctx, cat, "fix parser")
            self.assertEqual(captured[-1][1].get("resume_id"), "sess-hist-123")

            # Missing session raises SystemExit
            with self.assertRaises(SystemExit) as cm:
                hm.cmd_enter(ctx, cat, "nonexistent")
            self.assertIn("no session 'nonexistent' on roster or in history", str(cm.exception))
        finally:
            hm.exec_here, hm.load_roster, hm.discover_sessions = orig_exec, orig_roster, orig_discover


class StandaloneIdentify(unittest.TestCase):
    """LAB-294: a live CLI is identified by its cwd — harness id + place — with no herdr anywhere."""

    PS = """\
      1     0 ??       /sbin/launchd
    510     1 ttys001  -zsh
    511   510 ttys001  grok
    512     1 ttys002  -zsh
    513   512 ttys002  pi
    514     1 ??       claude --print hello
"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = os.path.realpath(self.tmp.name)
        self.pad = os.path.join(self.home, "cloud", "git-projects", "agent-lobby")
        self.inner = os.path.join(self.pad, "visitors", "inner-pad")
        os.makedirs(self.inner)
        self.cat = {**CAT, "defaults": {"lane": "yellow", "untitled_place": "lobby"},
                    "places": {"lobby": {"cwd": self.pad, "workspace_label": "lobby",
                                         "allow_harness": ["lobby", "claude", "grok"],
                                         "default_harness": "lobby", "lane": "green"},
                               "inner": {"cwd": self.inner, "workspace_label": "lobby",
                                         "allow_harness": ["grok"], "default_harness": "grok",
                                         "lane": "yellow"}}}

    def tearDown(self):
        self.tmp.cleanup()

    def _agents(self, cwd_511, cwd_513):
        cwds = {511: cwd_511, 513: cwd_513}
        return hm.agent_processes(hm.ps_table(self.PS), cwds=lambda pids: {p: cwds[p] for p in pids})

    def test_stub_process_table_identifies_harness_and_place(self):
        agents = self._agents(self.inner, self.inner)
        scoped = hm.scoped_catalog(self.cat, hm.places(self.cat)["inner"])
        reg = hm.build_registry(scoped, self.inner, agents, [], [], matcher=lambda t: {"verdict": "ok"})
        row = next(r for r in reg["live"] if r["kind"] == "grok")
        self.assertEqual(row["harness"], "grok")            # the catalog id, not just the exe
        self.assertEqual(row["place"], "inner")
        self.assertEqual(row["name"], "grok")

    def test_pi_resolves_to_the_one_harness_of_its_kind(self):
        # the lobby place's catalog has exactly one pi harness, so the pi exe is that harness
        agents = self._agents(self.pad, self.pad)
        scoped = hm.scoped_catalog(self.cat, hm.places(self.cat)["lobby"])
        reg = hm.build_registry(scoped, self.pad, agents, [], [], matcher=lambda t: {"verdict": "ok"})
        row = next(r for r in reg["live"] if r["kind"] == "pi")
        self.assertEqual(row["harness"], "lobby")
        self.assertEqual(row["place"], "lobby")

    def test_ambiguous_kind_stays_the_exe_name(self):
        # a place whose catalog has two pi wrappers cannot tell them apart from the exe alone
        cat = {**self.cat, "places": {"lobby": {**self.cat["places"]["lobby"],
                                                "allow_harness": ["oll-mid", "oll-memo"]}}}
        agents = self._agents(self.pad, self.pad)
        scoped = hm.scoped_catalog(cat, hm.places(cat)["lobby"])
        reg = hm.build_registry(scoped, self.pad, agents, [], [], matcher=lambda t: {"verdict": "ok"})
        row = next(r for r in reg["live"] if r["kind"] == "pi")
        self.assertEqual(row["harness"], "pi")

    def test_status_here_names_place_and_harness_with_herdr_down(self):
        # end to end: COWBELL_MODE=here semantics, no herdr binary anywhere in the path
        stub = [{"pane_id": "pid:511", "pid": 511, "tty": "ttys001", "agent": "grok",
                 "cwd": self.inner, "agent_status": "running", "tab_id": None, "workspace_id": None,
                 "terminal_title_stripped": "grok", "agent_session": {}}]
        orig = hm.agent_processes
        hm.agent_processes = lambda table=None, cwds=hm.process_cwds: stub
        try:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                hm.cmd_registry(hm.Ctx(cwd=self.inner, mode="here"), self.cat)
            out = buf.getvalue()
        finally:
            hm.agent_processes = orig
        self.assertIn("inner", out)      # the place
        self.assertIn("grok", out)       # the harness

    def test_registry_json_row_carries_its_own_place(self):
        agents = self._agents(self.inner, self.inner)
        scoped = hm.scoped_catalog(self.cat, hm.places(self.cat)["inner"])
        reg = hm.build_registry(scoped, self.inner, agents, [], [], matcher=lambda t: {"verdict": "ok"})
        payload = hm.registry_json(reg, hm.places(self.cat)["lobby"])   # a wider root place
        running = payload["running"][0]
        self.assertEqual(running["place"], "inner")                     # the row's, not the root's
        self.assertEqual(payload["place"], "lobby")


class Version(unittest.TestCase):
    def test_version_line_is_parseable(self):
        import io, re
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(hm.main(["--version"]), 0)
        self.assertRegex(buf.getvalue(), r"^cowbell \d+\.\d+\.\d+\n$")

    def test_version_needs_no_herdr(self):
        orig = hm.server_up
        hm.server_up = lambda: (_ for _ in ()).throw(AssertionError("server_up called"))
        try:
            import io
            from contextlib import redirect_stdout
            with redirect_stdout(io.StringIO()):
                self.assertEqual(hm.main(["-V"]), 0)
        finally:
            hm.server_up = orig



class Flags(unittest.TestCase):
    def test_parse_flags(self):
        opts, pos = hm.parse_flags(["--harness", "claude", "--lane=green", "--yes", "extra", "--", "--raw"])
        self.assertEqual(opts, {"harness": "claude", "lane": "green", "yes": True})
        self.assertEqual(pos, ["extra", "--raw"])


class NewUsage(unittest.TestCase):
    """LAB-424: `new -h|--help` prints usage and exits 0; an unknown flag exits 2. Neither raises."""

    def setUp(self):
        self._server_up = hm.server_up
        hm.server_up = lambda: (_ for _ in ()).throw(AssertionError("server_up called"))

    def tearDown(self):
        hm.server_up = self._server_up

    def test_help_exits_0_without_raising(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(hm.main(["new", "--help"]), 0)
            self.assertEqual(hm.main(["new", "-h"]), 0)
        text = out.getvalue()
        self.assertIn("cowbell new", text)
        self.assertIn("--harness", text)
        self.assertIn("--split", text)

    def test_unknown_flag_exits_2_with_usage(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(hm.main(["new", "--not-a-real-flag"]), 2)
            self.assertEqual(hm.main(["new", "--bogus", "claude"]), 2)
        text = err.getvalue()
        self.assertIn("unknown flag --not-a-real-flag", text)
        self.assertIn("unknown flag --bogus", text)
        self.assertIn("cowbell new", text)

    def test_double_dash_passthrough_is_not_an_unknown_flag(self):
        pre, passthrough = hm.split_passthrough(["claude", "--", "--resume", "abc"])
        opts, pos = hm.parse_flags(pre)
        self.assertEqual(hm.new_unknown_flags(opts, pos), [])
        self.assertEqual(pos, ["claude"])
        self.assertEqual(passthrough, ["--resume", "abc"])


class Sitting(unittest.TestCase):
    def test_head(self):
        self.assertEqual(hm.sitting_head("builder-minaret"), "builder")
        self.assertEqual(hm.sitting_head("Majordomo"), "majordomo")
        self.assertEqual(hm.sitting_head("coord-cowbell"), "coord")

    def test_grok_claim_only_when_defined(self):
        h = hm.harness_by_id(CAT, "grok")
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "builder.md").write_text("x")
            self.assertEqual(hm.claim_argv(h, "builder-minaret", agents_dir=d), ["--agent", "builder"])
            self.assertEqual(hm.claim_argv(h, "career", agents_dir=d), [])  # no career.md
        self.assertEqual(hm.claim_argv(hm.harness_by_id(CAT, "claude"), "builder-minaret"), [])

    def test_grok_argv_lane_and_claim(self):
        h = hm.harness_by_id(CAT, "grok")
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "builder.md").write_text("x")
            argv = hm.build_argv(CAT, h, lane="yellow", sitting="builder-minaret", agents_dir=d)
        self.assertEqual(argv, ["--permission-mode", "acceptEdits", "--agent", "builder"])

    def test_shell_ready_single_zsh(self):
        two = {"process_info": {"foreground_processes": [
            {"name": "zsh"}, {"name": "zsh"}]}}
        one = {"process_info": {"foreground_processes": [{"name": "zsh"}]}}
        grok = {"process_info": {"foreground_processes": [{"name": "grok"}]}}
        self.assertFalse(hm.shell_ready_from_process(two))
        self.assertTrue(hm.shell_ready_from_process(one))
        self.assertFalse(hm.shell_ready_from_process(grok))

    def test_live_names_are_tab_labels_not_titles(self):
        snap = {
            "tabs": [{"tab_id": "w1:t1", "label": "builder-minaret"},
                     {"tab_id": "w1:t2", "label": "cowbell"}],
            "agents": [
                {"pane_id": "w1:p1", "tab_id": "w1:t1",
                 "terminal_title_stripped": "- Inspect grok flags - Grok 4.6 - herdr-cowbell-core - grok"},
                {"pane_id": "w1:p2", "tab_id": "w1:t2",
                 "terminal_title_stripped": "herdr-cowbell-core"},
            ],
        }
        self.assertEqual(hm.live_names(snap), {"builder-minaret", "cowbell"})


class Seed(unittest.TestCase):
    def test_grok_lanes_and_claim_flag(self):
        import tomllib
        seed = Path(__file__).resolve().parent.parent / "harnesses.toml"
        cat = tomllib.loads(seed.read_text())
        grok = next(h for h in cat["harness"] if h["id"] == "grok")
        self.assertEqual(grok.get("claim_flag"), "--agent")
        self.assertEqual(cat["lanes"]["grok"]["green"], ["--permission-mode", "plan"])
        self.assertEqual(cat["lanes"]["grok"]["yellow"], ["--permission-mode", "acceptEdits"])

    def test_codex_lanes(self):
        import tomllib
        seed = Path(__file__).resolve().parent.parent / "harnesses.toml"
        cat = tomllib.loads(seed.read_text())
        self.assertEqual(cat["lanes"]["codex"]["green"], ["--sandbox", "read-only"])
        self.assertEqual(cat["lanes"]["codex"]["yellow"], ["--sandbox", "workspace-write"])
        self.assertEqual(cat["lanes"]["codex"]["red"],
                         ["--dangerously-bypass-approvals-and-sandbox"])

    def test_seed_is_standard_agents_only(self):
        import tomllib
        seed = Path(__file__).resolve().parent.parent / "harnesses.toml"
        cat = tomllib.loads(seed.read_text())
        self.assertFalse([h["id"] for h in cat["harness"] if "command" in h])   # no house wrappers
        self.assertFalse(cat["defaults"]["ask_name"])


class EmptyLive(hm.LiveSource):
    def snapshot(self):
        return {"agents": [], "tabs": []}


class OneLive(hm.LiveSource):
    def __init__(self, row):
        self.row = row

    def agents(self):
        return [self.row]

    def snapshot(self):
        return {"agents": [self.row], "tabs": [{"tab_id": self.row.get("tab_id"), "label": "majordomo"}]}


class RaiseCLI(unittest.TestCase):
    """LAB-296: new --place --harness --name is the assembly primitive; N raises return."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.place = Path(self.tmp.name) / "lab"
        self.place.mkdir()
        self.state = Path(self.tmp.name) / "state"
        self.state.mkdir()
        os.environ["COWBELL_STATE_DIR"] = str(self.state)
        self.addCleanup(lambda: os.environ.pop("COWBELL_STATE_DIR", None))
        warnings.filterwarnings("ignore", category=ResourceWarning)
        (self.state / "roster.json").write_text(json.dumps({"schema": 1, "harnesses": []}))
        self.cat = {
            "defaults": {"lane": "yellow"},
            "lanes": {},
            "places": {"lab": {"cwd": str(self.place)}},
            "harness": [{
                "id": "true", "kind": "true", "family": "true", "egress": "local",
                "trust_tool": "true", "models": [],
            }],
        }
        self._gate = hm.gate
        hm.gate = lambda *a, **k: {"verdict": "ok"}
        self.addCleanup(lambda: setattr(hm, "gate", self._gate))

    def test_spawn_flag(self):
        opts, _ = hm.parse_flags(["--spawn", "--name", "seat-a", "--place", "lab"])
        self.assertTrue(opts.get("spawn"))
        self.assertEqual(opts.get("name"), "seat-a")

    def test_n_spawn_raises_distinct_pids_and_roster(self):
        ctx = hm.Ctx(cwd="/tmp", mode="here", live=EmptyLive(), launch=hm.HereLaunch())
        hm.cmd_new(ctx, self.cat, "true", name="seat-a", place="lab", spawn=True, no_seat=True, assume_yes=True)
        hm.cmd_new(ctx, self.cat, "true", name="seat-b", place="lab", spawn=True, no_seat=True, assume_yes=True)
        rows = {r["name"]: r for r in hm.load_roster()}
        self.assertEqual(set(rows), {"seat-a", "seat-b"})
        root = str(self.place.resolve())
        self.assertEqual(rows["seat-a"]["cwd"], root)
        self.assertEqual(rows["seat-b"]["cwd"], root)
        self.assertEqual(rows["seat-a"]["harness"], "true")
        self.assertNotEqual(rows["seat-a"]["pane_id"], rows["seat-b"]["pane_id"])
        self.assertTrue(str(rows["seat-a"]["pane_id"]).startswith("pid:"))
        self.assertTrue(str(rows["seat-b"]["pane_id"]).startswith("pid:"))
        for r in rows.values():
            try:
                os.waitpid(int(str(r["pane_id"]).split(":")[1]), 0)
            except ChildProcessError:
                pass

    def test_here_launch_auto_spawns_when_not_a_tty(self):
        host = hm.HereLaunch()
        self.assertFalse(host.tabs)


class Adopt(unittest.TestCase):
    """LAB-293: cowbell adopt is a core command; no herdr required for a process-scan row."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state = Path(self.tmp.name) / "state"
        self.state.mkdir()
        os.environ["COWBELL_STATE_DIR"] = str(self.state)
        self.addCleanup(lambda: os.environ.pop("COWBELL_STATE_DIR", None))
        (self.state / "roster.json").write_text(json.dumps({"schema": 1, "harnesses": []}))
        self.row = agent("pid:42", "grok", ROOT, "running", "majordomo")
        self.row["pid"] = 42
        self.row["tty"] = "ttys002"
        self.row["tab_id"] = "w1:t1"
        self.ctx = hm.Ctx(cwd=ROOT, mode="here", live=OneLive(self.row), launch=hm.HereLaunch())

    def test_adopt_help(self):
        rc = hm.main(["adopt", "--help"])
        self.assertEqual(rc, 0)

    def test_adopt_writes_roster_and_status_running(self):
        row = hm.cmd_adopt(self.ctx, CAT, name="majordomo")
        self.assertEqual(row["name"], "majordomo")
        self.assertEqual(row["harness"], "grok")
        self.assertEqual(row["source"], "adopt")
        self.assertEqual(row["pane_id"], "pid:42")
        roster = hm.load_roster()
        self.assertEqual(len(roster), 1)
        self.assertEqual(roster[0]["name"], "majordomo")
        reg = hm.build_registry(CAT, ROOT, [self.row], [{"pane_id": "pid:42"}], roster,
                                matcher=lambda _t: {"verdict": "ok"})
        self.assertEqual(reg["live"][0]["name"], "majordomo")
        self.assertTrue(reg["live"][0]["on_roster"])
        payload = hm.registry_json(reg)
        self.assertEqual(payload["running"][0]["name"], "majordomo")
        self.assertEqual(payload["running"][0]["harness"], "grok")

    def test_adopt_pane_flag(self):
        hm.cmd_adopt(self.ctx, CAT, pane_id="pid:42")
        self.assertEqual(hm.load_roster()[0]["pane_id"], "pid:42")

    def test_adopt_missing_pane(self):
        with self.assertRaises(SystemExit) as e:
            hm.cmd_adopt(self.ctx, CAT, pane_id="w9:p9")
        self.assertIn("no live agent", str(e.exception))

    def test_adopt_uses_snapshot_focused_pane(self):
        """agent list often has focused=False on every row; snapshot has focused_pane_id."""
        grok = agent("wK:p1", "grok", ROOT, "working", "majordomo")
        grok["focused"] = False
        grok["tab_id"] = "wK:t1"
        claude = agent("wK:p6", "claude", ROOT, "idle", "sysadmin")
        claude["focused"] = False
        claude["tab_id"] = "wK:t6"

        class SnapLive(hm.LiveSource):
            def agents(self):
                return [grok, claude]

            def snapshot(self):
                return {"focused_pane_id": "wK:p6", "panes": [
                    {**grok, "focused": False}, {**claude, "focused": True},
                ]}

        ctx = hm.Ctx(cwd=ROOT, mode="tab", pane_id="wK:p9", live=SnapLive(), launch=hm.HereLaunch())
        row = hm.cmd_adopt(ctx, CAT)
        self.assertEqual(row["pane_id"], "wK:p6")
        self.assertEqual(row["harness"], "claude")

    def _two_unfocused(self):
        grok = agent("wK:pK", "grok", str(Path.home()), "idle", "metawork")
        grok["focused"] = False
        grok["tab_id"] = "wK:tK"
        grok["name"] = "metawork"
        claude = agent("wK:p6", "claude", str(Path.home()), "idle", "coord")
        claude["focused"] = False
        claude["tab_id"] = "wK:t6"
        claude["name"] = "coord-career"

        class TwoLive(hm.LiveSource):
            def agents(self):
                return [grok, claude]

            def snapshot(self):
                return {
                    "focused_pane_id": "wK:p9",  # the shell where adopt was typed
                    "panes": [{"pane_id": "wK:p9", "focused": True}],
                    "tabs": [{"tab_id": "wK:tK", "label": "metawork"},
                             {"tab_id": "wK:t6", "label": "coord-career"}],
                }

        ctx = hm.Ctx(cwd=ROOT, mode="tab", pane_id="wK:p9", live=TwoLive(), launch=hm.HereLaunch())
        return ctx, grok, claude

    def test_adopt_from_shell_needs_a_target(self):
        """Typing adopt in a shell: that shell is focused, and there are several agents."""
        ctx, grok, claude = self._two_unfocused()
        with self.assertRaises(SystemExit) as e:
            hm.cmd_adopt(ctx, CAT)
        msg = str(e.exception)
        self.assertIn("no focused agent pane to adopt", msg)
        self.assertIn("wK:pK", msg)
        self.assertIn("metawork", msg)
        self.assertNotIn("Live here:", msg)  # those agents sit at ~, not under ROOT
        self.assertIn("Live:", msg)

    def test_adopt_positional_pane_id(self):
        ctx, grok, claude = self._two_unfocused()
        row = hm.cmd_adopt(ctx, CAT, name="wK:pK")
        self.assertEqual(row["pane_id"], "wK:pK")
        self.assertEqual(row["name"], "metawork")  # pane id is identity, not the sitting
        self.assertEqual(row["harness"], "grok")

    def test_adopt_positional_sitting(self):
        ctx, grok, claude = self._two_unfocused()
        row = hm.cmd_adopt(ctx, CAT, name="coord-career")
        self.assertEqual(row["pane_id"], "wK:p6")
        self.assertEqual(row["name"], "coord-career")

    def test_picker_a_adopts_the_highlighted_running_row(self):
        grok = {"name": "metawork", "harness": "grok", "kind": "grok", "status": "idle",
                "pane_id": "wK:pK", "workspace_id": "wK"}
        resume = {"name": "old", "harness": "claude", "kind": "claude", "pane_id": "wK:p1"}
        running = {"action": "focus", "target": grok}
        cold = {"action": "enter", "target": resume}
        self.assertEqual(hm.adopt_pane_from_choice(running), "wK:pK")
        self.assertIsNone(hm.adopt_pane_from_choice(cold))
        self.assertIsNone(hm.adopt_pane_from_choice(None))

    def test_picker_a_adopts_from_the_active_census(self):
        """Active is not a menu. `a` still adopts the focused agent, or the only one."""
        live = [
            {"pane_id": "wK:pK", "name": "metawork"},
            {"pane_id": "wK:p6", "name": "coord-career"},
        ]
        resume = {"action": "enter", "target": {"pane_id": "wK:p1"}}
        self.assertEqual(hm.adopt_pane_for_picker(resume, live, "wK:p6"), "wK:p6")
        self.assertIsNone(hm.adopt_pane_for_picker(None, live, "wK:p9"))  # popup, not an agent
        self.assertEqual(hm.adopt_pane_for_picker(None, [live[0]], "wK:p9"), "wK:pK")
        self.assertEqual(hm.adopt_picker_flash(2), "several running — cowbell adopt <name>")
        self.assertEqual(hm.adopt_picker_flash(0), "no running sitting here to adopt")


class ExtensionPoints(unittest.TestCase):
    """The two hooks onto tools cowbell does not own (LAB-318)."""

    def setUp(self):
        self._ext = dict(hm.EXT)

    def tearDown(self):
        hm.EXT.clear(); hm.EXT.update(self._ext)

    def test_defaults_are_not_house_specific(self):
        self.assertEqual(hm.EXT["trust_command"], "harness-trust")
        self.assertEqual(hm.EXT["seat_file"], "SEAT.md")

    def test_catalog_overrides_both(self):
        hm.apply_ext({"defaults": {"trust_command": "my-checker", "seat_file": "BRIEF.md"}})
        self.assertEqual(hm.EXT["trust_command"], "my-checker")
        self.assertEqual(hm.EXT["seat_file"], "BRIEF.md")

    def test_blank_override_keeps_the_default(self):
        hm.apply_ext({"defaults": {"trust_command": "   "}})
        self.assertEqual(hm.EXT["trust_command"], "harness-trust")

    def test_missing_checker_means_no_verdicts(self):
        hm.EXT["trust_command"] = "cowbell-no-such-checker-xyz"
        self.assertFalse(hm.trust_available())
        self.assertEqual(hm.trust_subject("/tmp"), "?")
        self.assertEqual(hm.trust_badge("claude"), "?")
        self.assertEqual(hm.trust_match("claude", "/tmp")["verdict"], "unknown")

    def test_seat_file_honours_the_configured_name(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "BRIEF.md").write_text("brief\n")
            self.assertIsNone(hm.seat_file(td, home=td))
            hm.EXT["seat_file"] = "BRIEF.md"
            found = hm.seat_file(td, home=str(Path(td).parent))
            self.assertEqual(Path(found).name, "BRIEF.md")

    def test_both_spellings_of_the_prompt_flag(self):
        self.assertEqual(hm.prompt_flag({"system_prompt_flag": "--sys"}), "--sys")
        self.assertEqual(hm.prompt_flag({"seat_flag": "--old"}), "--old")
        self.assertEqual(hm.prompt_flag({"system_prompt_flag": "--sys", "seat_flag": "--old"}), "--sys")
        self.assertIsNone(hm.prompt_flag({}))


class SessionHistory(unittest.TestCase):
    """Discovery from each harness's own store (LAB-355)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        self.root = "/Users/x/code/acme"
        self.cat = {"defaults": {"session_history": "on"}, "harness": [{"id": "claude"}, {"id": "grok"}]}
        # a claude store: project dir is the cwd with / and . flattened to -
        cdir = self.home / ".claude" / "projects" / "-Users-x-code-acme"
        cdir.mkdir(parents=True)
        (cdir / "sess-a.jsonl").write_text(
            json.dumps({"type": "user", "timestamp": "2026-09-01T10:00:00Z",
                        "message": {"role": "user", "content": "fix the parser"}}) + "\n" +
            json.dumps({"type": "custom-title", "customTitle": "parser-work"}) + "\n" +
            json.dumps({"type": "assistant", "timestamp": "2026-09-02T11:00:00Z"}) + "\n")
        (cdir / "sess-b.jsonl").write_text(
            json.dumps({"type": "user", "timestamp": "2026-08-01T10:00:00Z",
                        "message": {"role": "user", "content": [{"type": "text", "text": "Caveat: injected"},
                                                                 {"type": "text", "text": "ignored"}]}}) + "\n")
        (cdir / "broken.jsonl").write_text("{not json\n")
        # a grok store: session dirs under the percent-encoded cwd
        gdir = self.home / ".grok" / "sessions" / "%2FUsers%2Fx%2Fcode%2Facme" / "01a0"
        gdir.mkdir(parents=True)
        (gdir / "chat_history.jsonl").write_text(
            json.dumps({"type": "system", "content": "you are grok"}) + "\n" +
            json.dumps({"type": "user", "content": [{"type": "text", "text": "<user_query>ship it</user_query>"}]}) + "\n")

    def tearDown(self):
        self.tmp.cleanup()

    def rows(self, cat=None):
        return hm.discover_sessions(self.root, cat or self.cat, home=self.home)

    def test_off_by_default(self):
        self.assertEqual(hm.discover_sessions(self.root, {"harness": [{"id": "claude"}]}, home=self.home), [])

    def test_finds_both_stores(self):
        got = {(r["harness"], r["session_id"]) for r in self.rows()}
        self.assertIn(("claude", "sess-a"), got)
        self.assertIn(("claude", "sess-b"), got)
        self.assertIn(("grok", "01a0"), got)

    def test_titles_prefer_rename_and_skip_injected(self):
        by_id = {r["session_id"]: r for r in self.rows()}
        self.assertEqual(by_id["sess-a"]["title"], "parser-work")
        self.assertEqual(by_id["sess-b"]["title"], "")          # "Caveat:" is the harness talking
        self.assertEqual(by_id["01a0"]["title"], "ship it")     # user_query unwrapped

    def test_malformed_file_does_not_break_discovery(self):
        self.assertIn("broken", {r["session_id"] for r in self.rows()})

    def test_missing_store_is_quiet(self):
        self.assertEqual(hm.discover_sessions("/Users/x/nowhere", self.cat, home=self.home), [])

    def test_catalog_governs_which_stores_are_read(self):
        only_grok = {"defaults": {"session_history": "on"}, "harness": [{"id": "grok"}]}
        self.assertEqual({r["harness"] for r in self.rows(only_grok)}, {"grok"})

    def test_duplicate_titles_stay_distinct_names(self):
        cdir = self.home / ".claude" / "projects" / "-Users-x-code-acme"
        (cdir / "sess-c.jsonl").write_text(
            json.dumps({"type": "custom-title", "customTitle": "parser-work"}) + "\n")
        (cdir / "sess-d.jsonl").write_text(
            json.dumps({"type": "custom-title", "customTitle": "parser-work"}) + "\n")
        named = [r for r in self.rows() if r["session_id"] in ("sess-a", "sess-c", "sess-d")]
        names = [r["name"] for r in named]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all(n.startswith("parser-work") for n in names))

    def test_newest_first(self):
        stamps = [r.get("last") or "" for r in self.rows()]
        self.assertEqual(stamps, sorted(stamps, reverse=True))

    def test_roster_row_wins_over_a_discovered_one(self):
        roster = [{"name": "adopted", "harness": "claude", "session_id": "sess-a", "cwd": self.root,
                   "last_seen": "2026-09-02", "pane_id": "w1:p1"}]
        cat = {"harness": [{"id": "claude", "kind": "claude", "family": "claude", "trust_tool": "claude",
                            "egress": "vendor", "models": [], "resume": []}]}
        reg = hm.build_registry(cat, self.root, [], [], roster,
                                matcher=lambda _t: {"verdict": "ok"}, history=self.rows())
        rows = [r for r in reg["cold"] if r.get("session_id") == "sess-a"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "adopted")

    def test_cmd_enter_resumes_discovered_history_session(self):
        cat = {**CAT, "defaults": {"session_history": "on"}}
        captured = []
        orig_exec, orig_roster, orig_discover = hm.exec_here, hm.load_roster, hm.discover_sessions
        hm.exec_here = lambda *a, **k: captured.append((a, k)) or {"pane_id": "here"}
        hm.load_roster = lambda: []
        hm.discover_sessions = lambda r, c, home=None: orig_discover(r, c, home=self.home)
        try:
            ctx = hm.Ctx(cwd=self.root, mode="here", live=hm.LiveSource())
            hm.cmd_enter(ctx, cat, "parser-work")
        finally:
            hm.exec_here, hm.load_roster, hm.discover_sessions = orig_exec, orig_roster, orig_discover
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0][1].get("resume_id"), "sess-a")


class UnixConfine(unittest.TestCase):
    """Place unix_user: drop uid (and optional nono) before exec."""

    def test_no_place_is_passthrough(self):
        cmd = ["grok", "--foo"]
        self.assertEqual(hm.unix_confine(CAT, "/tmp", cmd), cmd)

    def test_require_uid_without_user_refuses(self):
        tmp = tempfile.mkdtemp()
        cat = {**CAT, "places": {"lab": {"cwd": tmp, "require_uid": True}}}
        with self.assertRaises(SystemExit) as e:
            hm.unix_confine(cat, tmp, ["bash"])
        self.assertIn("unix_user", str(e.exception))

    def test_unknown_uid_refuses(self):
        tmp = tempfile.mkdtemp()
        cat = {**CAT, "places": {"lab": {"cwd": tmp, "unix_user": "no-such-agent-uid-xyz"}}}
        with self.assertRaises(SystemExit) as e:
            hm.unix_confine(cat, tmp, ["bash"])
        self.assertIn("not on this host", str(e.exception))

    def _as_user(self, which, euid=0, pw_uid=4242):
        pw = mock.Mock(pw_uid=pw_uid)
        return (
            mock.patch("pwd.getpwnam", return_value=pw),
            mock.patch.object(hm.os, "geteuid", return_value=euid),
            mock.patch.object(hm.shutil, "which", side_effect=lambda name: which.get(name)),
        )

    def test_agent_run_prefixes_when_present(self):
        tmp = tempfile.mkdtemp()
        cat = {**CAT, "places": {"lab": {"cwd": tmp, "unix_user": "lab"}}}
        patches = self._as_user({"agent-run": "/usr/local/bin/agent-run"})
        with patches[0], patches[1], patches[2]:
            out = hm.unix_confine(cat, tmp, ["/bin/bash"])
        self.assertEqual(out, ["/usr/local/bin/agent-run", "lab", "--", "/bin/bash"])

    def test_sudo_substitutes_when_agent_run_is_absent(self):
        tmp = tempfile.mkdtemp()
        cat = {**CAT, "places": {"lab": {"cwd": tmp, "unix_user": "lab"}}}
        patches = self._as_user({"sudo": "/usr/bin/sudo"})
        with patches[0], patches[1], patches[2]:
            out = hm.unix_confine(cat, tmp, ["/bin/bash"])
        self.assertEqual(out, ["/usr/bin/sudo", "-u", "lab", "--", "/bin/bash"])

    def test_neither_helper_refuses(self):
        tmp = tempfile.mkdtemp()
        cat = {**CAT, "places": {"lab": {"cwd": tmp, "unix_user": "lab"}}}
        patches = self._as_user({})
        with patches[0], patches[1], patches[2]:
            with self.assertRaises(SystemExit) as e:
                hm.unix_confine(cat, tmp, ["/bin/bash"])
        self.assertIn("sudo is not on PATH", str(e.exception))

    def test_same_uid_skips_the_drop(self):
        tmp = tempfile.mkdtemp()
        cat = {**CAT, "places": {"lab": {"cwd": tmp, "unix_user": "lab"}}}
        patches = self._as_user({"sudo": "/usr/bin/sudo"}, euid=4242, pw_uid=4242)
        with patches[0], patches[1], patches[2]:
            out = hm.unix_confine(cat, tmp, ["/bin/bash"])
        self.assertEqual(out, ["/bin/bash"])

    def test_nono_wraps_inside_the_uid_drop(self):
        tmp = tempfile.mkdtemp()
        cat = {**CAT, "places": {"lab": {
            "cwd": tmp, "unix_user": "lab", "nono_profile": "~/lab.json",
        }}}
        patches = self._as_user({"sudo": "/usr/bin/sudo", "nono": "/usr/bin/nono"})
        with patches[0], patches[1], patches[2]:
            out = hm.unix_confine(cat, tmp, ["/bin/bash"])
        self.assertEqual(out, [
            "/usr/bin/sudo", "-u", "lab", "--",
            "/usr/bin/nono", "run", "--silent", "--profile",
            os.path.expanduser("~/lab.json"), "--allow-cwd", "--", "/bin/bash",
        ])


class CatalogWriter(unittest.TestCase):
    """LAB-254: splice [[harness]] blocks, keep comments, backup first."""

    SEED = Path(__file__).resolve().parent.parent / "harnesses.toml"
    HOUSE = Path.home() / ".config" / "cowbell" / "harnesses.toml"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.state = self.dir / "state"
        self._saved_state = os.environ.get("COWBELL_STATE_DIR")
        os.environ["COWBELL_STATE_DIR"] = str(self.state)

    def tearDown(self):
        if self._saved_state is None:
            os.environ.pop("COWBELL_STATE_DIR", None)
        else:
            os.environ["COWBELL_STATE_DIR"] = self._saved_state
        self.tmp.cleanup()

    def _copy(self, src: Path) -> Path:
        dest = self.dir / "harnesses.toml"
        shutil.copy2(src, dest)
        return dest

    def _load(self, p: Path) -> dict:
        with open(p, "rb") as fh:
            return tomllib.load(fh)

    def _outside(self, text: str, hid: str) -> str:
        span = next(s for s in hm.harness_blocks(text) if s["id"] == hid)
        return text[:span["start"]] + text[span["end"]:]

    def _baks(self, p: Path) -> list[Path]:
        return sorted(p.parent.glob(p.name + ".bak-*"))

    def test_set_field_keeps_comments_on_seed(self):
        p = self._copy(self.SEED)
        before = p.read_text(encoding="utf-8")
        parsed = self._load(p)
        hm.harness_set_field("claude", "title", "Claude Code (edited)", path=p)
        after = p.read_text(encoding="utf-8")
        self.assertIn("# cowbell — which agents can be started", after)
        self.assertIn("system_prompt_flag = \"--append-system-prompt-file\"   # used only when", after)
        self.assertIn('id = "grok"', after)
        self.assertEqual(self._outside(before, "claude"), self._outside(after, "claude"))
        got = self._load(p)
        self.assertEqual(got["harness"][0]["title"], "Claude Code (edited)")
        parsed["harness"][0]["title"] = "Claude Code (edited)"
        self.assertEqual(got, parsed)
        baks = self._baks(p)
        self.assertEqual(len(baks), 1)
        self.assertEqual(baks[0].read_text(encoding="utf-8"), before)

    def test_set_field_keeps_inline_comment_on_the_same_line(self):
        p = self._copy(self.SEED)
        hm.harness_set_field("claude", "session_id_flag", "--sid", path=p)
        line = next(ln for ln in p.read_text(encoding="utf-8").splitlines()
                    if ln.startswith("session_id_flag"))
        self.assertIn("# outside herdr:", line)
        self.assertIn('"--sid"', line)

    def test_noop_replace_keeps_tomllib_and_bytes_outside_the_block(self):
        p = self._copy(self.SEED)
        before = p.read_text(encoding="utf-8")
        parsed = self._load(p)
        claude = next(h for h in parsed["harness"] if h["id"] == "claude")
        hm.harness_replace("claude", dict(claude), path=p)
        after = p.read_text(encoding="utf-8")
        self.assertEqual(self._load(p), parsed)
        self.assertEqual(self._outside(before, "claude"), self._outside(after, "claude"))
        self.assertEqual(self._baks(p)[0].read_text(encoding="utf-8"), before)

    def test_insert_then_delete_restores_seed_bytes(self):
        p = self._copy(self.SEED)
        before = p.read_bytes()
        hm.harness_insert({"id": "lab-probe", "kind": "bash", "title": "probe",
                           "command": "/bin/bash", "resume": []}, path=p)
        ids = [h["id"] for h in self._load(p)["harness"]]
        self.assertIn("lab-probe", ids)
        self.assertIn("# cowbell — which agents can be started", p.read_text(encoding="utf-8"))
        hm.harness_delete("lab-probe", path=p)
        self.assertEqual(p.read_bytes(), before)

    def test_delete_missing_id_is_noop(self):
        p = self._copy(self.SEED)
        before = p.read_bytes()
        hm.harness_delete("no-such-harness", path=p)
        self.assertEqual(p.read_bytes(), before)
        self.assertEqual(self._baks(p), [])

    def test_failed_write_leaves_prior(self):
        p = self._copy(self.SEED)
        prior = p.read_bytes()
        orig = hm.write_atomic

        def boom(path, text):
            raise OSError("disk full")

        hm.write_atomic = boom
        try:
            with self.assertRaises(OSError):
                hm.harness_set_field("claude", "title", "nope", path=p)
        finally:
            hm.write_atomic = orig
        self.assertEqual(p.read_bytes(), prior)
        self.assertEqual(self._baks(p)[0].read_bytes(), prior)

    def test_newer_schema_refuses_write(self):
        p = self._copy(self.SEED)
        text = p.read_text(encoding="utf-8").replace("schema = 1", f"schema = {hm.SCHEMA + 1}", 1)
        p.write_text(text, encoding="utf-8")
        prior = p.read_bytes()
        with self.assertRaises(hm.SchemaError):
            hm.harness_set_field("claude", "title", "nope", path=p)
        self.assertEqual(p.read_bytes(), prior)
        self.assertEqual(self._baks(p), [])

    def test_set_field_adds_a_missing_key(self):
        p = self._copy(self.SEED)
        hm.harness_set_field("gemini", "family", "gemini", path=p)
        gem = next(h for h in self._load(p)["harness"] if h["id"] == "gemini")
        self.assertEqual(gem["family"], "gemini")
        self.assertIn("family = \"gemini\"", p.read_text(encoding="utf-8"))

    def test_insert_duplicate_id_refuses(self):
        p = self._copy(self.SEED)
        prior = p.read_bytes()
        with self.assertRaises(SystemExit) as e:
            hm.harness_insert({"id": "claude", "kind": "claude"}, path=p)
        self.assertIn("already exists", str(e.exception))
        self.assertEqual(p.read_bytes(), prior)

    @unittest.skipUnless(
        (Path.home() / ".config" / "cowbell" / "harnesses.toml").is_file(),
        "no patron config-dir catalog on this host",
    )
    def test_round_trip_on_patron_catalog_copy(self):
        p = self._copy(self.HOUSE)
        before = p.read_text(encoding="utf-8")
        parsed = self._load(p)
        self.assertIn("# cowbell — the constitution of the herd.", before)
        self.assertIn("[places.lobby]", before)
        self.assertIn("unix_user = \"guest\"", before)
        hm.harness_set_field("local-ornith", "title", "ornith 9b — edited", path=p)
        after = p.read_text(encoding="utf-8")
        self.assertIn("# cowbell — the constitution of the herd.", after)
        self.assertIn("# House wrappers", after)
        self.assertIn("[places.lobby]", after)
        self.assertIn("unix_user = \"guest\"", after)
        self.assertIn("# --- aider on OpenRouter", after)
        self.assertEqual(self._outside(before, "local-ornith"), self._outside(after, "local-ornith"))
        got = self._load(p)
        self.assertEqual(got["harness"][4]["id"], "local-ornith")
        self.assertEqual(got["harness"][4]["title"], "ornith 9b — edited")
        parsed["harness"][4]["title"] = "ornith 9b — edited"
        self.assertEqual(got, parsed)
        self.assertEqual(self._baks(p)[0].read_text(encoding="utf-8"), before)
        hm.harness_insert({"id": "lab-probe", "kind": "bash", "title": "probe",
                           "command": "/bin/true"}, path=p)
        self.assertIn("[places.local-lab]", p.read_text(encoding="utf-8"))
        hm.harness_delete("lab-probe", path=p)
        # title edit remains; probe is gone; places comments still there
        self.assertNotIn("lab-probe", p.read_text(encoding="utf-8"))
        self.assertIn("[places.lobby]", p.read_text(encoding="utf-8"))
        self.assertIn("ornith 9b — edited", p.read_text(encoding="utf-8"))


class Pins(unittest.TestCase):
    """LAB-255: pin/hide per directory in state, overlay rank_harnesses, leave the catalog alone."""

    SEED = Path(__file__).resolve().parent.parent / "harnesses.toml"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.state = base / "state" / "cowbell"
        self.cfg = base / "cfg" / "cowbell"
        self.a = str(base / "proj-a")
        self.b = str(base / "proj-b")
        os.makedirs(self.a)
        os.makedirs(self.b)
        self.cfg.mkdir(parents=True)
        self.state.mkdir(parents=True)
        self.catalog = self.cfg / "harnesses.toml"
        shutil.copy2(self.SEED, self.catalog)
        self.env = {"COWBELL_STATE_DIR": str(self.state), "COWBELL_CONFIG_DIR": str(self.cfg)}
        self.saved = {k: os.environ.get(k) for k in self.env}
        os.environ.update(self.env)
        self.ids = ["claude", "grok", "pi", "agy"]
        self.roster = [{"harness": "grok", "cwd": "/Users/x/other", "last_seen": "2026-09-12"},
                       {"harness": "pi", "cwd": self.a, "last_seen": "2026-09-01"}]

    def tearDown(self):
        for k, v in self.saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()

    def _digest(self) -> str:
        return hashlib.sha256(self.catalog.read_bytes()).hexdigest()

    def test_pin_sorts_first_and_stays_in_one_directory(self):
        before = hm.rank_harnesses(self.ids, self.roster, self.a)
        self.assertEqual(before[0], "pi")  # usage here
        hm.pin_harness(self.a, "agy")
        self.assertEqual(hm.rank_harnesses(self.ids, self.roster, self.a)[0], "agy")
        self.assertEqual(hm.rank_harnesses(self.ids, self.roster, self.b),
                         hm.rank_harnesses(self.ids, self.roster, self.b, prefs={"pin": [], "hide": []}))
        data = json.loads((self.state / "pins.json").read_text())
        self.assertEqual(data["schema"], 1)
        self.assertEqual(data["dirs"][os.path.realpath(self.a)]["agy"], "pin")
        self.assertNotIn(os.path.realpath(self.b), data["dirs"])

    def test_hide_omits_from_start_new_in_that_directory(self):
        hm.hide_harness(self.a, "grok")
        ranked_a = hm.rank_harnesses(self.ids, self.roster, self.a)
        ranked_b = hm.rank_harnesses(self.ids, self.roster, self.b)
        self.assertNotIn("grok", ranked_a)
        self.assertIn("grok", ranked_b)

    def test_widen_root_uses_the_widened_directory_prefs(self):
        git_top = str(Path(self.a).parent)
        os.makedirs(git_top, exist_ok=True)
        hm.pin_harness(git_top, "claude")
        hm.hide_harness(self.a, "claude")
        self.assertNotIn("claude", hm.rank_harnesses(self.ids, self.roster, self.a))
        self.assertEqual(hm.rank_harnesses(self.ids, self.roster, git_top)[0], "claude")

    def test_pin_hide_do_not_touch_the_catalog(self):
        digest = self._digest()
        hm.pin_harness(self.a, "claude")
        hm.hide_harness(self.a, "agy")
        hm.pin_harness(self.b, "pi")
        hm.clear_pref(self.a, "claude")
        self.assertEqual(self._digest(), digest)

    def test_delete_drops_orphan_pin_hide(self):
        hm.pin_harness(self.a, "claude")
        hm.hide_harness(self.b, "claude")
        hm.harness_delete("claude", path=self.catalog)
        data = json.loads((self.state / "pins.json").read_text())
        self.assertNotIn("claude", json.dumps(data))
        self.assertEqual(data["dirs"], {})
        ids = [h["id"] for h in tomllib.loads(self.catalog.read_text())["harness"]]
        self.assertNotIn("claude", ids)

    def test_pin_beats_place_default(self):
        ranked = hm.rank_harnesses(["claude", "grok", "lobby"], self.roster, self.a,
                                   default="lobby", prefs={"pin": ["grok"], "hide": []})
        self.assertEqual(ranked[0], "grok")
        self.assertEqual(ranked[1], "lobby")

    def test_picker_start_section_follows_pin_and_hide(self):
        hm.pin_harness(self.a, "agy")
        hm.hide_harness(self.a, "claude")
        startable = [{"harness": h, "title": h, "installed": True, "trust": {"verdict": "ok"}}
                     for h in self.ids]
        reg = {"live": [], "cold": [], "startable": startable, "absent": startable,
               "root": self.a, "default_harness": ""}
        start = [c for c in hm.picker_choices(reg, self.roster) if c["section"] == "start"]
        hids = [c["target"]["harness"] for c in start if c.get("action") == "raise"]
        self.assertEqual(hids[0], "agy")
        self.assertNotIn("claude", hids)


class PickerEdit(unittest.TestCase):
    """LAB-256: save-as / edit / add / remove / hints; Esc writes nothing; comments kept."""

    SEED = Path(__file__).resolve().parent.parent / "harnesses.toml"
    HOUSE = Path.home() / ".config" / "cowbell" / "harnesses.toml"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.cfg = base / "cfg"
        self.state = base / "state"
        self.cfg.mkdir()
        self.state.mkdir()
        self.catalog = self.cfg / "harnesses.toml"
        shutil.copy2(self.SEED, self.catalog)
        self.env = {"COWBELL_CONFIG_DIR": str(self.cfg), "COWBELL_STATE_DIR": str(self.state)}
        self.saved = {k: os.environ.get(k) for k in self.env}
        os.environ.update(self.env)
        self.root = str(base / "proj")
        os.makedirs(self.root)

    def tearDown(self):
        for k, v in self.saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()

    def _text(self) -> str:
        return self.catalog.read_text(encoding="utf-8")

    def test_models_with_default_leads(self):
        self.assertEqual(hm.models_with_default(["a", "b", "c"], "b"), ["b", "a", "c"])
        self.assertEqual(hm.models_with_default(["a"], "z"), ["z", "a"])
        self.assertEqual(hm.models_with_default([], "z"), ["z"])

    def test_picker_hints_row_actions_only_on_start(self):
        start = {ev for *_, ev in hm.picker_hints(False, True)}
        other = {ev for *_, ev in hm.picker_hints(False, False)}
        self.assertTrue({"e", "p", "h", "-", "+", "n", "a", "enter", "esc"}.issubset(start))
        self.assertFalse({"e", "p", "h", "-"} & other)
        self.assertTrue({"+", "n", "a", "enter", "esc"}.issubset(other))
        self.assertIn("g", {ev for *_, ev in hm.picker_hints(True, False)})
        self.assertNotIn("g", other)
        _, spans = hm.hint_bar(hm.picker_hints(False, True))
        self.assertLessEqual(spans[-1][1], 80)

    def test_save_as_inserts_and_keeps_seed_comments(self):
        src = hm.harness_by_id(hm.load_catalog(), "claude")
        with mock.patch("cowbell.ask", return_value="lab-sonnet"):
            hid = hm.offer_save_as(src, "claude-sonnet-5", "yellow", "Read", "")
        self.assertEqual(hid, "lab-sonnet")
        after = self._text()
        self.assertIn("# cowbell — which agents can be started", after)
        self.assertIn("system_prompt_flag = \"--append-system-prompt-file\"   # used only when", after)
        self.assertIn('id = "lab-sonnet"', after)
        h = hm.harness_by_id(hm.load_catalog(), "lab-sonnet")
        self.assertEqual(h["kind"], "claude")
        self.assertEqual(h["models"][0], "claude-sonnet-5")
        self.assertEqual(h["lane"], "yellow")
        self.assertEqual(h["tools_allow"], "Read")

    def test_save_as_empty_and_esc_write_nothing(self):
        before = self.catalog.read_bytes()
        src = hm.harness_by_id(hm.load_catalog(), "claude")
        with mock.patch("cowbell.ask", return_value=""):
            self.assertEqual(hm.offer_save_as(src, "x", "yellow", "", ""), "")
        with mock.patch("cowbell.ask", side_effect=KeyboardInterrupt):
            self.assertEqual(hm.offer_save_as(src, "x", "yellow", "", ""), "")
        self.assertEqual(self.catalog.read_bytes(), before)

    def test_edit_writes_after_all_prompts(self):
        with mock.patch("cowbell.ask", side_effect=["Claude Code (256)", "alpha, beta", "Read", "Bash"]), \
             mock.patch("cowbell.choose", side_effect=[0, 0]):
            self.assertTrue(hm.edit_harness(hm.load_catalog(), "claude"))
        after = self._text()
        self.assertIn("# cowbell — which agents can be started", after)
        self.assertIn("system_prompt_flag = \"--append-system-prompt-file\"   # used only when", after)
        h = hm.harness_by_id(hm.load_catalog(), "claude")
        self.assertEqual(h["title"], "Claude Code (256)")
        self.assertEqual(h["models"], ["alpha", "beta"])
        self.assertEqual(h["lane"], "green")
        self.assertEqual(h["tools_allow"], "Read")
        self.assertEqual(h["tools_deny"], "Bash")

    def test_edit_esc_writes_nothing(self):
        before = self.catalog.read_bytes()
        with mock.patch("cowbell.ask", side_effect=["Edited", "m1, m2"]), \
             mock.patch("cowbell.choose", return_value=None):
            self.assertFalse(hm.edit_harness(hm.load_catalog(), "claude"))
        self.assertEqual(self.catalog.read_bytes(), before)

    def test_add_kind_and_remove_keep_comments(self):
        before = self._text()
        kinds = sorted(hm.AGENT_EXES)
        with mock.patch("cowbell.choose", side_effect=[0, kinds.index("pi")]), \
             mock.patch("cowbell.ask", side_effect=["lab-pi", "pi probe", ""]):
            self.assertTrue(hm.add_harness(self.root, hm.load_catalog()))
        mid = self._text()
        self.assertIn("# cowbell — which agents can be started", mid)
        self.assertIn('id = "lab-pi"', mid)
        with mock.patch("cowbell.choose", return_value=0):
            self.assertTrue(hm.remove_harness("lab-pi"))
        after = self._text()
        self.assertNotIn("lab-pi", after)
        self.assertIn("# cowbell — which agents can be started", after)
        self.assertEqual(after.count("[[harness]]"), before.count("[[harness]]"))

    def test_remove_keep_and_esc_write_nothing(self):
        before = self.catalog.read_bytes()
        with mock.patch("cowbell.choose", return_value=1):
            self.assertFalse(hm.remove_harness("claude"))
        with mock.patch("cowbell.choose", return_value=None):
            self.assertFalse(hm.remove_harness("claude"))
        self.assertEqual(self.catalog.read_bytes(), before)

    def test_add_unhide_uses_pins(self):
        hm.hide_harness(self.root, "claude")
        self.assertIn("claude", hm.dir_prefs(self.root)["hide"])
        with mock.patch("cowbell.choose", side_effect=[2, 0]):
            self.assertTrue(hm.add_harness(self.root, hm.load_catalog()))
        self.assertNotIn("claude", hm.dir_prefs(self.root)["hide"])
        self.assertEqual(self.catalog.read_bytes(), self.SEED.read_bytes())

    def test_raise_quick_honors_harness_lane_and_tools(self):
        class FakeLaunch:
            def start(self, cat, h, name, root, ctx, *args, **kw):
                self.got = args
                return {"pane_id": "p1"}

        fake = FakeLaunch()
        ctx = hm.Ctx(cwd=self.root, mode="tab", live=hm.LiveSource(), launch=fake)
        h = hm.harness_by_id(hm.load_catalog(), "claude")
        h["lane"] = "green"
        h["tools_allow"] = "Read"
        h["tools_deny"] = "Bash"
        cat = {"defaults": {"lane": "yellow"}, "harness": [h], "lanes": {}}
        with mock.patch("cowbell.trust_match", return_value={"verdict": "ok"}), \
             mock.patch("cowbell.installed", return_value=True), \
             mock.patch("cowbell.prompt_flag", return_value=None):
            self.assertTrue(hm.raise_quick(ctx, cat, "claude", self.root))
        self.assertEqual(fake.got[:4], ("claude-sonnet-5", "green", "Read", "Bash"))

    def test_edit_sitting_launches_chosen_model_and_lane(self):
        class FakeLaunch:
            def start(self, cat, h, name, root, ctx, *args, **kw):
                self.got = (name,) + args
                return {"pane_id": "p1"}

        fake = FakeLaunch()
        ctx = hm.Ctx(cwd=self.root, mode="tab", live=hm.LiveSource(), launch=fake)
        cat = hm.load_catalog()
        before = self.catalog.read_bytes()
        with mock.patch("cowbell.trust_match", return_value={"verdict": "ok"}), \
             mock.patch("cowbell.installed", return_value=True), \
             mock.patch("cowbell.prompt_flag", return_value=None), \
             mock.patch("cowbell.choose", side_effect=[1, 0]), \
             mock.patch("cowbell.ask", return_value=""):
            self.assertTrue(hm.edit_sitting(ctx, cat, "claude", self.root))
        self.assertEqual(fake.got[0], "claude")
        self.assertEqual(fake.got[1:5], ("claude-opus-5", "green", "", ""))
        self.assertEqual(self.catalog.read_bytes(), before)

    def test_edit_sitting_esc_does_not_launch(self):
        class FakeLaunch:
            def start(self, *a, **kw):
                self.called = True
                return {"pane_id": "p1"}

        fake = FakeLaunch()
        ctx = hm.Ctx(cwd=self.root, mode="tab", live=hm.LiveSource(), launch=fake)
        cat = hm.load_catalog()
        before = self.catalog.read_bytes()
        with mock.patch("cowbell.trust_match", return_value={"verdict": "ok"}), \
             mock.patch("cowbell.installed", return_value=True), \
             mock.patch("cowbell.choose", return_value=None):
            self.assertFalse(hm.edit_sitting(ctx, cat, "claude", self.root))
        self.assertFalse(hasattr(fake, "called"))
        self.assertEqual(self.catalog.read_bytes(), before)

    @unittest.skipUnless(
        (Path.home() / ".config" / "cowbell" / "harnesses.toml").is_file(),
        "no patron config-dir catalog on this host",
    )
    def test_patron_catalog_save_edit_remove_keeps_comments(self):
        shutil.copy2(self.HOUSE, self.catalog)
        before = self._text()
        self.assertIn("# cowbell — the constitution of the herd.", before)
        src = hm.harness_by_id(hm.load_catalog(), "claude")
        with mock.patch("cowbell.ask", return_value="lab-256-probe"):
            hm.offer_save_as(src, "claude-sonnet-5", "yellow", "", "")
        saved = self._text()
        self.assertIn("# cowbell — the constitution of the herd.", saved)
        self.assertIn("# House wrappers", saved)
        self.assertIn("[places.lobby]", saved)
        self.assertIn("unix_user = \"guest\"", saved)
        with mock.patch("cowbell.ask", side_effect=["probe edited", "m1", "", ""]), \
             mock.patch("cowbell.choose", side_effect=[0, 1]):
            hm.edit_harness(hm.load_catalog(), "lab-256-probe")
        edited = self._text()
        self.assertIn("# cowbell — the constitution of the herd.", edited)
        self.assertIn("[places.lobby]", edited)
        self.assertIn("unix_user = \"guest\"", edited)
        self.assertIn("probe edited", edited)
        with mock.patch("cowbell.choose", return_value=0):
            hm.remove_harness("lab-256-probe")
        after = self._text()
        self.assertNotIn("lab-256-probe", after)
        self.assertNotIn("probe edited", after)
        self.assertIn("# cowbell — the constitution of the herd.", after)
        self.assertIn("# House wrappers", after)
        self.assertIn("[places.lobby]", after)
        self.assertIn("unix_user = \"guest\"", after)


class Coherence(unittest.TestCase):
    """Pane border is a cache of the harness Herdr detects. The tab stays the sitting."""

    def test_no_claim_is_left_alone(self):
        self.assertIsNone(hm.harness_claim("butler"))
        self.assertIsNone(hm.harness_claim("butler · Hello"))
        self.assertIsNone(hm.reconcile_label("butler", "butler", "grok"))
        self.assertIsNone(hm.reconcile_label("", "butler", "grok"))

    def test_matching_claim_stays(self):
        self.assertEqual(hm.harness_claim("butler · grok"), ("butler", "grok"))
        self.assertIsNone(hm.reconcile_label("butler · grok", "butler", "grok"))

    def test_detected_agent_replaces_the_claimed_harness(self):
        self.assertEqual(
            hm.reconcile_label("butler · local-ornith", "butler", "grok"),
            "butler · grok",
        )

    def test_tab_sitting_wins_over_the_name_in_the_claim(self):
        self.assertEqual(hm.reconcile_label("butler · grok", "clerk", "grok"), "clerk · grok")

    def test_idle_shell_drops_the_claim(self):
        self.assertEqual(
            hm.reconcile_label("butler · local-ornith", "butler", "", idle_shell=True),
            "butler",
        )

    def test_unseen_wrapper_keeps_its_claim(self):
        self.assertIsNone(hm.reconcile_label("butler · oll-mid", "butler", "", idle_shell=False))

    def test_coherent_label_without_a_harness_is_the_sitting(self):
        self.assertEqual(hm.coherent_pane_label("butler", ""), "butler")
        self.assertEqual(hm.coherent_pane_label("butler", "grok"), "butler · grok")

    def test_idle_shell_is_a_prompt_with_no_agent(self):
        self.assertTrue(hm.pane_is_idle_shell({"terminal_title_stripped": "user@host: ~/x"}))
        self.assertFalse(hm.pane_is_idle_shell({"agent": "grok", "terminal_title_stripped": "user@host: ~/x"}))
        self.assertFalse(hm.pane_is_idle_shell({"terminal_title_stripped": "✳ butler"}))

    def test_dry_run_does_not_consume_the_next_argument(self):
        opts, pos = hm.parse_flags(["--dry-run", "extra"])
        self.assertIs(opts.get("dry-run"), True)
        self.assertEqual(pos, ["extra"])

    def test_raise_caches_the_harness_id_on_the_pane_border(self):
        calls = []
        saved = (hm.herdr, hm.report_identity, hm.start_native, hm.save_roster, hm.load_roster,
                 hm.create_tab, hm.pick_workspace)
        hm.herdr = lambda *a, **k: calls.append(a) or {}
        hm.report_identity = lambda *a, **k: True
        hm.create_tab = lambda *a, **k: {"pane_id": "w1C:p1", "tab_id": "w1C:t1", "workspace_id": "w1C"}
        hm.pick_workspace = lambda *a, **k: "w1C"
        hm.start_native = lambda *a, **k: {}
        hm.save_roster = lambda rows: None
        hm.load_roster = lambda: []
        try:
            hm.raise_harness(CAT, hm.harness_by_id(CAT, "grok"), "probe", ROOT, hm.Ctx(cwd=ROOT))
            hm.mark_harness("pid:9", "probe", "grok")
        finally:
            (hm.herdr, hm.report_identity, hm.start_native, hm.save_roster, hm.load_roster,
             hm.create_tab, hm.pick_workspace) = saved
        self.assertIn(("pane", "rename", "w1C:p1", "probe · grok"), calls)
        self.assertFalse(any(c[1] == "rename" and c[2] == "pid:9" for c in calls if len(c) > 2))

    def test_reconcile_command_is_not_a_harness(self):
        called = {}
        saved = (hm.apply_coherence, hm.server_up, hm.load_catalog)
        hm.server_up = lambda: False
        hm.load_catalog = lambda: CAT
        hm.apply_coherence = lambda dry_run=False: called.update(dry_run=dry_run) or []
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                self.assertEqual(hm.main(["reconcile", "--dry-run"]), 0)
                self.assertEqual(hm.main(["reconcile", "--help"]), 0)
        finally:
            hm.apply_coherence, hm.server_up, hm.load_catalog = saved
        self.assertEqual(called, {"dry_run": True})
        self.assertIn("cowbell reconcile", out.getvalue())
        self.assertIn("no harness claim", out.getvalue())


if __name__ == "__main__":
    unittest.main()
