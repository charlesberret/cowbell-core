# cowbell

Type `cowbell` in a directory to launch or re-launch a coding agent there with the settings you choose: model, effort, permissions, tools, other directories. You see the exact command before it runs. The same list shows who is already working here and which sessions can resume.

## Install

```bash
pipx install git+https://github.com/charlesberret/cowbell-core
# pipx install cowbell    # after the PyPI name cowbell is reserved
```

**Requires Python 3.11 or newer.** macOS ships `/usr/bin/python3` at 3.9, which is too old; use pipx (it picks a suitable Python), `brew install python`, or `uv python install 3.12`. Runs on macOS and Linux.

MIT licensed — see [LICENSE](LICENSE).

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

  ⏎ open   n new   + add   a adopt   g widen   o shape   r rename   esc
```

cowbell is for people who run several coding-agent CLIs (Claude Code, Codex, Grok and similar) across many folders and want to see and reach them by place. The choices are **Resume** or **New Session**, with an **Active** census of who is already working here. Active is every coding agent whose working directory is this one or below it. You can see them. You cannot take them over from this list. Resume is the sessions cowbell can pick up again. New Session is the agents in your catalog that are installed and allowed here, most used here first.

`o` on a row, or `n`, opens the **launch sheet** for that agent: every setting it takes, the account it runs as, and the command that will run. Here it is at the width of the herdr popup, with model, effort and permissions changed from the defaults:

```
  api  claude · Claude Code  new tab in ~/api

  ▶  start
     name           api
     model          claude-opus-5
     effort         high
     permissions    green
     tools allow    all
     tools deny     none
     also in        none
     seat file      none
     runs as        you

  $ claude --model claude-opus-5 --effort high
    --permission-mode plan

  ⏎ start   d defaults   a save as   esc cancel
