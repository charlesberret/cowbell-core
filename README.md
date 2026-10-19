# cowbell

Type `cowbell` in a directory to pick a coding agent for it: one already running there, a session to resume, or a new one.

cowbell is for people who run several coding-agent CLIs (Claude Code, Codex, Grok and similar) across many folders and want to see and reach them by place. The choices are **Resume** or **New Session**, with an **Active** census of who is already working here. Active is every coding agent whose working directory is this one or below it. You can see them. You cannot take them over from this list. Resume is the sessions cowbell can pick up again. New Session is the agents in your catalog that are installed and allowed here, most used here first.

```
  ~/code/projects/acme                         g widen to projects · 4 running

  ┌─ Active ──────────────────────────────────────────────────────────────┐
  │    api-claude             claude      idle                            │
  │    reviewer               grok        working  14s   in proj:docs     │
  └───────────────────────────────────────────────────────────────────────┘

  Resume
    1  notes-draft            oll-mid     2 days ago

  New Session
    2  claude                 Claude Code
    3  grok                   Grok CLI                           ! more reach than needed
    4  agy                    Antigravity (Gemini)
       + 9 more

  ⏎ open   n new with options   g widen   esc close
```

It is mouse-first: click or arrow to a row, Enter or the ⏎ button to open it, Esc to close. A digit jumps to its row, and every hint in the bottom bar is clickable. The list refreshes every two seconds. Off a terminal, or with `COWBELL_PLAIN=1`, it falls back to a typed-number prompt; `NO_COLOR` turns colour off.

