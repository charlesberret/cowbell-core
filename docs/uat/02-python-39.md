# 02 · Python 3.9 trap

Run cowbell under macOS system Python. The QA-C5 target is one line on stderr
and exit 2. This tree does not print that line yet. Record what you actually
see.

## Precondition

- macOS, where `/usr/bin/python3` is 3.9.x (run `/usr/bin/python3 --version`
  and keep that line).
- A checkout of this repository, so `cowbell.py` and `bin/cowbell` are on disk.
- For the launcher half only: no Python 3.11 or newer at
  `$HOME/.venvs/fleet/bin/python3`, `/opt/homebrew/bin/python3`,
  `/usr/local/bin/python3`, or `python3` on `PATH`. `bin/cowbell` tries those
  four, in that order, and keeps the first one whose
  `sys.version_info >= (3, 11)`.

## Steps

System Python on the module:

```bash
/usr/bin/python3 cowbell.py --version
echo $?
/usr/bin/python3 cowbell.py status
echo $?
```

Launcher, with every candidate older than 3.11 or missing. `dirname` must
stay on `PATH` (`/bin` or `/usr/bin`). Point `HOME` at an empty directory if
that is what hides `~/.venvs/fleet`:

```bash
bin/cowbell --version
echo $?
```

## Expected

### Launcher (`bin/cowbell`) — run

When none of the four Pythons is 3.11 or newer, stderr is one line, stdout
is empty, exit code **2**:

```
cowbell: no python >= 3.11 found (need tomllib)
```

Confirmed by running `bin/cowbell` with `HOME` empty of a fleet venv and with
`python3` on `PATH` being a program that fails the version probe. The real
`/usr/bin` stayed on `PATH`, so `dirname` was found. Stdout was empty.

### System Python on `cowbell.py` — read, not run

This pack was not executed under Python 3.9 (the writing environment has
3.12 only). The following is what `cowbell.py` does, read from the source.

`bin/cowbell` is not involved. A pip-installed `cowbell` script calls `cli()`,
which calls `main()`, same as `python3 cowbell.py`.

- `main()` handles `--version` before `load_catalog()`. A Python that can
  parse the file prints `cowbell 0.3.1` on stdout and returns 0. It never
  reaches the tomllib check.
- A command that loads the catalog (`status`, the picker, `catalog`, …)
  calls `load_catalog()`. If `import tomllib` failed, that function raises
  `SystemExit("cowbell: python >= 3.11 required (tomllib)")`. A string
  `SystemExit` is printed on stderr and the process exits **1**, not 2.

The same string is raised again in the catalog writer. The status path hits
the one in `load_catalog()`.

QA-C5 (LAB-629) asks for a guard before any `tomllib` import, including on
`--version`, printing exactly:

```
cowbell needs Python 3.11 or newer (found 3.9.6 at /usr/bin/python3). Install with pipx or Homebrew python.
```

and exiting **2**. That sentence is not in this tree. The parenthetical
version and path in that sentence are an example from QA-C5 (`3.9.6`,
`/usr/bin/python3`); the card says the line should name the interpreter that
was found.

**UNCLEAR: which line is a pass.** Matching the QA-C5 sentence fails this
tree. Matching `cowbell: python >= 3.11 required (tomllib)` with exit 1, or
`cowbell 0.3.1` with exit 0 on `--version`, fails the QA-C5 wording. Write
the exact stderr, the exact stdout, and the exit code. If Python 3.9 raises
`SyntaxError` instead, that is the result — record it; do not substitute the
line above.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

The launcher message and exit 2 were run. The `cowbell.py` under Python 3.9
lines were read from `cowbell.py` (`main`, `load_catalog`, `cli`) and from
Python's rule that `SystemExit("…")` exits 1. QA-C5 is LAB-629 and is still
to be done; this scenario does not implement it.
