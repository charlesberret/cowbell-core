# 09 · Keyboard and mouse

Navigation, `g`, quit, mouse when the terminal sends it, 80×24, and a wide
terminal.

## Precondition

A real terminal. `TERM` is not `dumb`. `COWBELL_PLAIN` is unset. Colour may
be on; compare the words.

Use a catalog with one installed harness whose command prints `launched` and
exits, and put the directory inside a git work tree that is not the
directory itself (`git init` in the parent is enough). No agent has to be
running for `g` to change the directory. The `g widen` hint is drawn only
when widening would show more running agents (`can_widen`, and not when the
cursor is on a New Session row).

Sizes: 80×24, then at least 100×24. `stty rows 24 cols 80`, then
`stty rows 24 cols 100`.

## Steps

1. `stty rows 24 cols 80`, then `cowbell`, with only a New Session row
   (empty roster).
2. Press Down, Up, `j`, `k`.
3. Press Enter.
4. `cowbell` again. Press `q`.
5. `cowbell` again. Press Esc.
6. `cowbell` again. Press `1`.
7. `cowbell` again. Press `g`. Look at the path. Press `q`.
8. After a Resume row exists, open `cowbell` again and read the hint bar
   without moving.
9. If the terminal sends mouse events, scroll the wheel once, then click the
   `esc` hint. If clicks do nothing, write "mouse not reported" and quit
   with `q`.
10. `stty rows 24 cols 100` (or wider). Open `cowbell` once. Quit with `q`.

## Expected

Opening the picker sends the alternate screen and SGR mouse:
`\x1b[?1049h` and `\x1b[?1006h` (and `\x1b[?1000h`). Confirmed by reading
the bytes from an 80×24 pty: both were present.

### Hint bar follows the row

One New Session row, nothing to resume, widen not offered. Captured at
80×24 with `NO_COLOR=1`:

```
  ⏎   n new   + add   a adopt   o shape   e edit   p pin   h hide   - rm   esc
```

`⏎` has no word. `esc` has no word. `g` is not on the bar.

After a Resume row exists, the cursor starts on it. Captured bar:

```
  ⏎ open   n new   + add   a adopt   o shape   r rename   esc close
```

`o shape` and `r rename` are the resume actions. `e edit`, `p pin`, `h hide`,
and `- rm` are the New Session actions. They are not both on the bar at once.
`picker_hints` adds `g widen` only when `can_widen` is true and the cursor
is not on a New Session row.

### Keys

| Key | Result |
| --- | --- |
| Down, Up, `j`, `k` | Move among numbered rows. One row stays selected. |
| Enter, or `1` when it is the only numbered row | Starts that row. The handoff line is printed, then `launched`. Exit code **0** for the script in scenario 04. |
| `q` | Leaves. Exit code **0**. Does not start the agent. |
| Esc, and Ctrl-C | Same as `q`. Ctrl-C is parsed as `esc`. |
| `g` | Sets the directory to the git root when there is one (`picker` on raw `g`). The hint does not have to be on the bar. Then `q` still exits 0. |

`g` with no git root leaves the directory as it is (`root = top or root`).
That branch was read from `picker`, not redrawn in this capture.

### Mouse

When the terminal delivers SGR 1006: wheel 65 moves down, 64 moves up; a
left press (code 0, the press) on a row selects it; a press on a hint runs
that hint; a release alone does nothing. This is `menu`'s mouse branch. A
terminal that never sends those bytes still quits with `q`. Record which
one you had.

### 80×24 and wide

The words stay: path, `New Session` or `Resume`, the numbered rows, the hint
bar. The selected row is padded to the terminal width, so a wide screen has
more trailing spaces. The section titles do not wrap for this one-row
fixture. The list redraws every 2 seconds while the picker is open.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

The two hint bars above were copied from pty captures of cowbell 0.3.2
(`NO_COLOR=1`, 80×24). The mouse event table was read from `menu`. The
plain-mode footer (`number = open …`) is scenario 03, not this one.
