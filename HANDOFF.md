# HANDOFF — cowbell

Board: Lab / Cowbell — https://linear.app/isruna/project/cowbell-77c7779d8e93 (protocol: document "Cowbell — agent handoff")
Milestone: Split (Now)
Locked: none

## 2026-09-15 — Guest wall (agent-lobby)

Place `lobby` now admits harness `lobby` first (`default_harness`). Resume omits roster rows whose harness is not in `allow_harness` (cold `oll-memo` is not a guest). `cowbell new --place lobby` with no `--harness` uses the default. Claude/Grok remain allowed as house labor. Tests in `tests/test_cowbell.py` Places. House constitution `~/.config/cowbell/harnesses.toml`.

**This file:** `/Users/example/code/cowbell/HANDOFF.md`
**What:** the cowbell core and CLI. The herdr plugin is `~/code/herdr-cowbell`.
**Launcher:** `~/code/bin/cowbell` (synced) execs `bin/cowbell` here.
**Authoritative `cowbell.py`:** this tree, from LAB-250 on. `herdr-cowbell` is a thin skin with a vendored copy of this core (LAB-252); after a core change, run `scripts/vendor-core` there.

Release notes before the split (0.2.0, 0.3.0, LAB-247, LAB-248, LAB-262, LAB-249) are in `herdr-cowbell/HANDOFF.md` and in this tree's git history.

## 2026-09-15 — LAB-250: the core tree

- Cloned from `herdr-cowbell` with full history and tags (`v0.2.0`, `v0.3.0`); origin remote removed (local-only). See README § Provenance.
- Removed from the core, kept in the plugin: `herdr-plugin.toml`, `cmd_open` / `invocation_ctx` / `picker_open_args`, the keybinding installer, `adopt`, `stop`, `import-seats`, the picker's hidden `a` key. `write_atomic` stays (the harness writer, LAB-254, needs it).
- `PLUGIN_ID` remains only to find 0.1–0.3 config and state in herdr's plugin dirs for the one-time migration.
- The house launcher now points here. From a plain `cowbell` you lose `adopt`, `stop`, `import-seats`, `keys` and `open`; until LAB-252 they still run from `~/code/herdr-cowbell/bin/cowbell`, and `prefix+c` is unaffected.

## 2026-09-15 — LAB-272: PyPI packaging (not uploaded)

- `pyproject.toml` (hatchling): name `cowbell`, version from `__version__`, python ≥ 3.11, no dependencies, console script `cowbell = cowbell:cli`; the seed ships as `share/cowbell/harnesses.toml`, found by `seed_path()` under `sys.prefix`. `uv build` → `dist/` (ignored).
- Upload is the patron's (LAB-251): `uv publish --token …` from this tree.

## Plan

On Linear (above). Update the `Locked:` line when you claim an issue that touches `cowbell.py`.
