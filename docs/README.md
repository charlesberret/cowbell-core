# Documentation index — cowbell

Every Markdown document in the tree, what it is for, and whether a reader can
trust it. Verdicts:

- **VERIFIED** — the named claim was checked against a file or command in this
  tree. The check is cited.
- **DRAFT** — the file asserts state that cannot be checked from the tree
  alone.

Scope: top-level `*.md` and `docs/*`. Gitignored local paths are not part of the published tree.

## Top level

| File | What it is | Verdict |
|------|------------|---------|
| `README.md` | User-facing intro, install, the picker's keys, catalog/places/rules reference, command list. | **VERIFIED** — version "pre-1.0 (0.3.x)" matches `__version__ = "0.3.3"` (`cowbell.py:63`); "one Python file with no required dependencies" matches `pyproject.toml` (`dependencies = []`, wheel `only-include = ["cowbell.py"]`); the dev command `python3 -m unittest discover -s tests` is what `.github/workflows/test.yml` runs; every command in the Commands block maps to a `main()` dispatch branch (`cowbell.py`). |
| `CHANGELOG.md` | Release notes: 0.3.3, then 0.3.2 / 0.3.1 / 0.3.0 / 0.2.0. | **VERIFIED** — release heading `0.3.3` corresponds to in-tree features: icon font (`cowbell.py` `cmd_font_install`, `LOBE_FONT_*`), requires/check (`harnesses.toml` comments; `cowbell.py` `run_requires`/`ensure_accepted`), `COWBELL_DEBUG` trace (`cowbell.py` `Trace`), save-as (`cowbell.py` `sheet_save_as`), error catalog (`docs/errors.md`), and seed catalog tests (`tests/test_seed_catalog.py`). |
| `AGENTS.md` | Runtime-neutral ingress for a coding agent: what the project is, doc map, write-box, test command, invariants. | **VERIFIED** — it is an index of this tree; each pointer and command in it is checked against the files it names (`.github/workflows/test.yml`, `cowbell.py` sections, `tests/`). |

## docs/

| File | What it is | Verdict |
|------|------------|---------|
| `docs/README.md` | This index. | **VERIFIED** — self-describing; every row's citation is itself the check. |
| `docs/architecture.md` | Module map: entry points, host seams, registry, picker, catalog, roster, history, resume, launch pipeline, confinement, trust hook, herdr adapter, fonts, tests. | **VERIFIED** — every factual line carries its own `(verified: …)` tag citing a function, file, or command; spot-check any citation to re-verify. |
| `docs/decision-2026-11-12-requires-check-join.md` | Decision record: history join of the `requires-check` line into the icon-font line, with addendum on sync with origin. | **VERIFIED** — `git log --oneline` shows `cb790ca Merge branch 'requires-check'` containing `12dd4d5`, and both named font commits are ancestors; addendum records the subsequent sync merge (`327769f`/`d110a53`) with origin/main bringing behind count to 0. |
| `docs/debug-trace.md` | Runbook for opt-in startup timing trace: flags (`--debug`, `COWBELL_DEBUG=1`), precedence, event reference, worked delay example, and safety guarantees. | **VERIFIED** — all event types, precedence rules, and arguments cited to `cowbell.py`. |
| `docs/errors.md` | Catalog of user-facing error templates across CLI, catalog loader, and launch paths with causes and suggested fixes. | **VERIFIED** — enforced by `tests/test_errors_catalog.py`. |
| `docs/catalog-fields.md` | Consolidated field reference for `[[harness]]` rows, `[lanes.*]` presets, and `[defaults]`. | **VERIFIED** — every key cited to `cowbell.py` and `harnesses.toml`. |

## Doc gaps

What a stranger still cannot learn from this tree:

- **The herdr contract.** Which JSON `herdr agent start`/`snapshot` return, and what `agent_session` means, lives in the herdr project. This tree only shows where the calls are made (the `# --- herdr adapter` section of `cowbell.py`).
- **External helpers.** `agent-run`, `nono`, and `harness-trust` are named by the catalog and README but are not in this repo; their install and full contract are undocumentated here.
- **How to contribute.** README says "bug reports and focused pull requests are welcome"; there is no CONTRIBUTING.md, style guide, or release-process doc.
- **The plugin relationship.** `herdr-cowbell` is linked out from README; nothing in-tree describes how the vendored copy relates to releases here.
- **Internal commands.** `cowbell identity stamp|sync` and the private `_history` worker appear only in the module docstring and `main()` dispatch, not in README's Commands block.
- **Stale docstring.** `cowbell.py`'s module docstring says "fzf is optional" but no code path uses fzf (`grep -n fzf cowbell.py` → only that line).
