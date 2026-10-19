# Changelog

## Unreleased (0.3.2)

- A bare pane border that is not the current tab is a stale sitting: `reconcile_label` rewrites it, and `identity sync` restamps `sitting · kind` on `pane.agent_detected`.
- A sitting opens on a grouped `proj:` workspace when a pane there already has this directory, instead of the caller's line.
- Harness rows can carry `provider`, a model cycle, and an inline `system_prompt`; `build_argv` emits them when the row sets the matching flags, and picker `e` edits the three fields.
- Picker `e` on a wrapper harness lists every launch control.
- `cowbell new --yes` is documented as accepted and unused; `reconcile --dry-run` with no herdr binary names the skip.
- Agent-list `$glyph` restamps on `pane.agent_detected` / `pane.exited` and from detector kind, so a tab that swaps harnesses does not keep the old mark.
- An existing catalog is filled once with `droid` and `devin` when on PATH; the seed carries a commented `[places.lab]` example; session-history discovery runs as the launch uid for `unix_user` places.
- Codex lane flags verified against Codex 0.160.1.
- Tests: Lobe glyph table and identity tokens pinned, sdist no longer ships `tests/`, host-dependent premises pinned by lookup and mock.

## 0.3.1 — 2026-09-30

- `[places.*]` walls: per-directory `allow_harness`, `default_harness`, `lane`, and `unix_user`/`nono` confinement.
- Resume reads each harness's own session store (`~/.claude/projects`, `~/.grok/sessions`), ids and titles only.
- Picker `e` sets this sitting's model, permissions and tools without rewriting the catalog.
- Advisory over-privilege marks via `trust_command`; blocked agents are left off.

## 0.3.0 — 2026-09-13

- Split from the herdr plugin `herdr-cowbell` into its own command.
- Standalone: bare `cowbell` on a terminal is the picker; `exec` here mode needs no herdr.
- Config and state moved to `~/.config/cowbell` and `~/.local/state/cowbell` with `schema = 1`.
- Mouse-first picker: click, arrows, digits, clickable hint bar, 2 s refresh, `COWBELL_PLAIN` fallback.
- `adopt` in the core; Claude gets `session_id_flag` so terminal-started sessions resume.

## 0.2.0 — 2026-09-13

- The herdr popup (`prefix+c`) is the product: Running here / Resume / Start new, roster, seed catalog of standard agents.
