# Changelog

## Unreleased

- `a` on a launch sheet saves its shape as a named agent (a `[[harness]]` row copied whole from this one, with the sheet's model, effort, permissions and tools as defaults); the sheet stays open and launches nothing. Not on a resume sheet.

## 0.3.2 — 2026-11-02

- A saved harness launches like the one it was saved from: save-as copies the source row whole and overrides only what the sheet set, so the seat file, `--name`, and a confining `unix_user` are kept.
- A resume launches the model id it ran with. herdr's quota label ("Sonnet 5") no longer overwrites the roster's `model`; rows written before take the id from their recorded argv, and a display name with no argv resumes on the agent's own default.
- The hint bar fits the terminal it is drawn in: a bar too wide sheds words right to left, then whole hints, keeping ⏎ first and esc last (herdr's popup is 56 columns inside its border).
- Two sessions with one title: the row with the best name source keeps it, the rest take a session-id tail; recomputed names are written back to unpinned rows.
- codex resumes with `codex resume <id>` first and its options after; "last launch here" counts a herdr row by its created day.
- pi resumes outside herdr: the seed gives it `session_id_flag = "--session-id"` (pi opens or creates the session with that id; a UUID passes its id check) and `name_flag = "--name"`. A resume carries only `--session`, which pi refuses to combine with `--session-id`.
- Other directories are a launch setting: `add_dir_flag` on a harness row, an "also in" row on the sheet, `cowbell new --add-dir a,b`; the roster keeps them and resume replays them. Seeded for claude, codex, grok, agy and omp. A refusal on the sheet shows on the sheet.
- The seed's pi row resumes with `--session <id>`. It had `--continue`, which takes no id: pi read the session id as a prompt and continued the latest session instead.
- `o` shapes the launch under the cursor. On a New Session row it opens that harness's sheet on the settings last used for it in this directory; on a Resume row it opens the sheet over the recorded session and resumes with any change, and the roster row is rewritten with what ran. The hint bar fits 80 columns on every row.
- Effort is a launch setting: harness rows carry `effort_flag` (a `{}` marks where the level goes), `efforts` and an optional default `effort`; the launch sheet has an effort row, `cowbell new --effort` passes one, the roster keeps it and resume replays it. The seed sets it for claude, codex, grok, agy, pi and omp from each CLI's `--help`. `catalog --check` rejects a malformed effort field.
- `n` opens a launch sheet instead of a run of prompts: start, then every setting the harness takes with defaults dim and changes bright, the uid it runs as, and the exact command. `d` resets. A launch is now a `LaunchSpec`; a roster row rebuilds to the argv it recorded, and passthrough argv after `--` is kept on the row as `extra`.
- The seed catalog carries `omp` (oh-my-pi): `--model`, `--resume`, `--tools`, the seat file through `--append-system-prompt`, and lanes on `--approval-mode` (`always-ask` · `write` · `yolo`).
- In-place harness editor (`e` menu) improvements:
  - Live Launch Command Preview (`launch preview`): shows the exact expanded argv, directory, lane permissions, and confinement uid drops (`agent-run` / `sudo -u`).
  - Per-harness `unix_user` configuration: individual harnesses can specify a confined UNIX user, overriding place defaults or satisfying `require_uid`.
  - Dynamic model auto-discovery (`(probe installed)`): detects locally installed models via Ollama CLI/API, Codex, Grok, and `--help` CLI inspection.
  - Clone harness preset (`clone harness`): duplicates any harness definition into a new catalog preset with custom ID and title, seamlessly switching editor focus.
  - In-place harness sanity check (`verify harness`): checks executable existence on PATH, unix user validity, declared flags, tools allow/deny configuration, and CLI help concordance.
  - Polished edit interface: rich header banner showing kind, lane badge, and title, with styled row values and status colors.
- A bare pane border that is not the current tab is a stale sitting: `reconcile_label` rewrites it, and `identity sync` restamps `sitting · kind` on `pane.agent_detected`.
- A sitting opens on a grouped `proj:` workspace when a pane there already has this directory, instead of the caller's line.
- Harness rows can carry `provider`, a model cycle, and an inline `system_prompt`; `build_argv` emits them when the row sets the matching flags, and picker `e` edits the three fields.
- Picker `e` on a wrapper harness lists every launch control.
- `cowbell new --yes` is documented as accepted and unused; `reconcile --dry-run` with no herdr binary names the skip.
- Agent-list `$glyph` restamps on `pane.agent_detected` / `pane.exited` and from detector kind, so a tab that swaps harnesses does not keep the old mark.
- An existing catalog is filled once with `droid` and `devin` when on PATH; the seed carries a commented `[places.lab]` example; session-history discovery runs as the launch uid for `unix_user` places.
- `cowbell new --split` opens a pane split in the project workspace instead of being dropped; outside herdr it is ignored.
- Session titles read from a harness's store drop terminal controls (CSI, OSC title and hyperlink sequences, other control characters) before the picker prints them.
- A hung herdr server or harness-trust check times out instead of freezing the picker. Agent start still waits up to 35s.
- Codex lane flags verified against Codex 0.160.1.
- Tests: Lobe glyph table and identity tokens pinned, sdist no longer ships `tests/`, host-dependent premises pinned by lookup and mock.

## 0.3.1 — 2026-09-30

- `[places.*]` walls: per-directory `allow_harness`, `default_harness`, `lane`, and `unix_user`/`nono` confinement.
- Resume reads each harness's own session store (`~/.claude/projects`, `~/.grok/sessions`), ids and titles only.
- Picker `e` sets this sitting's model, permissions and tools without rewriting the catalog.
- Advisory over-privilege marks via `trust_command`; blocked agents are left off.

## 0.3.0 — 2026-09-13

- Split from the herdr plugin `herdr-cowbell` into its own command.
- Standalone: bare `cowbell` on a terminal is the picker; `exec` here mode needs no herdr.
- Config and state moved to `~/.config/cowbell` and `~/.local/state/cowbell` with `schema = 1`.
- Mouse-first picker: click, arrows, digits, clickable hint bar, 2 s refresh, `COWBELL_PLAIN` fallback.
- `adopt` in the core; Claude gets `session_id_flag` so terminal-started sessions resume.

## 0.2.0 — 2026-09-13

- The herdr popup (`prefix+c`) is the product: Running here / Resume / Start new, roster, seed catalog of standard agents.
