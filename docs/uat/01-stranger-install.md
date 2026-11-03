# 01 · Stranger install

A machine that does not have cowbell yet. Follow the README and nothing else,
until `cowbell --version` works.

## Precondition

- No `cowbell` on `PATH`.
- No `~/.config/cowbell` and no `~/.local/state/cowbell` (and the same under
  `$XDG_CONFIG_HOME` / `$XDG_STATE_HOME` if those are set).
- Python 3.11 or newer on `PATH` as `python3`, or at one of the paths
  `bin/cowbell` searches (see scenario 02).
- `git` can clone `https://github.com/charlesberret/cowbell-core.git`.

## Steps

Do only what the Install section of `README.md` says. On this tree that is:

```bash
git clone https://github.com/charlesberret/cowbell-core.git
cd cowbell-core
./bin/cowbell --version
echo $?
```

Do not `pip install`, do not `pipx install`, and do not copy `cowbell.py`
onto `PATH` by hand. The README's next step, a symlink into
`$HOME/.local/bin`, is optional for this scenario. The version command is
the stop.

## Expected

Stdout is one line. Stderr is empty. Exit code **0**.

```
cowbell 0.3.2
```

That is `__version__` in `cowbell.py`, printed by `main()` for `--version`
before the catalog is loaded. `./bin/cowbell --version` in this checkout
printed that line and exited 0. `cowbell --version` does not create the
config or state directory.

The README's Install section says the expected output is `cowbell X.Y.Z`.
The program's line is `cowbell 0.3.2`, which is that shape with this tree's
version filled in.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

The clone itself was not repeated from an empty machine while writing this
pack. The version line was. If `git clone` fails, paste that error and stop.
That is a fail of the stranger path, not a different cowbell version line.
