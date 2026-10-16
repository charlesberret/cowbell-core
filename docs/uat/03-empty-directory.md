# 03 · Empty directory

`cowbell` in a directory with no agents running, no roster, and no harness
from the catalog installed. What the picker shows, and how to leave it.

## Precondition

- `NO_COLOR=1`.
- `command -v harness-trust` fails. The shipped catalog sets
  `trust_command = "harness-trust"`. If that program is on `PATH`, the
  `subject: ?` line and the `?` marks below change; stop and use a `PATH`
  that does not contain it.
- None of these are on `PATH`: `claude`, `codex`, `grok`, `gemini`, `agy`,
  `opencode`, `pi`. Those are the harness `kind`s in the shipped
  `harnesses.toml`. An installed one makes this scenario 04 or 05 instead.
- Scratch config and state (see the pack README), so the roster is empty and
  cowbell copies the shipped catalog on first use.
- `session_history` stays `"off"` (the seed default). No herdr server is
  required. `COWBELL_MODE` unset or `here`.
- A directory that is not inside a git work tree, or a directory whose git
  root has no agent processes under it. Otherwise a widen hint is added; that
  is scenario 09.

## Steps

From that directory, text picker first:

```bash
export COWBELL_PLAIN=1
cowbell
# at the "> " prompt, press Enter
echo $?
cowbell
# at the prompt, type q and press Enter
echo $?
printf 'q\n' | cowbell
echo $?
cowbell status
echo $?
cowbell list
echo $?
cowbell list --all
echo $?
```

Then a real terminal (unset `COWBELL_PLAIN`, `TERM` not `dumb`):

```bash
unset COWBELL_PLAIN
cowbell
```

Press Enter once. Then press `q`. Run it again and press Esc.

## Expected

### Text picker (`COWBELL_PLAIN=1`)

Stdout, with `<cwd>` the directory you started in (`~` if it is under your
home). Nothing on stderr. Confirmed by running the picker with a seeded
catalog and no matching binaries on `PATH`:

```
  <cwd>

  nothing to start here: no agents from harnesses.toml are installed

  number = open   [n] new   [+] add   [q]
  > 
```

There is no `Active` box, no `Resume`, and no `New Session` heading. The
footer is that one `number = open` line (two spaces of indent, three spaces
between items). The prompt is `  > `.

Empty Enter and `q` both leave. Exit code **0** either way.

### Terminal picker

The same two body lines (`<cwd>`, then `nothing to start here: no agents from harnesses.toml are installed`). The hint bar is:

```
  ⏎ open   n new   + add   a adopt   esc close
```

Enter does not leave: the same screen is drawn again. `q` leaves, exit code
**0**. Esc leaves, exit code **0**.

Confirmed in an 80×24 terminal: mouse reporting and the alternate screen were
turned on, Enter redrew the same text, and the hint bar was the line above.
`q` and Esc were confirmed to exit 0 on a one-row picker in scenario 09's
setup; the empty picker uses the same `cancel` path (`q` and Esc both return
`("cancel",)`).

### `status`

Exit code **0**. Stdout for the shipped seed, `<cwd>` substituted, every
other character exact (the absent list wraps at 100 columns in the source,
so the line breaks below do not follow the terminal width):

```
  cowbell  <cwd>   subject: ?

  nothing raised here yet

  ABSENT HERE  ⌂ local  ↑ vendor · ok  ! more reach  ⊘ blocked  ? unknown
  claude ↑? (not installed) · codex ↑? (not installed) · grok ↑? (not installed)
  gemini ↑? (not installed) · agy ↑? (not installed) · opencode ↑? (not installed)
  pi ↑? (not installed)
```

There is no `LIVE HERE` and no `COLD HERE`. `subject: ?` is what
`trust_subject` returns when `harness-trust` is not on `PATH`.

### `list`

Exit code **0**.

```
no roster entries under <cwd>  (try --all)
```

Two spaces before `(try --all)`.

```
cowbell list --all
```

```
no roster entries
```

Exit code **0**.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

The phrase `nothing to start here: no agents from harnesses.toml are installed`
is `render_picker` when `picker_choices` returns no rows. `nothing raised here yet`
is `render_registry` when there is no live row and no cold row with a
session id. Both were printed by cowbell 0.3.1 under `NO_COLOR=1`.
