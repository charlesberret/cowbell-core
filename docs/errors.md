# User-facing error catalog

Stable message templates cowbell may print or exit with. Placeholders: `{}` is substituted text; `{!r}` is a Python `repr` of the value.

CI enforces that every template extracted from source appears below (see `tests/test_errors_catalog.py`).

### FAIL {}

| | |
|--|--|
| Message | `  FAIL {}` |
| Cause | Catalog validation reported a hard failure. |
| Fix | Address the failure text printed on the preceding line of `cowbell catalog --check`. |
| Source | `cowbell.py` |

### binary not found on PATH: {}

| | |
|--|--|
| Message | `  binary not found on PATH: {}` |
| Cause | A required executable is not on PATH. |
| Fix | Install the binary or extend PATH before invoking cowbell. |
| Source | `cowbell.py` |

### harness {!r} already exists

| | |
|--|--|
| Message | `  harness {!r} already exists` |
| Cause | Harness id, install, or catalog field does not match what you asked for. |
| Fix | Run `cowbell catalog`, install the agent CLI, or adjust harness/place settings. |
| Source | `cowbell.py` |

### target executable/kind is not specified

| | |
|--|--|
| Message | `  target executable/kind is not specified` |
| Cause | Interactive harness manager or verify subcommand rejected the request. |
| Fix | Follow the on-screen hint: pick a valid harness, install the binary, or fix catalog fields. |
| Source | `cowbell.py` |

### unix user {!r} does not exist on this host

| | |
|--|--|
| Message | `  unix user {!r} does not exist on this host` |
| Cause | Interactive harness manager or verify subcommand rejected the request. |
| Fix | Follow the on-screen hint: pick a valid harness, install the binary, or fix catalog fields. |
| Source | `cowbell.py` |

### unknown harness {}

| | |
|--|--|
| Message | `  unknown harness {}` |
| Cause | Harness id, install, or catalog field does not match what you asked for. |
| Fix | Run `cowbell catalog`, install the agent CLI, or adjust harness/place settings. |
| Source | `cowbell.py` |

### {} is not installed here

| | |
|--|--|
| Message | `  {} is not installed here` |
| Cause | Interactive harness manager or verify subcommand rejected the request. |
| Fix | Follow the on-screen hint: pick a valid harness, install the binary, or fix catalog fields. |
| Source | `cowbell.py` |

### ⊘ refused: {} on {} is blocked {}

| | |
|--|--|
| Message | `  ⊘ refused: {} on {} is blocked {}` |
| Cause | Trust clearance blocked launching the harness in this directory. |
| Fix | Use a lower-privilege lane, a different directory, or adjust trust/policy for this tree. |
| Source | `cowbell.py` |

### agent start {} failed

| | |
|--|--|
| Message | `agent start {} failed` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### cowbell adopt --pane ID  (or a sitting name)

| | |
|--|--|
| Message | `cowbell adopt --pane ID  (or a sitting name)` |
| Cause | No unique live agent pane matched the adopt/focus request. |
| Fix | Pass `--pane` with a pane id from Active, or focus the agent in herdr first. |
| Source | `cowbell.py` |

### cowbell identity stamp|sync

| | |
|--|--|
| Message | `cowbell identity stamp|sync` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### ! {} has more reach than {} needs{}

| | |
|--|--|
| Message | `cowbell: ! {} has more reach than {} needs{}` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### ambiguous session {!r}

| | |
|--|--|
| Message | `cowbell: ambiguous session {!r}` |
| Cause | Resume, rename, or history lookup could not resolve the session. |
| Fix | Pick a name from `cowbell sessions`, refresh history, or pass an unambiguous id. |
| Source | `cowbell.py` |

### ambiguous session {!r} matches: {}

| | |
|--|--|
| Message | `cowbell: ambiguous session {!r} matches: {}` |
| Cause | Resume, rename, or history lookup could not resolve the session. |
| Fix | Pick a name from `cowbell sessions`, refresh history, or pass an unambiguous id. |
| Source | `cowbell.py` |

### ambiguous sitting {!r}

| | |
|--|--|
| Message | `cowbell: ambiguous sitting {!r}` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### cannot discover sessions as unix user {!r} (agent-run is not installe...

