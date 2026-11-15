# Architecture — cowbell

A module map of the tree, written for someone reading the code for the first time.
Factual lines end with ` (verified: <file, symbol, or command>)`. Anything that
cannot be checked from this tree is marked `DRAFT — needs maintainer check:`.

## Shape

- The whole program is one file, `cowbell.py` (~6,950 lines), with a `__version__`
  constant at the top (currently `0.3.3`) (verified: `cowbell.py:65`, `wc -l cowbell.py` → 6948).
- Stdlib only: the imports are `datetime`, `json`, `os`, `re`, `shutil`,
  `signal`, `stat`, `subprocess`, `sys`, `tempfile`, `threading`, `time`, `urllib.parse`,
  `concurrent.futures`, `dataclasses`, `pathlib`, and a guarded `tomllib`
  (verified: `cowbell.py:41-63` import block; `pyproject.toml:14` `dependencies = []`).
- Python ≥ 3.11 is required for `tomllib`; the shell launcher `bin/cowbell`
  probes candidate interpreters and execs `cowbell.py` with the first one that
  passes, following symlinks so a PATH symlink back into the repo still works
  (verified: `bin/cowbell:2-18`).
- The file is organized into 22 named banner sections (`# --- <name>`): redaction
  (`:180`), colour, paths, context, scope, catalog, roster, live, session history, trust,
  registry, launch, standalone, hosts, herdr adapter, commands, files, catalog
  writer, tui, ui, launch sheet, main. The `Trace` class (`:95`) sits above the first banner
  (verified: `grep -n "^# ---" cowbell.py`, 22 lines; `cowbell.py:95`).

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
  install state (verified: `cowbell.py:381` `config_dir()`, `:480` `catalog_path()`,
  `:366` `seed_path()`, `:518` `fill_missing_seed_kinds()`, `:493` `SEED_FILL_IDS`;
  `pyproject.toml` shared-data).
- Each `[[harness]]` row maps a kind (the CLI executable, or `command` for a
  wrapper script) to launch flags: `model_flag`, `effort_flag`/`efforts`,
  `add_dir_flag`, `resume`, `tools_allow_flag`/`tools_deny_flag`,
  `system_prompt_flag`, `session_id_flag`, `name_flag`, `claim_flag`,
  `provider`/`provider_flag`, `cycle_flag`, plus `requires` and `check`
  (verified: `harnesses.toml` seed rows and comments; `cowbell.py:2499`
  `build_argv()`).
- `check` is one argv (a non-empty list of strings); `requires` is a list of such argvs. A bare
  string is refused for both, never wrapped or split (verified: `cowbell.py:1166` `is_argv()`,
  `:1175` `run_check()`, `:1205` `run_requires()`, `:4512-4517` `cmd_catalog_check()`).
