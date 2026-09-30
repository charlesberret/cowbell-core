# HANDOFF — cowbell

Board: Lab / Cowbell — https://linear.app/isruna/project/cowbell-77c7779d8e93 (protocol: document "Cowbell — agent handoff")
Milestone: Split (Now)
Locked: none

## 2026-09-30 — picker: Active is a census; Resume and New Session are the menus

Selecting a live sitting used to try `focus` (herdr pane) or print that cowbell
cannot switch terminals. That is not a takeover, and the failure is a dead end.
Active (was Running) stays ink, unnumbered, not in the cursor/digit/Enter set,
inside an ink light box with the heading on the top rule. Resume heading is gold;
New Session heading is green (kettle `#7dba6f`). Option numbers are kettle blue
(`#7d9fc7`). `+ N more` on Active still expands, from inside the box. `a` adopt
uses the focused pane when no live row is a menu item.

## 2026-09-30 — prefix+c claim survives herdr upgrades (plugin)

Herdr 0.9.1 / native-tab rewrites of `~/.config/herdr/config.toml` dropped the
cowbell `[[keys.command]]` block and the blanked `new_tab`, so `prefix+c` went
back to herdr's bare new-tab. `keys install` now writes
`~/.config/cowbell/prefix-c.claimed`. A `[[startup]]` hook runs `keys ensure`:
one-shot, no panes, no `report-metadata`, no clocks (LAB-297 still holds). If
the claim file is present and the block is gone, it puts the binding back and
reloads config. `keys uninstall` restores herdr's binding and deletes the claim.
Strangers who never ran install-keys are left alone.

## 2026-09-23 — over-privilege is advisory, never a gate

Trust exit 3 (over-privilege) no longer asks `start anyway? [y/N]`; it prints one dim note with the
checker's own reason, and the picker badge is a dim `! more reach than needed` (was red `! asks first`).
Blocked (`⊘`) still refuses, and is now the red mark in `status`. `parse_match` keeps only the reason
in `flag`, not the checker's bracketed aside. Patron ruling in the metawork sitting (T4: visible, not silent).

## 2026-09-25 — resume history-discovered sessions when absent from roster

- **History-discovered resume**: Sessions discovered by `discover_sessions` (Claude Code `~/.claude/projects/...` and Grok `~/.grok/sessions/...`) appear in the picker's Resume list, but previously failed upon selection or `cowbell enter <name>` with `no roster entry for that session` if they were created outside cowbell.
- `cmd_enter` now accepts an optional `target` record directly (passed from `picker()` and `cmd_dispatch()`).
- When called from the CLI (`cowbell enter <target>`), `cmd_enter` queries `load_roster()`, and if absent, queries `discover_sessions(root, cat)` by exact name, session ID prefix, substring, or title.
- Resuming automatically records the sitting into `roster.json` via `raise_harness` or `_record_here`.
- Tested in `tests/test_cowbell.py` (`ResumeOutside`, `SessionHistory`; 127/127 tests pass).

## 2026-09-25 — delegation vision & standalone without herdr CLI (LAB-497)

- **Delegation & tab defaults (`3d5cfb2`, `af00c45`)**: Human callers running `cowbell new` default to `mode="here"` (replacing the current shell). Agent callers (`caller_is_agent()`) default to creating a new tab via herdr. The `herdr-cowbell` plugin sets `COWBELL_MODE=tab` so `prefix+c` retains tab-creation behavior for humans. `raise_harness` defaults to `create_tab` within the project workspace (`--split` opts into pane splitting).
- **LAB-497 standalone without herdr binary**: Added `has_herdr()` check in the herdr adapter; `server_up()` returns `False` if the `herdr` binary is missing from PATH/environment, so standalone cowbell (`COWBELL_MODE=here` or outside herdr) never attempts to run a missing binary even if a server socket exists. All standalone operations (`status`, `picker`, `enter`, `new`, `list`, `dispatch`) run with zero `herdr` subprocess calls. Tested in `tests/test_cowbell.py` (`NoHerdrCalls`).

