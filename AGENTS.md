# cowbell — agent ingress

Orientation for any agent working in this tree. One screen.

## What this is

`cowbell` is a terminal program that picks a coding-agent CLI for the directory
you are in: a running agent to reach (the **Active** census), a session to
**Resume**, or a **New Session** raised with chosen model, effort, permissions,
tools and extra directories — the exact command is shown before it runs
(verified: `cowbell.py` `picker_choices()`, `build_registry()`,
`launch_sheet()`). It is the engine behind the `herdr-cowbell` plugin
(verified: `cowbell.py:37`). Single file, Python ≥ 3.11, stdlib only
(verified: `cowbell.py` is the only module — `wc -l cowbell.py`;
`pyproject.toml` `requires-python = ">=3.11"` (:10), `dependencies = []` (:14);
import block `cowbell.py:41-60`, all stdlib). See `README.md` for the
user-facing picture.

## Map

| Path | What it holds |
|------|----------------|
| `cowbell.py` | The whole program, organized into `# --- <name>` sections (catalog, roster, registry, launch, hosts, herdr adapter, tui, main) (verified: `grep -n "^# ---" cowbell.py`). |
| `harnesses.toml` | Seed catalog: the `[[harness]]` rows copied to the user config dir on first run, plus `[lanes.*]` permission presets and inline docs for every key (verified: `harnesses.toml` seed rows and comments; `cowbell.py` `catalog_path()`, `seed_path()`). |
| `bin/cowbell` | Shell launcher: follows symlinks, picks a Python ≥ 3.11, execs `cowbell.py` (verified: `bin/cowbell`). |
| `tests/` | `test_cowbell.py` (main unittest suite), `test_pty.py` (real-PTY menu/picker tests), `test_packaging.py` (PyPI surface), `test_errors_catalog.py` (error message catalog coverage), `test_seed_catalog.py` (seed catalog parse/check/argv tests) (verified: `ls tests/`). |
| `docs/` | `architecture.md` (module map, every line cited), `README.md` (doc index with verified/draft verdicts), `debug-trace.md` (startup trace runbook), `errors.md` (user-facing error catalog), `catalog-fields.md` (field reference table), decision records (verified: `ls docs/`). |
| `README.md` | User documentation: install, picker keys, catalog/places reference, commands (verified: `README.md` headings). |
| `CHANGELOG.md` | Release notes; Unreleased section is the running diff vs the last cut (verified: `CHANGELOG.md` headings — Unreleased, then 0.3.2 / 0.3.1 / 0.3.0 / 0.2.0). |

`docs/architecture.md` is the deep map — start there before editing a section
of `cowbell.py` you have not read.

## Write-box

Work inside this tree only. Do not commit, push, switch branches, or edit files
outside the repo unless the task explicitly asks. `.local/` and other gitignored
local paths are private to each environment — leave them alone.

## Run the tests

```bash
python3 -m unittest discover -s tests    # what CI runs (Python 3.11)
python3 -m pytest tests/ -q              # also works; suite takes ~50 s
```

(verified: `python3 -m unittest discover -s tests` → "Ran 394 tests", "OK";
`.github/workflows/test.yml:15` runs the same command; `pytest tests/ -q`
passes — pytest 9.2.0, all unittest.TestCase so either runner works)

CI: `.github/workflows/test.yml` (ubuntu, Python 3.11, `unittest discover`)
(verified: `.github/workflows/test.yml:9,14-15`).
The suite stubs the herdr binary via `HERDR_BIN_PATH`, so tests are safe to run
with a live herdr server on the machine — a failure of `ZSuiteSeam` means a
test reached the real binary (verified: `tests/test_cowbell.py:87-97`
`setUpModule` stub, `:4839` `class ZSuiteSeam`).

## Invariants the suite enforces — do not break these

- **Stdlib only.** No new imports outside the standard library; `tomllib`
  requires Python ≥ 3.11 (verified: `cowbell.py:41-60` import block, all
  stdlib, `tomllib` guarded at :57-60; `pyproject.toml` `dependencies = []`
  (:14), `requires-python = ">=3.11"` (:10); `bin/cowbell` probes for 3.11).
- **herdr adapter.** Every `herdr(` call lives inside the `# --- herdr adapter`
  section of `cowbell.py` (`test_every_herdr_call_is_inside_the_adapter`
  greps for violations). New herdr interaction goes in that section
  (verified: `cowbell.py:2784` adapter banner;
  `tests/test_cowbell.py:1137` the test).
- **Catalog writes.** Edit `harnesses.toml` through the splice writer
  (`harness_insert`/`harness_replace`/`harness_delete`), never a full TOML
  dump — comments and ordering must survive (verified: `cowbell.py`
  `harness_insert` :4410, `harness_replace` :4427, `harness_delete` :4439 in
  the `# --- catalog writer` section :4199).
- **Schema.** Catalog and roster carry `schema = 1`; files with a newer schema
  are read, never overwritten (verified: `cowbell.py` `SCHEMA = 1` :248,
  `check_writable()` :301-304 raises `SchemaError`; defaults at :762, :921;
  `harnesses.toml` `schema = 1`).
- **Packaging.** The wheel ships only `cowbell.py` (+ `harnesses.toml` as
  shared data); the sdist excludes `tests/` (`tests/test_packaging.py`)
  (verified: `pyproject.toml` wheel `only-include = ["cowbell.py"]` (:31),
  shared-data `"harnesses.toml"` (:33-34), sdist `only-include` (:37) has no
  `tests/`).

## Good first reads

1. `README.md` — the product as a user sees it.
2. `docs/architecture.md` — where each behavior lives in `cowbell.py`.
3. `harnesses.toml` — the catalog schema by example.
4. The `# --- main` section of `cowbell.py` — the command surface.