| | |
|--|--|
| Message | `cowbell: cannot discover sessions as unix user {!r} (agent-run is not installed and sudo is not on PATH)` |
| Cause | The configured Unix account or privilege helper is missing or wrong. |
| Fix | Set a valid `unix_user`, install `agent-run` or `sudo`, or fix the account name on this host. |
| Source | `cowbell.py` |

### cannot drop to unix user {!r} (agent-run is not installed and sudo is...

| | |
|--|--|
| Message | `cowbell: cannot drop to unix user {!r} (agent-run is not installed and sudo is not on PATH)` |
| Cause | The configured Unix account or privilege helper is missing or wrong. |
| Fix | Set a valid `unix_user`, install `agent-run` or `sudo`, or fix the account name on this host. |
| Source | `cowbell.py` |

### cannot write a null TOML value

| | |
|--|--|
| Message | `cowbell: cannot write a null TOML value` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### cannot write {} as TOML

| | |
|--|--|
| Message | `cowbell: cannot write {} as TOML` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### harness needs an id

| | |
|--|--|
| Message | `cowbell: harness needs an id` |
| Cause | Harness id, install, or catalog field does not match what you asked for. |
| Fix | Run `cowbell catalog`, install the agent CLI, or adjust harness/place settings. |
| Source | `cowbell.py` |

### harness {!r} already exists

| | |
|--|--|
| Message | `cowbell: harness {!r} already exists` |
| Cause | Harness id, install, or catalog field does not match what you asked for. |
| Fix | Run `cowbell catalog`, install the agent CLI, or adjust harness/place settings. |
| Source | `cowbell.py` |

### invalid harness field {!r}

| | |
|--|--|
| Message | `cowbell: invalid harness field {!r}` |
| Cause | Harness id, install, or catalog field does not match what you asked for. |
| Fix | Run `cowbell catalog`, install the agent CLI, or adjust harness/place settings. |
| Source | `cowbell.py` |

### lane must be one of {}

| | |
|--|--|
| Message | `cowbell: lane must be one of {}` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### no catalog at {}

| | |
|--|--|
| Message | `cowbell: no catalog at {}` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### no focused agent pane to adopt. Live{}:

| | |
|--|--|
| Message | `cowbell: no focused agent pane to adopt. Live{}:` |
| Cause | No unique live agent pane matched the adopt/focus request. |
| Fix | Pass `--pane` with a pane id from Active, or focus the agent in herdr first. |
| Source | `cowbell.py` |

### no harness {!r}

| | |
|--|--|
| Message | `cowbell: no harness {!r}` |
| Cause | Harness id, install, or catalog field does not match what you asked for. |
| Fix | Run `cowbell catalog`, install the agent CLI, or adjust harness/place settings. |
| Source | `cowbell.py` |

### no live agent in pane {}

| | |
|--|--|
| Message | `cowbell: no live agent in pane {}` |
| Cause | No unique live agent pane matched the adopt/focus request. |
| Fix | Pass `--pane` with a pane id from Active, or focus the agent in herdr first. |
| Source | `cowbell.py` |

### no place {!r} in {} (have: {})

| | |
|--|--|
| Message | `cowbell: no place {!r} in {} (have: {})` |
| Cause | The named place is missing or disallows the requested harness. |
| Fix | Define the place in `harnesses.toml` or choose an allowed harness for that place. |
| Source | `cowbell.py` |

### no python >= 3.11 found (need tomllib)

| | |
|--|--|
| Message | `cowbell: no python >= 3.11 found (need tomllib)` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `bin/cowbell` |

### no session {!r}

| | |
|--|--|
| Message | `cowbell: no session {!r}` |
| Cause | Resume, rename, or history lookup could not resolve the session. |
| Fix | Pick a name from `cowbell sessions`, refresh history, or pass an unambiguous id. |
| Source | `cowbell.py` |

### no session {!r} on roster or in history

| | |
|--|--|
| Message | `cowbell: no session {!r} on roster or in history` |
| Cause | Resume, rename, or history lookup could not resolve the session. |
| Fix | Pick a name from `cowbell sessions`, refresh history, or pass an unambiguous id. |
| Source | `cowbell.py` |

### nono is not on PATH (needed for this place)

| | |
|--|--|
| Message | `cowbell: nono is not on PATH (needed for this place)` |
| Cause | The named place is missing or disallows the requested harness. |
| Fix | Define the place in `harnesses.toml` or choose an allowed harness for that place. |
| Source | `cowbell.py` |

