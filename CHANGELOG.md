# Changelog

## 0.3.3 — 2026-11-13

- Agent marks no longer depend on a font installed by hand. With the Lobe Icons Font installed, kinds show its logos; without it, one ASCII letter per kind (`C` claude, `G` grok, `X` codex, …) instead of empty boxes. `COWBELL_GLYPHS=lobe|text` forces either. `cowbell font` reports what it found; `cowbell font install` downloads the pinned v5.23.0 font, refuses it unless the sha256 matches, and writes it to the user font directory.
- A harness row may carry `requires` and `check`. `requires` is a list of argvs run in order before every start or resume (say, to start the model server the agent talks to); the first that exits non-zero refuses the launch. `check` is one argv, the row's acceptance: when it has no pass in the last 7 days, the launch runs it after `requires` and opens only if it passes. `cowbell accept [id ...]` runs checks ahead of time. Results are kept in `accept.json` in the state directory; the verdict recorded is the last line the check prints on stdout. `cowbell catalog` shows a row with a stale check as `unproven`, and `catalog --check` rejects a malformed `requires` or `check`.
- The `requires` refusal quotes its argv in a form the error catalog can match.
- `COWBELL_DEBUG=1` or `--debug` appends a timed trace of each herdr call, the history scan, trust checks, process scan, picker frame, shell wait, and the launch command to `debug.log` in the state directory. Off unless set.
- Debug trace runbook in `docs/debug-trace.md` documents that the opt-in debug log is written mode 0600, what it masks, and its stated limit.
- The debug trace masks secrets in command lines: the executable's basename and flag names stay; every word after `--` (including the words typed after `--` in `cowbell new`), the value of a sensitive flag, and every `NAME=value` word become `***`. A flag counts as sensitive by a whole name part (`--api-key`, `--system-prompt`), so a boolean flag like `--dangerously-bypass-approvals-and-sandbox` no longer swallows a following `--`. The herdr `pane run` event is logged from the masked argv. The log is opened without following a symlink and refused unless it is a regular file; `accept.tmp` is created with `O_EXCL|O_NOFOLLOW`, and a directory planted there is a clean refusal.
- Stated limit: free text in a `check`'s last output line and in herdr's error text is masked only where it has a credential shape. Other words are written to the trace as they are.
- `a` on a launch sheet saves its shape as a named agent (a `[[harness]]` row copied whole from this one, with the sheet's model, effort, permissions and tools as defaults); the sheet stays open and launches nothing. Not on a resume sheet.
- User-facing error catalog in `docs/errors.md`: documents error templates across the codebase with their cause and suggested user fix. A dedicated AST test (`tests/test_errors_catalog.py`) enforces documentation coverage by failing CI if any user-visible error string is added or modified without an entry in the catalog.
- Seed catalog test suite in `tests/test_seed_catalog.py`: verifies `harnesses.toml` parsing, `cowbell catalog --check` validation, launch argv construction for all seed harnesses, and public-surface hygiene (detecting unexpanded tildes, private usernames, internal hostnames, and stale defaults).
- Harness `check` subprocess now has a 5-second timeout; a hung check fails closed instead of hanging the picker.
- Every subprocess cowbell runs for its own bookkeeping is bounded: `git rev-parse`, `ps`, `lsof`, the trust `subject` probe, `requires` and `check` go through `run_bounded`, and every other `subprocess.run` carries an explicit timeout. A captured call that hits its bound SIGKILLs the child's whole process group, so a grandchild holding the captured pipe cannot hang the picker; an attached call (`requires`) kills only the child, so a tty prompt still works. A missing binary is a clean failure (rc 127, OS error as the detail), and a `check` or `requires` value that is not a real argv is refused rather than split into characters. A bare string is never wrapped into one argv, at the top level or as a `requires` entry: a launch refuses it with the rule `catalog --check` reports (`check must be one argv, a list of strings`; `requires must be a list of argvs (lists of strings)`), and `requires` is checked whole before any entry runs.
- Captured-mode calls (`check`, the trust probe, `git`, `ps`, `lsof`) run with stdin at EOF and no controlling tty: a check can no longer prompt or read your keystrokes. Ctrl-C during one kills its whole process group instead of orphaning it, and a NUL byte in an argv is a clean failure (rc 127), not a traceback.
- The last unguarded file paths take the fifo guard too: the session-history scan (a `*.jsonl` that is a fifo no longer hangs the scan) and the history-cache write (`O_NONBLOCK` then fstat, same as the reads). A truncated `roster.json` is a named refusal (`cowbell: <path>: <reason>`) instead of a traceback, and a Grok chat line with a bad byte is decoded again instead of silently skipped. `catalog --check` speaks plainer — `checks up to schema 2` for a far-newer file, `newer file: read, never rewritten` for one a rev ahead, `1 problem` pluralized — `Permission denied` no longer echoes the path twice, a `schema` that is not an integer is told `schema must be an int` rather than to upgrade, and an undecodable file is `not valid UTF-8` instead of a raw codec dump.
- The picker cannot stack herdr timeouts: after one herdr call times out, later calls in the next ~30 seconds fail fast (`herdr {} skipped: marked down after a timeout`) instead of each waiting 5 seconds. A stalled session-history lookup no longer crashes the picker frame; it yields no history for that place. And a catalog row with no `id` — tolerated by `catalog` and named by `catalog --check` — is skipped by `cowbell accept` and the New-with-options wizard instead of raising KeyError.
- `fc-cache` subprocess now has a 30-second timeout during `cowbell font install`.
- `accept.json` is written mode 0600 explicitly before atomic replace (was umask-dependent).
- `roster.json` — which stores raw argv, prompts included — is written mode 0600 from creation, and the state and config directories are created mode 0700 and a pre-existing looser one is tightened (the catalog can carry secrets in `check`/`requires` argv).
- The harness verify hint now names `agent-run` only; the stale "or sudo" wording is gone (cowbell never falls back to `sudo -u`).
- `cowbell catalog` prints a glyph legend footer (`⌂ local  ↑ vendor · ok  ! more reach  ⊘ blocked  ? unknown`).
- The shipped seed `harnesses.toml` documents `egress` and `family` fields in comments.
- `CHANGELOG.md` now ships inside the sdist.
- `docs/errors.md` corrections: the `nono` row names the real cause/fix, and both home-permission rows' fixes repair the home rather than telling users to install `agent-run`.

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
