# HANDOFF — herdmark

**This file:** `/Users/example/code/herdmark-core/HANDOFF.md`
**Plugin:** linked in herdr as `herdmark` (`prefix+c` → registry picker). One commit so far: `799bd7c Raise herdmark`.

## Why this is now urgent (2026-09-12)

Charles has been launching herdr seats **through agent-deck inside a herdr pane** only because agent-deck ties a session to a cwd. That nesting makes the seat **invisible to herdr's agent list**: herdr detects a Claude pane by its foreground process and its `✳` terminal title, and inside agent-deck the foreground process is `agent-deck` and the title is agent-deck's tmux `set-titles-string` (`[charles] herdr`). Verified on pane `wK:pC` this sitting: `pane.report_agent` / `report_agent_session` over the socket answer `ok` and change nothing; passing the inner title through tmux did not propagate. So no deck-launched seat will ever show in the sidebar the round just redesigned (`~/code/notes/braintrust/rounds/2026-09-12-herdr-sidebar-two-panels/synthesis.md` § Taken).

**Finishing herdmark removes the only reason agent-deck was inside herdr:** raise a sitting in a herdr tab with the cwd, model, lane and tools chosen on purpose — natively, so herdr detects it and the bt-reporter badges it (`✼ ✳ ϟ`).

## What "finished" means for that use

- `herdmark open` from any pane: pick a harness from `harnesses.toml` for **this directory**, or an established one to attach to, and it lands in a **new herdr tab in this workspace with that cwd** (no tmux, no deck).
- The tab is named the sitting (the seat / office name), not the terminal title — `tab` is the sidebar's identity token.
- Adopt (`herdmark adopt`) already exists for the reverse direction.
- Out of scope: quota, sidebar rows (those are `bt-reporter` / config).

## 2026-09-12 — raise path works; popup is a first pass

Live probe: `herdmark new --harness grok --name herdmark-probe` created tab `w1A:t6` labelled **herdmark-probe**, herdr detected grok idle at this cwd; probe tab closed. `prefix+c` smoke-tested the same day — it works, and it is clunky.

- Tab label = sitting (`--name`); never pane `--title` / rename.
- Wait for a single foreground shell before `agent start` (fresh tabs were `agent_pane_busy`).
- Grok lanes verified against `grok --help`; `--agent <sitting-head>` when `~/.grok/agents/<head>.md` exists.

`herdr-seats` still on `prefix+shift+s`. Wrappers still `pane run`. Constitution sync / fleet / marquee: later.

## Related

- Sidebar plate and reporter: `…/rounds/2026-09-12-herdr-sidebar-two-panels/variants/F4/` (live) and `variants/B/plugin/bt-reporter.py`.
- Must-nots inherited: never `--title` a pane as identity; never nest agent-deck in herdr.