- `installed(h)` checks the wrapper `command` path exists or the kind resolves
  on PATH — only installed harnesses appear in New Session (verified:
  `cowbell.py:1052` `installed()`, `harnesses.toml` comment "shown only when
  installed").
- `[places.<name>]` scopes a directory: `cwd`, `allow_harness`,
  `default_harness`, `lane`, `workspace_label`, `unix_user`,
  `require_uid`, `nono_profile`, `nono_proxy_port`; `place_for` picks the
  deepest matching place and `scoped_catalog` filters the catalog to it
  (verified: `cowbell.py:1005` `place_for()`, `places()`, `scoped_catalog()`;
  `README.md` "A directory can have its own rules").
- `[defaults] untitled_place` remaps a sitting started in the home directory
  into a named place (verified: `cowbell.py` `resolve_root()`; `README.md`
  defaults example).
- Edits go through a splice writer (`harness_insert`, `harness_replace`,
  `harness_delete`, `harness_set_field`, `place_blocks`) that rewrites only the
  changed TOML block, preserving comments and ordering — never a full TOML
  dump (verified: `cowbell.py:4568` `# --- catalog writer` banner, `:4786` `_splice()`,
  `:4790` `harness_insert()`, `_format_harness_block()`).
- `cowbell catalog` prints one row per harness: id, kind, an egress glyph, `installed`
  (`yes`, `unproven` when installed but its `check` has no fresh pass, or `no`), the trust
  badge, and the title, then a one-line glyph legend (verified: `cowbell.py:4406` `cmd_catalog()`,
  `:71-72` `GLYPH`, `LEGEND`, `:4414` legend print).
- `cowbell catalog --check` (`cmd_catalog_check`, `:4471`, dispatched from `main()` at
  `:6898-6901`) rejects a malformed catalog by name and exits 1. Schema rules (`:4479-4485`):
  a `schema` that is not a positive int is a FAIL; `schema > SCHEMA + 1` is a FAIL ("upgrade
  cowbell"); `schema == SCHEMA + 1` is a `warn` (a newer file is read, never rewritten).
  Per-row FAILs (`:4487-4517`): no id, duplicate id, no kind, `egress` not one of
  `local|mesh|vendor`, `lane` not `green|yellow|red`, `models` not a list, `effort_flag` not a
  non-empty list of strings, `efforts` not a list of strings, `add_dir_flag` not a non-empty
  string, `effort` set with no `effort_flag`, `check` not one argv, `requires` not a list of
  argvs. Place FAILs (`:4526-4532`): `allow_harness` or `default_harness` naming an unknown
  harness. Each installed harness's `--help` is probed for its declared flags (`flag_probe`,
  `:4434`); a miss is a `warn`, and a not-installed or unprobeable harness is a `skip` line.
  Output is `FAIL`/`warn`/`skip` lines, then `ok: N harnesses, M places`, or
  `cowbell: check failed (n problem|problems)` on stderr; the singular/plural is an inline
  conditional, not a helper (verified: `cowbell.py:4533-4544`, esp. `:4541`).

## Roster, pins, and state files

- `roster.json` in the state dir (`~/.local/state/cowbell`,
  `COWBELL_STATE_DIR`/`XDG_STATE_HOME` override) records every sitting cowbell
  raised or adopted: name, cwd, harness/kind, model, lane, allow/deny, seat,
  session id, pane binding, recorded argv, effort, dirs, extra (verified:
  `cowbell.py:392` `state_dir()`, `:474` `roster_path()`, `:3430` `raise_harness()` row dict).
- The state dir is created and, unless it is a symlink, chmod'd to `0700` whenever its mode
  differs; the roster, `accept.json` and `debug.log` live there (verified: `cowbell.py:392-400`
  `state_dir()`).
- `save_roster` writes through a `.json.tmp` that is unlinked first, then created
  `O_EXCL|O_NOFOLLOW` at mode `0600` (the roster holds raw argv, prompts included), then
  `os.replace`d over the roster. It first calls `check_writable` on the file's current schema
  (verified: `cowbell.py:1256-1266` `save_roster()`, `:1234` `roster_schema()`).
- `load_roster` opens through `_open_regular`; an `OSError` (unreadable, or a fifo/socket/device
  at the path) or a `ValueError` (invalid JSON or invalid UTF-8) refuses with
  `cowbell: <path>: <reason>` instead of reading as an empty roster. An absent file is `[]`
  (verified: `cowbell.py:1244-1253` `load_roster()`, `:466` `_file_error()`). By contrast
  `load_accepts` and `roster_schema` swallow the same errors and fall back to `{}` / `SCHEMA`
  (verified: `cowbell.py:1067-1073`, `:1234-1241`).
- `_open_regular(path)` opens `O_RDONLY|O_NONBLOCK` and `fstat`s: anything that is not a regular
  file raises `OSError("not a regular file")`, so a fifo planted at a state path cannot hang
  cowbell. `_open_regular_write` is the write side (`O_WRONLY|O_NONBLOCK|O_CREAT|O_TRUNC`; a
  fifo with no reader fails `ENXIO` at once) (verified: `cowbell.py:440-463`).
- `pins.json` holds per-directory harness pin/hide prefs; `accept.json` holds `check` results
  (written by `run_check` through a `0600` `O_EXCL|O_NOFOLLOW` tmp, then `replace`);
  `history-cache.json` caches session-discovery rows (see Session discovery); `debug.log`
  (created `0600` with `O_NOFOLLOW`, rotated to `debug.log.1` once it passes `DEBUG_LOG_MAX` =
  1,000,000 bytes) holds the opt-in `COWBELL_DEBUG`/`--debug` trace; `seed-fill.json` marks
  completed seed splices (verified: `cowbell.py:1269` `pins_path()`, `:1063` `accept_path()`,
  `:1186-1196` `run_check()` tmp, `:153-174` `Trace._open()`, `:80` `DEBUG_LOG_MAX`,
  `:496` `seed_fill_marker_path()`).
- `schema = 1` on catalog and roster: a file with a newer schema is read but
  never overwritten (`SchemaError`) (verified: `cowbell.py:374` `SCHEMA`, `:377` `SchemaError`,
  `:431` `check_writable()`; `harnesses.toml` `schema = 1`).
- `refresh_sessions` re-binds a roster row to the agent still occupying its
  pane and unbinds rows whose pane was taken by different work (verified:
  `cowbell.py:3261` `refresh_sessions()`, `occupant_same()`).

## Debug trace and redaction

- `trace` (a module-level `Trace`, class `:95`, instance `:177`) is off unless `COWBELL_DEBUG` is
  one of `1|true|yes|on|verbose` or `--debug` forces it; events are appended to
  `<state dir>/debug.log` or the path in `COWBELL_DEBUG_LOG`. A failed write marks the trace dead
  and is ignored: debugging never breaks a launch (verified: `cowbell.py:79` `_DEBUG_ON`,
  `:105-110` `enabled()`, `:126-142` `event()`, `:144-151` `path()`).
- `Trace._open` creates the log `0600` at `os.open` time (no umask window) with
  `O_APPEND|O_NONBLOCK|O_NOFOLLOW`: a symlink planted at the log path is refused, a fifo fails
  `ENXIO` instead of hanging, an `fstat` refuses any non-regular file, and `fchmod(0600)` tightens
  a log left by an older run (verified: `cowbell.py:153-174`).
- Argv and free text are masked before they reach the trace; the launch sheet's printed command is
  the product and is never redacted (verified: `cowbell.py:180-184` banner comment; `:2991`
  `exec_here` prints `shell_join(cmd)` unredacted).
- `redact_argv(argv)` keeps the executable's basename and flag names. Masked as `***`: every word
  after a literal `--`; the value of a sensitive flag (the next word, or the part after `=`);
  the value of every `NAME=value` word; and credential shapes inside any other word (via
  `redact_text`) (verified: `cowbell.py:238-274`).
- A flag is sensitive when one of its `-`/`_`/`.`-separated parts matches `_SECRET_PART`: it ends
  in `key|token|secret|prompt` (optionally plural), or is exactly `pass|password|passwd|passphrase|
  passcode` (optionally plural), `auth|oauth|authentication|authorization`, `bearer`, or
  `credential(s)`. Whole-part matching keeps `--dangerously-bypass-approvals-and-sandbox` readable
  (verified: `cowbell.py:186-190` `_SECRET_PART`, `:205` `_sensitive_flag()`).
- `redact_text(s)` masks, in order: URL userinfo, the value after each sensitive flag
  (`_mask_flag_values`, `:210`), `NAME=value` where NAME contains
  `key|token|secret|pass|auth|bearer|credential|prompt`, and token-shaped words (`sk-`/`pk-`,
  `gh[pousr]_`, `github_pat_`, `Bearer x`). Other prose is not masked: free text has no structure
  that tells a secret from a word (verified: `cowbell.py:227-235`, `:195-202`;
  `docs/debug-trace.md`).
- `redact_launch(cmd, passthrough)` is `redact_argv` plus the words typed after `--` in
  `cowbell new`: `split_passthrough` drops that `--`, so the words are found by their last
  occurrence in the command and masked (verified: `cowbell.py:277-290`).
- Call sites: `requires` (`:1208`), `check` (`:1226`), `trust` (`:1907`), `exec` (`:2989`),
  `spawn` (`:3027`), the herdr call trace (`:3145`, `:3156`), the launch line shown for a herdr
  pane (`:3472`), `raise` (`:3516`) and `start` (`:6840`) (verified: `grep -n "redact_" cowbell.py`).

## Session discovery (history)

- `discover_sessions` reads each harness's own session store when
  `[defaults] session_history` is `"on"` or `"all"`: Claude under
  `~/.claude/projects/<cwd flattened to ->`, Grok under
  `~/.grok/sessions/<percent-encoded cwd>/` (`HISTORY_PROVIDERS` maps harness
  id → reader) (verified: `cowbell.py:1759` `HISTORY_PROVIDERS`, `:1575`
  `claude_store()`, `:1657` `grok_store()`, `:1825` `discover_sessions()`;
  `harnesses.toml` session_history comment).
- Only titles and timestamps are kept — session id, timestamps, title/first utterance
  (60 characters) — never transcript bodies. The reader does open the transcript: `_claude_hit`
  reads up to the first 401 lines of the `.jsonl` for a `custom-title` record and the first real
  user line; `_grok_hit` reads `summary.json` and, only when that title is missing or is chrome,
  up to 41 lines of `chat_history.jsonl` (verified: `cowbell.py:1588-1612` `_claude_hit()`
  (`i > 400` break), `:1672-1711` `_grok_hit()` (`i > 40` break), `:1560` `session_title()`).
- Every history read goes through `_open_regular`, so a fifo or device at a store path is
  skipped, not waited on, and every line or file is decoded as UTF-8 with `errors="replace"`, so
  an invalid byte cannot abort a scan (verified: `cowbell.py:1592`/`:1597` `_claude_hit`,
  `:1665`/`:1667` `_read_json`, `:1694`/`:1699` `_grok_hit`, `:1514-1515` `history_cache`). An
  `OSError` leaves the hit with blank fields.
- Results are cached in `history-cache.json` in the state dir, keyed by `path:mtime:size` (a Grok
  key joins the chat and summary signatures); the cache holds those title/utterance fields, so it
  is as private as the state dir (`0700`) (verified: `cowbell.py:1512` `history_cache()`, `:1530`
  `cache_key()`, `:1638-1654` `claude_sessions()`, `:1714-1734` `grok_sessions()`).
- `write_history_cache` writes through `_open_regular_write`, so a fifo planted at
  `history-cache.json` fails `ENXIO` and the write is dropped, never blocked; any `OSError` is
  swallowed ("a slow cowbell, not a broken one"). The JSON text is cut at 4,000,000 characters
  before encoding, so an over-cap cache is truncated mid-document and `history_cache()` then reads
  it back as `{}` (verified: `cowbell.py:1520-1527`, `:1516`).
- `"all"` also keeps sessions whose title looks dispatched (a role prompt);
  `"on"` filters them out via `DISPATCHED` (verified: `cowbell.py:1509`
  `DISPATCHED`, `:1839-1840` `discover_sessions()` tail).
- For a `unix_user` place, discovery runs as that user through `agent-run` and the `_history`
  worker (`main()` branch `:6845-6849`; the child is `sys.executable -I <cowbell.py> _history`,
  15 s timeout). Returned rows are checked before use: every `session_id` must fully match
  `SESSION_ID`; every `cwd` must equal the requested root, be a plain absolute path and be owned by
  that account; and `title`, `harness_title`, `utterance` and `name` lose C0 and C1 control
  characters (`CONTROL_WIDE`) (verified: `cowbell.py:1762-1822` `launch_history()`, `:2557`
  `SESSION_ID`, `:2555` `CONTROL_WIDE`).

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
  to `ctx.launch.start`: the row's `requires` argvs in order (first failure refuses), then the
  row's `check` when no pass is recorded within `ACCEPT_MAX_AGE` (7 days); `cowbell accept`
  runs checks ahead of time (verified: `cowbell.py:3031` `launch()`, `:1200` `run_requires()`,
  `:1220` `ensure_accepted()`, `:1076` `accepted()`, `:1060` `ACCEPT_MAX_AGE`, `:4451`
  `cmd_accept()`; `harnesses.toml` requires/check comment).
- `run_requires` validates the whole `requires` value first: it must be a list and every entry an
  argv (`is_argv`: a non-empty list of strings), or it refuses `requires must be a list of argvs
  (lists of strings)` before any entry runs; a bare string is never wrapped or split. Each entry
  then runs through `run_bounded(argv, REQUIRES_TIMEOUT=60, attached=True)`: output goes to this
  terminal, and the first entry that times out, exits non-zero, or will not start (rc 127 with the
  OS error) refuses the launch. Each entry's trace line is the redacted argv (verified:
  `cowbell.py:1200-1217`, `:1097` `REQUIRES_TIMEOUT`, `:1166-1168` `is_argv()`, `:1208`).
