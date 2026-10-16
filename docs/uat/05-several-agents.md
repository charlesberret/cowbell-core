# 05 · Several agents, several running

Active lists who is working here and is not a menu. Resume and New Session
are the menu. You cannot take a running sitting over from the list.

## Precondition

Scratch config and state, `NO_COLOR=1` for the text checks, `COWBELL_MODE=here`.
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
models = ["claude-sonnet-5"]
model_flag = ["--model"]
resume = ["--resume"]
session_id_flag = "--session-id"

[[harness]]
id = "grok"
kind = "grok"
title = "Grok CLI"
resume = ["--resume"]

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
# two here, one in the sibling directory (so widen counts 3)
python3 "$ROOT/bin/claude" &
echo $! > "$ROOT/claude.pid"
python3 "$ROOT/bin/grok" &
echo $! > "$ROOT/grok.pid"
( cd "$ROOT/proj/other" && python3 "$ROOT/bin/claude" ) &
echo $! > "$ROOT/other.pid"
```

Those three processes must be on a real tty (`python3` in a pipeline is not;
start them in a terminal, or from a pty). `ps` must show a tty other than
`?` or `??`. On Linux that is `pts/N`. On macOS it is `ttysNNN`. The expected
text uses `<tty>` for whichever `ps` prints.

Lobe marks: claude U+F4036, grok U+F4079, codex U+F403E.

When you are done, kill the three pids.

## Steps

```bash
export COWBELL_PLAIN=1 NO_COLOR=1
cowbell status
echo $?
printf 'q\n' | cowbell
echo $?
cowbell list
echo $?
cowbell claude
echo $?
cowbell enter claude
echo $?
```

In a real terminal (unset `COWBELL_PLAIN`), open `cowbell`, try to move onto
an Active row with the arrow keys and with a click, press Enter, then `q`.

## Expected

### Active is a census

Text picker stdout contains an Active box, then Resume, then New Session.
Active rows have **no** number. The first numbered row is Resume.

The box top begins `┌─ Active ` and ends with `┐`. Each sitting line begins
`│    `, then the name padded to 22 columns, the Lobe mark, ` running  on `,
and `<tty>`, and ends with ` │`. The bottom begins `└` and ends with `┘`.
For this fixture the names inside the box are `claude` and `grok` only. The
claude in `other` is not inside the box.

The first line of the picker ends with:

```
g widen to proj · 3 running
```

(two spaces, the cwd, at least three spaces, then that phrase). `3` is the
count of agent processes under the git root, which is one more than the two
in this directory.

Resume is only `old-claude`. `no-id` has an empty `session_id` and is absent
from Resume and from `COLD HERE`. The ago word is `today` because `last_seen`
is today's date.

New Session numbers start at 2. Order for this fixture (equal use, catalog
order, then the unused harness): grok's roster row and claude's roster row
score the same, so catalog order stands: `claude`, then `grok`, then `codex`
(installed because `command = "/bin/true"` exists). Titles `Claude Code`,
`Grok CLI`, `Codex`.

```
  Resume
    1  old-claude             󴀶 today

  New Session
    2  󴀶 claude                 Claude Code
    3  󴁹 grok                   Grok CLI
    4  󴀾 codex                  Codex
```

The mark after `old-claude` is U+F4036. The marks before `claude`, `grok`,
and `codex` are U+F4036, U+F4079, and U+F403E.

Footer, because widen applies:

```
  number = open   [n] new   [+] add   [g] widen   [q]
```

`q` exits **0**.

### `status`

Exit code **0**. Headings, in order: the `cowbell` line with `subject: ?`,
then

```
  git root: /tmp/cowbell-uat-several/proj   (3 live under it)   [g] widen
```

then `LIVE HERE` with numbered rows for the two processes in this directory
(`running`, pane `pid:<pid>`, `(not on roster)`), then `COLD HERE  resumable`
with `old-claude` only (`cold`, pane `—` which is U+2014 EM DASH, session
`sess-old`), then `ABSENT HERE` which does **not** list `claude` or `grok`
(they are present) and does list `codex` as `codex ↑?` without
`(not installed)`.

### `list`

`list` reads the roster, not the process census. Exit code **0**. Both
roster rows are shown, including `no-id`, which Resume hides. Status `cold`
for both, because their panes are not live herdr panes. The running `claude`
and `grok` processes do not add rows of their own.

### Cannot take over a running sitting

From the picker, Active rows are not in the menu. Arrow keys, digits, and
Enter move among Resume and New Session only. Clicking an Active row does
not select it. Enter does not focus it and prints no error. Confirmed from
`picker_selectable`: a running row is selectable only when its action is
`more` (the `+ N more` fold), which this fixture does not need.

Naming the harness on the command line does try to focus, and refuses.
`cowbell claude` prints this on stderr and exits **1** (`<tty>` and `<pid>`
from `ps`):

```
claude runs on <tty> (pid <pid>); cowbell can't switch to another terminal
```

There is no `cowbell:` prefix on that line. Stdout is empty. The same
sentence is what `ProcessScan.focus` raises.

`cowbell enter claude` does not find the live process. The name `claude` is
not a roster name and not a session id (`old-claude` is the roster name).
Stderr, exit code **1**:

```
cowbell: no session 'claude' on roster or in history
```

`no-id` stays out of Resume because its `session_id` is empty. `cmd_enter`
does not have a separate refusal for that: a roster hit with an empty
session id is launched as a fresh start (`here_command` only adds a resume
argument when the id is non-empty). Do not run `cowbell enter no-id` against
the sleeper in this fixture. That command execs into `grok` and the sleeper
does not exit. The menu check is the one that matters here: `no-id` is not
a numbered row.

### Resume versus New Session

Resume is `old-claude` only (has a session id, not currently the live
process). New Session is the installed catalog: `claude`, `grok`, `codex`.
`no-id` is in neither menu. A blocked harness would be left off New Session;
this fixture has no checker, so nothing is blocked.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

The Active box, the widen phrase `g widen to proj · 3 running`, the
`running  on <tty>` cell, and the focus refusal were printed by cowbell 0.3.1
with three Python sleepers on ptys and this catalog. The tty in that run was
`pts/N` because the machine was Linux. The refusal string is
`ProcessScan.focus` in `cowbell.py`.

Ranking: a roster row at this cwd scores 3. Equal scores keep catalog order
after a stable sort on `last_seen`. Setting both `last_seen` values to today
makes the New Session order `claude`, `grok`, `codex`. A different `last_seen`
on `no-id` puts `grok` first; if your order differs, compare the dates in
`roster.json` before calling it a fail.
