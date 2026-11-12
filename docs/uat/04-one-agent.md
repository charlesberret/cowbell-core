# 04 · One agent installed

The catalog shows it. `new` starts it. `list` shows it. `enter` resumes it.

## Precondition

Scratch config and state. `NO_COLOR=1`, `COWBELL_PLAIN=1`, `COWBELL_MODE=here`.
No `herdr` on `PATH`. `command -v harness-trust` fails.

The harness is native (no `command` key), so cowbell looks up `pi` on `PATH`.
Resume uses `--session`, which is what the shipped `pi` row declares.

```bash
ROOT=/tmp/cowbell-uat-one
rm -rf "$ROOT"
mkdir -p "$ROOT/bin" "$ROOT/work" "$COWBELL_CONFIG_DIR" "$COWBELL_STATE_DIR"
cat > "$ROOT/bin/pi" << 'EOF'
#!/bin/sh
echo "PI $*"
EOF
chmod +x "$ROOT/bin/pi"
export PATH="$ROOT/bin:$PATH"
cat > "$COWBELL_CONFIG_DIR/harnesses.toml" << 'EOF'
schema = 1

[defaults]
lane = "yellow"
ask_name = false
trust_command = "harness-trust-not-on-path"
seat_file = "SEAT.md"
session_history = "off"

[lanes.pi]
green = ["--tools", "read"]
yellow = ["--tools", "read,edit,write"]
red = []

[[harness]]
id = "pi"
kind = "pi"
title = "pi stand-in"
models = ["model-a", "model-b"]
model_flag = ["--model"]
tools_allow_flag = "--tools"
resume = ["--session"]
session_id_flag = "--session-id"
name_flag = "--name"
EOF
cd "$ROOT/work"
```

The Lobe mark for kind `pi` is U+F413E. In the lines below it is that
character. A font with no glyph for it still has the code point in the output.

## Steps

```bash
cowbell catalog
echo $?
cowbell list
echo $?
printf 'q\n' | cowbell picker
echo $?
cowbell new --harness pi --spawn --name probe
echo $?
cowbell list
echo $?
cowbell enter probe
echo $?
```

`--spawn` starts the process and returns, so `list` can be read before
`enter`. `enter` then execs `pi`. The script prints one line and exits.

## Expected

### `catalog`

Exit code **0**. `↑` is the vendor mark (egress defaults to `vendor`):

```
harness          kind     egress  installed badge      title
pi               pi       ↑ vendor yes       ?          pi stand-in
```

`yes` is `installed()`. `?` is the badge when the checker is not on `PATH`.

### `list` before `new`

Exit code **0**:

```
no roster entries under /tmp/cowbell-uat-one/work  (try --all)
```

### Picker

Exit code **0**. Body:

```
  /tmp/cowbell-uat-one/work

  New Session
    1  pi                     󴄾  pi stand-in

  number = open   [n] new   [+] add   [q]
  > 
```

The name `pi` is padded to 22 columns, then U+F413E, then two spaces, then
`pi stand-in`. No Active box and no Resume. No `! more reach than needed`.

### `new --spawn`

Exit code **0**. Stderr empty. `<pid>` is digits:

```
raised probe  pi model-a yellow  in pid:<pid>  /tmp/cowbell-uat-one/work
```

`model-a` is the first `models` entry. `yellow` is the catalog default lane.
There is no effort word: this harness row sets no `effort`, and the command
passed no `--effort`.

### `list` after `new`

Exit code **0**. `<sid8>` is the first 8 characters of the roster session id.
Status is `cold` once the short-lived process has exited. Columns are name
24, harness 14, status 9, pane 8, session 8, then the cwd. A pid that makes
`pid:<pid>` longer than 8 runs into the next column.

```
name                     harness        status    pane     session  cwd
probe                    pi             cold      pid:<pid> <sid8> /tmp/cowbell-uat-one/work
```

### `enter probe`

The handoff line, then the agent's line. Exit code is the agent's (**0**
here). `<uuid>` is the 36-character session id. Resume spec is `--session`,
not `--continue`:

```
  probe  pi --model model-a --tools read,edit,write --session <uuid> --name probe  /tmp/cowbell-uat-one/work
PI --model model-a --tools read,edit,write --session <uuid> --name probe
```

Confirmed by running this fixture: `raised probe  pi model-a yellow  in pid:…`
and, on `enter`, the handoff line with `--session` and then `PI …`.

On a terminal, `exec_here` clears the screen first (`\x1b[H\x1b[2J`) and
then prints that same handoff line.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

Resume is offered only for a roster row with a session id. This harness has
`session_id_flag`, so `new` stores one. A harness without that flag, started
outside herdr, still shows up in `cowbell list` and is not a Resume row.
That split is scenario 05.
