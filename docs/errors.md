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

### cowbell font [status|install]

| | |
|--|--|
| Message | `cowbell font [status|install]` |
| Cause | Cowbell rejected the command with the message shown. |
| Fix | Read the message, fix arguments or environment, and consult `cowbell catalog` / `cowbell sessions`. |
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

### cannot discover sessions as unix user {!r} (agent-run is not on PATH;...

| | |
|--|--|
| Message | `cowbell: cannot discover sessions as unix user {!r} (agent-run is not on PATH; cowbell does not fall back to sudo -u)` |
| Cause | Discovering another account's sessions needs `agent-run`, which is not on PATH. |
| Fix | Install `agent-run` and put it on PATH; cowbell does not use `sudo -u`. |
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

### catalog is schema {}; cowbell {} checks up to schema {} (upgrade cowbell)

| | |
|--|--|
| Message | `catalog is schema {}; cowbell {} checks up to schema {} (upgrade cowbell)` |
| Cause | The catalog's `schema` is more than one revision ahead of this cowbell, so `cowbell catalog --check` cannot vouch for it. |
| Fix | Upgrade cowbell. Editing the file does not help. |
| Source | `cowbell.py` |

### catalog is schema {}; this cowbell writes schema {} (newer file: read, never rewritten)

| | |
|--|--|
| Message | `catalog is schema {}; this cowbell writes schema {} (newer file: read, never rewritten)` |
| Cause | The catalog is one schema revision newer than this cowbell. It is read, never rewritten; this is a warning, not a failure. |
| Fix | Nothing to edit. Upgrade cowbell before you add or change a harness, since writes are refused until then. |
| Source | `cowbell.py` |

### catalog schema {} must be a positive int

| | |
|--|--|
| Message | `catalog schema {} must be a positive int` |
| Cause | The harness catalog fails `cowbell catalog --check` validation. |
| Fix | Edit `harnesses.toml` to satisfy the constraint named in the message. |
| Source | `cowbell.py` |

### check failed ({} {})

| | |
|--|--|
| Message | `cowbell: check failed ({} {})` |
| Cause | `cowbell catalog --check` printed one or more `FAIL` lines on stdout. |
| Fix | Read the `FAIL` lines above this one and fix each in `harnesses.toml`. |
| Source | `cowbell.py` |

### checking {} (no pass in the last 7 days)

| | |
|--|--|
| Message | `cowbell: checking {} (no pass in the last 7 days)` |
| Cause | The harness row's `check` has no recorded pass in the last 7 days, so it runs now before the launch. |
| Fix | No action needed when the check passes; when it fails the launch is refused with `cowbell: refused — {} failed its check`. |
| Source | `cowbell.py` |

### could not download {}: {}

| | |
|--|--|
| Message | `cowbell: could not download {}: {}` |
| Cause | `cowbell font install` could not fetch the pinned icon font. |
| Fix | Check connectivity and retry `cowbell font install`; the URL and sha256 are pinned in source. |
| Source | `cowbell.py` |

### could not show {} in the Herdr app: {}

| | |
|--|--|
| Message | `cowbell: could not show {} in the Herdr app: {}` |
| Cause | `cowbell enter` found the sitting running in a Herdr desktop app terminal, but `herdr-app do agent.focus` failed (the window is closed, or the app is older than that command). |
| Fix | Open the Herdr app and retry, or switch to the terminal named in the message by hand. |
| Source | `cowbell.py` |

### could not tighten {} to 0700: {}

| | |
|--|--|
| Message | `cowbell: could not tighten {} to 0700: {}` |
| Cause | The config or state dir exists with looser permissions and cowbell could not chmod it to owner-only (commonly a `COWBELL_CONFIG_DIR`/`COWBELL_STATE_DIR` naming a directory you do not own). Warning only; the command continues. |
| Fix | Point the env var at a directory you own, or tighten it yourself with `chmod 700`. |
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

