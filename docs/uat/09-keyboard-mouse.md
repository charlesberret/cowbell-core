# 09 · Keyboard and mouse

Navigation keys, `g` to widen, quit, mouse when the terminal supports it,
an 80×24 terminal, and a wide one.

## Precondition

A real terminal. `TERM` is not `dumb`. `COWBELL_PLAIN` is unset. `NO_COLOR`
may be unset (colour is allowed; compare the words, not the RGB values).

Use scenario 04's one-harness catalog so New Session has a single row whose
command is a script that prints `launched` and exits. Put that directory
inside a git work tree:

```bash
# from scenario 04's ROOT=/tmp/cowbell-uat-one
# work tree root is /tmp/cowbell-uat-one, picker cwd is .../work
```

If `…/work` is not its own git root, `g` has somewhere to go. `git init` in
the parent of `work` is enough. No agent process has to be running for `g`
to change directory; the hint is shown only when widening would reveal more
running agents.

Second size: 80 columns by 24 rows, then at least 100 columns by 24 rows.
`stty rows 24 cols 80` and `stty rows 24 cols 100`, or the terminal's own
resize.

## Steps

1. `stty rows 24 cols 80`, then `cowbell`.
2. Press Down, then Up. Press `j`, then `k`.
3. Press Enter.
4. Run `cowbell` again. Press `q`.
5. Run `cowbell` again. Press Esc.
6. Run `cowbell` again. Press `1` (the only numbered row).
7. Run `cowbell` again. Press `g`, look at the path, press `q`.
8. If the terminal sends mouse events: scroll the wheel one notch, then
   click the `esc` hint. If clicks do nothing, record "mouse not reported"
   and quit with `q`. That is not a fail by itself.
9. `stty rows 24 cols 100` (or wider) and open `cowbell` once. Quit with `q`.

Do not set `COWBELL_PLAIN` during this scenario. The text footer
(`number = open …`) is the plain picker, scenario 03.

## Expected

Opening the picker enables the alternate screen and SGR mouse:
the stream contains `\x1b[?1049h` and `\x1b[?1006h` (and `\x1b[?1000h`).
Quit restores the terminal (`\x1b[?1049l`). Confirmed by reading the bytes
from an 80×24 pty and a 120×24 pty.

### Keys

With one New Session row, the hint bar is (two spaces indent, three spaces
between items). `esc` has no following word, because the cursor is on a
New Session row:

```
  ⏎ open   n new   + add   a adopt   e edit   p pin   h hide   - rm   esc
```

| Key | Result |
| --- | --- |
| Down, Up, `j`, `k` | Move among numbered rows. One row stays selected. |
| Enter | Starts that row. Stdout includes the handoff line and then `launched`. Exit code **0** (the script's status). |
| `1` | Same as Enter when there is a single numbered row (a digit picks immediately when `n * 10` is greater than the number of numbered rows). |
| `q` | Leaves the picker. Exit code **0**. Does not start the agent. |
| Esc | Same as `q`. Exit code **0**. |
| Ctrl-C | Same as Esc (`\x03` is parsed as `esc`). |

`g`: the path in the header changes from the cwd to its git root when those
differ (`/tmp/cowbell-uat-one/work` becomes `/tmp/cowbell-uat-one` if that is
the git root). Then `q` still exits 0. Confirmed: after `g` the drawn path
was the parent git root, and the process then exited 0 on `q`.

The `g widen` hint is not on the bar unless more agents are running under
the git root than in the cwd (`wider > len(live)`). With nothing running,
the bar has no `g`, and the key still widens. When scenario 05's three
processes are up, the header ends with `g widen to <basename> · 3 running`
and the bar includes `g widen` (plain mode) or `g` `widen` (this terminal
bar, inserted after `a adopt`).

### Mouse

When the terminal delivers SGR 1006 events: wheel code 65 moves down, 64
moves up; a left press (code 0, the press, not the release) on a row selects
it; a press on a hint runs that hint (`esc` cancels, `⏎` picks); a release
with no press does nothing. A terminal that never sends those bytes still
quits with `q`. Record which one you had.

### 80×24 and wide

The words are the same at 80×24 and at 100 (or 120) columns: the path, `New
Session`, the one numbered row, the hint bar. The selected row is padded out
to the terminal width, so the wide screen has more trailing spaces and the
narrow screen does not wrap the section title onto a second line for this
one-row fixture. Nothing is added or dropped between the two sizes. Confirmed
by opening the same picker at 80×24 and at 120×24.

The list redraws every 2 seconds while the picker is open (`REFRESH_S`).

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

Hint strings are `picker_hints` in `cowbell.py`. Quit is `menu` treating `q`
and `esc` as `("cancel",)`, and `picker` returning 0 on cancel. Mouse
tracking was observed as the setup bytes above; the wheel and click table is
`menu`'s mouse branch, which the unit tests in `tests/test_pty.py` also
drive. This scenario is the one a person confirms in a terminal those tests
do not replace.
