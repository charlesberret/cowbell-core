# 03 · Empty directory

`cowbell` where no agent is running, the roster is empty, and no harness
from the shipped catalog is installed. What the picker shows, and how to
leave it.

## Precondition

- `NO_COLOR=1`.
- `command -v harness-trust` fails. The shipped catalog sets
  `trust_command = "harness-trust"`. If that program is on `PATH`, `subject:`
  and the `?` marks change. Use a `PATH` that does not contain it.
- None of these are on `PATH`: `claude`, `codex`, `grok`, `gemini`, `agy`,
  `opencode`, `pi`, `omp`, `devin`, `droid`. Those are the `kind`s in the
  shipped `harnesses.toml`. One of them installed makes this scenario 04
  or 05.
- Scratch config and state, so the roster is empty and the first command
  copies the shipped catalog.
- `session_history` stays `"off"`.
- The directory is not a git work tree, or its git root has no agent
  process under it. Otherwise a widen hint is added (scenario 09).

## Steps

```bash
export COWBELL_PLAIN=1
printf 'q\n' | cowbell
echo $?
cowbell status
echo $?
cowbell list
echo $?
cowbell list --all
echo $?
```

Then a real terminal (`COWBELL_PLAIN` unset, `TERM` not `dumb`):

```bash
unset COWBELL_PLAIN
cowbell
```

Press Enter. Then `q`. Run it again and press Esc.

## Expected

### Text picker

Stdout, `<cwd>` replaced by the directory (`~` if it is under your home).
Stderr empty. Exit code **0** for `q` and for an empty Enter (both return
from the plain prompt). Confirmed with a seeded catalog and no matching
binary on `PATH`:

```
  <cwd>

  nothing to start here: no agents from harnesses.toml are installed

  number = open   [n] new   [+] add   [q]
  > 
```

No `Active` box, no `Resume`, no `New Session`. The footer is that one
line: two spaces of indent, three spaces between items.

### `status`

Exit code **0**. For the shipped seed, every character other than `<cwd>`
is exact. The absent list wraps at 100 columns in `render_registry`, so
these line breaks do not follow the terminal width:

```
  cowbell  <cwd>   subject: ?

  nothing raised here yet

  ABSENT HERE  ⌂ local  ↑ vendor · ok  ! more reach  ⊘ blocked  ? unknown
  claude ↑? (not installed) · codex ↑? (not installed) · grok ↑? (not installed)
  gemini ↑? (not installed) · agy ↑? (not installed) · opencode ↑? (not installed)
  pi ↑? (not installed) · omp ↑? (not installed) · devin ↑? (not installed)
  droid ↑? (not installed)
```

No `LIVE HERE` and no `COLD HERE`. `subject: ?` is `trust_subject` when
`harness-trust` is not on `PATH`.

### `list`

Exit code **0**. Two spaces before `(try --all)`:

```
no roster entries under <cwd>  (try --all)
```

`cowbell list --all` prints `no roster entries` and exits **0**.

### Terminal picker

The same two body lines. With no numbered row the hint bar is the empty
case of `picker_hints` (no start row, no resume row, widen false):

```
  ⏎ open   n new   + add   a adopt   esc close
```

That bar was not redrawn in the empty-terminal capture for this pack. It is
the string `picker_hints(False, False)` builds: `⏎` plus `open`, then `n new`,
`+ add`, `a adopt`, `esc close`, joined by three spaces, with two spaces of
indent. **UNCLEAR: the empty terminal's drawn bar.** The capture that was
run had one New Session row (a harness whose `command` existed). That bar is
scenario 09. If the empty terminal's bar differs from the line above, paste
it. Do not treat scenario 09's bar as this one.

Enter does not leave an empty menu (`menu` ignores Enter when there are no
rows). `q` and Esc cancel and the picker returns 0. Confirmed for a menu
with rows in scenario 09's setup; the empty menu uses the same `cancel`
path. If Enter quits the empty picker, that is a fail: paste what happened.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

`nothing to start here: no agents from harnesses.toml are installed` is
`render_picker` when there are no choices. `nothing raised here yet` is
`render_registry` when nothing is live and nothing cold has a session id.
Both were printed by cowbell 0.3.2 under `NO_COLOR=1`.
