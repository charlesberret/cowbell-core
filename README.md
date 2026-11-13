# cowbell

Type `cowbell` in a directory to launch or re-launch a coding agent there with the settings you choose: model, effort, permissions, tools, other directories. You see the exact command before it runs. The same list shows who is already working here and which sessions can resume. (verified: cowbell.py:4-9, 3969-3982, 5661-5729)

cowbell is for people who run several coding-agent CLIs (Claude Code, Codex, Grok and similar) across many folders and want to see and reach them by place. The choices are **Resume** or **New Session**, with an **Active** census of who is already working here. Active is every coding agent whose working directory is this one or below it. You can see them. You cannot take them over from this list. Resume is the sessions cowbell can pick up again. New Session is the agents in your catalog that are installed and allowed here, most used here first. (verified: cowbell.py:1600, 1823-1826, 1832-1835, 1952-1956, 6251)

```
  ~/code/projects/acme                         g widen to projects · 4 running  (verified: cowbell.py:2067)

  ┌─ Active ──────────────────────────────────────────────────────────────┐  (verified: cowbell.py:1821)
  │    api-claude             claude      idle                            │  (verified: cowbell.py:179, 1638-1640)
  │    reviewer               grok        working  14s   in proj:docs     │  (verified: cowbell.py:1648, 1910-1921)
  └───────────────────────────────────────────────────────────────────────┘

  Resume  (verified: cowbell.py:1821)
    1  notes-draft            oll-mid     2 days ago  (verified: cowbell.py:1856-1864)

  New Session  (verified: cowbell.py:1821)
    2  claude                 Claude Code  (verified: harnesses.toml:149-164)
    3  grok                   Grok CLI                           ! more reach than needed  (verified: cowbell.py:1962-1963)
    4  agy                    Antigravity (Gemini)  (verified: harnesses.toml:197-205)
       + 9 more  (verified: cowbell.py:1871-1874, 1904-1908)

  ⏎ open   n new   + add   a adopt   g widen   o shape   r rename   esc  (verified: cowbell.py:5481-5496)
```

`o` on a row, or `n`, opens the **launch sheet** for that agent: every setting it takes, the account it runs as, and the command that will run. Here it is at the width of the herdr popup, with model, effort and permissions changed from the defaults: (verified: cowbell.py:5919-5933, 6267-6273, 5661-5686)

```
  api  claude · Claude Code  new tab in ~/api  (verified: cowbell.py:5699-5705, 5946)

  ▶  start  (verified: cowbell.py:5706-5709)
     name           api  (verified: cowbell.py:5668)
     model          claude-opus-5  (verified: cowbell.py:5669-5670; harnesses.toml:153)
     effort         high  (verified: cowbell.py:5671-5672; harnesses.toml:155-156)
     permissions    green  (verified: cowbell.py:5673-5674; harnesses.toml:117-120)
     tools allow    all  (verified: cowbell.py:5675-5676)
     tools deny     none  (verified: cowbell.py:5677-5679)
     also in        none  (verified: cowbell.py:5680-5683)
     seat file      none  (verified: cowbell.py:5684-5686)
     runs as        you  (verified: cowbell.py:5721-5723)

  $ claude --model claude-opus-5 --effort high  (verified: cowbell.py:5725-5729; harnesses.toml:154-155)
    --permission-mode plan  (verified: harnesses.toml:117-118)

  ⏎ start   d defaults   a save as   esc cancel  (verified: cowbell.py:5773-5778)
```

It is mouse-first: click or arrow to a row, Enter or the ⏎ button to open it, Esc to close. A digit jumps to its row, and every hint in the bottom bar is clickable. The list refreshes every two seconds. Off a terminal, or with `COWBELL_PLAIN=1`, it falls back to a typed-number prompt; `NO_COLOR` turns colour off. (verified: cowbell.py:4677-4725, 5995, 4486-4487, 183, 4783-4796)

