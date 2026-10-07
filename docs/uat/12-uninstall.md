# 12 · Uninstall

`pipx uninstall cowbell`. The command is gone. Nothing cowbell created is
left outside the XDG config and state directories. Those directories are
listed, not deleted, by uninstall.

## Precondition

- cowbell was installed with pipx (scenario 01, once the README has an
  install command, or a checkout `pipx install` you are explicitly throwing
  away — a checkout install is not a pass of scenario 01).
- You have run at least one command other than `--version` and `--help`, so
  the catalog exists. `cowbell list` is enough.
- Note the directories before uninstall:

  ```bash
  python3 - << 'PY'
  import os
  from pathlib import Path
  cfg = os.environ.get("COWBELL_CONFIG_DIR") or str(
      Path(os.environ.get("XDG_CONFIG_HOME") or "~/.config").expanduser() / "cowbell")
  state = os.environ.get("COWBELL_STATE_DIR") or str(
      Path(os.environ.get("XDG_STATE_HOME") or "~/.local/state").expanduser() / "cowbell")
  print("config", cfg)
  print("state", state)
  PY
  pipx list
  command -v cowbell
  ```

  If scenario 01 used the default pipx paths, config is `~/.config/cowbell`
  and state is `~/.local/state/cowbell`.

## Steps

```bash
pipx uninstall cowbell
echo $?
command -v cowbell
echo $?
pipx list
# list only the two directories printed above; do not delete them
find "$cfg" "$state" -print
```

Replace `$cfg` and `$state` with the paths you printed.

## Expected

`pipx uninstall cowbell` exits **0**. With pipx 1.17.11 the success line is:

```
uninstalled cowbell! ✨ 🌟 ✨
```

A different pipx may word that line differently. The pass is exit 0 and the
command gone. Paste the line you saw if it is not this one.

`command -v cowbell` prints nothing and exits non-zero (127 in bash).

The pipx venv for cowbell is gone (`pipx list` no longer shows cowbell).
The symlink pipx put on its bin path (default `~/.local/bin/cowbell`) is gone.

These remain, and they are the XDG dirs (or `COWBELL_CONFIG_DIR` /
`COWBELL_STATE_DIR` if you set them):

| Path | What a normal run leaves |
| --- | --- |
| `<config>/harnesses.toml` | Copied from the shipped seed the first time a command loads the catalog. |
| `<config>/.migrated_from` and `<config>/migration-backup/` | Only if a 0.1–0.3 file was copied out of herdr's plugin directory. Absent on a clean install. |
| `<state>/` | The directory itself. Created on the first roster touch (`list`, `status`, the picker, `new`, `enter`), even when empty. |
| `<state>/roster.json` | Only after a sitting is recorded (`new`, or a live agent cowbell remembers). `list` on an empty roster does not create this file. |
| `<state>/pins.json` | Only after a pin or a hide in the picker. |

`cowbell --version` alone does not create either directory. Confirmed: after
`--version`, neither path existed; after `list`, config contained
`harnesses.toml` and state was an empty directory; `pipx uninstall cowbell`
printed the success line, removed the venv and the bin symlink, and left
those two directories in place.

No other cowbell file should appear under the home directory. pipx's own
shared files (`PIPX_HOME`, default `~/.local/pipx`) are pipx's, and they
remain if other tools were installed with pipx. They are not cowbell's
catalog or roster.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

The uninstall line and the leftover paths were produced with pipx 1.17.11
installing this checkout into a private `PIPX_HOME`, then `cowbell list`
under a private `COWBELL_CONFIG_DIR` and `COWBELL_STATE_DIR`, then
`pipx uninstall cowbell`. Default XDG locations were not used for that run;
the code that chooses them is `config_dir()` and `state_dir()` in
`cowbell.py`.