### pane {} hosts no recognized agent

| | |
|--|--|
| Message | `cowbell: pane {} hosts no recognized agent` |
| Cause | No unique live agent pane matched the adopt/focus request. |
| Fix | Pass `--pane` with a pane id from Active, or focus the agent in herdr first. |
| Source | `cowbell.py` |

### pin/hide needs a harness id

| | |
|--|--|
| Message | `cowbell: pin/hide needs a harness id` |
| Cause | Harness id, install, or catalog field does not match what you asked for. |
| Fix | Run `cowbell catalog`, install the agent CLI, or adjust harness/place settings. |
| Source | `cowbell.py` |

### python >= 3.11 required (tomllib)

| | |
|--|--|
| Message | `cowbell: python >= 3.11 required (tomllib)` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### refused — no unix_user for {}; set [places.*] unix_user or use agent-...

| | |
|--|--|
| Message | `cowbell: refused — no unix_user for {}; set [places.*] unix_user or use agent-run <uid> -- …` |
| Cause | The configured Unix account or privilege helper is missing or wrong. |
| Fix | Set a valid `unix_user`, install `agent-run` or `sudo`, or fix the account name on this host. |
| Source | `cowbell.py` |

### refused — {} on {}: blocked {} (T4 under-clearance)

| | |
|--|--|
| Message | `cowbell: refused — {} on {}: blocked {} (T4 under-clearance)` |
| Cause | Trust clearance blocked launching the harness in this directory. |
| Fix | Use a lower-privilege lane, a different directory, or adjust trust/policy for this tree. |
| Source | `cowbell.py` |

### session discovery as {!r} failed: {}

| | |
|--|--|
| Message | `cowbell: session discovery as {!r} failed: {}` |
| Cause | Resume, rename, or history lookup could not resolve the session. |
| Fix | Pick a name from `cowbell sessions`, refresh history, or pass an unambiguous id. |
| Source | `cowbell.py` |

### session discovery as {!r} returned invalid metadata

| | |
|--|--|
| Message | `cowbell: session discovery as {!r} returned invalid metadata` |
| Cause | Resume, rename, or history lookup could not resolve the session. |
| Fix | Pick a name from `cowbell sessions`, refresh history, or pass an unambiguous id. |
| Source | `cowbell.py` |

### unix_user {!r} is not on this host

| | |
|--|--|
| Message | `cowbell: unix_user {!r} is not on this host` |
| Cause | The configured Unix account or privilege helper is missing or wrong. |
| Fix | Set a valid `unix_user`, install `agent-run` or `sudo`, or fix the account name on this host. |
| Source | `cowbell.py` |

### unknown command or harness {!r} (see: cowbell catalog)

| | |
|--|--|
| Message | `cowbell: unknown command or harness {!r} (see: cowbell catalog)` |
| Cause | Harness id, install, or catalog field does not match what you asked for. |
| Fix | Run `cowbell catalog`, install the agent CLI, or adjust harness/place settings. |
| Source | `cowbell.py` |

### unknown flag {}

| | |
|--|--|
| Message | `cowbell: unknown flag {}` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### unknown harness {!r} (see: cowbell catalog)

| | |
|--|--|
| Message | `cowbell: unknown harness {!r} (see: cowbell catalog)` |
| Cause | Harness id, install, or catalog field does not match what you asked for. |
| Fix | Run `cowbell catalog`, install the agent CLI, or adjust harness/place settings. |
| Source | `cowbell.py` |

### {!r} is not a session name

| | |
|--|--|
| Message | `cowbell: {!r} is not a session name` |
| Cause | Resume, rename, or history lookup could not resolve the session. |
| Fix | Pick a name from `cowbell sessions`, refresh history, or pass an unambiguous id. |
| Source | `cowbell.py` |

### {}

| | |
|--|--|
| Message | `cowbell: {}` |
| Cause | Herdr or internal runtime failure surfaced at CLI exit. |
| Fix | Run with `HERDR_BIN_PATH` pointing at a working herdr, or retry after the server responds. |
| Source | `cowbell.py` |

### {} cannot be focused from here