Cowbell is the standalone engine: running `cowbell` directly in any terminal provides the full interactive picker, session resumption, launch sheets, and harness catalog without requiring Herdr. The companion plugin `herdr-cowbell` embeds this engine inside Herdr workspaces, binding the picker to `prefix+c` as a popup and adding workspace-aware actions like `adopt`, `stop`, and `import-seats`. Both standalone CLI invocations and the Herdr plugin share the exact same configuration catalog and session roster (`~/.config/cowbell` and `~/.local/state/cowbell`), so agents started in a bare terminal seamlessly surface and resume inside Herdr workspaces. (verified: cowbell.py:30-37, 236-270)

## Install

cowbell is one Python file with no required dependencies (the icon font below is optional). It needs **Python 3.11 or newer**. macOS ships `/usr/bin/python3` at 3.9, which is too old; `brew install python` or `uv python install 3.12` is enough. It runs on macOS and Linux. (verified: pyproject.toml:10,14; bin/cowbell:2-18)

### From a release archive (pip, pipx, or uv)

Install the sdist or wheel into your environment or tool cache: (verified: pyproject.toml:10,24-25,37)

```bash
pip install cowbell-0.3.3.tar.gz
# or
pipx install cowbell-0.3.3.tar.gz
# or
uv tool install cowbell-0.3.3.tar.gz
```

The installer puts the console script `cowbell` on your PATH. (verified: pyproject.toml:24-25)

Check that it runs: (verified: cowbell.py:6464)

```bash
cowbell --version
```

Expected output: `cowbell 0.3.3`. (verified: cowbell.py:63, 6464)

On first run, cowbell seeds its catalog at `~/.config/cowbell/harnesses.toml` (or under `COWBELL_CONFIG_DIR` or `$XDG_CONFIG_HOME/cowbell`). For package installs, the seed catalog is copied from the package's shared data at `<sys.prefix>/share/cowbell/harnesses.toml`. (verified: cowbell.py:240-245, 255-261, 314-322; pyproject.toml:33-34)

### From a clone

Clone and run the launcher directly: (verified: curl -sIL → HTTP 200; clone of cowbell-core.git yields cowbell-core/)

```bash
git clone https://github.com/charlesberret/cowbell-core.git
cd cowbell-core
./bin/cowbell --version
```

Expected output: `cowbell 0.3.3`. In a clone, the seed catalog is copied from `harnesses.toml` beside `cowbell.py`. To run it from any directory, link the launcher onto your PATH. The launcher follows symlinks and picks a Python 3.11 or newer for you: (verified: bin/cowbell:5-18; cowbell.py:240-244, 314-320)

```bash
mkdir -p "$HOME/.local/bin"
ln -s "$PWD/bin/cowbell" "$HOME/.local/bin/cowbell"
```

`$HOME/.local/bin` must be on your PATH. Then run `cowbell` in any project directory. (verified: bin/cowbell:6-17)

### Icons for each agent (optional)

Each row shows a mark for its agent's kind. The marks come from the [Lobe Icons Font](https://github.com/hschne/lobe-icons-font) (MIT), which is not part of macOS or any Linux distribution. Without it, cowbell shows one letter for each kind instead: `C` claude, `G` grok, `X` codex, `M` gemini, `A` antigravity, `P` pi, `D` devin, `H` copilot, `O` openai, `L` ollama, and `·` for anything else. (verified: cowbell.py:3135-3151, 3265-3269) To get the marks: (verified: cowbell.py:24-26, 3224-3252)

```bash
cowbell font install
```

Expected output: `installed: <font dir>/lobe-icons.ttf (v5.23.0, sha256 checked)`. It downloads one pinned release, refuses any file whose sha256 differs, and writes it to `~/Library/Fonts` on macOS or `~/.local/share/fonts` on Linux (then runs `fc-cache`). It needs no sudo. `cowbell font` reports whether the font was found and which kind of mark cowbell is using. (verified: cowbell.py:3153-3158, 3163-3168, 3224-3252, 3214-3217)

