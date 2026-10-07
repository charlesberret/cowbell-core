# 07 · `status` and `catalog`

Live, cold, and absent. Trust badges. The "more reach than needed" warning
appears when the checker says so, and does not appear when it does not.

## Precondition

Same scratch layout as scenario 04 (one native `pi` on `PATH`, catalog id
`pi`, title `pi stand-in`), plus the ability to swap `trust_command`.
`NO_COLOR=1`, `COWBELL_PLAIN=1`, `COWBELL_MODE=here`.

Three checkers, selected by editing `trust_command` in the catalog and
putting that name on `PATH`:

```bash
# missing: trust_command names a program that is not on PATH (scenario 04)
# warn: exit 3
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

`subject` must print a single line. `trust_subject` uses the whole stripped
stdout as the header, so a second line breaks the `cowbell` header onto two
physical lines.

## Steps

With the checker **absent** (rename `harness-trust` off `PATH`):

```bash
cowbell status
cowbell catalog
printf 'q\n' | cowbell
```

With the checker **warning** (the script above, `trust_command = "harness-trust"`):

```bash
cowbell catalog
printf 'q\n' | cowbell
cowbell status
cowbell new --harness pi --spawn --yes --name warned
echo $?
```

With the checker **blocking** — same script, but `exit 4`, badge `T4`, and
`verdict: blocked (H2)` / `flag: H2`:

```bash
printf 'q\n' | cowbell
cowbell new --harness pi --spawn --yes --name blocked
echo $?
cowbell catalog
```

Also, with no checker, a cold roster row and a live process, so all three
status sections exist at once. Reuse scenario 05's `status` output for the
shape of `LIVE HERE` and `COLD HERE`, or start one `pi` sleeper on a tty in
this directory and keep one roster row with a `session_id` whose process has
exited.

## Expected

### No checker

`status` sections:

- Nothing running and no resumable row: `nothing raised here yet`, then
  `ABSENT HERE`. The `pi` cell is `pi ↑?` with no `(not installed)` once
  `pi` is on `PATH`. Header `subject: ?`.
- A process on a tty whose cwd is here: `LIVE HERE`, status text `running`,
  pane `pid:<pid>`, and ` (not on roster)` when the roster has no row for
  that pane.
- A roster row with a non-empty `session_id` whose process is gone:
  `COLD HERE  resumable`, status `cold`, pane `—` (U+2014) when the row has
  no pane id.
- A harness that is neither live nor cold: `ABSENT HERE`.

`catalog` header, then the row. Badge `?`, installed `yes`:

```
harness          kind     egress  installed badge      title
pi               pi       ↑ vendor yes       ?          pi stand-in
```

The picker New Session row has the title `pi stand-in` and does **not**
contain `more reach than needed`.

Exit code **0** for `status`, `catalog`, and the picker (`q`).

### Warning (checker exit 3)

`catalog` badge is the checker's badge stdout, here `T3`:

```
pi               pi       ↑ vendor yes       T3         pi stand-in
```

Picker New Session row ends with the warning. The words are exact:

```
! more reach than needed
```

There are three spaces before `!`. The row still has a number and can be
opened. The warning does not refuse the launch.

`status` header is `subject: internal` (the one line from `subject`). The
absent cell uses the mark `!`, not the sentence:

```
pi ↑!
```

The legend on that section is:

```
ABSENT HERE  ⌂ local  ↑ vendor · ok  ! more reach  ⊘ blocked  ? unknown
```

`new --yes --spawn` still exits **0**. Stderr is one line (`<root>` is the
directory; for this fixture `/tmp/cowbell-uat-one/work` or whichever cwd you
used):

```
cowbell: ! pi has more reach than <root> needs (W1)
```

Stdout is still the `raised warned  pi …` line. Confirmed by running a
checker that exits 3: catalog badge `T3`, picker contained
`! more reach than needed`, stderr was that `cowbell: !` line, exit 0.

### Blocked (checker exit 4)

The picker does **not** show `pi` under New Session. Blocked harnesses are
left off (`verdict != "blocked"` is required to be in the start pool). If a
resumable row exists it is still under Resume. If nothing else is installed,
the body is Resume only, or the empty sentence from scenario 03 when Resume
is empty too.

`new` does not start. Stderr, exit code **1**:

```
cowbell: refused — pi on <root>: blocked H2 (T4 under-clearance)
```

`catalog` still lists it. Badge is the checker's badge text (`T4` with the
script above). `status` does not use the sentence `more reach than needed`
for a block.

The warning sentence is absent when the checker is missing (marks are `?`)
and when the checker blocks (the row is omitted, `new` refuses). It is
present only for over-privilege (exit 3, or a stdout `verdict: overprivilege`).

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

Badge text is whatever `harness-trust badge <tool>` prints, stripped, or `?`
if that prints nothing or the program is not on `PATH`. `T3` / `T4` above are
the fixture, not a built-in cowbell badge. On a machine with a real
`harness-trust`, compare against that program's `badge` and `match` output;
the cowbell sentences (`! more reach than needed`, the `cowbell: !` stderr
line, the `cowbell: refused —` line) stay as written.

`status` calls a live row's status whatever the process scan stored. Outside
herdr that word is `running`. Herdr panes use herdr's own status word
(`idle`, `working`, and so on). Do not require `idle` from the README sketch
unless the row came from herdr.