In [herdr](https://github.com/herdrdev/herdr), the plugin [`herdr-cowbell`](https://github.com/charlesberret/herdr-cowbell) puts this same picker on `prefix+c` as a popup, and adds `adopt`, `stop` and `import-seats`. The plugin and this command read the same catalog and roster, so a session started in one resumes in the other.

## Install

cowbell is one Python file with no dependencies. It needs **Python 3.11 or newer**. macOS ships `/usr/bin/python3` at 3.9, which is too old; `brew install python` or `uv python install 3.12` is enough. It runs on macOS and Linux.

From a clone:

```bash
git clone https://github.com/charlesberret/cowbell-core.git
cd cowbell-core
./bin/cowbell --version
```

Expected output: `cowbell X.Y.Z`. To run it from any directory, link the launcher onto your PATH. The launcher follows symlinks and picks a Python 3.11 or newer for you:

```bash
mkdir -p "$HOME/.local/bin"
ln -s "$PWD/bin/cowbell" "$HOME/.local/bin/cowbell"
```

`$HOME/.local/bin` must be on your PATH. Then run `cowbell` in any project directory.

## Status

Pre-1.0 (0.3.x). The command line, the picker and the catalog format (`schema = 1`) may still change between releases; changes are listed in [CHANGELOG.md](CHANGELOG.md). Bug reports and focused pull requests are welcome.

## Where agents open

- **Inside a herdr pane**, starting or resuming opens a new herdr tab named for the session, and Active lists herdr's agents.
- **Anywhere else**, or with `COWBELL_MODE=here`, cowbell hands this terminal to the agent, `exec`, in the chosen directory. Quit the agent and you are back at your shell. Active lists herdr's agents when a herdr server is listening, plus agent CLIs found running in plain terminals by working directory. Those rows say where they run, `on ttys012`. Cowbell can't switch to another terminal window.
- **Resume** lists only sessions that can resume. Claude started outside herdr gets its session id up front, `session_id_flag`, so it can. Agents without such a flag are not listed.
- **Enter on New Session** opens the agent at once with an automatic name, `claude` or `claude-2`, and the default permissions. `[defaults] ask_name = true` asks for the name first. **`e` on a New Session row** opens a menu of that harness: description, models, default model, permissions, tools, provider, model cycle, and system prompt. A launcher script also lists its command. Empty fields stay on the menu. Pick a row to change that field. Esc inside a field cancels it. Esc on the menu returns to the list. `+` adds a harness, a herdr kind or a launcher script. `n` asks for agent, name, model, and permissions, then optional save-as, and starts.
- **Trust** appears only if a checker is configured and on PATH, and only as an exception: a dim `! more reach than needed` on a row the checker calls over-privileged. That is advisory and never stops a launch; blocked agents are left off.

Two hooks let cowbell use tools it does not own, both set in `[defaults]`:

- `trust_command` is a program asked `subject <path>`, `match <harness> <path>` and `badge <harness>`. Exit 4 refuses. Exit 3 warns and asks. If it is unset, or not on PATH, no trust marks appear at all.
- `seat_file` is a briefing file, default `SEAT.md`, found by walking up from the directory and handed to a harness through its `system_prompt_flag`.
- `session_history` set to `"on"` lets Resume read the stores the harnesses keep themselves, `~/.claude/projects` and `~/.grok/sessions`, so a directory shows every session it has seen, including sessions cowbell did not start. Only ids, times and titles are read. Transcript bodies never are. `"all"` also lists agents that a session dispatched rather than a person chose. For a place with `unix_user`, discovery runs as that launch user and reads that user's stores, so Resume never offers a session the launched process cannot open. Default `"off"`.

## Catalog, places, state

The catalog is `~/.config/cowbell/harnesses.toml`, or the same file under `COWBELL_CONFIG_DIR` or `$XDG_CONFIG_HOME/cowbell`, seeded from [`harnesses.toml`](harnesses.toml) on first run with the standard agents, shown only when installed. An existing copy that is missing `droid` or `devin` is filled once from the seed when that binary is on PATH. A later delete stays deleted. Add your own launchers, models and permission presets there. The roster is `~/.local/state/cowbell/roster.json`, or the same file under `COWBELL_STATE_DIR` or `$XDG_STATE_HOME/cowbell`. Both carry `schema = 1`. A cowbell that finds a newer schema reads the file but will not overwrite it. Versions up to 0.3 kept both in herdr's plugin directories. The first run copies them over once. A harness may set `provider`, a model cycle, and a `system_prompt`, and cowbell passes them on the launch line when the row sets the matching `provider_flag`, `cycle_flag`, and `system_prompt_flag`.

Permission presets are called lanes: `green` reads and plans, `yellow` allows edits, `red` bypasses approvals. Each agent kind maps the three names to its own CLI flags under `[lanes.<kind>]` in the catalog, and `--lane` picks one at launch.

A directory can have its own rules:

```toml
[defaults]
untitled_place = "lobby"          # a session started from ~ opens here instead

[places.lobby]
cwd = "~/code/projects/acme"
workspace_label = "lobby"         # herdr workspace its sessions open in (created if missing)
allow_harness = ["lobby", "claude", "grok"]
default_harness = "lobby"         # guest door; `new --place lobby` with no --harness
lane = "yellow"                   # default permission preset for this place
```

Anything started at or below `cwd` opens in that workspace. New lists only the allowed agents. Resume omits roster rows whose harness is not allowed, so a cold `oll-memo` in that cwd is not a guest. `cowbell new --place lobby` with no `--harness` uses `default_harness`. Claude and Grok stay allowed there for your own work; the place keeps guests to the `lobby` harness. `[places.*]` are walls, not a roster of project workspaces. When a pane already has this directory on a grouped `proj:` line, the session opens there.

### A place that drops to another unix account

`unix_user` is an account name, `getpwnam`. Create that account on your own machine, give it a directory it can write, and add a wrapper harness plus the place to `~/.config/cowbell/harnesses.toml`:

```toml
[[harness]]
id = "lab"
kind = "lab"
title = "Lab shell"
command = "/bin/bash"

[places.lab]
cwd = "~/lab"
allow_harness = ["lab"]
default_harness = "lab"
unix_user = "lab"
require_uid = true
# nono_profile = "~/.config/nono/lab.json"   # optional; omit if you do not use nono
```

`cowbell new --harness claude --place lab` refuses to start, because `claude` is not in `allow_harness`. `cowbell new --place lab` starts the bash wrapper.

When `unix_user` is set and the process is not already that user, cowbell prefixes `agent-run <user> --` if `agent-run` is on PATH. That helper is not part of cowbell. If it is absent, cowbell uses `sudo -u <user> --` instead. Session-history discovery uses the same identity boundary and returns only derived Resume metadata to the caller. You can also leave `unix_user` unset and drop privileges yourself with `sudo -u lab -- cowbell new --place lab`. `require_uid = true` with no `unix_user` refuses to start. `nono_profile`, when set, wraps the command as `nono run --silent --profile <path> --allow-cwd --` inside the uid drop, and `nono` must be on PATH.

## Commands

```
cowbell                      the picker (on a terminal); piped, the long registry
cowbell --version            cowbell X.Y.Z
cowbell status               long registry: live · cold · absent, session ids, trust
cowbell claude               focus a claude running here, else resume one, else start one
cowbell new --harness claude --model claude-opus-5 --lane green --allow Read,Grep
cowbell new --harness grok --place lobby
cowbell enter <name>         focus if live, else resume
cowbell list [--all]
cowbell catalog              every harness: kind, egress, installed, trust badge
cowbell catalog --check      fail named malformed rows; warn on declared flags missing from a CLI's help
cowbell reconcile [--dry-run]   pane borders that claim a harness, matched to the agent Herdr detects
```

`bin/cowbell` picks a python ≥ 3.11, for tomllib, and follows symlinks. macOS `/usr/bin/python3` is 3.9 and must not run this. Stdlib only.

## Development

```bash
python3 -m unittest discover -s tests -v
```

`tests/test_pty.py` drives the menu, the prompt and the whole picker in a real pseudo-terminal. The code keeps two seams: `ctx.live`, what is running, and `ctx.launch`, where an agent opens. Every `herdr` CLI call lives in the `# --- herdr adapter` section of `cowbell.py`, and a test enforces it.

## License

MIT. See [LICENSE](LICENSE).