If the marks still draw as boxes, tell your terminal to take that range from the font, then open a new window: (verified: cowbell.py:3205-3212 prints this same fix)

```
# Ghostty (~/.config/ghostty/config)  (verified: cowbell.py:3208)
font-codepoint-map = U+F4000-U+F47FF=lobe-icons  (verified: cowbell.py:3158, 3208)
# kitty (~/.config/kitty/kitty.conf)  (verified: cowbell.py:3209)
symbol_map U+F4000-U+F47FF lobe-icons  (verified: cowbell.py:3158, 3209)
```

cowbell checks the machine it runs on. Over ssh the terminal that draws the screen is on another machine, so set `COWBELL_GLYPHS=lobe` (font is on your local machine) or `COWBELL_GLYPHS=text` (it is not). (verified: cowbell.py:3188-3196, 3215-3217)

## Status

Pre-1.0 (0.3.x). The command line, the picker and the catalog format (`schema = 1`) may still change between releases; changes are listed in [CHANGELOG.md](CHANGELOG.md). (verified: cowbell.py:63 `__version__ = "0.3.3"`; harnesses.toml:91 `schema = 1`; CHANGELOG.md exists) Bug reports and focused pull requests are welcome.

## Where agents open

- **Inside a herdr pane**, starting or resuming opens a new herdr tab named for the session, and Active lists herdr's agents. (verified: cowbell.py:2939-2950, 6321-6323)
- **Anywhere else**, or with `COWBELL_MODE=here`, cowbell hands this terminal to the agent, `exec`, in the chosen directory. Quit the agent and you are back at your shell. Active lists herdr's agents when a herdr server is listening, plus agent CLIs found running in plain terminals by working directory. Those rows say where they run, `on ttys012`. Cowbell can't switch to another terminal window. (verified: cowbell.py:6321-6323, 2650-2657, 2209-2277, 1920-1921, 2734-2735)
- **Resume** lists only sessions that can resume. Claude started outside herdr gets its session id up front, `session_id_flag`, so it can. Agents without such a flag are not listed. Resume shows the harness's current session title; a herdr tab that differs is the location. When several sessions share a title, the harness title keeps the bare name and the others gain a short id tail. `cowbell rename` pins a name. (verified: cowbell.py:1776-1787, 620-638, 673-700, 1910-1921; harnesses.toml:31-38, 162)
- **Enter on New Session** opens the agent at once with an automatic name, `claude` or `claude-2`, and the default permissions. `[defaults] ask_name = true` asks for the name first. **`e` on a New Session row** opens a menu of that harness. The first line is its name. Then description, models, default model, permissions, tools, provider, model cycle, and system prompt. A field with a known set of values offers those, plus none, and a line to type another. A launcher script also lists its command. Empty fields stay on the menu. Pick a row to change that field. Esc inside a field cancels it. Esc on the menu returns to the list. `+` adds a harness, a herdr kind or a launcher script. (verified: cowbell.py:526-535, 5963-5985, 5043-5063, 5409-5440; harnesses.toml:110)
- **`n`** asks for the agent, then opens its **launch sheet**: one screen with start at the top, then every setting that harness takes (name, model, effort, permissions, tools, other directories it may work in, seat file) and the account it runs as, then the exact command that will run. A setting left at the harness default is dim; one you changed is bright. Enter on a setting changes it, `s` or Enter on start launches, `d` puts every setting back to the default, Esc cancels. Starting changes this launch only. `a` saves what the sheet shows as a new harness instead, with its own New Session row and `cowbell <id>`: a copy of this agent with the sheet's model, effort, permissions and tools as its defaults. The sheet stays open, and nothing launches until you start. If you start from `n` without saving, `n` offers to save afterwards. A resume sheet has no `a`, because a session is not a shape. **`o` on a New Session row** opens that harness's sheet straight away, on the settings it was last started with in this directory (else its defaults); `d` there means the harness defaults. **`o` on a Resume row** opens the sheet over that session as it was recorded, so you can resume it with another model, effort, permissions or tools; `d` puts the recording back, and the roster keeps what you resumed with. New Session lists as many harnesses as the window can hold, and ten when the height is unknown. Active and Resume show five, then a more row. DRAFT — needs maintainer check: "show five, then a more row" — FOLD=5 shows FOLD-1=4 rows + a "+ N more" row when a section is longer than 5 (cowbell.py:1818, 1867-1874, 1876-1880). Rest of line verified (cowbell.py:5661-5686, 5773-5778, 5919-5985, 6267-6269, 1819, 1886-1895, 3660-3671).
- **Trust** appears only if a checker is configured and on PATH, and only as an exception: a dim `! more reach than needed` on a row the checker calls over-privileged. That is advisory and never stops a launch; blocked agents are left off. (verified: cowbell.py:746, 1523, 1953, 1962-1963, 3916-3919, 5939)

