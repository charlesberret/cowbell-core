# 06 · `new` with flags

`--harness`, `--model`, `--lane`, `--allow`, `--yes`, and `--place`. A
harness the place does not allow is refused with the place's message.

## Precondition

Scratch config and state. `NO_COLOR=1`. `COWBELL_MODE=here`. No herdr binary.
The harness is native (no `command` key). A wrapper only appends catalog
flags in `_wrapper_catalog_argv` when they match the row's own defaults; do
not use a wrapper for this check.

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
effort_flag = ["--thinking"]
tools_allow_flag = "--tools"
resume = ["--session"]
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
cowbell new --harness pi --model model-b --lane green --allow Read,Grep --effort high --yes --spawn --name probe
echo $?
python3 -c 'import json,os; print(json.load(open(os.environ["COWBELL_STATE_DIR"]+"/roster.json"))["harnesses"][-1]["argv"])'

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

### The flags

Exit code **0**. Stdout:

```
raised probe  pi model-b high green  in pid:<pid>  /tmp/cowbell-uat-new/work
```

`<pid>` is digits. Stderr is empty when no trust checker is on `PATH`.

The words in that line, from `cmd_new`: name, harness id, model, effort, lane,
then `in`, the pane id, the directory.

The roster `argv` is these twelve strings, in order:

```
--session-id
<uuid>
--model
model-b
--thinking
high
--tools
read
--tools
Read,Grep
--name
probe
```

| Flag | Where it shows up |
| --- | --- |
| `--harness pi` | id `pi` in the raised line; the command is `pi` |
| `--model model-b` | `model-b` in the raised line; `--model` `model-b` in argv |
| `--lane green` | `green` in the raised line; `--tools` `read` from `[lanes.pi] green` |
| `--allow Read,Grep` | `--tools` `Read,Grep` in argv |
| `--effort high` | `high` in the raised line; `--thinking` `high` because `effort_flag` is `["--thinking"]` |
| `--yes` | accepted. It is not an unknown flag (those exit 2). It adds no argv. The usage line is `Accepted and unused; this path has no prompt` |
| `--spawn` | the process returns; the pane id is `pid:<pid>` |
| `--name probe` | the sitting name, and `--name` `probe` |

`--session-id` and the uuid are added because `session_id_flag` is set and
this is not a resume. Confirmed by running the command: stdout was
`raised probe  pi model-b high green  in pid:…`, stderr empty, exit 0, and
the argv was those twelve strings.

A second `new --harness pi --spawn --name … --yes` with no other flags, on a
fresh state, prints `raised <name>  pi model-a yellow  in pid:<pid>  <cwd>`
and exits 0. `--yes` does not change that shape.

### `--place`

`cowbell new --place lab --spawn --yes` with no `--harness` uses
`default_harness` (`pi`) and the place lane (`green`). Model is the first
model. Exit code **0**:

```
raised pi  pi model-a green  in pid:<pid>  /tmp/cowbell-uat-new/place
```

The directory is the place `cwd`, not the directory you started in.
Confirmed: that line, exit 0.

### Disallowed harness

Stderr, stdout empty, exit code **1**:

```
cowbell: other may not start in place lab (allowed: pi)
```

Confirmed by running it.

### Bad flag and bad lane

Unknown flag. Stdout empty, exit code **2**. Stderr starts:

```
cowbell: unknown flag --bogus
```

and the usage that follows includes:

```
  -y, --yes       Accepted and unused; this path has no prompt
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

`--allow` and the green lane both use `--tools` for this harness, so both
pairs are in argv. `build_argv` appends the lane list and then the allow
flag. One does not replace the other.

`--yes` is not a guess. `new_usage` prints `Accepted and unused; this path has no prompt`, and `gate()` takes `assume_yes` without reading it. A launch with `--yes` still exits 0 and still records a normal argv.
