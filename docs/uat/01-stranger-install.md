# 01 · Stranger install

A clean machine. Follow the project README and nothing else, until
`cowbell --version` works.

## Precondition

- A machine with no `cowbell` on `PATH`, no `~/.config/cowbell`, and no
  `~/.local/state/cowbell` (and the same under `$XDG_CONFIG_HOME` /
  `$XDG_STATE_HOME` if those are set).
- Python 3.11 or newer available to pipx, and `pipx` itself installed.
- The only instructions you follow are in the repository `README.md`.

## Steps

1. Open `README.md` from the start. Use only an install command written there.
2. Run that command. Do not pass extra flags, do not install from a local
   checkout, and do not put `bin/cowbell` on `PATH` by hand.
3. Run:

   ```bash
   cowbell --version
   echo $?
   ```

## Expected

`cowbell --version` prints one line on stdout and nothing on stderr:

```
cowbell 0.3.1
```

Exit code **0**.

That line is `__version__` in `cowbell.py`, printed by `main()` for `--version`
before the catalog is loaded. Confirmed by running `python3 cowbell.py --version`
and by `pipx install` of this checkout (pipx 1.17.11, Python 3.12.3), which
then printed the same line.

`cowbell --version` does not create the config or state directories.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

**UNCLEAR: the README has no install command.** As of cowbell 0.3.1 the file
opens with "Type `cowbell` in this directory." and the Development section
only shows how to run unit tests. A stranger who follows the README cannot
reach `cowbell --version`. That gap is QA-C5 (LAB-629), which is to add:

```bash
pipx install git+https://github.com/charlesberret/cowbell-core
```

Until that paragraph is in the README, this scenario is a fail. Do not use a
checkout install as a pass.

A checkout install was used only to confirm the version line. It printed
`installed package cowbell 0.3.1` and then `cowbell 0.3.1`. The GitHub URL
above was not run from here: the repository is still private (LAB-253), so a
stranger without access would not be able to fetch it even after the README
gains the command. Record which of those two you hit.