- `run_check` runs the `check` argv (captured, `CHECK_TIMEOUT` = 5 s) and records
  `{ok, ts, detail}` under the row id in `accept.json`. A `check` that is not an argv is a failed
  check ("check must be one argv, a list of strings"), the same refusal `catalog --check` makes; a
  timeout is a failed check; the detail is the last line of stdout, else of stderr, else `exit N`.
  The trace records the detail through `redact_text` (verified: `cowbell.py:1171-1197`
  `run_check()`, `:1098` `CHECK_TIMEOUT`, `:1226`).
- `run_bounded(argv, timeout, attached=False)` is the one bounded runner (verified:
  `cowbell.py:1105-1163`). Captured (default): the child gets a new session
  (`start_new_session`), `stdin=DEVNULL` and piped output, so it has no controlling tty and cannot
  prompt; on timeout, or on an interrupt such as Ctrl-C (which a session leader does not
  receive), the whole process group is `SIGKILL`ed with `os.killpg(proc.pid, …)` and the pipes
  are closed; worst case `timeout + KILL_GRACE` (2 s). Attached: the child inherits this terminal
  (a `sudo` prompt still works) and a timeout `terminate`s then `kill`s the child alone — never
  `killpg` — so its grandchildren are orphaned by design; worst case `timeout + 2 × KILL_GRACE`.
  It returns the `CompletedProcess`, or `None` when the bound was hit; a binary that will not
  start, or an argv containing a NUL byte (`ValueError`), comes back as rc 127 with the error in
  `stderr`, like a shell.