Two hooks let cowbell use tools it does not own, both set in `[defaults]`: (verified: cowbell.py:734-746)

- `trust_command` is a program asked `subject <path>`, `match <harness> <path>` and `badge <harness>`. Exit 4 refuses. Exit 3 warns and asks. If it is unset, or not on PATH, no trust marks appear at all. DRAFT — needs maintainer check: "Exit 3 warns and asks" — overprivilege (exit 3) prints a `!` note only; no prompt exists on this path (cowbell.py:3918-3919, 5985-5987, 6355 "-y … this path has no prompt"). Exit 4 refuses and unset/not-on-PATH → no marks: verified (cowbell.py:1520-1585, 3916-3917, 746).
- `seat_file` is a briefing file, default `SEAT.md`, found by walking up from the directory and handed to a harness through its `system_prompt_flag`. (verified: cowbell.py:737, 746, 494-499, 2126 — walk stops at $HOME)
- `session_history` set to `"on"` lets Resume read the stores the harnesses keep themselves, `~/.claude/projects` and `~/.grok/sessions`, so a directory shows every session it has seen, including sessions cowbell did not start. Only ids, times and titles are read. Transcript bodies never are. `"all"` also lists agents that a session dispatched rather than a person chose. For a place with `unix_user`, discovery runs as that launch user and reads that user's stores, so Resume never offers a session the launched process cannot open. Default `"off"`. DRAFT — needs maintainer check: "Only ids, times and titles are read. Transcript bodies never are" — the history scan also reads each session's first real user line (`utterance`) for naming and dispatch detection (cowbell.py:1256-1277, 1340-1374, 1179). Rest of line verified (cowbell.py:1168-1169, 1246-1252, 1327-1329, 1446-1460).

## Catalog, places, state

The catalog is `~/.config/cowbell/harnesses.toml`, or the same file under `COWBELL_CONFIG_DIR` or `$XDG_CONFIG_HOME/cowbell`, seeded from [`harnesses.toml`](harnesses.toml) on first run with the standard agents, shown only when installed. An existing copy that is missing `droid` or `devin` is filled once from the seed when that binary is on PATH. A later delete stays deleted. Add your own launchers, models and permission presets there. The roster is `~/.local/state/cowbell/roster.json`, or the same file under `COWBELL_STATE_DIR` or `$XDG_STATE_HOME/cowbell`. Both carry `schema = 1`. A cowbell that finds a newer schema reads the file but will not overwrite it. Versions up to 0.3 kept both in herdr's plugin directories. The first run copies them over once. A harness may set `provider`, a model cycle, and a `system_prompt`, and cowbell passes them on the launch line when the row sets the matching `provider_flag`, `cycle_flag`, and `system_prompt_flag`. Effort works the same way: `effort_flag` is how the CLI takes a reasoning level (`["--effort"]` for claude, `["--thinking"]` for pi and omp, `["-c", "model_reasoning_effort={}"]` for codex, where `{}` is the level), `efforts` lists the levels the sheet offers, and `effort` sets a default. `add_dir_flag` is how a CLI takes another directory (`--add-dir` for claude, codex, grok, agy and omp); it is passed once per directory, and a directory that does not exist is refused. (verified: cowbell.py:256-267, 316-321, 327-389, 301-304, 57, 2174-2181, 2084-2086, 5732-5745; harnesses.toml:149-238)

