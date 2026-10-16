# 06 · `new` with flags

`--harness`, `--model`, `--lane`, `--allow`, `--yes`, and `--place` each
show up in the launch. A harness the place does not allow is refused with
the place's message.

## Precondition

Scratch config and state, `NO_COLOR=1`, `COWBELL_MODE=here`, no herdr binary.
The harness is native (no `command` key) so model, lane, and allow become
arguments. A wrapper (`command = …`) ignores those flags in `build_argv` and
only records them on the roster; do not use a wrapper for this scenario.

```bash
ROOT=/tmp/cowbell-uat-new
rm -rf "$ROOT"
mkdir -p "$ROOT/bin" "$ROOT/work" "$ROOT/place" \
  "$COWBELL_CONFIG_DIR" "$COWBELL_STATE_DIR"
cat > "$ROOT/bin/pi" << 'EOF'
#!/bin/sh
echo "PI $*"
EOF
chmod +x "$ROOT/bin/pi"
export PATH="$ROOT/bin:/usr/bin:/bin"
cat > "$COWBELL_CONFIG_DIR/harnesses.toml" << EOF
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

[[harness]]
id = "other"
kind = "pi"
title = "other stand-in"
command = "$ROOT/bin/pi"

[places.lab]
cwd = "$ROOT/place"
allow_harness = ["pi"]
default_harness = "pi"
lane = "green"
EOF
cd "$ROOT/work"
```

## Steps

```bash
cowbell new --harness pi --model model-b --lane green --allow Read,Grep --yes --spawn --name probe
echo $?
python3 -c 'import json,os; print(json.load(open(os.environ["COWBELL_STATE_DIR"]+"/roster.json"))["harnesses"][-1]["argv"])'

# fresh state, so the next name is not probe-2
rm -rf "$COWBELL_STATE_DIR"; mkdir -p "$COWBELL_STATE_DIR"
cowbell new --place lab --spawn --yes
echo $?

cowbell new --harness other --place lab --spawn --yes
echo $?

cowbell new --bogus
echo $?

cowbell new --lane purple --harness pi --spawn
echo $?
```

## Expected

### Flags on a native harness

Exit code **0**. Stdout:

```
raised probe  pi model-b green  in pid:<pid>  /tmp/cowbell-uat-new/work
```

`<pid>` is digits. Stderr is empty (no trust checker on `PATH`).

The roster row's `argv` is these ten strings, in order:

```
--session-id
<uuid>
--model
model-b
--tools
read
--tools
Read,Grep
--name
probe
```

Where each flag comes from:

| Flag | What was printed / recorded |
| --- | --- |
| `--harness pi` | sitting id `pi`, command starts with `pi` |
| `--model model-b` | the words `model-b` in the raised line, and `--model` `model-b` in argv (`model_flag`) |
| `--lane green` | the word `green` in the raised line, and `--tools` `read` in argv (`[lanes.pi] green`) |
| `--allow Read,Grep` | `--tools` `Read,Grep` in argv (`tools_allow_flag`) |
| `--name probe` | the sitting name `probe`, and `--name` `probe` (`name_flag`) |
| `--yes` | the command is accepted (not exit 2). It adds no argv. See the note below. |
| `--spawn` | the process returns instead of exec'ing, and the pane id is `pid:<pid>` |

`--session-id` and the uuid are added because `session_id_flag` is set and this is not a resume. Confirmed by running this command: stdout was `raised probe  pi model-b green  in pid:…`, and the argv list was exactly the ten strings above.

### `--place`

`cowbell new --place lab --spawn --yes` with no `--harness` uses the place's
`default_harness` (`pi`) and the place lane (`green`). Model falls back to
the first model. Exit code **0**:

```
raised pi  pi model-a green  in pid:<pid>  /tmp/cowbell-uat-new/place
```

The directory is the place `cwd`, not the directory you launched from.

### Disallowed harness

Stderr, stdout empty, exit code **1**:

```
cowbell: other may not start in place lab (allowed: pi)
```

`other` is a real harness in the catalog. The place's `allow_harness` is
only `pi`. The message is raised in `cmd_new` before anything is spawned.
Confirmed by running that command: exit 1, stderr that line, stdout empty.

An unknown harness name is a different line, exit code **1**:

```
cowbell: unknown harness 'nope' (see: cowbell catalog)
```

### Bad flag and bad lane

Unknown flag. Stdout empty, exit code **2**. Stderr starts:

```
cowbell: unknown flag --bogus
cowbell new [harness] [options...] [-- extra...]
```

and ends with:

```
Tokens after -- are passed to the harness. Any other flag exits 2.
```

Bad lane. Stderr, exit code **1**:

```
cowbell: lane must be one of green, yellow, red
```

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

**UNCLEAR: what `--yes` is supposed to change.** `new_usage` says "Assume yes
to prompts". `gate()` accepts `assume_yes` and never reads it, and
`cowbell new` does not ask a question. With a trust checker that exits 3,
the same `new --yes` still prints

```
cowbell: ! pi has more reach than <root> needs (W1)
```

on stderr and still starts (exit 0). `--yes` does not remove that line.
Filed as LAB-635. For this scenario, pass `--yes` as "accepted, exit 0, no
extra argv". Fail it if you expected a prompt to be skipped: there is no
prompt on this path. Write which of the two you were checking.

`--allow` and the lane both use `--tools` for this harness, so both pairs
appear. That is `build_argv` applying the lane list and then the allow flag,
not one replacing the other.
