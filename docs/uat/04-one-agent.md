# 04 · One agent installed

The catalog shows it. `new` starts it. `list` shows it. `enter` resumes it.

## Precondition

Scratch config and state, `NO_COLOR=1`, `COWBELL_PLAIN=1`, `COWBELL_MODE=here`.
No `herdr` binary on `PATH` (scenario 10 covers that on its own; `new` outside
herdr execs in this terminal). `command -v harness-trust` fails.

Create a directory and a one-harness catalog. The harness has no `command`
key, so cowbell looks up `pi` on `PATH` and passes model, lane, and allow
flags. The script must be named `pi`.

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
resume = ["--continue"]
session_id_flag = "--session-id"
name_flag = "--name"
EOF
cd "$ROOT/work"
```

The Lobe mark for kind `pi` is U+F413E (one private-use character). In the
lines below it is written as that character. A font that has no glyph for it
still has that code point in the output.

## Steps

```bash
cowbell catalog
echo $?
cowbell list
echo $?
printf 'q\n' | cowbell
echo $?
cowbell new --harness pi --spawn --name probe
echo $?
cowbell list
echo $?
cowbell enter probe
echo $?
```

`--spawn` starts the agent and returns, so `list` can be read before
`enter`. `enter` then hands this terminal to `pi` (it `exec`s). The script
above prints one line and exits.

## Expected

### `catalog`

Exit code **0**. Header, then one data row. `↑` is the vendor mark
(the seed default egress is `vendor`):

```
harness          kind     egress  installed badge      title
pi               pi       ↑ vendor yes       ?          pi stand-in
```

`yes` is `installed()`. `?` is `trust_badge` when the checker is not on `PATH`.

### `list` before `new`

Exit code **0**.

```
no roster entries under /tmp/cowbell-uat-one/work  (try --all)
```

### Picker

Exit code **0**. `q` leaves. Body:

```
  /tmp/cowbell-uat-one/work

  New Session
    1  󴄾 pi                     pi stand-in

  number = open   [n] new   [+] add   [q]
  > 
```

The character between the number and `pi` is U+F413E. There is no Active
box and no Resume section: nothing is running here and the roster is empty.
No `! more reach than needed`.

### `new --spawn`

Exit code **0**. Stdout is one line. `<pid>` is the child's pid (digits
only). Nothing on stderr when the checker is absent:

```
raised probe  pi model-a yellow  in pid:<pid>  /tmp/cowbell-uat-one/work
```

`model-a` is the first entry in `models`. `yellow` is the catalog default
lane. The name is the one passed to `--name`.

### `list` after `new`

Exit code **0**. Header, then one row. `<sid8>` is the first 8 characters of
the session id stored in the roster. Status is `cold` once that short-lived
process has exited:

```
name                     harness        status    pane     session  cwd
probe                    pi             cold      pid:<pid> <sid8> /tmp/cowbell-uat-one/work
```

Columns are name 24, harness 14, status 9, pane 8, session 8, then the cwd.
The pane cell is `pid:<pid>` from `--spawn`. If the process is still alive,
status is `running` (process scan) rather than `cold`.

### `enter probe`

Stdout begins with the handoff line, then the agent's own line. Exit code
is the agent's (**0** for the script above). `<uuid>` is the session id from
the roster (36 characters). `--continue` is this harness's `resume` spec:

```
  probe  pi --model model-a --tools read,edit,write --continue <uuid> --name probe  /tmp/cowbell-uat-one/work
PI --model model-a --tools read,edit,write --continue <uuid> --name probe
```

The first line is `exec_here`: two spaces, the sitting name, the command,
the directory. There is no screen clear when stdout is not a terminal. On a
terminal the screen is cleared first (`\x1b[H\x1b[2J`) and then that same
handoff line is printed.

Confirmed by running this fixture: `catalog` showed `yes` and `?`, `new
--spawn` printed `raised probe  pi …`, `list` printed the header and the
row, and `enter` printed the handoff line and then `PI …`.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

Resume is offered only when the roster row has a `session_id`. This harness
sets `session_id_flag`, so `new` stores one and `enter` can resume. A harness
without that flag, started outside herdr, is listed by `cowbell list` and is
not offered under Resume. That split is scenario 05.
