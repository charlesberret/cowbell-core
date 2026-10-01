# LAB-496 — cowbell raise vs agent-deck resume

**Result: GAP.** Observed 2026-09-23 on avicenna. No sitting was raised. No nerve session was restarted.

Command: `python3 scripts/side-by-side-deck.py` (reads `~/.local/state/cowbell/roster.json` and `agent-deck list --json`).

| Registry | Count | Identity it actually has |
|---|---|---|
| Cowbell roster | 43 | `name`, `harness`, `cwd`, `pane_id` (`wK:…`), `source` (`herdr-seats` or `seen`) |
| Agent-deck | 845 | `id`, `title`, `path`, `tool`, `command`, `tmux_session` |

Join on an agent-deck session id: **0** rows. Cowbell does not store `agent_deck_id`. Deck sessions do not store a herdr `pane_id`.

Shared titles (not the same sitting): builder-minaret, designer-primitives, scholar, kettle-core, system-coord, herdr, kettle-all, designer-palettes, incanter-all, plurabel-coord, fonts-data-2026, butler.

Deck `command` contains the string `agent-deck` on **0 / 845** sessions. The known nesting bug is the other way: a deck process *inside* a herdr pane makes herdr see `agent-deck` instead of the agent. This check does not use that nesting.

`agent-deck session attach <id>` therefore cannot be pointed at a cowbell roster row. Resume stays a deck id. Raise stays a cowbell/herdr pane. Until a row carries a deck id (or a deck row carries a pane id), LAB-492 and LAB-495 stay blocked.
