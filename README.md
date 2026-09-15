# cowbell

Type `cowbell` in this directory.

cowbell picks an agent for the directory you are in: **running here**, **resume**, or
**start new**. Running here is every coding agent whose working directory is this one
or below it. Resume is the sessions cowbell can pick up again. Start new is the agents
in your catalog that are installed and allowed here, most used here first.

```
  ~/code/notes/nomogenesis            g widen to metawork · 4 running

  Running here
    1  nomogenesis-claude     claude      idle
    2  philologist            grok        working  14s   in sys:clubhouse

  Resume
    3  kimi-ballots           oll-mid     2 days ago

  Start new
    4  claude                 Claude Code
    5  grok                   Grok CLI                           ! asks first
    6  agy                    Antigravity (Gemini)
       + 9 more

  ⏎ open   n new with options   g widen   esc close
```

It is mouse-first: click or arrow to a row, Enter (or the ⏎ button) to open it, Esc
to close. A digit jumps to its row, and every hint in the bottom bar is clickable. The
list refreshes every two seconds. Off a terminal, or with `COWBELL_PLAIN=1`, it falls
back to a typed-number prompt; `NO_COLOR` turns colour off.

**In herdr:** the plugin [`herdr-cowbell`](../herdr-cowbell) puts this same picker on
`prefix+c` as a popup, and adds `adopt`, `stop` and `import-seats`. The plugin and this
command read the same catalog and roster, so a session started in one resumes in the other.

## Where agents open

- **Inside a herdr pane**, starting or resuming opens a new herdr tab named for the
  sitting, and Running here lists herdr's agents.
- **Anywhere else** (or with `COWBELL_MODE=here`), cowbell hands this terminal to the
  agent (`exec`) in the chosen directory; quit the agent and you are back at your shell.
  Running here lists herdr's agents when a herdr server is listening, plus agent CLIs
  found running in plain terminals by working directory. Those rows say where they run
  (`on ttys012`); cowbell can't switch to another terminal window.
- **Resume** lists only sessions that can resume. Claude started outside herdr gets its
  session id up front (`session_id_flag`) so it can; agents without such a flag are not
  listed.
- **Enter on Start new** opens the agent at once with an automatic name (`claude`,
  `claude-2`) and the default permissions; `[defaults] ask_name = true` asks for the
  name first. `n` asks for agent, name, model, and permissions.
- **Trust** appears only if `agent-deck-trust` is on PATH, and only as an exception:
  `! asks first` on an over-privileged row. Blocked agents are left off.

## Catalog, places, state

The catalog is `~/.config/cowbell/harnesses.toml` (`COWBELL_CONFIG_DIR`, or
`$XDG_CONFIG_HOME/cowbell`), seeded from [`harnesses.toml`](harnesses.toml) on first
run: the standard agents, shown only when installed. Add your own launchers, models and
permission presets there. The roster is `~/.local/state/cowbell/roster.json`
(`COWBELL_STATE_DIR`, or `$XDG_STATE_HOME/cowbell`). Both carry `schema = 1`; a cowbell
that finds a newer schema reads the file but will not overwrite it. Versions up to 0.3
kept both in herdr's plugin directories; the first run copies them over once.

A directory can have its own rules:

```toml
[defaults]
untitled_place = "lobby"          # a sitting started from ~ opens here instead

[places.lobby]
cwd = "~/code/agent-lobby"
workspace_label = "lobby"         # herdr workspace its sittings open in (created if missing)
allow_harness = ["claude", "grok"]
lane = "yellow"
```

Anything started at or below `cwd` opens in that workspace, Start new lists only the
allowed agents, and `cowbell new --place lobby` targets it from anywhere.

## Commands

```
cowbell                      the picker (on a terminal); piped, the long registry
cowbell --version            cowbell X.Y.Z
cowbell status               long registry: live · cold · absent, session ids, trust
cowbell claude               focus a claude running here, else resume one, else start one
cowbell new --harness claude --model claude-opus-5 --lane green --allow Read,Grep --yes
cowbell new --harness grok --place lobby
cowbell enter <name>         focus if live, else resume
cowbell list [--all]
cowbell catalog              every harness: kind, egress, installed, trust badge
```

`bin/cowbell` picks a python ≥ 3.11 (tomllib) and follows symlinks; macOS
`/usr/bin/python3` is 3.9 and must not run this. Stdlib only.

## Development

```bash
python3 -m unittest discover -s tests -v
```

`tests/test_pty.py` drives the menu, the prompt and the whole picker in a real
pseudo-terminal. The code keeps two seams: `ctx.live` (what is running) and
`ctx.launch` (where an agent opens). Every `herdr` CLI call lives in the
`# --- herdr adapter` section of `cowbell.py`, and a test enforces it.

## Provenance

This tree was cloned from `~/code/herdr-cowbell` on 2026-09-15, with its
full history and tags. It carries tag `v0.3.0` (`84d223b`) and the commits after it:
`941ed40` (plan moves to Linear), `5ce4be2` (`--version`, LAB-247), `f67a8b3` (XDG
config and state, LAB-248), `f095314` (places, LAB-262), `70fc3e2` (host seams,
LAB-249). The split commit removed what belongs to the herdr plugin: the manifest, the
popup entry (`open`), the `prefix+c` keybinding installer, `adopt`, `stop` and
`import-seats`.