| | |
|--|--|
| Message | `cowbell: {} cannot be focused from here` |
| Cause | No unique live agent pane matched the adopt/focus request. |
| Fix | Pass `--pane` with a pane id from Active, or focus the agent in herdr first. |
| Source | `cowbell.py` |

### {} has no add_dir_flag in the catalog; --add-dir has nowhere to go

| | |
|--|--|
| Message | `cowbell: {} has no add_dir_flag in the catalog; --add-dir has nowhere to go` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### {} has no effort_flag in the catalog; --effort has nowhere to go

| | |
|--|--|
| Message | `cowbell: {} has no effort_flag in the catalog; --effort has nowhere to go` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### {} is not a directory

| | |
|--|--|
| Message | `cowbell: {} is not a directory` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### {} is not installed here ({})

| | |
|--|--|
| Message | `cowbell: {} is not installed here ({})` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### {} is not on PATH

| | |
|--|--|
| Message | `cowbell: {} is not on PATH` |
| Cause | A required executable is not on PATH. |
| Fix | Install the binary or extend PATH before invoking cowbell. |
| Source | `cowbell.py` |

### {} is schema {}; cowbell {} writes schema {}. Upgrade cowbell before ...

| | |
|--|--|
| Message | `cowbell: {} is schema {}; cowbell {} writes schema {}. Upgrade cowbell before changing it.` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### {} may not start in place {} (allowed: {})

| | |
|--|--|
| Message | `cowbell: {} may not start in place {} (allowed: {})` |
| Cause | The named place is missing or disallows the requested harness. |
| Fix | Define the place in `harnesses.toml` or choose an allowed harness for that place. |
| Source | `cowbell.py` |

### {} rename failed: {}

| | |
|--|--|
| Message | `cowbell: {} rename failed: {}` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### {} uses harness {!r} which may not resume in {}

| | |
|--|--|
| Message | `cowbell: {} uses harness {!r} which may not resume in {}` |
| Cause | Harness id, install, or catalog field does not match what you asked for. |
| Fix | Run `cowbell catalog`, install the agent CLI, or adjust harness/place settings. |
| Source | `cowbell.py` |

### enter <name>

| | |
|--|--|
| Message | `enter <name>` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

### harness row with no id

| | |
|--|--|
| Message | `harness row with no id` |
| Cause | The harness catalog fails `cowbell catalog --check` validation. |
| Fix | Edit `harnesses.toml` to satisfy the constraint named in the message. |
| Source | `cowbell.py` |

### harness {}: add_dir_flag must be a flag string

| | |
|--|--|
| Message | `harness {}: add_dir_flag must be a flag string` |
| Cause | The harness catalog fails `cowbell catalog --check` validation. |
| Fix | Edit `harnesses.toml` to satisfy the constraint named in the message. |
| Source | `cowbell.py` |

### harness {}: duplicate id

| | |
|--|--|
| Message | `harness {}: duplicate id` |
| Cause | The harness catalog fails `cowbell catalog --check` validation. |
| Fix | Edit `harnesses.toml` to satisfy the constraint named in the message. |
| Source | `cowbell.py` |

### harness {}: effort {!r} set but no effort_flag

| | |
|--|--|
| Message | `harness {}: effort {!r} set but no effort_flag` |
| Cause | The harness catalog fails `cowbell catalog --check` validation. |
| Fix | Edit `harnesses.toml` to satisfy the constraint named in the message. |
| Source | `cowbell.py` |

### harness {}: effort_flag must be a list of strings

| | |
|--|--|
| Message | `harness {}: effort_flag must be a list of strings` |
| Cause | The harness catalog fails `cowbell catalog --check` validation. |
| Fix | Edit `harnesses.toml` to satisfy the constraint named in the message. |
| Source | `cowbell.py` |

### harness {}: efforts must be a list of strings

| | |
|--|--|
| Message | `harness {}: efforts must be a list of strings` |
| Cause | The harness catalog fails `cowbell catalog --check` validation. |
| Fix | Edit `harnesses.toml` to satisfy the constraint named in the message. |
| Source | `cowbell.py` |

### harness {}: missing kind

| | |
|--|--|
| Message | `harness {}: missing kind` |
| Cause | The harness catalog fails `cowbell catalog --check` validation. |
| Fix | Edit `harnesses.toml` to satisfy the constraint named in the message. |
| Source | `cowbell.py` |

### harness {}: models must be a list

