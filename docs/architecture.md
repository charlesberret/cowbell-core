# Architecture — cowbell

A module map of the tree, written for someone reading the code for the first time.
Factual lines end with ` (verified: <file, symbol, or command>)`. Anything that
cannot be checked from this tree is marked `DRAFT — needs maintainer check:`.

## Shape

- The whole program is one file, `cowbell.py` (~6,600 lines), with a `__version__`
  constant at the top (currently `0.3.3`) (verified: `cowbell.py:63`, `wc -l cowbell.py`).
- Stdlib only: the imports are `datetime`, `json`, `os`, `re`, `shutil`,
  `subprocess`, `sys`, `tempfile`, `threading`, `time`, `urllib.parse`,
  `concurrent.futures`, `dataclasses`, `pathlib`, and a guarded `tomllib`
  (verified: `cowbell.py` import block, lines ~41–61; `pyproject.toml`
  `dependencies = []`).
- Python ≥ 3.11 is required for `tomllib`; the shell launcher `bin/cowbell`
  probes candidate interpreters and execs `cowbell.py` with the first one that
  passes, following symlinks so a PATH symlink back into the repo still works
  (verified: `bin/cowbell`).
- The file is organized into named banner sections (`# --- <name>`): colour,
  paths, context, scope, catalog, roster, live, session history, trust,
  registry, launch, standalone, hosts, herdr adapter, commands, files, catalog
  writer, tui, ui, launch sheet, main (verified: `grep -n "^# ---" cowbell.py`).

## Entry points

- `cli()` wraps `main(sys.argv[1:])`, translating `HerdrError` to exit 1 and
  `KeyboardInterrupt` to 130; `pyproject.toml` exposes it as the `cowbell`
  console script (verified: `cowbell.py` `cli()`; `pyproject.toml`
  `[project.scripts]`).
- `main(argv)` strips `--debug`, handles `--help`/`--version`, and dispatches
  subcommands: `picker` (default on a tty), `status`/`registry`/`here`, `new`,
  `list`, `catalog [--check]`, `accept`, `enter`, `rename`, `adopt`,
  `reconcile`, `identity`, `font`, plus `cowbell <harness-id>` as a shortcut
  (verified: `cowbell.py` `main()`).
- With no arguments: `picker` when `tui_ok()` (tty, TERM set, no
  `COWBELL_PLAIN`), else `status` (verified: `cowbell.py` `main()`,
  `tui_ok()`).
- `_history` is a private worker subcommand: it reads a JSON payload on stdin
  and prints session rows, used to run discovery as a different unix user
  inside a confinement boundary (verified: `cowbell.py` `main()` `_history`
  branch, `launch_history()`).

## Host seams: `Ctx.live` and `Ctx.launch`

- `Ctx` records where cowbell was invoked from (pane/workspace ids, cwd, mode)
  and carries the two seams: `live` (a `LiveSource`: what is running) and
  `launch` (a `HostLaunch`: where a started agent goes) (verified: `cowbell.py`
  `class Ctx`, comment `# --- hosts`).
- `choose_host(herdr_up)` picks once per run: a herdr-tab context for an agent
  caller inside a herdr pane (or `COWBELL_MODE=tab`), otherwise `mode="here"`
  with `CombinedLive(HerdrLive() if herdr_up else None, ProcessScan())`
  (verified: `cowbell.py` `choose_host()`, `caller_is_agent()`,
  `in_herdr_pane()`).
- `LiveSource` subclasses: `HerdrLive` (agents from the herdr server),
  `ProcessScan` (agent CLIs found by process working directory),
  `CombinedLive` (union of both; a live row keeps an `on tty…` location when it
  came from the process scan) (verified: `cowbell.py` `class HerdrLive`,
  `ProcessScan`, `CombinedLive`, `agent_processes()`).
- `HostLaunch` subclasses: `HerdrLaunch` → `raise_harness` (open a herdr tab
  and start the agent through the herdr CLI); `HereLaunch` → `exec_here`
  (interactive: `os.execv` replaces this terminal) or `spawn_here`
  (`--spawn`/non-tty: detached `Popen` in a new session) (verified:
  `cowbell.py` `class HerdrLaunch`, `HereLaunch`, `exec_here()`,
  `spawn_here()`).

