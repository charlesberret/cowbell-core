# 02 · Python 3.9 trap

Run under macOS system Python, and run the repo launcher when it cannot find
Python 3.11. Record the line and the exit code you actually get.

## Precondition

- macOS, where `/usr/bin/python3` reports 3.9.x (`/usr/bin/python3 --version`).
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

### System Python on `cowbell.py` — read, not run

This pack was not executed under Python 3.9. The writing machine has
Python 3.12 only. The following is what `cowbell.py` does.

`bin/cowbell` is not involved. A pip-installed `cowbell` script calls
`cli()` → `main()`, same as `python3 cowbell.py`.

- `main()` handles `--version` before `load_catalog()`. A Python that can
  parse the file prints `cowbell 0.3.2` and returns 0. It never reaches the
  tomllib check.
- A command that loads the catalog calls `load_catalog()`. If
  `import tomllib` failed, that function raises
  `SystemExit("cowbell: python >= 3.11 required (tomllib)")`. A string
  `SystemExit` is printed on stderr and the process exits **1**.

**UNCLEAR: what Python 3.9 actually prints.** The source has no line of the
shape "cowbell needs Python 3.11 or newer (found …)". If 3.9 raises
`SyntaxError` before `main` runs, that error is the result. Paste the
stderr and the exit code. Do not substitute the launcher line or the
`SystemExit` string above if you did not see them.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

The launcher line and exit 2 were run against this tree. The 3.9 module
path was read from `main()` and `load_catalog()` and was not executed.
Passing the launcher half does not pass the system-Python half.