### harness wall = {!r}: the only value is "door" (the command raises i...

| | |
|--|--|
| Message | `cowbell: harness wall = {!r}: the only value is "door" (the command raises its own wall)` |
| Cause | The harness sets a `wall` value other than `door`. |
| Fix | Use `wall = "door"` (the command raises its own wall) or remove `wall`. |
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
| Cause | The launch uses a `nono_profile`, but the `nono` executable is not on PATH. |
| Fix | Install `nono` and ensure it is on PATH in the environment running cowbell. |
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

### refused {}: sha256 {}, expected {}

| | |
|--|--|
| Message | `cowbell: refused {}: sha256 {}, expected {}` |
| Cause | The downloaded icon font's sha256 does not match the value pinned in source, so it was not installed. |
| Fix | Do not trust the fetched file; retry `cowbell font install`, and update the pinned hash only deliberately. |
| Source | `cowbell.py` |

### refused — a control character in a command word: {!r}

| | |
|--|--|
| Message | `cowbell: refused — a control character in a command word: {!r}` |
| Cause | A launch argument contains a control byte a shell line editor would act on before quoting applies. |
| Fix | Remove the control byte — or rename the file, folder, or name carrying it — and launch again. |
| Source | `cowbell.py` |

### refused — a control character in the launch line or its folder

| | |
|--|--|
| Message | `cowbell: refused — a control character in the launch line or its folder` |
| Cause | A launch argument contains a control byte a shell line editor would act on before quoting applies. |
| Fix | Remove the control byte — or rename the file, folder, or name carrying it — and launch again. |
| Source | `cowbell.py` |

### refused — dropping to unix user {!r} needs agent-run on PATH (cowbel...

| | |
|--|--|
| Message | `cowbell: refused — dropping to unix user {!r} needs agent-run on PATH (cowbell does not fall back to sudo -u, which would skip agent-run's checks)` |
| Cause | Dropping to another account for the launch needs `agent-run`, which is not on PATH. |
| Fix | Install `agent-run` and put it on PATH; cowbell does not use `sudo -u`. |
| Source | `cowbell.py` |

### refused — no unix_user for {}; set [places.*] unix_user or use agent-...

| | |
|--|--|
| Message | `cowbell: refused — no unix_user for {}; set [places.*] unix_user or use agent-run <uid> -- …` |
| Cause | The configured Unix account or privilege helper is missing or wrong. |
| Fix | Set a valid `unix_user`, install `agent-run`, or fix the account name on this host. |
| Source | `cowbell.py` |

### refused — nono_profile {} {}

| | |
|--|--|
| Message | `cowbell: refused — nono_profile {} {}` |
| Cause | The named `nono_profile` cannot be trusted as a wall: it is not absolute, not a regular file, not owned by root, or is writable by group or other. |
| Fix | Point `nono_profile` at an absolute, root-owned file nobody else can write. |
| Source | `cowbell.py` |

### refused — session id {!r} reads as an option

| | |
|--|--|
| Message | `cowbell: refused — session id {!r} reads as an option` |
| Cause | A resume id starting with `-` would be parsed as a flag by the agent CLI, and `--` cannot guard every shape. |
| Fix | Resume a different session from `cowbell sessions`, or rename the session so its id starts with a letter or digit. |
| Source | `cowbell.py` |

### refused — the home of {!r} is not a directory it owns

| | |
|--|--|
| Message | `cowbell: refused — the home of {!r} is not a directory it owns` |
| Cause | The account's home cannot be trusted: it is not an absolute path, resolves to `/`, is not a directory, or is owned by another account. |
| Fix | Repair the account's configured home path and ownership, or choose an account whose home is valid. |
| Source | `cowbell.py` |

### refused — the launch folder moved under it ({})