A row may set requires, a list of argvs run in order before every start or resume. The first that exits non-zero refuses the launch. check is one argv. When that check has no pass in the last 7 days, the launch runs it after requires and opens only if it passes. cowbell accept [id ...] runs those checks ahead of time. Results are kept in accept.json in the state directory (the same directory as roster.json). The verdict recorded is the last line the check prints on stdout. cowbell catalog shows a row with a stale check as unproven. This check is the row's own acceptance. It is not the trust checker. (verified: cowbell.py:841-911, 3986-3989, 4036-4044)

Permission presets are called lanes: `green` reads and plans, `yellow` allows edits, `red` bypasses approvals. Each agent kind maps the three names to its own CLI flags under `[lanes.<kind>]` in the catalog, and `--lane` picks one at launch. (verified: cowbell.py:59, 6344; harnesses.toml:112-147)

A directory can have its own rules: (verified: cowbell.py:780-820)

```toml
[defaults]  (verified: cowbell.py:780-801)
untitled_place = "lobby"          # a session started from ~ opens here instead  (verified: cowbell.py:801)

[places.lobby]  (verified: cowbell.py:780-800)
cwd = "~/code/projects/acme"  (verified: cowbell.py:786)
workspace_label = "lobby"         # herdr workspace its sessions open in (created if missing)  (verified: cowbell.py:2944, 3032-3033)
allow_harness = ["lobby", "claude", "grok"]  (verified: cowbell.py:816-820, 1662-1663, 3937-3940)
default_harness = "lobby"         # guest door; `new --place lobby` with no --harness  (verified: cowbell.py:814-815, 3935-3940)
lane = "yellow"                   # default permission preset for this place  (verified: cowbell.py:812-813)
```

Anything started at or below `cwd` opens in that workspace. New lists only the allowed agents. Resume omits roster rows whose harness is not allowed, so a cold `oll-memo` in that cwd is not a guest. `cowbell new --place lobby` with no `--harness` uses `default_harness`. Claude and Grok stay allowed there for your own work; the place keeps guests to the `lobby` harness. `[places.*]` are walls, not a roster of project workspaces. When a pane already has this directory on a grouped `proj:` line, the session opens there. (verified: cowbell.py:808-820, 1662-1663, 1684-1687, 3935-3940, 2895-2910, 3028-3033)

### A place that drops to another unix account

`unix_user` is an account name, `getpwnam`. Create that account on your own machine, give it a directory it can write, and add a wrapper harness plus the place to `~/.config/cowbell/harnesses.toml`: (verified: cowbell.py:1435-1446, 2351-2353, 2482-2484)

```toml
[[harness]]  (verified: cowbell.py:cat.get("harness") rows; harnesses.toml:44-48 same example)
id = "lab"  (verified: harnesses.toml:44-48)
kind = "lab"  (verified: harnesses.toml:44-48)
title = "Lab shell"  (verified: harnesses.toml:44-48)
command = "/bin/bash"  (verified: harnesses.toml:44-48; wrapper `command` rows at cowbell.py:5047-5048)

[places.lab]  (verified: cowbell.py:780-800)
cwd = "~/lab"  (verified: cowbell.py:786)
allow_harness = ["lab"]  (verified: cowbell.py:816-820, 3937-3940)
default_harness = "lab"  (verified: cowbell.py:814-815, 3935-3940)
unix_user = "lab"  (verified: cowbell.py:1435-1446, 2448-2464)
require_uid = true  (verified: cowbell.py:2471-2477)
nono_profile = "/usr/local/share/walls/lab.json"   # the wall; see below  (verified: cowbell.py:2370-2386, 2459-2499)
```

