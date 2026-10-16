# Cowbell acceptance pack

Twelve scenarios for the `cowbell` command in this repository. Each file is
one scenario: precondition, steps, the output to expect, a pass/fail box, and
notes. The sheet for a whole run is [`RESULTS-template.md`](RESULTS-template.md).

This pack was written against cowbell **0.3.1** (`__version__` in `cowbell.py`).
Expected lines were taken by running that code, or by reading it where a run
was not possible. A line marked **UNCLEAR** is a finding. Record it. Do not
pick an interpretation and call the scenario a pass.

Running this pack is a later sign-off. Writing it is not that sign-off.

## Before you start

```bash
cowbell --version
```

The first line must be `cowbell 0.3.1` and the exit code 0. Any other version
means these expected lines may have moved. Stop, and write the version you
saw in the sheet.

Compare text with colour off, except in scenario 09:

```bash
export NO_COLOR=1
```

Scenarios 03–08 and 10 also want a predictable picker. For those, run the
non-interactive checks with `COWBELL_PLAIN=1` as the steps say. Scenario 09
is a real terminal: leave `COWBELL_PLAIN` unset and do not set `TERM=dumb`.

Use a scratch catalog and roster so a run does not rewrite your own:

```bash
export COWBELL_CONFIG_DIR=/tmp/cowbell-uat-config
export COWBELL_STATE_DIR=/tmp/cowbell-uat-state
rm -rf "$COWBELL_CONFIG_DIR" "$COWBELL_STATE_DIR"
```

`COWBELL_CONFIG_DIR` is the catalog (`harnesses.toml`). `COWBELL_STATE_DIR`
is the roster (`roster.json`) and pins (`pins.json`). Unset, those are
`$XDG_CONFIG_HOME/cowbell` or `~/.config/cowbell`, and
`$XDG_STATE_HOME/cowbell` or `~/.local/state/cowbell`.

`cowbell --version` and `cowbell --help` do not create those directories.
Any other command creates the config directory and, on first use, copies
the shipped `harnesses.toml` into it. The state directory is created as
soon as the roster is touched, even when `roster.json` does not exist yet.

## Order

| File | Run when |
| --- | --- |
| [01-stranger-install.md](01-stranger-install.md) | A machine that has never had cowbell. Follow the README only. |
| [02-python-39.md](02-python-39.md) | macOS system Python, and the repo launcher with no Python 3.11. |
| [03-empty-directory.md](03-empty-directory.md) | No agent CLIs, no roster, no history. |
| [04-one-agent.md](04-one-agent.md) | One installed harness. |
| [05-several-agents.md](05-several-agents.md) | Several installed, several running. |
| [06-new-flags.md](06-new-flags.md) | `new` flags, including a harness a place does not allow. |
| [07-status-catalog.md](07-status-catalog.md) | `status` and `catalog`, including trust. |
| [08-reconcile-dry-run.md](08-reconcile-dry-run.md) | `reconcile --dry-run` with and without herdr. |
| [09-keyboard-mouse.md](09-keyboard-mouse.md) | A real terminal, 80×24 and a wide one. |
| [10-no-herdr.md](10-no-herdr.md) | No `herdr` binary. |
| [11-unix-user.md](11-unix-user.md) | Not run here. Pointer only. |
| [12-uninstall.md](12-uninstall.md) | Last. `pipx uninstall` removes the command and leaves the XDG dirs. |

01 and 12 use the real install. 12 undoes 01, so run 12 last. 02 does not need
a successful install. 03–10 can use the installed `cowbell` or
`python3 cowbell.py` from a checkout, with the scratch directories above.

## How to record a result

1. Copy the template. Do not edit the template itself.

   ```bash
   cp docs/uat/RESULTS-template.md docs/uat/RESULTS-YYYY-MM-DD-<name>.md
   ```

   The sign-off run uses a name like `docs/uat/RESULTS-2026-10-patron.md`.

2. One row per scenario. Fill **Tester**, **Date**, **Pass/fail**, and **Notes**.
3. **Pass/fail** is `pass` or `fail`. A scenario with an **UNCLEAR** line is
   `fail` until that line is resolved, even if every other line matched.
4. In **Notes**, paste the first line that disagreed, the exit code, and any
   **UNCLEAR** sentence from the scenario.
5. Also tick the pass/fail box in the scenario file only in your copy of the
   results, not by rewriting the scenario.

Exit codes below are the process status (`echo $?` immediately after the
command). A `SystemExit` raised with a string is printed on stderr and the
process exits 1.