| | |
|--|--|
| Message | `cowbell: refused — the launch folder moved under it ({})` |
| Cause | The launch directory resolved somewhere else between the checks and the chdir — a symlink or mount moved under it. |
| Fix | Launch from a stable, symlink-free path. |
| Source | `cowbell.py` |

### refused — wall = "door" on a {}; it belongs on the harness that rai...

| | |
|--|--|
| Message | `cowbell: refused — wall = "door" on a {}; it belongs on the harness that raises its own wall, with that harness's unix_user` |
| Cause | `wall = "door"` is set on a place or `[defaults]` — levels that cannot raise a wall. |
| Fix | Move `wall = "door"` onto the harness whose command raises the wall, beside that harness's `unix_user`. |
| Source | `cowbell.py` |

### refused — {} failed its check: {}

| | |
|--|--|
| Message | `cowbell: refused — {} failed its check: {}` |
| Cause | The harness row's `check` argv exited non-zero; the detail is the check's last output line. A `check` that is not one argv (a bare string, an empty list, or a list holding non-strings) is refused here too, with the detail `check must be one argv, a list of strings`, the rule `cowbell catalog --check` reports. |
| Fix | Fix what the check verifies, or adjust `check` in `harnesses.toml` (a list of strings, for example `["model-server", "accept"]`); a pass is recorded for 7 days. |
| Source | `cowbell.py` |

### refused — {} names a wall but no unix_user of its own; the level tha...

| | |
|--|--|
| Message | `cowbell: refused — {} names a wall but no unix_user of its own; the level that names the account names the wall` |
| Cause | The harness sets `nono_profile` or `wall` without a `unix_user` of its own. |
| Fix | Set `unix_user` on the same harness row, or remove its wall fields. |
| Source | `cowbell.py` |

### refused — {} on {}: blocked {} (T4 under-clearance)

| | |
|--|--|
| Message | `cowbell: refused — {} on {}: blocked {} (T4 under-clearance)` |
| Cause | Trust clearance blocked launching the harness in this directory. |
| Fix | Use a lower-privilege lane, a different directory, or adjust trust/policy for this tree. |
| Source | `cowbell.py` |

### refused — {}: requires must be a list of argvs (lists of strings)

| | |
|--|--|
| Message | `cowbell: refused — {}: requires must be a list of argvs (lists of strings)` |
| Cause | The harness's `requires` is not a list of argvs: a bare string (as the whole value or as an entry), an empty entry, or an entry holding non-strings. It is checked whole, so no entry runs. `cowbell catalog --check` reports the same rule as `harness {}: requires must be a list of argvs (lists of strings)`. |
| Fix | Make `requires` a list of argvs, each a list of strings: `requires = [["model-server", "status"]]`. |
| Source | `cowbell.py` |

### refused — {} requires {!r}, which exited {}

| | |
|--|--|
| Message | `cowbell: refused — {} requires {!r}, which exited {}` |
| Cause | A `requires` argv on the harness exited non-zero, so the launch was refused before it began. |
| Fix | Make the named command succeed, or remove it from `requires` in `harnesses.toml`. |
| Source | `cowbell.py` |

### refused — {} requires {!r}, which timed out after {}s

| | |
|--|--|
| Message | `cowbell: refused — {} requires {!r}, which timed out after {}s` |
| Cause | A `requires` argv on the harness did not finish inside its bound, so the launch was refused rather than hang the picker. |
| Fix | Make the named command finish faster, or remove it from `requires` in `harnesses.toml`. |
| Source | `cowbell.py` |

### refused — {} requires {!r}: {}

| | |
|--|--|
| Message | `cowbell: refused — {} requires {!r}: {}` |
| Cause | A `requires` argv on the harness could not start at all; the trailing text is the OS error (usually a missing binary). |
| Fix | Install the named command, or remove it from `requires` in `harnesses.toml`. |
| Source | `cowbell.py` |

### refused — {} resolved to {} after the change of directory