## 2026-09-24 — picker `a` adopts the highlighted Running row

Typing `cowbell adopt` (or picker `a`) in a shell made that shell the focused pane, so
adopt died with `no focused agent pane` and dumped a multi-line list into the popup.
`a` now adopts the highlighted Running sitting; a positional pane id or sitting name
selects when focus is a shell; the TUI flash stays one line.

## 2026-09-20 — Wrangler accuracy batch: LAB-294, 295, 297, 298

- **LAB-295 places**: `cowbell status` names the resolved place (header line + `--json`, matching the picker); tie rule documented (longest cwd wins, first declared on equal length); nested-place, status, and `new`/`--place` tests. Commit `9bd47f0`.
- **LAB-294 identify**: live rows carry a harness id (roster first, then a kind only one catalog harness has, else the exe name) and the place their own cwd resolves to; `--json` rows report the row's place. Stub process-table tests cover the no-herdr path. Commit `ed0d169`.
- **LAB-298 resume**: the seed documents the session-flag table — claude is resume-capable outside herdr (`--session-id` → `--resume`), every other seeded harness is honestly absent from Resume (its CLI picks ids cowbell cannot replay); status `--json` and the plain COLD HERE section filter sessionless rows like the picker always did. Commit `fb4fa07`.
- **LAB-297 tokens**: one `pane report-metadata --source cowbell` per event cowbell owns — raise, adopt, or a state change seen in a picker refresh (diffed, never per-refresh); `$line1` = `<glyph> <sitting>` with the sidebar's glyph table; no `[[startup]]`, no clocks, bt-reporter stays disabled. Commit `1b21850`.
- Vendored into the plugin: `herdr-cowbell` commit `19285a5` (cowbell 0.3.0 @ `1b21850`, plugin tests 17/17).

## 2026-09-15 — Guest wall (agent-lobby)

Place `lobby` now admits harness `lobby` first (`default_harness`). Resume omits roster rows whose harness is not in `allow_harness` (cold `oll-memo` is not a guest). `cowbell new --place lobby` with no `--harness` uses the default. Claude/Grok remain allowed as house labor. Tests in `tests/test_cowbell.py` Places. House constitution `~/.config/cowbell/harnesses.toml`.

**This file:** `/Users/example/code/cowbell/HANDOFF.md`
**What:** the cowbell core and CLI. The herdr plugin is `~/code/herdr-cowbell`.
**Launcher:** `~/code/bin/cowbell` (synced) execs `bin/cowbell` here.
**Authoritative `cowbell.py`:** this tree, from LAB-250 on. `herdr-cowbell` is a thin skin with a vendored copy of this core (LAB-252); after a core change, run `scripts/vendor-core` there.

Release notes before the split (0.2.0, 0.3.0, LAB-247, LAB-248, LAB-262, LAB-249) are in `herdr-cowbell/HANDOFF.md` and in this tree's git history.

## 2026-09-15 — LAB-250: the core tree

- Cloned from `herdr-cowbell` with full history and tags (`v0.2.0`, `v0.3.0`); origin remote removed (local-only). See README § Provenance.
- Removed from the core, kept in the plugin: `herdr-plugin.toml`, `cmd_open` / `invocation_ctx` / `picker_open_args`, the keybinding installer, `adopt`, `stop`, `import-seats`, the picker's hidden `a` key. `write_atomic` stays (the harness writer, LAB-254, needs it).
- `PLUGIN_ID` remains only to find 0.1–0.3 config and state in herdr's plugin dirs for the one-time migration.
- The house launcher now points here. From a plain `cowbell` you lose `stop`, `import-seats`, `keys` and `open` (plugin doors). **LAB-293:** `cowbell adopt` is in this core.

## 2026-09-15 — LAB-272: PyPI packaging (not uploaded)

- `pyproject.toml` (hatchling): name `cowbell`, version from `__version__`, python ≥ 3.11, no dependencies, console script `cowbell = cowbell:cli`; the seed ships as `share/cowbell/harnesses.toml`, found by `seed_path()` under `sys.prefix`. `uv build` → `dist/` (ignored).
- Upload is the patron's (LAB-251): `uv publish --token …` from this tree.