- `build_argv` assembles the agent argv: provider, model, effort (with `{}`
  interpolation), model cycle, lane args from `[lanes.<kind>]`, tool
  allow/deny, extra dirs, seat file, inline `system_prompt`, grok `claim_flag`,
  then the resume spec and passthrough `extra` (verified: `cowbell.py:2499`
  `build_argv()`, `effort_argv()`, `dirs_argv()`, `claim_argv()`).
- `shell_join` refuses control characters rather than quoting them (verified:
  `cowbell.py:2560` `shell_join()`, `:2553` `CONTROL`).
- `gate` runs the trust `match` verdict before `new`: `blocked` refuses,
  `overprivilege` warns (verified: `cowbell.py:4335` `gate()`, `:1892` `trust_match()`).

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
  from PATH means no verdicts are shown at all (verified: `cowbell.py:910` `EXT`,
  `:1860` `trust_available()`, `:1864` `trust_subject()`, `:1892` `trust_match()`,
  `:1911` `trust_badge()`; `harnesses.toml` trust comment).
- `TRUST_TIMEOUT = 2.5` seconds bounds a slow checker (verified: `cowbell.py:911`
  `TRUST_TIMEOUT`, used at `:1867`, `:1899`, `:1916`).
- Calls that go through `run_bounded` (verified: `grep -n "run_bounded(" cowbell.py`):
  `git_root` (`:661`, `GIT_TIMEOUT`), the `check` (`:1177`, captured), `requires` (`:1209`,
  attached), `trust_subject` (`:1867`), and the `ps` and `lsof` scans (`:2615`, `:2651`).
  Captured callers kill the whole process group on timeout or interrupt; the one attached caller
  (`requires`) kills the child only.
