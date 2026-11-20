# Cowbell acceptance pack

Twelve scenarios for the `cowbell` command. Each file has a precondition,
the steps, the output to expect, a pass/fail box, and notes. The sheet for a
whole run is [`RESULTS-template.md`](RESULTS-template.md).

Written against cowbell **0.3.2** (`__version__` in `cowbell.py` on this
tree). An expected line was printed by that code, or it is quoted from the
source where a run was not possible. A line marked **UNCLEAR** is a finding.
Record it. Do not choose an interpretation and mark the scenario pass.

This file is the pack. Running it is a later sign-off.

## Before you start

```bash
cowbell --version
```

The line must be `cowbell 0.3.2` and the exit code 0. Any other version means
these lines may have moved. Stop, and write the version in the sheet.

For the text scenarios, turn colour off:

```bash
export NO_COLOR=1
```

Scenarios 03–08 and 10 also set `COWBELL_PLAIN=1` where the steps say so.
Scenario 09 is a real terminal: leave `COWBELL_PLAIN` unset and do not set
`TERM=dumb`.

With no arguments, `main` runs `status` when `tui_ok()` is false: stdin is
not a terminal (a pipe), or `COWBELL_PLAIN=1` is set. The text picker in
these scenarios is `cowbell picker`.

Use a scratch catalog and roster:

```bash
export COWBELL_CONFIG_DIR=/tmp/cowbell-uat-config
export COWBELL_STATE_DIR=/tmp/cowbell-uat-state
rm -rf "$COWBELL_CONFIG_DIR" "$COWBELL_STATE_DIR"
```

Unset, those are `$XDG_CONFIG_HOME/cowbell` or `~/.config/cowbell`, and
`$XDG_STATE_HOME/cowbell` or `~/.local/state/cowbell`.

`cowbell --version` and `cowbell --help` do not create those directories.
On Python 3.11 or newer, a command that loads the catalog creates the config
directory and, the first time, copies the shipped `harnesses.toml` into it.
On Python 3.9 that copy does not happen: `cowbell.py status` prints
`cowbell: python >= 3.11 required (tomllib)` on stderr, exits 1, and leaves
no config directory (scenario 02). The state directory is created when the
roster is touched on a Python that gets that far, even if `roster.json` does
not exist yet.

## Order

| File | What it covers |
| --- | --- |
| [01-stranger-install.md](01-stranger-install.md) | Follow the README install. Reach `cowbell --version`. |
| [02-python-39.md](02-python-39.md) | macOS system Python, and the launcher with no Python 3.11. |
| [03-empty-directory.md](03-empty-directory.md) | No agents, no roster, no history. How to leave. |
| [04-one-agent.md](04-one-agent.md) | Catalog, `new`, `list`, `enter`. |
| [05-several-agents.md](05-several-agents.md) | Active census, Resume, New Session. |
| [06-new-flags.md](06-new-flags.md) | `new` flags, and a harness a place refuses. |
| [07-status-catalog.md](07-status-catalog.md) | Live, cold, absent, trust badges, the reach warning. |
| [08-reconcile-dry-run.md](08-reconcile-dry-run.md) | `reconcile --dry-run` with and without herdr. |
| [09-keyboard-mouse.md](09-keyboard-mouse.md) | Keys, `g`, quit, mouse, 80×24 and wide. |
| [10-no-herdr.md](10-no-herdr.md) | Core commands with no `herdr` binary. |
| [11-unix-user.md](11-unix-user.md) | Not run here. Pointer to the privilege pack. |
| [12-uninstall.md](12-uninstall.md) | `pipx uninstall cowbell`, and what remains. |

01 and 12 use a real install. 12 removes it, so run 12 last. 02 does not need
that install. 03–10 can use `./bin/cowbell` from a checkout.

## How to record a result

1. Copy the template. Do not edit the template.

   ```bash
   cp docs/uat/RESULTS-template.md docs/uat/RESULTS-YYYY-MM-DD-<name>.md
   ```

2. One row per scenario. Fill tester, date, pass/fail, and notes.
3. Pass/fail is `pass` or `fail`. A scenario with an **UNCLEAR** line is
   `fail` until that line is resolved.
4. In notes, paste the first line that disagreed, the exit code, and any
   **UNCLEAR** sentence.

A `SystemExit` raised with a string is printed on stderr and the process
exits 1.
