# 08 · `reconcile --dry-run`

With herdr, and without it. This is the LAB-497 behaviour of the reconcile
command: the core still runs when no herdr binary exists.

## Precondition

Scratch config with any valid `harnesses.toml` (`schema = 1` and one
`[[harness]]` is enough). `NO_COLOR=1`. A directory to stand in.

Know whether `herdr` is visible before each half:

```bash
command -v herdr; echo $?
test -x "$HOME/.local/bin/herdr"; echo $?
echo "HERDR_BIN_PATH=${HERDR_BIN_PATH-<unset>}"
```

## Steps

### Without herdr

Move any `herdr` off `PATH`, including `~/.local/bin/herdr`. Unset
`HERDR_BIN_PATH`. Then:

```bash
unset HERDR_BIN_PATH
cowbell reconcile --dry-run
echo $?
cowbell reconcile --help
echo $?
```

### With herdr, borders already matching

Put the real `herdr` back on `PATH` (or set `HERDR_BIN_PATH` to it) and have
its server listening. Run:

```bash
cowbell reconcile --dry-run
echo $?
```

If you have no herdr server, skip this half and say so in the sheet. The
controlled half below does not need a server.

### Controlled mismatch (no real server)

This is how the arrow line was captured. A stub `herdr` on `HERDR_BIN_PATH`
that answers JSON is enough; cowbell does not open the socket for
`reconcile`.

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
HERDR_BIN_PATH="$STUB/herdr" HERDR_SOCKET_PATH="$STUB/no.sock" cowbell reconcile --dry-run
echo $?
```

The stub's stdout must be the JSON object itself (what `herdr()` parses),
not wrapped. The script above prints the object.

## Expected

### Without herdr

Stdout, exit code **0**:

```
panes agree with the harness Herdr detects
```

Stderr empty. `reconcile --help` exits **0** and prints:

```
cowbell reconcile [--dry-run]
  Rewrite pane borders that claim a harness so they match the agent Herdr detects.
  The tab label stays the sitting. A border with no harness claim is left alone.
```

Confirmed by running `reconcile --dry-run` with `HERDR_BIN_PATH` pointing at
a path that is not a file, and again with no binary on `PATH`: both printed
the agree line and exited 0. `snapshot()` and `workspaces()` swallow
`HerdrError`, the row list is empty, and the empty list is this sentence.

### With herdr, nothing to change

The same agree line, exit code **0**. Confirmed with a stub whose pane label
was already `butler · grok` while the detected agent was `grok`.

### Mismatch, dry run

Stdout, exit code **0**, stderr empty (the stub's `RENAMED` must not appear):

```
w1:p1 butler · local-ornith → butler · grok
```

The arrow is `→` (U+2192). The format from `apply_coherence` is
`{pane_id} {old} → {new}`. Dry run prints that and does not call
`herdr pane rename`. Confirmed: stderr was empty, exit 0, stdout was that
line.

A real herdr with one mismatched pane prints one such line per pane and
exits 0. It must not rename while `--dry-run` is set. Check a pane label
before and after if you have a real mismatch; they stay the same.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

**UNCLEAR: the agree line means two different things.** No herdr binary, and
a herdr whose borders already match, both print `panes agree with the harness Herdr detects` and both exit 0. A tester cannot tell "not checked" from
"checked and agreed" from that sentence alone. Filed as LAB-636. Pass each
half on the lines above. In the sheet, write whether herdr was actually on
`PATH` for the second half (`command -v herdr`). Do not treat the agree line
by itself as proof that herdr ran.

LAB-497 is the requirement that these commands run with no herdr binary.
Scenario 10 is the rest of that requirement.