`cowbell new --harness claude --place lab` refuses to start, because `claude` is not in `allow_harness`. `cowbell new --place lab` starts the bash wrapper. (verified: cowbell.py:3935-3942, 814-820)

When `unix_user` is set and the process is not already that user, cowbell prefixes `agent-run <user> --`. That helper is not part of cowbell. Without `agent-run` on PATH cowbell refuses; it does not fall back to `sudo -u`, which would skip the helper's checks. Session-history discovery uses the same identity boundary and returns only derived Resume metadata to the caller. You can also leave `unix_user` unset and drop privileges yourself with `sudo -u lab -- cowbell new --place lab`. `require_uid = true` with no `unix_user` refuses to start. (verified: cowbell.py:1446-1460, 2471-2477, 2511-2515)

A drop to another account fails closed. The level that names the account names its wall: a place's `unix_user` takes the place's `nono_profile`, a harness's takes the harness's own. A wall on a harness without its own `unix_user` is refused. `nono_profile` must be an absolute path to a regular, root-owned file that group and other cannot write; it wraps the command as `nono run --silent --profile <path> -- …` inside the drop, and `nono` must be on PATH. A harness whose `command` raises its own sandbox says `wall = "door"` instead: nono cannot wrap such a command on macOS, where a sandboxed process cannot apply a second Seatbelt profile. The door command is root-installed, like a profile: an absolute path with no symlink in it, owned by root, and neither it nor any directory above it owned by anyone but root or writable by group or other (a root-owned sticky directory such as `/tmp` is allowed). A copy in your home or a synced tree is refused. `nono_proxy_port`, beside a `nono_profile` at the same level, adds `--proxy-port <port>` for an account whose firewall passes only that loopback port to nono's proxy. A door and a `nono_profile` in one launch refuse; places and `[defaults]` cannot say `door`. (verified: cowbell.py:2370-2425, 2428-2515)

```toml
[[harness]]  (verified: harnesses.toml:71-76 same example)
id = "lobby"  (verified: harnesses.toml:71-76)
kind = "pi"  (verified: harnesses.toml:71-76)
command = "/usr/local/libexec/agent-uids/lobby"  (verified: harnesses.toml:71-76; door rules at cowbell.py:2389-2425)
unix_user = "guest"  (verified: harnesses.toml:71-76; cowbell.py:2448-2459)
wall = "door"  (verified: harnesses.toml:71-76; cowbell.py:2448-2457)
```

A harness can carry the account, the wall and its folder itself, so it is walled wherever it is started: (verified: cowbell.py:2428-2437, 2325-2331)

```toml
[[harness]]  (verified: harnesses.toml:83-89 same example)
id = "gemini-guest"  (verified: harnesses.toml:83-89)
kind = "gemini"  (verified: harnesses.toml:83-89)
title = "Gemini (guest)"  (verified: harnesses.toml:83-89)
unix_user = "guest"  (verified: harnesses.toml:83-89; cowbell.py:2448-2459)
nono_profile = "/usr/local/share/walls/guest.json"  (verified: harnesses.toml:83-89; cowbell.py:2370-2386)
cwd = "/srv/agents/guest/work"  (verified: harnesses.toml:83-89; cowbell.py:2325-2331, 2503-2505)
```

A harness with `cwd` starts there, not in the directory you called it from. The folder must be absolute with no symlink in it, under that account's home or inside a place that account owns, and you must be able to enter it, because cowbell starts the process there before the drop. nono gets `--allow-cwd` only when the launch starts in that folder, inside a place whose own `unix_user` is the dropping account, or when no account is dropped; otherwise the profile alone decides what it may read. (verified: cowbell.py:2325-2331, 2404, 2426, 2503-2508)