## Plan

On Linear (above). Update the `Locked:` line when you claim an issue that touches `cowbell.py`.

---

# Plugin handoff — herdr-cowbell (moved here 2026-09-19)

The plugin tree is going to GitHub, so its house process notes live here in the private core
instead (patron ruling 2026-09-19). Everything below is the plugin's handoff as it stood.

# HANDOFF — herdr-cowbell

Board: Lab / Cowbell — https://linear.app/isruna/project/cowbell-77c7779d8e93 (protocol: document "Cowbell — agent handoff")
Milestone: Split (Now)
Locked: none (core cowbell.py lives in ~/cloud/git-projects/cowbell)

**This file:** `/Users/charles/cloud/git-projects/herdr-cowbell/HANDOFF.md`
**Plugin:** `herdr-cowbell` (`prefix+c` → cowbell picker). CLI: `cowbell` (core tree `~/cloud/git-projects/cowbell`).
**Vendored core:** `cowbell 0.3.0` from core commit `4a43710` (`vendor/VENDORED.json`; refresh with `scripts/vendor-core`).
**Name:** chosen 2026-09-11 as herdmark; reopened 2026-09-13 → herdr-cowbell / cowbell.
**Ballot:** `~/cloud/sync/metawork/nomogenesis/ballots/2026-09-11-herdmark.md`

## Why this is now urgent (2026-09-12)

Charles has been launching herdr seats **through agent-deck inside a herdr pane** only because agent-deck ties a session to a cwd. That nesting makes the seat **invisible to herdr's agent list**: herdr detects a Claude pane by its foreground process and its `✳` terminal title, and inside agent-deck the foreground process is `agent-deck` and the title is agent-deck's tmux `set-titles-string` (`[charles] herdr`). Verified on pane `wK:pC` this sitting: `pane.report_agent` / `report_agent_session` over the socket answer `ok` and change nothing; passing the inner title through tmux did not propagate. So no deck-launched seat will ever show in the sidebar the round just redesigned (`~/cloud/sync/metawork/braintrust/rounds/2026-09-12-herdr-sidebar-two-panels/synthesis.md` § Taken).

**Finishing the *plugin* removes the only reason agent-deck was inside herdr:** the same cowbell raise (project + harness, named on purpose) lands as a native herdr tab, so herdr detects it. A herdr tab is this plugin's endpoint, not cowbell's. Cowbell itself pinpoints, identifies, recalls, and spins up sessions in any terminal (`exec` here, or a tab when invoked from herdr). Patron correction 2026-09-17.

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
- Config and state moved to `~/.config/cowbell/` and `~/.local/state/cowbell/` (`COWBELL_CONFIG_DIR` / `COWBELL_STATE_DIR`, then XDG homes). herdr's plugin dirs are only a migration source: copied once, originals untouched, dated copies in `migration-backup/`, `.migrated_from` marker. Migrated on avicenna 2026-09-15 11:41 (catalog byte-identical; 26 roster rows).
- `schema = 1` in the seed catalog and in every roster save; a newer schema is read but never overwritten (`SchemaError`). `check_writable()` is what LAB-254's writer must call.

## 2026-09-15 — LAB-258: herdr-seats retired

Patron: no reason to keep the tree. Never on GitHub (no remote; `gh repo view charlesberret/herdr-seats` 404). Plugin unlinked; `prefix+shift+s` removed from `~/.config/herdr/config.toml` (backup beside it). Tree moved to `~/cloud/git-projects/_archive/herdr-seats`. All 10 seats.json names are on the cowbell roster (`source = herdr-seats`). Plugin config `seats.json` left in place for `import-seats`.

## 2026-09-15 — LAB-262: places

