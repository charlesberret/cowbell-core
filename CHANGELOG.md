# Changelog

## Unreleased (0.3.2)

- A bare pane border that is not the current tab is a stale sitting: `reconcile_label` rewrites it, and `identity sync` restamps `sitting · kind` on `pane.agent_detected` (`24427b4`).
- A sitting opens on a grouped `proj:` workspace when a pane there already has this directory, instead of the caller's line (`c4a74d5`, LAB-938).
- Harness rows can carry `provider`, a model cycle, and an inline `system_prompt`; `build_argv` emits them when the row sets the matching flags (`851e8b9`), and picker `e` edits the three fields (`30af0c5`, `cde787b`, `1405c7b`).
- Picker `e` on a wrapper harness lists every launch control (`5ca7b0b`).
- `cowbell new --yes` is documented as accepted and unused (`32e5b03`, LAB-635); `reconcile --dry-run` with no herdr binary names the skip (`bc89a94`, LAB-636).
- Agent-list `$glyph` restamps on `pane.agent_detected` / `pane.exited` and from detector kind, so a tab that swaps harnesses does not keep the old mark (`fab919d`, `ff95fda`).
- An existing catalog is filled once with `droid` and `devin` when on PATH (`d3728e1`); the seed carries a commented `[places.lab]` example (`0fd3a02`); session-history discovery runs as the launch uid for `unix_user` places (`840b943`, LAB-525).
- Codex lane flags verified against Codex 0.160.1 (`1f6fc4b`, LAB-260).
- Tests: Lobe glyph table and identity tokens pinned (`d129024`, `e04124c`), sdist no longer ships `tests/` (`02de7f7`), host-dependent premises pinned by lookup and mock (`caa51d0`, `3207d43`).

## 0.3.1 — 2026-09-30

- `[places.*]` walls: per-directory `allow_harness`, `default_harness`, `lane`, and `unix_user`/`nono` confinement (LAB-262, LAB-357).
- Resume reads each harness's own session store (`~/.claude/projects`, `~/.grok/sessions`), ids and titles only (LAB-355).
- Picker `e` sets this sitting's model, permissions and tools without rewriting the catalog (LAB-656).
- Advisory over-privilege marks via `trust_command`; blocked agents are left off.

## 0.3.0 — 2026-09-13

- Standalone: bare `cowbell` on a terminal is the picker; `exec` here mode needs no herdr (LAB-250, LAB-249 host seams).
- Config and state moved to `~/.config/cowbell` and `~/.local/state/cowbell` with `schema = 1` (LAB-247, LAB-248).
- Mouse-first picker: click, arrows, digits, clickable hint bar, 2 s refresh, `COWBELL_PLAIN` fallback.
- `adopt` in the core (LAB-293); Claude gets `session_id_flag` so terminal-started sessions resume.

## 0.2.0 — 2026-09-13

- The herdr popup (`prefix+c`) is the product: Running here / Resume / Start new, roster, seed catalog of standard agents.
