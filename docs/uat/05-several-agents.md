# 05 · Several agents, several running

Active lists who is working here. It is not a menu. Resume and New Session
are the menu. You cannot take a running sitting over from this list.

## Precondition

Scratch config and state. `NO_COLOR=1` for the text checks. `COWBELL_MODE=here`.
No herdr binary. `command -v harness-trust` fails.

```bash
ROOT=/tmp/cowbell-uat-several
rm -rf "$ROOT"
mkdir -p "$ROOT/bin" "$ROOT/proj/pkg" "$ROOT/proj/other" \
  "$COWBELL_CONFIG_DIR" "$COWBELL_STATE_DIR"
git init -q "$ROOT/proj"
echo x > "$ROOT/proj/README"
git -C "$ROOT/proj" add README
git -C "$ROOT/proj" -c user.email=dev@example.com -c user.name=dev commit -qm init

for name in claude grok; do
  cat > "$ROOT/bin/$name" << 'EOF'
#!/usr/bin/env python3
import time
time.sleep(120)
EOF
  chmod +x "$ROOT/bin/$name"
done

cat > "$COWBELL_CONFIG_DIR/harnesses.toml" << 'EOF'
schema = 1

[defaults]
lane = "yellow"
ask_name = false
trust_command = "harness-trust-not-on-path"
seat_file = "SEAT.md"
session_history = "off"

[[harness]]
id = "claude"
kind = "claude"
title = "Claude Code"

[[harness]]
id = "grok"
kind = "grok"
title = "Grok CLI"

[[harness]]
id = "codex"
kind = "codex"
title = "Codex"
command = "/bin/true"
EOF

TODAY=$(date +%F)
cat > "$COWBELL_STATE_DIR/roster.json" << EOF
{
  "schema": 1,
  "harnesses": [
    {"name": "old-claude", "cwd": "$ROOT/proj/pkg", "harness": "claude", "kind": "claude",
     "session_id": "sess-old-1", "created": "${TODAY}T00:00:00", "last_seen": "$TODAY"},
    {"name": "no-id", "cwd": "$ROOT/proj/pkg", "harness": "grok", "kind": "grok",
     "session_id": "", "created": "${TODAY}T00:00:00", "last_seen": "$TODAY"}
  ]
}
EOF

export PATH="$ROOT/bin:/usr/bin:/bin"
cd "$ROOT/proj/pkg"
```

Start three processes on a real tty (a pipeline is not one; `ps` must show a
tty other than `?`). Two in this directory, one in `$ROOT/proj/other`:

```bash
python3 "$ROOT/bin/claude" &
python3 "$ROOT/bin/grok" &
( cd "$ROOT/proj/other" && python3 "$ROOT/bin/claude" ) &
```

On Linux the tty looks like `pts/N`. On macOS it looks like `ttysNNN`. The
expected text uses `<tty>` for whichever `ps` prints. Kill the three pids
when you are done.

Lobe marks, after the padded name: claude U+F4036, grok U+F4079, codex U+F403E.

## Steps

```bash
export COWBELL_PLAIN=1 NO_COLOR=1
cowbell status
echo $?
printf 'q\n' | cowbell picker
echo $?
cowbell list
echo $?
cowbell claude
echo $?
cowbell enter claude
echo $?
```

In a real terminal, open `cowbell`. Try to move onto an Active row with the
arrows and with a click. Press Enter. Then `q`.

## Expected

### The three sections

The text picker has an Active box, then Resume, then New Session. Active
rows have no number. The first numbered row is Resume.

From `picker_choices` and `render_picker` (this 0.3.2 tree was not re-run
with three live processes; the row shape is the source):

- Box top begins `┌─ Active ` and ends with `┐`.
- Each sitting line begins `│    `, then the name padded to 22 columns,
  the Lobe mark, two spaces, `running`, and ` on <tty>`.
- The two names inside the box are `claude` and `grok`. The claude process
  whose cwd is `other` is not in the box.
- Box bottom begins `└` and ends with `┘`.

The first picker line ends with `g widen to proj · 3 running` when the git
root is `$ROOT/proj` and three agent processes are under it. That phrase is
`render_picker`: `g widen to {basename} · {wider} running`, and only when
`wider` is greater than the number of live rows in this directory.

Resume is `old-claude` only. `no-id` has an empty session id and is not a
Resume row and not a `COLD HERE` row. The ago word is `today` because
`last_seen` is today's date. The Resume line is the name padded to 22,
U+F4036, two spaces, `today`.

New Session numbers start at 2. Both roster rows are at this cwd, so they
score the same, and equal `last_seen` keeps catalog order: `claude`, then
`grok`, then `codex` (`command = "/bin/true"` exists, so codex is installed).
Titles `Claude Code`, `Grok CLI`, `Codex`. Each line is the id padded to 22,
its Lobe mark, two spaces, then the title.

Footer, because widen applies:

```
  number = open   [n] new   [+] add   [g] widen   [q]
```

`q` exits **0**.

**UNCLEAR: the exact Active box width on your tty.** The dash count follows
the tty string. Do not fail a longer or shorter rule. Fail a number on an
Active row, a missing `running`, or a missing `on <tty>`.

### `status`

Exit code **0**. A `cowbell` line with `subject: ?`, then a git line:

```
  git root: /tmp/cowbell-uat-several/proj   (3 live under it)   [g] widen
```

then `LIVE HERE` for the two processes here (`running`, pane `pid:<pid>`,
`(not on roster)`), then `COLD HERE  resumable` for `old-claude` only
(`cold`, pane `—` U+2014 when the row has no pane id, session `sess-old`),
then `ABSENT HERE` listing `codex` as `codex ↑?` and not listing `claude` or
`grok`.

The git line's `(3 live under it)` is `cmd_registry` counting agent cwd
values under the git root. It was read from that function, not reprinted
from a three-process run on this tree.

### `list`

Exit code **0**. `list` prints roster rows, not the process census. Both
`old-claude` and `no-id` appear. The running processes do not add rows.

### Cannot take one over

Active rows are not selectable (`picker_selectable` is false unless the row's
action is `more`). Arrows, digits, and Enter stay on Resume and New Session.
Clicking an Active row does not select it.

`cowbell claude` tries to focus the live process. Stderr, stdout empty,
exit code **1**, from `ProcessScan.focus`:

```
claude runs on <tty> (pid <pid>); cowbell can't switch to another terminal
```

There is no `cowbell:` prefix. `<tty>` and `<pid>` come from the process.

`cowbell enter claude` does not see that process. The roster name is
`old-claude`. Stderr, exit code **1**:

```
cowbell: no session 'claude' on roster or in history
```

Do not run `cowbell enter no-id`. The row has no session id, and `cmd_enter`
still launches a hit it found. That execs the sleeper. The check here is
that `no-id` is not a numbered Resume row.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

The refusal string and the `no session` string were read from `cowbell.py`.
The New Session glyph-after-name shape was printed by a one-harness picker
on this tree (scenario 04) and is the same `picker_choices` format. The
three-process screen was not captured again for 0.3.2.