- `[places.<name>]` in the config-dir catalog: `cwd`, `workspace_label` (the herdr pen), `allow_harness`, `lane`. `[defaults] untitled_place` names where a sitting from `~` goes. Set on avicenna: `untitled_place = "lobby"`, `[places.lobby]` → `~/cloud/git-projects/agent-lobby`, pen `lobby`, claude + grok, yellow (backup `~/.config/cowbell/migration-backup/harnesses.toml.pre-places-20260915-115853`).
- Picker, `status`, `new`, bare `cowbell <harness>`: root `~` → the untitled place; a place's catalog shows only its harnesses; a raise at/under a place opens a tab in the workspace labelled `workspace_label` (created if missing), never the caller's workspace. `cowbell new --place <name>`.
- Fix found on the way: a command typed in a herdr pane used the *pane's* cwd (asked herdr) instead of its own; now only plugin-launched processes (`HERDR_PLUGIN_ROOT`) ask herdr.
- Live 2026-09-15 12:00: `cowbell new --harness grok --name untitled` from `~` created workspace `w1C lobby`, cwd = the pad; `home ~` unchanged; the sitting wrote `visitors/2026-09-15-untitled/` + one GUESTBOOK row. A separate `w1B proj:agent-lobby` workspace exists (not cowbell's); left alone.

## 2026-09-15 — LAB-249: host seams

- Two seams, chosen once by `choose_host()` in `main` and carried on `ctx`: **`ctx.live`** (`LiveSource`: `HerdrLive`, `ProcessScan`, `CombinedLive`, or the empty base) answers what is running, focus, refresh; **`ctx.launch`** (`HostLaunch`: `HerdrLaunch` = new tab, `HereLaunch` = exec here) starts and resumes. Picker, status, enter, list, new, dispatch, stop, adopt use them.
- Every `herdr(` call lives in the `# --- herdr adapter` section (a test enforces it). `server_up()` now probes `HERDR_SOCKET_PATH` (default `~/.config/herdr/herdr.sock`) instead of running the CLI, so standalone with no server never runs `herdr` (subprocess test with a logging stub: 0 calls; the pre-change code made 5 on `status`).
- `COWBELL_MODE=here` forces standalone even inside a herdr pane.
- `tests/test_pty.py` puts the menu / prompt / whole-picker pty cases in the repo (they used to live in a scratchpad).
- Fixed: a long turn clock (`26h55m`) ran into the workspace column in Running here.

## 2026-09-15 — LAB-250: the core moved out

- `~/cloud/git-projects/cowbell` is now the core + CLI (cloned from this repo with history; plugin-only code removed there). It is the authoritative `cowbell.py`; do not develop core here.
- The house launcher `~/cloud/sync/code/bin/cowbell` execs the core tree. This repo's `bin/cowbell` still runs this full copy, so the plugin (`prefix+c`, `open`, `adopt`, `stop`, `import-seats`, `keys`) is unchanged until LAB-252 makes it a thin skin over the core.

## 2026-09-15 — LAB-252: thin skin

- This tree is now the plugin only: `herdr-plugin.toml`, `bin/cowbell` (shim), `herdr_cowbell.py` (open, adopt, stop, import-seats, keys), `vendor/` (pinned core + seed + `VENDORED.json`), `harnesses.toml` → `vendor/harnesses.toml`, `scripts/vendor-core`, `tests/test_plugin.py` (packaging only). The full `cowbell.py` and core tests are gone from here.
- Which core: picker and non-plugin commands exec a PATH `cowbell` whose `--version` ≥ vendored, else the vendored core. Plugin commands always use the vendored core. On avicenna the house launcher (core 0.3.0) wins today.

## Plan

Lives on Linear (above). Filed 2026-09-13 from braintrust round `~/cloud/sync/metawork/braintrust/rounds/2026-09-13-cowbell-roadmap/synthesis.md`: Split (Now) LAB-247–253, Harness D (Next) LAB-254–256, Reach (Later) LAB-257–261. Update the `Locked:` line when you claim an issue that touches `cowbell.py`.

## Related

- Sidebar plate and reporter: `…/rounds/2026-09-12-herdr-sidebar-two-panels/variants/F4/` (live) and `variants/B/plugin/bt-reporter.py`.
- Must-nots inherited: never `--title` a pane as identity; never nest agent-deck in herdr.
