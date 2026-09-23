#!/usr/bin/env python3
"""LAB-496. Read-only. Does not raise a sitting and does not touch nerve seats.

Cowbell's roster and agent-deck's session list are different registries.
A shared title is not a shared sitting. Report GAP unless a roster row
carries an agent-deck session id that `agent-deck session show` can open.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def roster_rows() -> list[dict]:
    base = os.environ.get("COWBELL_STATE_DIR") or str(
        Path(os.environ.get("XDG_STATE_HOME") or "~/.local/state").expanduser() / "cowbell"
    )
    path = Path(base).expanduser() / "roster.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text())
    return list(data.get("harnesses") or data.get("rows") or [])


def deck_sessions() -> list[dict]:
    proc = subprocess.run(
        ["agent-deck", "list", "--json"], capture_output=True, text=True, timeout=90,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.strip() or "agent-deck list failed")
    data = json.loads(proc.stdout)
    if isinstance(data, list):
        return data
    return list(data.get("sessions") or data.get("items") or [])


def main() -> int:
    rows = roster_rows()
    sessions = deck_sessions()
    deck_ids = {s.get("id") for s in sessions if s.get("id")}
    linked = [
        r for r in rows
        if r.get("agent_deck_id") in deck_ids or r.get("deck_id") in deck_ids
    ]
    titles = {(s.get("title") or "").lower() for s in sessions}
    title_hits = sorted({(r.get("name") or "").lower() for r in rows} & titles)
    nested = sum(1 for s in sessions if "agent-deck" in str(s.get("command") or ""))
    print(f"roster={len(rows)} deck={len(sessions)} id_links={len(linked)} "
          f"title_hits={len(title_hits)} command_mentions_agent_deck={nested}")
    if linked:
        print("PASS")
        return 0
    print("GAP")
    print("cowbell roster has pane_id/source; agent-deck sessions have id/tmux_session.")
    print("No roster field joins to a deck id, so agent-deck cannot resume a cowbell sitting.")
    print("Title overlap is not identity:", ", ".join(title_hits[:12]) or "(none)")
    print("Do not close the gap by nesting agent-deck inside a herdr pane.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