| | |
|--|--|
| Message | `cowbell: refused — {} resolved to {} after the change of directory` |
| Cause | The launch directory resolved somewhere else between the checks and the chdir — a symlink or mount moved under it. |
| Fix | Launch from a stable, symlink-free path. |
| Source | `cowbell.py` |

### refused — {} runs as {!r} with no wall; set nono_profile beside tha...

| | |
|--|--|
| Message | `cowbell: refused — {} runs as {!r} with no wall; set nono_profile beside that unix_user, or wall = "door" on a harness whose command raises its own` |
| Cause | A drop to another account was requested with no wall around it; cowbell fails closed. |
| Fix | Set `nono_profile` beside that `unix_user`, or `wall = "door"` on a harness whose command raises its own wall. |
| Source | `cowbell.py` |

### refused — {} starts in {}, which this user cannot enter; this user ...

| | |
|--|--|
| Message | `cowbell: refused — {} starts in {}, which this user cannot enter; this user needs traverse (search) on it` |
| Cause | The invoking user lacks traverse (search) permission on the harness's launch folder. |
| Fix | Grant execute on the folder and its parents for this user, or choose a folder it can enter. |
| Source | `cowbell.py` |

### refused — {}: cwd {!r} must be an absolute path with no symlink in it

| | |
|--|--|
| Message | `cowbell: refused — {}: cwd {!r} must be an absolute path with no symlink in it` |
| Cause | A harness `cwd` is not an absolute, symlink-free path. |
| Fix | Set `cwd` to a real absolute path with no symlink component. |
| Source | `cowbell.py` |

### refused — {}: cwd {} is not under {} home nor inside a place that a...

| | |
|--|--|
| Message | `cowbell: refused — {}: cwd {} is not under {} home nor inside a place that account owns` |
| Cause | A harness `cwd` lies outside the home — and outside any place — of the account it runs as. |
| Fix | Move `cwd` under that account's home or inside a place the account owns. |
| Source | `cowbell.py` |

### refused — {}: nono_proxy_port needs a nono_profile beside it

| | |
|--|--|
| Message | `cowbell: refused — {}: nono_proxy_port needs a nono_profile beside it` |
| Cause | `nono_proxy_port` is set with no `nono_profile` on the same level. |
| Fix | Add a `nono_profile`, or remove `nono_proxy_port`. |
| Source | `cowbell.py` |

### refused — {}: nono_proxy_port {!r} must be a port number 1024-65535

| | |
|--|--|
| Message | `cowbell: refused — {}: nono_proxy_port {!r} must be a port number 1024-65535` |
| Cause | `nono_proxy_port` is not an integer TCP port in 1024–65535. |
| Fix | Set an integer port in that range, or remove the field. |
| Source | `cowbell.py` |

### refused — {}: the home of {} is not a directory it owns

| | |
|--|--|
| Message | `cowbell: refused — {}: the home of {} is not a directory it owns` |
| Cause | The account's home cannot be trusted: it is not an absolute path, resolves to `/`, is not a directory, or is owned by another account. |
| Fix | Repair the account's configured home path and ownership, or choose an account whose home is valid. |
| Source | `cowbell.py` |

### refused — {}: wall = "door" and a nono_profile in the same launch; ...

| | |
|--|--|
| Message | `cowbell: refused — {}: wall = "door" and a nono_profile in the same launch; pick one` |
| Cause | The launch names both `wall = "door"` and a `nono_profile`; only one wall may apply. |
| Fix | Keep either `wall = "door"` or the `nono_profile`, not both. |
| Source | `cowbell.py` |

### refused — {}: {}

| | |
|--|--|
| Message | `cowbell: refused — {}: {}` |
| Cause | A door harness's command — or a directory above it — cannot be trusted to raise the wall: the detail names why. |
| Fix | Install the door command root-owned under root-owned, non-group/other-writable directories, exactly as the reason states. |
| Source | `cowbell.py` |

