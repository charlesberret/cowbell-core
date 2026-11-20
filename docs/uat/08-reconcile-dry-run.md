# 08 · `reconcile --dry-run`

With a herdr binary, and without one.

## Precondition

A scratch catalog (`schema = 1` and one `[[harness]]` is enough). `NO_COLOR=1`.

```bash
command -v herdr; echo $?
test -x "$HOME/.local/bin/herdr"; echo $?
echo "HERDR_BIN_PATH=${HERDR_BIN_PATH-<unset>}"
```

## Steps

### No herdr binary

Move every `herdr` off `PATH`, including `~/.local/bin/herdr`. Unset
`HERDR_BIN_PATH`.

```bash
unset HERDR_BIN_PATH
cowbell reconcile --dry-run
echo $?
cowbell reconcile --help
echo $?
```

### Borders already in agreement

Put a real `herdr` back on `PATH` with its server up, and run:

```bash
cowbell reconcile --dry-run
echo $?
```

If you have no server, skip this half and say so. The stub below does not
need one.

### A mismatch, dry run

```bash
STUB=/tmp/cowbell-uat-herdr
mkdir -p "$STUB"
cat > "$STUB/herdr" << 'EOF'
#!/usr/bin/env python3
import json, sys
args = sys.argv[1:]
def emit(obj):
    print(json.dumps(obj))
if args[:2] == ["api", "snapshot"]:
    emit({"snapshot": {
        "panes": [{"pane_id": "w1:p1", "agent": "grok", "tab_id": "w1:t1"}],
        "tabs": [{"tab_id": "w1:t1", "label": "butler"}],
        "workspaces": [{"workspace_id": "w1"}],
    }})
elif args[:3] == ["pane", "list", "--workspace"]:
    emit({"panes": [{"pane_id": "w1:p1", "label": "butler · local-ornith",
                     "tab_id": "w1:t1", "agent": "grok"}]})
elif args[:2] == ["pane", "rename"]:
    print("RENAMED", file=sys.stderr)
    emit({})
else:
    emit({})
EOF
chmod +x "$STUB/herdr"
HERDR_BIN_PATH="$STUB/herdr" HERDR_SOCKET_PATH="$STUB/no.sock" \
  cowbell reconcile --dry-run
echo $?
```

The stub prints the JSON object itself. cowbell accepts that as the `herdr`
payload.

## Expected

### No binary

Stdout, exit code **0**, stderr empty:

```
herdr is not installed; nothing to reconcile
```

`has_herdr()` is false, so `apply_coherence` prints that and returns before
`coherence_rows()`. Confirmed with `HERDR_BIN_PATH` pointing at a missing
file: that line, exit 0, stderr empty.

`reconcile --help` exits **0** and prints:

```
cowbell reconcile [--dry-run]
  Rewrite pane borders so they match the sitting and the agent Herdr detects.
  The tab label stays the sitting. A bare border that is not the sitting is stale.
  With no herdr binary: 'herdr is not installed; nothing to reconcile'.
```

### Herdr present, nothing to change

```
panes agree with the harness Herdr detects
```

Exit code **0**. That sentence is `apply_coherence` when the binary exists
and `coherence_rows()` is empty.

### Mismatch, dry run

Stdout, exit code **0**, stderr empty (the stub must not print `RENAMED`):

```
w1:p1 butler · local-ornith → butler · grok
```

The arrow is `→` (U+2192). The format is `{pane_id} {old} → {new}`.
`--dry-run` prints the line and does not call `herdr pane rename`.
Confirmed: stdout that line, stderr empty, exit 0.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

The no-binary sentence and the agree sentence are different. A pass on the
first half is the not-installed line, not the agree line.
