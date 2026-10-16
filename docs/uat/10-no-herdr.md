# 10 · No herdr binary

The core runs standalone. LAB-497: pinpoint, identify, recall, and start do
not need a `herdr` binary. The herdr tab path stays in the code; it is not
taken on this run.

## Precondition

- No `herdr` on `PATH`, and `~/.local/bin/herdr` missing or not executable.
- `HERDR_BIN_PATH` unset. `HERDR_SOCKET_PATH` unset, or pointing at a socket
  that does not exist. (`server_up` returns false when `has_herdr()` is
  false, before it touches a socket. A socket with no binary still does not
  run `herdr`, because `has_herdr()` is false.)
- `COWBELL_MODE=here` or unset. Not inside a herdr pane (`HERDR_PANE_ID`
  unset).
- Scratch catalog from scenario 04 so `new` has something to start, or the
  shipped catalog if no agent CLI is installed (then `new` is not required
  to launch; `status` and the picker still must run).
- `NO_COLOR=1`, `COWBELL_PLAIN=1` for the text commands.

Optional proof the binary was not executed: a script named `herdr` that
appends its arguments to a log and exits 1, placed on `PATH`, with
`HERDR_SOCKET_PATH` pointing at a missing socket so `server_up` is false.
The log file must still be absent after the commands below. (If the stub is
on `PATH`, `has_herdr()` is true and cowbell will try the socket. A missing
socket means it never execs the stub. Do not point `HERDR_BIN_PATH` at the
stub for this proof; that forces the binary path.)

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
# only if the scenario 04 pi harness is installed:
cowbell new --harness pi --spawn --name solo
echo $?
```

If you planted the logging stub, `test ! -f "$LOG"`.

## Expected

Every command above exits **0**.

`cowbell --version` prints `cowbell 0.3.1`.

`status`, `catalog`, `list`, and the picker print the same text as scenarios
03, 04, or 07 for the catalog you used. They do not print `herdr unavailable`.

`reconcile --dry-run` prints:

```
panes agree with the harness Herdr detects
```

That sentence when herdr is absent is scenario 08. It is still exit 0 here.

`new --spawn` prints a `raised …` line and returns. It does not print a
herdr error. Outside a herdr pane, `choose_host` uses this terminal
(`HereLaunch`), which calls `exec_here` or `spawn_here` and does not call
`herdr()`.

The logging stub's log is not created.

Confirmed in the test suite (`NoHerdrCalls`: status, picker, enter, new, and
list with a failing `herdr` stub and a missing socket leave the log absent)
and by running `status`, `catalog`, `list`, the picker, and
`reconcile --dry-run` with no herdr binary for this pack. `new --spawn` of
the `pi` fixture likewise returned 0 without a herdr error.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

`herdr_bin()` falls back to `~/.local/bin/herdr` when `HERDR_BIN_PATH` is
unset and `which herdr` fails. `has_herdr()` only treats that path as present
when it is an executable file. A leftover non-executable file there does not
count. An executable there means this scenario's precondition is not met.

**UNCLEAR**, same as scenario 08: the agree line does not say that herdr was
missing. Pass this scenario on exit 0 and on the log staying empty, and note
LAB-636 in the sheet if you want that sentence changed.
