# 12 · Uninstall

`pipx uninstall cowbell`. The command pipx installed is gone. Cowbell's
files outside the XDG config and state directories are gone. Those two
directories are listed, not removed.

## Precondition

The README install is a symlink of `bin/cowbell`, not a pipx package. This
scenario is the pipx path. Use a private pipx home if you do not want to
touch a real one:

```bash
export PIPX_HOME=/tmp/cowbell-uat-pipx
export PIPX_BIN_DIR=/tmp/cowbell-uat-pipx/bin
export PIPX_MAN_DIR=/tmp/cowbell-uat-pipx/man
export COWBELL_CONFIG_DIR=/tmp/cowbell-uat-pipx-cfg
export COWBELL_STATE_DIR=/tmp/cowbell-uat-pipx-state
```

Python's venv module has to work (`python3 -m venv`). On Debian or Ubuntu
that needs the `python3-venv` package. Without it, pipx stops at
`No module named ensurepip` and does not install cowbell.

## Steps

```bash
pipx install /path/to/cowbell-core
echo $?
"$PIPX_BIN_DIR/cowbell" --version
echo $?
"$PIPX_BIN_DIR/cowbell" list
echo $?
find "$COWBELL_CONFIG_DIR" "$COWBELL_STATE_DIR" -print
pipx uninstall cowbell
echo $?
command -v cowbell
find "$COWBELL_CONFIG_DIR" "$COWBELL_STATE_DIR" -print
ls "$PIPX_BIN_DIR"
pipx list
```

Use the checkout path you actually have. If `PIPX_BIN_DIR` is on `PATH`,
`command -v cowbell` is meaningful; otherwise look at the bin directory
itself.

## Expected

`pipx install` of this tree exits **0**. pipx 1.18.11 printed:

```
done! ✨ 🌟 ✨
  installed package cowbell 0.3.2, installed using Python 3.12.3
  These apps are now available
    - cowbell
```

The Python version in that line is the interpreter pipx used. The package
version is `0.3.2`.

`cowbell --version` prints `cowbell 0.3.2` and exits **0**. It does not
create the XDG directories.

`cowbell list` exits **0** and creates them. After that, the tree is the
config directory containing `harnesses.toml`, and the state directory with
nothing in it yet. `list` on an empty roster does not write `roster.json`.

`pipx uninstall cowbell` exits **0**. pipx 1.18.11 printed:

```
uninstalled cowbell! ✨ 🌟 ✨
```

The venv is gone. The `cowbell` symlink in `PIPX_BIN_DIR` is gone.
`pipx list` no longer shows cowbell (`nothing has been installed with pipx 😴`
when it was the only package).

These remain:

| Path | What is there |
| --- | --- |
| `<config>/harnesses.toml` | Copied from the shipped seed the first time a command loads the catalog. |
| `<state>/` | The directory. Created on the first roster touch. Empty if nothing was recorded. |
| `<state>/roster.json` | Only after a sitting is recorded. |
| `<state>/pins.json` | Only after a pin or a hide. |

Confirmed with pipx 1.18.11, `PIPX_HOME=/tmp/uat-pipx`, and private
`COWBELL_CONFIG_DIR` / `COWBELL_STATE_DIR`: install exit 0, version
`cowbell 0.3.2`, `list` created `harnesses.toml` and an empty state
directory, uninstall printed the line above and exited 0, and those two
directories were still there.

If pipx never installed cowbell (the README symlink, or a failed venv),
`pipx uninstall cowbell` prints:

```
Nothing to uninstall for cowbell 😴
```

and exits **1**. That was run on this machine before the install succeeded.
It is the result for "pipx has no cowbell", not the result of a successful
install. A README symlink is removed by deleting the symlink. pipx does not
remove it.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

A different pipx may word the success line differently. Paste the line if it
is not the one above. The pass for a real install is exit 0, the bin symlink
gone, the venv gone, and only the config and state directories left from
cowbell.
