# Cutting a Release

Step-by-step procedure for verifying, packaging, and tagging a cowbell release.

## 1. Version and Changelog

Version is defined in one place: `__version__` in `cowbell.py` (verified: cowbell.py:63). Hatchling dynamically reads this during package build via `[tool.hatch.version]` (verified: pyproject.toml:7,27-28).

Ensure the release branch updates `__version__` and `CHANGELOG.md` with matching version headings (verified: CHANGELOG.md:3). The test suite enforces that the top changelog heading keeps pace with `__version__` (verified: tests/test_cowbell.py:1873-1883).

## 2. Build Artifacts

Build the distribution wheel and source distribution into `dist/`:

```bash
python3 -m build
```

To build only the source distribution:

```bash
python3 -m build --sdist
```

In offline environments or when hatchling is already installed locally, pass `--no-build-isolation`. Artifacts are generated under `dist/`:
- `dist/cowbell-0.3.4.tar.gz`
- `dist/cowbell-0.3.4-py3-none-any.whl`

## 3. Verify Before Publishing

Packaging tests ensure that the wheel includes only `cowbell.py` and `harnesses.toml` shared data, and that the sdist excludes test trees (verified: pyproject.toml:30-37; tests/test_packaging.py:10-24).

Run package tests:

```bash
python3 -m unittest tests/test_packaging.py
```

Perform an isolated clean-venv smoke check against the sdist artifact:

```bash
python3 -m venv /tmp/cowbell-check
/tmp/cowbell-check/bin/pip install dist/cowbell-0.3.4.tar.gz
/tmp/cowbell-check/bin/cowbell catalog
rm -rf /tmp/cowbell-check
```

## 4. Tag and Push

Pushing and tagging are maintainer actions. Tag the release commit and push to remote:

```bash
git tag v0.3.4
git push origin main --tags
```

## 5. Continuous Integration Gate

GitHub Actions executes the unit test suite on Ubuntu with Python 3.11 on every push and pull request (verified: .github/workflows/test.yml:8-15):

```bash
python3 -m unittest discover -s tests
```

The workflow run for the release commit and tag serves as the final validation gate before distribution.

## 6. PyPI Publication

If publishing to PyPI, upload the built artifacts using twine:

```bash
python3 -m twine upload dist/*
```

PyPI publication remains an optional maintainer decision outside the scope of this document. The repository currently omits `project.urls` metadata in `pyproject.toml` (verified: pyproject.toml:5-22) and treats repository clones and direct sdist installations as the primary distribution paths (verified: README.md:53-73).