## The registry: one partition of the world

- `build_registry(cat, root, agents, panes, roster, …)` partitions everything
  into `live` (running agents at/below root), `cold` (roster/history rows that
  could resume), `absent` and `startable` (catalog harnesses), applying a
  place's `allow_harness` scoping (verified: `cowbell.py` `build_registry()`).
- A roster row already in Active is removed from Resume by session id, so a
  running sitting is never listed twice (verified: `cowbell.py`
  `build_registry()` — `live_sids` filter).
- Names are computed by `canonical_name` from sources in priority order
  (pinned name, harness title, tab label, stored name, first user utterance,
  kind+session-id fallback); `disambiguate_names` adds a session-id tail when
  titles collide (verified: `cowbell.py` `canonical_name()`,
  `disambiguate_names()`).
- `cmd_registry` renders the same partition as the long-form `status` listing,
  or `--json` (verified: `cowbell.py` `cmd_registry()`, `registry_json()`,
  `render_registry()`).

## The picker

- `picker(ctx, cat)` is the main loop: resolve root → load catalog/roster →
  `live.refresh_sessions` → `live.snapshot` → `launch_history` →
  `build_registry` → `picker_choices` → `render_picker` → `menu`, refreshing
  every `REFRESH_S = 2.0` seconds (verified: `cowbell.py` `picker()`,
  `REFRESH_S`).
- Sections: `Active` (census only — a running sitting cannot be taken over),
  `Resume` (cold rows that can resume), `New Session` (installed, allowed
  harnesses ranked by use here via `rank_harnesses`) (verified: `cowbell.py`
  `picker_choices()`, `build_registry()`; `README.md` "Where agents open").
- Input is mouse-first: `menu()`/`parse_input()` handle clicks, arrows, digits
  and hotkeys (`PICKER_HOTKEYS = "nwgae+ph-ro"`); the plain fallback prints the
  same list and reads a typed key (verified: `cowbell.py` `menu()`,
  `parse_input()`, `PICKER_HOTKEYS`, picker `else` branch).
- Keys: `⏎` open, `n` launch-sheet wizard, `e` edit harness, `o` shape launch
  (or resume sheet on a Resume row), `a` adopt a live sitting, `+` add harness,
  `-` remove, `p`/`h` pin/hide a harness for this directory, `r` rename, `g`
  widen to the git root (verified: `cowbell.py` `picker()` key dispatch,
  `PICKER_HOTKEYS`, `picker_hints()`).

## Launch sheet (`LaunchSpec`)

- A launch is a `LaunchSpec` (name, model, effort, lane, allow/deny, dirs,
  seat, extra); `spec_default` seeds from harness+place defaults,
  `spec_from_row` rebuilds from a recorded roster row, `spec_argv` renders it
  (verified: `cowbell.py` `class LaunchSpec`, `spec_default()`,
  `spec_from_row()`, `spec_argv()`).
- `launch_sheet` is the interactive editor (start / fields / previewed
  command); `a` saves the shape as a new catalog harness via `sheet_save_as` +
  `harness_preset` (verified: `cowbell.py` `launch_sheet()`,
  `sheet_save_as()`, `harness_preset()`; `README.md` launch-sheet paragraph).
- `resume_sheet` does the same over a recorded session so a resume can carry a
  different model/effort/lane/tools (verified: `cowbell.py` `resume_sheet()`,
  `cmd_enter()` `shape=` path).

## Catalog and places

- The catalog is TOML at `~/.config/cowbell/harnesses.toml`
  (`COWBELL_CONFIG_DIR`/`XDG_CONFIG_HOME` override); first run seeds it by
  copying `harnesses.toml` from beside `cowbell.py` or the wheel's
  `share/cowbell/` data; a missing `droid`/`devin` row is spliced in once per
  install state (verified: `cowbell.py` `config_dir()`, `catalog_path()`,
  `seed_path()`, `fill_missing_seed_kinds()`; `pyproject.toml` shared-data).
