# HANDOFF — herdr-cowbell

Board: Lab / Cowbell — https://linear.app/isruna/project/cowbell-77c7779d8e93 (protocol: document "Cowbell — agent handoff")
Milestone: Split (Now)
Locked: none

**This file:** `/Users/example/code/herdr-cowbell/HANDOFF.md`
**Plugin:** `herdr-cowbell` (`prefix+c` → cowbell picker). CLI: `cowbell`.
**Name:** chosen 2026-09-11 as herdmark; reopened 2026-09-13 → herdr-cowbell / cowbell.
**Ballot:** `~/code/notes/nomogenesis/ballots/2026-09-11-herdmark.md`

## Why this is now urgent (2026-09-12)

Charles has been launching herdr seats **through agent-deck inside a herdr pane** only because agent-deck ties a session to a cwd. That nesting makes the seat **invisible to herdr's agent list**: herdr detects a Claude pane by its foreground process and its `✳` terminal title, and inside agent-deck the foreground process is `agent-deck` and the title is agent-deck's tmux `set-titles-string` (`[charles] herdr`). Verified on pane `wK:pC` this sitting: `pane.report_agent` / `report_agent_session` over the socket answer `ok` and change nothing; passing the inner title through tmux did not propagate. So no deck-launched seat will ever show in the sidebar the round just redesigned (`~/code/notes/braintrust/rounds/2026-09-12-herdr-sidebar-two-panels/synthesis.md` § Taken).

**Finishing cowbell removes the only reason agent-deck was inside herdr:** raise a sitting in a herdr tab with the cwd, model, lane and tools chosen on purpose — natively, so herdr detects it and the bt-reporter badges it (`✼ ✳ ϟ`).

## What "finished" means for that use

- `cowbell open` from any pane: pick a harness from `harnesses.toml` for **this directory**, or an established one to attach to, and it lands in a **new herdr tab in this workspace with that cwd** (no tmux, no deck).
- The tab is named the sitting (the seat / office name), not the terminal title — `tab` is the sidebar's identity token.
- Adopt (`cowbell adopt`) already exists for the reverse direction.
- Out of scope: quota, sidebar rows (those are `bt-reporter` / config).

## 2026-09-12 — raise path works; popup is a first pass

Live probe: `herdmark new --harness grok --name herdmark-probe` created tab `w1A:t6` labelled **herdmark-probe**, herdr detected grok idle at this cwd; probe tab closed. `prefix+c` smoke-tested the same day — it works, and it is clunky.

- Tab label = sitting (`--name`); never pane `--title` / rename.
- Wait for a single foreground shell before `agent start` (fresh tabs were `agent_pane_busy`).
- Grok lanes verified against `grok --help`; `--agent <sitting-head>` when `~/.grok/agents/<head>.md` exists.

`herdr-seats` still on `prefix+shift+s`. Wrappers still `pane run`. Constitution sync / fleet / marquee: later.

## 2026-09-13 — 0.2.0: the popup is the product

