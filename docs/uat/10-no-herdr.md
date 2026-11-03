# 10 · No herdr binary

The core runs with no `herdr` binary. Status, the picker, list, catalog,
reconcile, and `new` do not need it.

## Precondition

- `command -v herdr` fails, and `~/.local/bin/herdr` is missing or not
  executable.
- `HERDR_BIN_PATH` unset.
- `COWBELL_MODE=here` or unset. `HERDR_PANE_ID` unset.
- Scratch catalog from scenario 04, or the shipped catalog if no agent CLI
  is installed. In the shipped case, skip the `new` step.
- `NO_COLOR=1`, `COWBELL_PLAIN=1` for the text commands.

Optional: a script named `herdr` that appends its arguments to a log and
exits 1, on `PATH`, with `HERDR_SOCKET_PATH` pointed at a missing socket.
`server_up` connects only when `has_herdr()` is true, and a missing socket
means it does not exec the script. The log file must still be absent after
the commands. Do not set `HERDR_BIN_PATH` to that script; that counts as a
binary, and reconcile then tries to run it.

## Steps

```bash
command -v herdr; echo $?
unset HERDR_BIN_PATH
cowbell --version
echo $?
cowbell status
echo $?
cowbell catalog
echo $?
cowbell list
echo $?
printf 'q\n' | cowbell
echo $?
cowbell reconcile --dry-run
echo $?
cowbell new --harness pi --spawn --name solo
echo $?
```

Run the `new` line only when the scenario 04 `pi` harness is installed.

## Expected

Every command exits **0**.

`cowbell --version` prints `cowbell 0.3.2`.

`status`, `catalog`, `list`, and the picker print the same text as scenarios
03, 04, or 07 for the catalog you used. They do not print
`herdr unavailable`.

`reconcile --dry-run` prints:

```
herdr is not installed; nothing to reconcile
```

`new --spawn` prints a `raised …` line and returns. Outside a herdr pane,
`choose_host` uses this terminal. `spawn_here` does not call `herdr()`.

The logging stub's log is not created.

Confirmed on this tree with no herdr binary: `status`, `catalog`, `list`,
the picker, and `reconcile --dry-run` exited 0, and reconcile printed the
not-installed line. `new --spawn` of the `pi` fixture returned 0 with a
`raised` line and no herdr error.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

`herdr_bin()` falls back to `~/.local/bin/herdr` when `HERDR_BIN_PATH` is
unset and `which herdr` fails. `has_herdr()` counts that path only when it
is an executable file. An executable there means this precondition is not met.