- `trust_match` and `trust_badge` do not use it: they call `subprocess.run` with
  `timeout=TRUST_TIMEOUT` (`:1898`, `:1915`), so a timeout reads as "no verdict" (`unknown` / `?`),
  but nothing puts the checker in its own session or kills a grandchild. Also bounded only by an
  explicit `timeout=`: `launch_history` (15 s, `:1797`), `flag_probe` (15 s, `:4444`), `herdr()`
  (`HERDR_TIMEOUT`, `:3147`), `fc-cache` (30 s, `:3672`).
- DRAFT — needs maintainer check: the checker's verdict taxonomy beyond the
  `blocked`/`overprivilege`/`ok` outcomes handled in `parse_match` (`:1871`).

## The herdr adapter boundary

- Every `herdr(…)` CLI call lives inside the `# --- herdr adapter` section of
  `cowbell.py`; `Hosts.test_every_herdr_call_is_inside_the_adapter` scans the
  source and fails on any call outside it (verified: `cowbell.py:3124` adapter
  banner; `tests/test_cowbell.py:1145` `class Hosts`, `:1150`
  `test_every_herdr_call_is_inside_the_adapter`).
- `herdr()` runs the binary (`HERDR_BIN_PATH` or `which herdr` or
  `~/.local/bin/herdr`) with `HERDR_TIMEOUT = 5.0`s; `server_up()` probes the
  socket rather than the CLI (verified: `cowbell.py:3126` `herdr_bin()`, `:3130`
  `HERDR_TIMEOUT`, `:3140` `herdr()`, `:3195` `server_up()`).