- Each `[[harness]]` row maps a kind (the CLI executable, or `command` for a
  wrapper script) to launch flags: `model_flag`, `effort_flag`/`efforts`,
  `add_dir_flag`, `resume`, `tools_allow_flag`/`tools_deny_flag`,
  `system_prompt_flag`, `session_id_flag`, `name_flag`, `claim_flag`,
  `provider`/`provider_flag`, `cycle_flag`, plus `requires` and `check`
  (verified: `harnesses.toml` seed rows and comments; `cowbell.py`
  `build_argv()`).
- `installed(h)` checks the wrapper `command` path exists or the kind resolves
  on PATH — only installed harnesses appear in New Session (verified:
  `cowbell.py` `installed()`, `harnesses.toml` comment "shown only when
  installed").
- `[places.<name>]` scopes a directory: `cwd`, `allow_harness`,
  `default_harness`, `lane`, `workspace_label`, `unix_user`,
  `require_uid`, `nono_profile`, `nono_proxy_port`; `place_for` picks the
  deepest matching place and `scoped_catalog` filters the catalog to it
  (verified: `cowbell.py` `places()`, `place_for()`, `scoped_catalog()`;
  `README.md` "A directory can have its own rules").
- `[defaults] untitled_place` remaps a sitting started in the home directory
  into a named place (verified: `cowbell.py` `resolve_root()`; `README.md`
  defaults example).
- Edits go through a splice writer (`harness_insert`, `harness_replace`,
  `harness_delete`, `harness_set_field`, `place_blocks`) that rewrites only the
  changed TOML block, preserving comments and ordering — never a full TOML
  dump (verified: `cowbell.py` `# --- catalog writer` section, `_splice()`,
  `_format_harness_block()`).

## Roster, pins, and state files

- `roster.json` in the state dir (`~/.local/state/cowbell`,
  `COWBELL_STATE_DIR`/`XDG_STATE_HOME` override) records every sitting cowbell
  raised or adopted: name, cwd, harness/kind, model, lane, allow/deny, seat,
  session id, pane binding, recorded argv, effort, dirs, extra (verified:
  `cowbell.py` `state_dir()`, `roster_path()`, `raise_harness()` row dict).
- `pins.json` holds per-directory harness pin/hide prefs; `accept.json` holds
  `check` results; `debug.log` (mode 0600, rotated at 1 MB) holds the opt-in
  `COWBELL_DEBUG`/`--debug` trace; `seed-fill.json` marks completed seed
  splices (verified: `cowbell.py` `pins_path()`, `accept_path()`, `Trace`,
  `seed_fill_marker_path()`).
- `schema = 1` on catalog and roster: a file with a newer schema is read but
  never overwritten (`SchemaError`) (verified: `cowbell.py` `SCHEMA`,
  `check_writable()`; `harnesses.toml` `schema = 1`).
- `refresh_sessions` re-binds a roster row to the agent still occupying its
  pane and unbinds rows whose pane was taken by different work (verified:
  `cowbell.py` `refresh_sessions()`, `occupant_same()`).

## Session discovery (history)

- `discover_sessions` reads each harness's own session store when
  `[defaults] session_history` is `"on"` or `"all"`: Claude under
  `~/.claude/projects/<cwd flattened to ->`, Grok under
  `~/.grok/sessions/<percent-encoded cwd>/` (`HISTORY_PROVIDERS` maps harness
  id → reader) (verified: `cowbell.py` `HISTORY_PROVIDERS`,
  `claude_store()`, `grok_store()`, `discover_sessions()`;
  `harnesses.toml` session_history comment).
- Only metadata is read — session id, timestamps, title/first utterance —
  never transcript bodies; results are cached in the state dir keyed by file
  signatures (verified: `cowbell.py` `_claude_hit()` (reads first 400 lines
  for titles), `_grok_hit()` (reads `summary.json` + first 40 lines),
  `history_cache()`).
- `"all"` also keeps sessions whose title looks dispatched (a role prompt);
  `"on"` filters them out via `DISPATCHED` (verified: `cowbell.py`
  `DISPATCHED`, `discover_sessions()` tail).
- For a `unix_user` place, discovery runs as that user through `agent-run` and
  the `_history` worker; returned text is sanitized (control characters
  stripped, session ids validated) before use (verified: `cowbell.py`
  `launch_history()`).

## Resume mechanism

- Inside herdr: the session id is observed from the started agent
  (`agent_session` in the start response) and stored on the roster row;
  resume replays the harness's `resume` spec with that id — under herdr any
  harness with a `resume` spec can resume (verified: `cowbell.py`
  `raise_harness()` `launched_session`, `build_argv()` resume branch).
- Outside herdr a harness can resume only when cowbell chooses the id itself:
  `session_id_flag` mints a UUID before launch, and resume replays it through
  the `resume` spec (verified: `cowbell.py` `here_command()`;
  `harnesses.toml` comment "Resuming outside herdr"; seed rows: `claude` and
  `pi` set `session_id_flag`).
- `cmd_enter` resolves a name against the roster then history, focuses it if
  live (via `ctx.live.focus`), resumes into a still-present pane when under
  herdr, else launches fresh with `resume_id` (verified: `cowbell.py`
  `cmd_enter()`).
- A resume id that starts with `-` is refused (it would read as an option);
  the `codex` spec is the subcommand form `resume <id> …` (verified:
  `cowbell.py` `build_argv()` resume branch).
- `cowbell rename` pins a name so refreshes never overwrite it; the pin is a
  roster `name_source` (verified: `cowbell.py` `pin_session_name()`,
  `canonical_name()` pinned branch; `README.md`).

## Launch pipeline

- `launch()` runs `run_requires(h)` then `ensure_accepted(h)` before handing
  to `ctx.launch.start` — `requires` argvs in order (first non-zero refuses),
  then the row's `check` when no pass is recorded within `ACCEPT_MAX_AGE`
  (7 days); `cowbell accept` runs checks ahead of time (verified: `cowbell.py`
  `launch()`, `run_requires()`, `ensure_accepted()`, `accepted()`,
  `cmd_accept()`; `harnesses.toml` requires/check comment).
- `build_argv` assembles the agent argv: provider, model, effort (with `{}`
  interpolation), model cycle, lane args from `[lanes.<kind>]`, tool
  allow/deny, extra dirs, seat file, inline `system_prompt`, grok `claim_flag`,
  then the resume spec and passthrough `extra` (verified: `cowbell.py`
  `build_argv()`, `effort_argv()`, `dirs_argv()`, `claim_argv()`).
- `shell_join` refuses control characters rather than quoting them (verified:
  `cowbell.py` `shell_join()`, `CONTROL`).
- `gate` runs the trust `match` verdict before `new`: `blocked` refuses,
  `overprivilege` warns (verified: `cowbell.py` `gate()`, `trust_match()`).

## Confinement (`unix_confine`)

- A harness, place, or `[defaults]` `unix_user` drops the launch to another
  account by prefixing `agent-run <user> --`; no `agent-run` on PATH is a
  refusal — never a `sudo -u` fallback (verified: `cowbell.py`
  `unix_confine()` tail; `harnesses.toml` unix_user comment).
- Fails closed: a drop needs a wall named at the same level as the
  `unix_user` — `nono_profile` (absolute, root-owned, unwritable by
  group/other) wrapped as `nono run --silent --profile <path> --`, or on a
  harness only `wall = "door"` when the root-installed `command` raises its
  own sandbox; a door and a profile in one launch refuse (verified:
  `cowbell.py` `unix_confine()`, `_wall_file_problem()`, `_door_problem()`).
- `nono` gets `--allow-cwd` only when no uid drops, the harness starts in its
  own `cwd`, or the launch is inside a place owned by the dropping account;
  `nono_proxy_port` adds `--proxy-port` (verified: `cowbell.py`
  `unix_confine()`).
- DRAFT — needs maintainer check: what `agent-run`, `nono`, and a "door" command
  actually enforce — they are external binaries; this tree only verifies how
  cowbell invokes them.

## Trust hook

- `[defaults] trust_command` names an external checker asked `subject <path>`,
  `match <tool> <path>`, `badge <tool>`; exit 4 refuses, exit 3 warns; absent
  from PATH means no verdicts are shown at all (verified: `cowbell.py` `EXT`,
  `trust_available()`, `trust_subject()`, `trust_match()`, `trust_badge()`;
  `harnesses.toml` trust comment).
- `TRUST_TIMEOUT = 2.5` seconds bounds a slow checker (verified: `cowbell.py`
  `TRUST_TIMEOUT`, `trust_match()`).
- DRAFT — needs maintainer check: the checker's verdict taxonomy beyond the
  `blocked`/`overprivilege`/`ok` outcomes handled in `parse_match`.

## The herdr adapter boundary

- Every `herdr(…)` CLI call lives inside the `# --- herdr adapter` section of
  `cowbell.py`; `Hosts.test_every_herdr_call_is_inside_the_adapter` scans the
  source and fails on any call outside it (verified: `cowbell.py` adapter
  banner ~line 2784; `tests/test_cowbell.py`
  `test_every_herdr_call_is_inside_the_adapter`).
- `herdr()` runs the binary (`HERDR_BIN_PATH` or `which herdr` or
  `~/.local/bin/herdr`) with `HERDR_TIMEOUT = 5.0`s; `server_up()` probes the
  socket rather than the CLI (verified: `cowbell.py` `herdr_bin()`,
  `herdr()`, `server_up()`).
- The adapter covers: snapshot/agents/panes/workspaces reads, tab create/focus,
  pane split/run/rename/process-info, agent start/focus, identity publish
  (`report_identity`, `stamp_live_identities`, `sync_identity_from_plugin_event`)
  (verified: `cowbell.py` functions inside the adapter section).
- `start_native` waits for a shell in the pane (`wait_shell`,
  `shell_ready_from_process` against `SHELLS`) then runs `herdr agent start`
  with up to 35s timeout and retries on busy (verified: `cowbell.py`
  `start_native()`, `wait_shell()`).
- DRAFT — needs maintainer check: the JSON shapes herdr returns (`agent_session`,
  workspace/pane records) are herdr's contract; this tree only shows how
  cowbell consumes them.

## Identity and coherence

- `mark_harness`/`reconcile_label` keep a pane border as `sitting · harness`
  matching the agent herdr detects; `cowbell reconcile [--dry-run]` rewrites
  stale borders (`coherence_rows`, `apply_coherence`) (verified: `cowbell.py`
  `mark_harness()`, `coherence_rows()`, `apply_coherence()`,
  `reconcile_label()`; `README.md` Commands block).
- `identity stamp|sync` publishes `$glyph` tokens for live agent panes, driven
  by `pane.agent_detected`-style plugin events (verified: `cowbell.py`
  `stamp_live_identities()`, `sync_identity_from_plugin_event()`).

## Glyphs and the icon font

- `glyph_for` returns a kind's mark: a Lobe Icons Font glyph when the font is
  found, else one ASCII letter; `COWBELL_GLYPHS=lobe|text` forces a mode
  (verified: `cowbell.py` `glyph_mode()`, `glyph_for()`,
  `lobe_font_path()`).
- `cowbell font install` downloads the pinned `lobe-icons.ttf`
  (`LOBE_FONT_VERSION v5.23.0`, `LOBE_FONT_URL`), verifies
  `LOBE_FONT_SHA256`, and writes to the user font directory (verified:
  `cowbell.py` `cmd_font_install()`, `LOBE_FONT_*` constants).

## Tests

- `tests/test_cowbell.py` (~5,000 lines) is the main unittest suite; it stubs
  the herdr binary via `HERDR_BIN_PATH` pointing at a logging sentinel so no
  test can reach a live server, and `ZSuiteSeam` fails if it was ever invoked
  (verified: `tests/test_cowbell.py` `setUpModule`, class list via
  `grep -n "class.*TestCase"`).
- `tests/test_pty.py` drives `menu`, `line_input`, and the picker in a real
  pseudo-terminal (verified: `tests/test_pty.py` module docstring).
- `tests/test_packaging.py` pins the PyPI surface: sdist excludes `tests/`,
  wheel ships only `cowbell.py` plus the `harnesses.toml` shared-data file
  (verified: `tests/test_packaging.py`; `pyproject.toml` hatch targets).
- CI runs `python3 -m unittest discover -s tests` on Python 3.11/ubuntu
  (verified: `.github/workflows/test.yml`).