- **Surface:** Running here / Resume / Start new. Plain words on screen; house words (harness, sitting, lane) stay in `harnesses.toml`, the CLI registry and docs. Cut: pane ids, subject line, `ok`/`?` marks, blocked and not-installed lines. Trust shows only as `! asks first`; blocked rows are omitted.
- **Keys and mouse:** raw-mode menu, SGR mouse (press-only), alternate screen. Click selects, Enter or the ⏎ button confirms; bottom hints clickable; no hover. Refreshes every 2s, keeps the selection. Plain typed-number fallback off a terminal or with `COWBELL_PLAIN=1`.
- **Start new:** ranked by starts here (×3) then anywhere, folds at 5 rows to 4 + `+ N more`. Enter starts at once with an automatic name; `[defaults] ask_name = true` asks first (set in Charles's config copy). `n` = agent, name, model, permissions.
- **Roster:** running agents with a session id are recorded as they are seen (`source = "seen"`); `adopt` left on the CLI only.
- **Seed** `harnesses.toml` is standard agents only (claude, codex, grok, gemini, agy, opencode, pi); house wrappers live only in the config-dir copy. Codex lane flags are from docs, not verified here.
- **Colour:** Kettle Dark tokens; gold only on what you press, red only for trust. `NO_COLOR` honoured.
- Verified: 35 unit tests; pty-driven menu cases (keys, click, wheel, buttons, esc in prompts); real popup in a pty against the live herd; live `prefix+c` clicks confirmed by Charles.

## 2026-09-13 — 0.3.0: standalone

- Bare `cowbell` on a terminal = the picker; piped = `cowbell status`. Only `adopt` / `stop` need a herdr server; herdr not installed at all is handled.
- Host is decided once: inside a herdr pane (or its popup) → herdr tabs; anywhere else → `ctx.mode = "here"`, and `launch()` routes start/resume to `exec_here` (exec in this terminal, roster row with `source = "here"`).
- Running here outside herdr = herdr agents (if up) + `agent_processes()`: ps + lsof cwd (or /proc), tty required, skip anything with a herdr or agent ancestor, skip `.app/` bundles. Opening a process row flashes its tty and pid.
- Claude: `session_id_flag` / `name_flag` in the seed and in Charles's config copy, so terminal-started Claude is resumable. Resume lists only rows with a session id.
- Decisions (Charles, 2026-09-13): opens in this terminal; running = herdr + any agent process; bare `cowbell`.
- Verified: 40 unit tests; pty runs of bare `cowbell` outside herdr (herdr row + process row, process-row message, stand-in agent exec'd in the right cwd, resume row).

## 2026-09-15 — LAB-247, LAB-248

- `cowbell --version` → `cowbell 0.3.0`; `__version__` kept equal to `herdr-plugin.toml` by test.
- Config and state moved to `~/.config/cowbell/` and `~/.local/state/cowbell/` (`COWBELL_CONFIG_DIR` / `COWBELL_STATE_DIR`, then XDG homes). herdr's plugin dirs are only a migration source: copied once, originals untouched, dated copies in `migration-backup/`, `.migrated_from` marker. Migrated on this laptop 2026-09-15 11:41 (catalog byte-identical; 26 roster rows).
- `schema = 1` in the seed catalog and in every roster save; a newer schema is read but never overwritten (`SchemaError`). `check_writable()` is what LAB-254's writer must call.

## 2026-09-15 — LAB-258: herdr-seats retired

Patron: no reason to keep the tree. Never on GitHub (no remote; `gh repo view charlesberret/herdr-seats` 404). Plugin unlinked; `prefix+shift+s` removed from `~/.config/herdr/config.toml` (backup beside it). Tree moved to `~/code/_archive/herdr-seats`. All 10 seats.json names are on the cowbell roster (`source = herdr-seats`). Plugin config `seats.json` left in place for `import-seats`.

## 2026-09-15 — LAB-262: places

- `[places.<name>]` in the config-dir catalog: `cwd`, `workspace_label` (the herdr pen), `allow_harness`, `lane`. `[defaults] untitled_place` names where a sitting from `~` goes. Set on this laptop: `untitled_place = "lobby"`, `[places.lobby]` → `~/code/agent-lobby`, pen `lobby`, claude + grok, yellow (backup `~/.config/cowbell/migration-backup/harnesses.toml.pre-places-20260915-115853`).
- Picker, `status`, `new`, bare `cowbell <harness>`: root `~` → the untitled place; a place's catalog shows only its harnesses; a raise at/under a place opens a tab in the workspace labelled `workspace_label` (created if missing), never the caller's workspace. `cowbell new --place <name>`.
- Fix found on the way: a command typed in a herdr pane used the *pane's* cwd (asked herdr) instead of its own; now only plugin-launched processes (`HERDR_PLUGIN_ROOT`) ask herdr.
- Live 2026-09-15 12:00: `cowbell new --harness grok --name untitled` from `~` created workspace `w1C lobby`, cwd = the pad; `home ~` unchanged; the sitting wrote `visitors/2026-09-15-untitled/` + one GUESTBOOK row. A separate `w1B proj:agent-lobby` workspace exists (not cowbell's); left alone.

## 2026-09-15 — LAB-249: host seams

- Two seams, chosen once by `choose_host()` in `main` and carried on `ctx`: **`ctx.live`** (`LiveSource`: `HerdrLive`, `ProcessScan`, `CombinedLive`, or the empty base) answers what is running, focus, refresh; **`ctx.launch`** (`HostLaunch`: `HerdrLaunch` = new tab, `HereLaunch` = exec here) starts and resumes. Picker, status, enter, list, new, dispatch, stop, adopt use them.
- Every `herdr(` call lives in the `# --- herdr adapter` section (a test enforces it). `server_up()` now probes `HERDR_SOCKET_PATH` (default `~/.config/herdr/herdr.sock`) instead of running the CLI, so standalone with no server never runs `herdr` (subprocess test with a logging stub: 0 calls; the pre-change code made 5 on `status`).
- `COWBELL_MODE=here` forces standalone even inside a herdr pane.
- `tests/test_pty.py` puts the menu / prompt / whole-picker pty cases in the repo (they used to live in a scratchpad).
- Fixed: a long turn clock (`26h55m`) ran into the workspace column in Running here.

## Plan

Lives on Linear (above). Filed 2026-09-13 from braintrust round `~/code/notes/braintrust/rounds/2026-09-13-cowbell-roadmap/synthesis.md`: Split (Now) LAB-247–253, Harness D (Next) LAB-254–256, Reach (Later) LAB-257–261. Update the `Locked:` line when you claim an issue that touches `cowbell.py`.

## Related

- Sidebar plate and reporter: `…/rounds/2026-09-12-herdr-sidebar-two-panels/variants/F4/` (live) and `variants/B/plugin/bt-reporter.py`.
- Must-nots inherited: never `--title` a pane as identity; never nest agent-deck in herdr.