- `herdr()` writes its trace line from the redacted argv (`redact_argv`; `log_argv` lets a caller
  show a masked launch line in place of one packed argument) and redacts the error text it traces
  (verified: `cowbell.py:3140-3156`).
- The adapter covers: snapshot/agents/panes/workspaces reads, tab create/focus,
  pane split/run/rename/process-info, agent start/focus, identity publish
  (`report_identity`, `stamp_live_identities`, `sync_identity_from_plugin_event`)
  (verified: `cowbell.py` functions inside `:3124-3983`).
- `start_native` waits for a shell in the pane (`wait_shell`, 10 s,
  `shell_ready_from_process` against `SHELLS`) then runs `herdr agent start`
  with a 35 s subprocess timeout (`--timeout 30000` to herdr itself) and up to 5 attempts on
  `agent_pane_busy` / "not an available shell" (verified: `cowbell.py:3392` `wait_shell()`,
  `:3408-3427` `start_native()`, `:70` `SHELLS`).
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

- `tests/test_cowbell.py` (~5,700 lines, 46 `TestCase` classes) is the main unittest suite; it
  stubs the herdr binary via `HERDR_BIN_PATH` pointing at a logging sentinel so no
  test can reach a live server, and `ZSuiteSeam` fails if it was ever invoked
  (verified: `tests/test_cowbell.py:88` `setUpModule`, `:5331` `ZSuiteSeam`, class list via
  `grep -n "class.*TestCase"`; `wc -l` → 5700). The classes that pin the hardening work:
  `DebugLog` (`:1903`), `SessionHistory` (`:3016`), `CatalogCheck` (`:4954`),
  `SubprocessTimeouts` (`:5286`), `RequiresCheck` (`:5342`), `BoundedSubprocess` (`:5548`).
- `tests/test_pty.py` (315 lines) drives `menu`, `line_input`, and the picker in a real
  pseudo-terminal (verified: `tests/test_pty.py` module docstring; classes `Menu`, `Prompt`,
  `PickerHere`).
- `tests/test_packaging.py` pins the PyPI surface: sdist excludes `tests/` and includes
  `CHANGELOG.md`, the console script is `cowbell:cli`, and the wheel ships only `cowbell.py` plus
  the `harnesses.toml` shared-data file (verified: `tests/test_packaging.py:10-24`; `pyproject.toml`
  hatch targets).
- `tests/test_errors_catalog.py` requires every user-facing error template in `cowbell.py` to
  appear in `docs/errors.md` (verified: `tests/test_errors_catalog.py` module docstring).
- `tests/test_seed_catalog.py` parses the seed `harnesses.toml`, runs `catalog --check` and the
  launch argv over it, and checks public-surface hygiene (verified: `tests/test_seed_catalog.py`
  module docstring).
- CI runs `python3 -m unittest discover -s tests` on Python 3.11/ubuntu
  (verified: `.github/workflows/test.yml`).