## Commands

```
cowbell                      the picker (on a terminal); piped, the long registry  (verified: cowbell.py:4-5, 4486-4487, 6156-6200)
cowbell --version            cowbell 0.3.3  (verified: ./bin/cowbell --version → "cowbell 0.3.3"; cowbell.py:6, 6464)
cowbell --debug              opt-in startup timing trace; see docs/debug-trace.md  (verified: cowbell.py:27, 6444-6454)
cowbell status               long registry: live · cold · absent, session ids, trust  (verified: cowbell.py:7, 1593, 1765-1810)
cowbell claude               focus a claude running here, else resume one, else start one  (verified: cowbell.py:9, 3969-3982)
cowbell new --harness claude --model claude-opus-5 --lane green --allow Read,Grep  (verified: cowbell.py:10, 6333-6346; harnesses.toml:153-160)
cowbell new --harness codex --effort high  (verified: cowbell.py:6342, 3955; harnesses.toml:171-172)
cowbell new --harness claude --add-dir ~/notes,../shared  (verified: cowbell.py:6343, 6426, 5732-5745)
cowbell new --harness grok --place lobby  (verified: cowbell.py:6348, 780-820, 3935-3940)
cowbell enter <name>         focus if live, else resume  (verified: cowbell.py:14, 3640-3671)
cowbell list [--all]  (verified: cowbell.py:16)
cowbell catalog              every harness: kind, egress, installed, trust badge  (verified: cowbell.py:17, 3985-3989)
cowbell catalog --check      fail named malformed rows; warn on declared flags missing from a CLI's help  (verified: cowbell.py:4046-4110)
cowbell accept [id ...]      run each named row's check now, or every row that has one, and record it  (verified: cowbell.py:19-20, 875-888, 4036-4044)
cowbell reconcile [--dry-run]   pane borders that claim a harness, matched to the agent Herdr detects  (verified: cowbell.py:21, 3534-3559)
cowbell font [install]       is the icon font here; install fetches the pinned font  (verified: cowbell.py:24-26, 3214-3252)
```

`bin/cowbell` picks a python ≥ 3.11, for tomllib, and follows symlinks. macOS `/usr/bin/python3` is 3.9 and must not run this. Stdlib only. (verified: bin/cowbell:1-19; pyproject.toml:14)

### Internal commands

`cowbell identity stamp` and `cowbell identity sync` are internal plumbing commands for Herdr integration, marked as advanced and rarely needed in day-to-day use:

- `cowbell identity stamp` scans live Herdr agent panes and publishes each pane's `$glyph` badge and sitting name from detector state. (verified: cowbell.py:22, 3412-3428, 6546-6549)
- `cowbell identity sync` restamps or clears a single pane's badge from a Herdr occupancy event payload (`HERDR_PLUGIN_EVENT_JSON`). (verified: cowbell.py:23, 3450-3470, 6550-6552)

Day-to-day users do not need these commands; they run from plugin hooks or during seed and catalog maintenance to re-synchronize pane identities. (verified: cowbell.py:3383-3470, 6553-6556)

## Development

Run the test suite: (verified: .github/workflows/test.yml runs the same suite)

```bash
python3 -m unittest discover -s tests -v
```

The GitHub workflow at `.github/workflows/test.yml` runs `python3 -m unittest discover -s tests` on Python 3.11. (verified: .github/workflows/test.yml)

`tests/test_pty.py` drives the menu, the prompt and the whole picker in a real pseudo-terminal. The code keeps two seams: `ctx.live`, what is running, and `ctx.launch`, where an agent opens. Every `herdr` CLI call lives in the `# --- herdr adapter` section of `cowbell.py`, and a test enforces it. (verified: tests/test_pty.py; cowbell.py:394, 2784; tests/test_cowbell.py:1137)

## License

MIT. See [LICENSE](LICENSE). (verified: LICENSE file; pyproject.toml:11)