### session discovery as {!r} returned a folder it does not own

| | |
|--|--|
| Message | `cowbell: session discovery as {!r} returned a folder it does not own` |
| Cause | Resume, rename, or history lookup could not resolve the session. |
| Fix | Pick a name from `cowbell sessions`, refresh history, or pass an unambiguous id. |
| Source | `cowbell.py` |

### session discovery as {!r} returned a malformed session id

| | |
|--|--|
| Message | `cowbell: session discovery as {!r} returned a malformed session id` |
| Cause | Resume, rename, or history lookup could not resolve the session. |
| Fix | Pick a name from `cowbell sessions`, refresh history, or pass an unambiguous id. |
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
| Fix | Set a valid `unix_user`, install `agent-run`, or fix the account name on this host. |
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

### {}: empty catalog

| | |
|--|--|
| Message | `cowbell: {}: empty catalog` |
| Cause | The catalog file parses to no keys at all — truncated to zero bytes, or left comments-only. |
| Fix | Restore the rows from the seed `harnesses.toml` that ships with cowbell, or delete the file and cowbell copies the seed in on next run. |
| Source | `cowbell.py` |

### {}: {}

| | |
|--|--|
| Message | `cowbell: {}: {}` |
| Cause | A state or catalog file could not be opened or parsed; the first slot names the file, the second the OS or format error (for example `not a regular file` on a fifo or device, `Permission denied`, `not valid UTF-8`). |
| Fix | Replace the named file with a regular file cowbell can read, or remove it and let cowbell recreate it. |
| Source | `cowbell.py` |

### {}: schema must be an int

| | |
|--|--|
| Message | `cowbell: {}: schema must be an int` |
| Cause | The named file's `schema` is not an integer (for example `schema = "two"` or `schema = true` in a catalog, or a string in `roster.json`/`pins.json`). |
| Fix | Set `schema` to an integer — this cowbell writes `schema = 1` — or remove the file and let cowbell recreate it. |
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

### harness {}: check must be one argv, a list of strings

| | |
|--|--|
| Message | `harness {}: check must be one argv, a list of strings` |
| Cause | The row's `check` is not a non-empty list of strings. A bare string is refused, not wrapped into one argv; at launch the same rule refuses the row (see `failed its check`). |
| Fix | Write `check = ["model-server", "accept"]`, not `check = "model-server accept"`. |
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

### harness {}: requires must be a list of argvs (lists of strings)

| | |
|--|--|
| Message | `harness {}: requires must be a list of argvs (lists of strings)` |
| Cause | The row's `requires` is not a list of non-empty lists of strings. A bare string, as the whole value or as an entry, is refused, not wrapped into one argv; at launch the same rule refuses the row (see `requires must be a list of argvs`). |
| Fix | Write `requires = [["model-server", "status"]]`, not `requires = "model-server status"` or `requires = ["model-server"]`. |
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

### herdr {} skipped: marked down after a timeout

| | |
|--|--|
| Message | `herdr {} skipped: marked down after a timeout` |
| Cause | A herdr call timed out, so cowbell skips further calls for about 30 seconds instead of waiting on each one. |
| Fix | Restart or unstick the herdr server; cowbell resumes calling it after the short window. |
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

### this terminal is not in a Herdr app space (no herdr.space label); set COWBELL_HC_SPACE to the space a new tab should open in

| | |
|--|--|
| Message | `cowbell: this terminal is not in a Herdr app space (no herdr.space label); set COWBELL_HC_SPACE to the space a new tab should open in` |
| Cause | A launch that opens a Herdr app tab ran in a herdr-core terminal the app does not show (started with `hc run` and no `herdr.space` label), so cowbell has no space to put the tab in. Nothing was started. |
| Fix | Set `COWBELL_HC_SPACE` to a local space id (`herdr-app ls` lists them), or run cowbell from a terminal inside the app. |
| Source | `cowbell.py` |
