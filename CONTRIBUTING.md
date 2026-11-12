# Contributing

cowbell is a single stdlib module plus tests. Pull requests that fix bugs or add focused behaviour are welcome; large refactors without discussion are harder to review.

## Before you open a PR

1. Run the full test suite:

   ```bash
   python3 -m unittest discover -s tests -v
   ```

   `tests/test_pty.py` needs a pseudo-terminal; on Linux CI that is the default environment.

2. Run the public-surface scan (no house paths, coordination dirs, or Linear ids in tracked files):

   ```bash
   ./scripts/public-surface-scan.sh
   ```

3. If you change user-visible behaviour or commands, add a short note under **Unreleased** in `CHANGELOG.md` (no issue ids in the changelog body).

## Pull request expectations

- One logical change per PR when possible.
- Match existing style in `cowbell.py` (sparse comments, plain names).
- Do not commit agent working files listed in `.gitignore` (HANDOFF notes, `.coordination/`, local catalog copies).
- Packaging changes must keep `pipx install git+https://github.com/charlesberret/cowbell-core` working with `requires-python = ">=3.11"`.

## Development setup

Clone the repo and use Python 3.11 or newer (macOS `/usr/bin/python3` is too old):

```bash
git clone https://github.com/charlesberret/cowbell-core.git
cd cowbell-core
python3 -m unittest discover -s tests -v
```

Or install with pipx from the same URL and run `cowbell` on your PATH.

## Security

See [SECURITY.md](SECURITY.md) for privilege-related catalog settings and how to report problems.