| | |
|--|--|
| Message | `harness {}: models must be a list` |
| Cause | The harness catalog fails `cowbell catalog --check` validation. |
| Fix | Edit `harnesses.toml` to satisfy the constraint named in the message. |
| Source | `cowbell.py` |

### harness {}: unknown egress {!r}

| | |
|--|--|
| Message | `harness {}: unknown egress {!r}` |
| Cause | The harness catalog fails `cowbell catalog --check` validation. |
| Fix | Edit `harnesses.toml` to satisfy the constraint named in the message. |
| Source | `cowbell.py` |

### harness {}: unknown lane {!r}

| | |
|--|--|
| Message | `harness {}: unknown lane {!r}` |
| Cause | The harness catalog fails `cowbell catalog --check` validation. |
| Fix | Edit `harnesses.toml` to satisfy the constraint named in the message. |
| Source | `cowbell.py` |

### harness {}: {} not in {} help

| | |
|--|--|
| Message | `harness {}: {} not in {} help` |
| Cause | The harness catalog fails `cowbell catalog --check` validation. |
| Fix | Edit `harnesses.toml` to satisfy the constraint named in the message. |
| Source | `cowbell.py` |

### herdr is not installed; nothing to reconcile

| | |
|--|--|
| Message | `herdr is not installed; nothing to reconcile` |
| Cause | The herdr CLI failed, timed out, or returned unexpected output. |
| Fix | Confirm herdr is installed, the socket is reachable, and server commands succeed outside cowbell. |
| Source | `cowbell.py` |

### herdr unavailable: {}

| | |
|--|--|
| Message | `herdr unavailable: {}` |
| Cause | The herdr CLI failed, timed out, or returned unexpected output. |
| Fix | Confirm herdr is installed, the socket is reachable, and server commands succeed outside cowbell. |
| Source | `cowbell.py` |

### herdr {} exited {}

| | |
|--|--|
| Message | `herdr {} exited {}` |
| Cause | The herdr CLI failed, timed out, or returned unexpected output. |
| Fix | Confirm herdr is installed, the socket is reachable, and server commands succeed outside cowbell. |
| Source | `cowbell.py` |

### herdr {} timed out after {}s

| | |
|--|--|
| Message | `herdr {} timed out after {}s` |
| Cause | The herdr CLI failed, timed out, or returned unexpected output. |
| Fix | Confirm herdr is installed, the socket is reachable, and server commands succeed outside cowbell. |
| Source | `cowbell.py` |

### herdr {}: non-JSON output: {}

| | |
|--|--|
| Message | `herdr {}: non-JSON output: {}` |
| Cause | The herdr CLI failed, timed out, or returned unexpected output. |
| Fix | Confirm herdr is installed, the socket is reachable, and server commands succeed outside cowbell. |
| Source | `cowbell.py` |

### new --harness <id> (or set default_harness on the place)

| | |
|--|--|
| Message | `new --harness <id> (or set default_harness on the place)` |
| Cause | Harness id, install, or catalog field does not match what you asked for. |
| Fix | Run `cowbell catalog`, install the agent CLI, or adjust harness/place settings. |
| Source | `cowbell.py` |

### no root pane returned: {}

| | |
|--|--|
| Message | `no root pane returned: {}` |
| Cause | No unique live agent pane matched the adopt/focus request. |
| Fix | Pass `--pane` with a pane id from Active, or focus the agent in herdr first. |
| Source | `cowbell.py` |

### place {}: allow_harness names unknown harness {!r}

| | |
|--|--|
| Message | `place {}: allow_harness names unknown harness {!r}` |
| Cause | A place references a harness id that does not exist in the catalog. |
| Fix | Add the harness or correct `allow_harness` / `default_harness` for that place. |
| Source | `cowbell.py` |

### place {}: default_harness names unknown harness {!r}

| | |
|--|--|
| Message | `place {}: default_harness names unknown harness {!r}` |
| Cause | A place references a harness id that does not exist in the catalog. |
| Fix | Add the harness or correct `allow_harness` / `default_harness` for that place. |
| Source | `cowbell.py` |

### {} runs on {} (pid {}); cowbell can't switch to another terminal

| | |
|--|--|
| Message | `{} runs on {} (pid {}); cowbell can't switch to another terminal` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
| Source | `cowbell.py` |