```

It is mouse-first: click or arrow to a row, Enter or the ⏎ button to open it, Esc to close. A digit jumps to its row, and every hint in the bottom bar is clickable. The list refreshes every two seconds. Off a terminal, or with `COWBELL_PLAIN=1`, it falls back to a typed-number prompt; `NO_COLOR` turns colour off.

In [herdr](https://github.com/herdrdev/herdr), the plugin [`herdr-cowbell`](https://github.com/charlesberret/herdr-cowbell) puts this same picker on `prefix+c` as a popup, and adds `adopt`, `stop` and `import-seats`. The plugin and this command read the same catalog and roster, so a session started in one resumes in the other.

## Status

Pre-1.0 (0.3.x). The command line, the picker and the catalog format (`schema = 1`) may still change between releases; changes are listed in [CHANGELOG.md](CHANGELOG.md). Bug reports and focused pull requests are welcome.

## Where agents open

- **Inside a herdr pane**, starting or resuming opens a new herdr tab named for the session, and Active lists herdr's agents.
- **Anywhere else**, or with `COWBELL_MODE=here`, cowbell hands this terminal to the agent, `exec`, in the chosen directory. Quit the agent and you are back at your shell. Active lists herdr's agents when a herdr server is listening, plus agent CLIs found running in plain terminals by working directory. Those rows say where they run, `on ttys012`. Cowbell can't switch to another terminal window.
- **Resume** lists only sessions that can resume. Claude started outside herdr gets its session id up front, `session_id_flag`, so it can. Agents without such a flag are not listed. Resume shows the harness's current session title; a herdr tab that differs is the location. When several sessions share a title, the harness title keeps the bare name and the others gain a short id tail. `cowbell rename` pins a name.
- **Enter on New Session** opens the agent at once with an automatic name, `claude` or `claude-2`, and the default permissions. `[defaults] ask_name = true` asks for the name first. **`e` on a New Session row** opens a menu of that harness. The first line is its name. Then description, models, default model, permissions, tools, provider, model cycle, and system prompt. A field with a known set of values offers those, plus none, and a line to type another. A launcher script also lists its command. Empty fields stay on the menu. Pick a row to change that field. Esc inside a field cancels it. Esc on the menu returns to the list. `+` adds a harness, a herdr kind or a launcher script.
- **`n`** asks for the agent, then opens its **launch sheet**: one screen with start at the top, then every setting that harness takes (name, model, effort, permissions, tools, other directories it may work in, seat file) and the account it runs as, then the exact command that will run. A setting left at the harness default is dim; one you changed is bright. Enter on a setting changes it, `s` or Enter on start launches, `d` puts every setting back to the default, Esc cancels. Starting changes this launch only. `a` saves what the sheet shows as a new harness instead, with its own New Session row and `cowbell <id>`: a copy of this agent with the sheet's model, effort, permissions and tools as its defaults. The sheet stays open, and nothing launches until you start. If you start from `n` without saving, `n` offers to save afterwards. A resume sheet has no `a`, because a session is not a shape. **`o` on a New Session row** opens that harness's sheet straight away, on the settings it was last started with in this directory (else its defaults); `d` there means the harness defaults. **`o` on a Resume row** opens the sheet over that session as it was recorded, so you can resume it with another model, effort, permissions or tools; `d` puts the recording back, and the roster keeps what you resumed with. New Session lists as many harnesses as the window can hold, and ten when the height is unknown. Active and Resume show five, then a more row.
- **Trust** appears only if a checker is configured and on PATH, and only as an exception: a dim `! more reach than needed` on a row the checker calls over-privileged. That is advisory and never stops a launch; blocked agents are left off.

Two hooks let cowbell use tools it does not own, both set in `[defaults]`:

- `trust_command` is a program asked `subject <path>`, `match <harness> <path>` and `badge <harness>`. Exit 4 refuses. Exit 3 warns and asks. If it is unset, or not on PATH, no trust marks appear at all.
- `seat_file` is a briefing file, default `SEAT.md`, found by walking up from the directory and handed to a harness through its `system_prompt_flag`.
- `session_history` set to `"on"` lets Resume read the stores the harnesses keep themselves, `~/.claude/projects` and `~/.grok/sessions`, so a directory shows every session it has seen, including sessions cowbell did not start. Only ids, times and titles are read. Transcript bodies never are. `"all"` also lists agents that a session dispatched rather than a person chose. For a place with `unix_user`, discovery runs as that launch user and reads that user's stores, so Resume never offers a session the launched process cannot open. Default `"off"`.

## Catalog, places, state

The catalog is `~/.config/cowbell/harnesses.toml`, or the same file under `COWBELL_CONFIG_DIR` or `$XDG_CONFIG_HOME/cowbell`, seeded from [`harnesses.toml`](harnesses.toml) on first run with the standard agents, shown only when installed. An existing copy that is missing `droid` or `devin` is filled once from the seed when that binary is on PATH. A later delete stays deleted. Add your own launchers, models and permission presets there. The roster is `~/.local/state/cowbell/roster.json`, or the same file under `COWBELL_STATE_DIR` or `$XDG_STATE_HOME/cowbell`. Both carry `schema = 1`. A cowbell that finds a newer schema reads the file but will not overwrite it. Versions up to 0.3 kept both in herdr's plugin directories. The first run copies them over once. A harness may set `provider`, a model cycle, and a `system_prompt`, and cowbell passes them on the launch line when the row sets the matching `provider_flag`, `cycle_flag`, and `system_prompt_flag`. Effort works the same way: `effort_flag` is how the CLI takes a reasoning level (`["--effort"]` for claude, `["--thinking"]` for pi and omp, `["-c", "model_reasoning_effort={}"]` for codex, where `{}` is the level), `efforts` lists the levels the sheet offers, and `effort` sets a default. `add_dir_flag` is how a CLI takes another directory (`--add-dir` for claude, codex, grok, agy and omp); it is passed once per directory, and a directory that does not exist is refused.

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
cowbell new --harness codex --effort high
cowbell new --harness claude --add-dir ~/notes,../shared
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
git clone https://github.com/charlesberret/cowbell-core.git
cd cowbell-core
python3 -m unittest discover -s tests -v
./scripts/public-surface-scan.sh
```

From a clone, `./bin/cowbell --version` also works: the launcher follows symlinks and picks a Python 3.11 or newer for you (macOS `/usr/bin/python3` is 3.9 and must not run this module).

`tests/test_pty.py` drives the menu, the prompt and the whole picker in a real pseudo-terminal. The code keeps two seams: `ctx.live`, what is running, and `ctx.launch`, where an agent opens. Every `herdr` CLI call lives in the `# --- herdr adapter` section of `cowbell.py`, and a test enforces it. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
