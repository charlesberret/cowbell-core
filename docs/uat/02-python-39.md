# 02 · Python 3.9 trap

Run under macOS system Python, and run the repo launcher when it cannot find
Python 3.11. Record the line and the exit code you actually get.

## Precondition

- macOS system Python at `/usr/bin/python3`, measured as **3.9.6**.
- A checkout, so `cowbell.py` and `bin/cowbell` are on disk.
- For the launcher half: none of these is Python 3.11 or newer:
  `$HOME/.venvs/fleet/bin/python3`, `/opt/homebrew/bin/python3`,
  `/usr/local/bin/python3`, and `python3` on `PATH`. `bin/cowbell` tries
  those four, in that order, and keeps the first whose
  `sys.version_info >= (3, 11)`.

## Steps

Launcher, with every candidate missing or older than 3.11. Keep `dirname` on
`PATH` (`/bin` or `/usr/bin`):

```bash
bin/cowbell --version
echo $?
```

System Python on the module:

```bash
/usr/bin/python3 cowbell.py --version
echo $?
/usr/bin/python3 cowbell.py status
echo $?
```

## Expected

### Launcher — run on this tree

Stderr is one line, stdout is empty, exit code **2**:

```
cowbell: no python >= 3.11 found (need tomllib)
```

Confirmed by running `bin/cowbell` with `HOME` empty of a fleet venv and with
`python3` on `PATH` being a program that fails the version probe. `/usr/bin`
stayed on `PATH`. Stdout was empty. Exit code 2.

### System Python on `cowbell.py` — measured, `/usr/bin/python3` 3.9.6

This is the first sign-off result for this half. `bin/cowbell` is not
involved. `/usr/bin/python3 cowbell.py` calls `cli()` → `main()`.

`/usr/bin/python3 cowbell.py --version` prints one line on stdout, nothing
on stderr, and exits **0**:

```
cowbell 0.3.2
```

`main()` handles `--version` before `load_catalog()`, so the missing
`tomllib` is not reached.

`/usr/bin/python3 cowbell.py status` prints nothing on stdout. Stderr is
one line, and the exit code is **1**:

```
cowbell: python >= 3.11 required (tomllib)
```

No config directory is created. `load_catalog()` raises that `SystemExit`
before `catalog_path()` makes the directory.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

The launcher line and exit 2 were run on a machine whose `python3` is 3.12,
with the version probe forced to fail. The 3.9.6 lines above were measured
with `/usr/bin/python3` 3.9.6: `--version` exited 0, and `status` exited 1
with the tomllib line and no config directory. Passing one half does not
pass the other.
