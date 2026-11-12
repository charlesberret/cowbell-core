# 07 · `status` and `catalog`

Live, cold, and absent. Trust badges. `! more reach than needed` appears
when the checker says the harness is over-privileged, and does not appear
otherwise.

## Precondition

Scenario 04's one native `pi`, plus a checker you can put on `PATH` and take
off it. `NO_COLOR=1`, `COWBELL_PLAIN=1`, `COWBELL_MODE=here`.

```bash
cat > "$ROOT/bin/harness-trust" << 'EOF'
#!/bin/sh
if [ "$1" = badge ]; then echo T3; exit 0; fi
if [ "$1" = subject ]; then echo internal; exit 0; fi
echo "verdict: overprivilege (W1)"
echo "flag: W1"
exit 3
EOF
chmod +x "$ROOT/bin/harness-trust"
```

`subject` must print one line. `trust_subject` puts the whole stripped
stdout into the header.

Set `trust_command = "harness-trust"` in the catalog when the checker should
be used, and a name that is not on `PATH` when it should not.

## Steps

Checker absent:

```bash
cowbell status
cowbell catalog
printf 'q\n' | cowbell picker
```

Checker warning (the script above, exit 3):

```bash
cowbell catalog
printf 'q\n' | cowbell picker
cowbell new --harness pi --spawn --yes --name warned
echo $?
```

Checker blocking: same script, but `echo T4`, `verdict: blocked (H2)`,
`flag: H2`, `exit 4`:

```bash
printf 'q\n' | cowbell picker
cowbell new --harness pi --spawn --yes --name blocked
echo $?
cowbell catalog
```

## Expected

### No checker

`status` with nothing running and no resumable row: `nothing raised here yet`,
then `ABSENT HERE`. Once `pi` is on `PATH` the cell is `pi ↑?` with no
`(not installed)`. Header `subject: ?`.

A process on a tty whose cwd is here: `LIVE HERE`, status `running`, pane
`pid:<pid>`, and ` (not on roster)` when the roster has no row for that pane.

A roster row with a session id whose process is gone: `COLD HERE  resumable`,
status `cold`, pane `—` (U+2014) when the row has no pane id.

`catalog`:

```
harness          kind     egress  installed badge      title
pi               pi       ↑ vendor yes       ?          pi stand-in
```

The picker row does not contain `more reach than needed`.

`status`, `catalog`, and the picker (`q`) exit **0**.

### Warning (exit 3)

Badge is the checker's badge stdout:

```
pi               pi       ↑ vendor yes       T3         pi stand-in
```

The New Session row ends with `! more reach than needed` (three spaces
before `!`). The row stays numbered. The warning does not refuse the launch.

`new --yes --spawn` exits **0**. Stderr:

```
cowbell: ! pi has more reach than <root> needs (W1)
```

Stdout is still `raised warned  pi model-a yellow  in pid:<pid>  <root>`.
Confirmed with a checker that exits 3: badge `T3`, the picker contained
`! more reach than needed`, stderr was that line, exit 0.

`status`, when this harness is not already live or cold, shows the absent
mark `!` (`pi ↑!`), not the sentence. The section legend is:

```
ABSENT HERE  ⌂ local  ↑ vendor · ok  ! more reach  ⊘ blocked  ? unknown
```

The header subject is the one line from `harness-trust subject` (`internal`
for this script).

### Blocked (exit 4)

The picker does not list `pi` under New Session. A blocked harness is left
out of the start pool. If the warning run left a resumable `warned` row, the
picker shows Resume and no New Session. Confirmed after an exit-4 checker:
the body was Resume (`warned`, the ago word `today`) and no `pi stand-in` row.

`new` does not start. Stderr, exit code **1**:

```
cowbell: refused — pi on <root>: blocked H2 (T4 under-clearance)
```

`catalog` still lists the harness. The badge is `T4` with this script.

The sentence `more reach than needed` is absent when the checker is missing
(marks are `?`) and when the checker blocks (the row is omitted, `new`
refuses). It is present for over-privilege (exit 3, or stdout
`verdict: overprivilege`).

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

`T3` and `T4` are the fixture's badge text, not a cowbell constant. A real
`harness-trust` prints its own badge. The cowbell sentences stay as written:
`! more reach than needed`, the `cowbell: !` stderr line, and
`cowbell: refused —`.

Outside herdr, a live row's status word is `running`. Herdr's own status
words (`idle`, `working`, and the rest) show up only on herdr panes.
