# Catalog Field Reference

Cowbell manages agent launch configurations, permission tiers, directory boundaries, and security policies via a TOML catalog file. On first run, Cowbell seeds this configuration from `harnesses.toml` into `~/.config/cowbell/harnesses.toml` (or `$XDG_CONFIG_HOME/cowbell/harnesses.toml`).

The configuration file is divided into four main sections:
- `[[harness]]`: Declarations for how each agent executable is invoked, configured, resumed, and sandboxed.
- `[lanes.<kind>]`: Preset CLI arguments mapping permission tiers (`green`, `yellow`, `red`) for each agent kind.
- `[defaults]`: Global operational settings, fallback permission presets, and external verification tools.
- `[places.<name>]`: Directory-scoped constraints, account isolation, and allowed launcher lists.

This document provides a field reference for every `[[harness]]` configuration key and `[lanes.*]` preset tier. Every field is verified against Cowbell's catalog loader (`load_catalog`), argument constructor (`build_argv`), and launch execution paths.

---

## `[[harness]]` Field Reference

The table below documents every key accepted within a `[[harness]]` block. Ground-truth keys defined or commented in the seed file (`harnesses.toml`) are included, along with keys supported by Cowbell's loader but omitted from the seed (marked as *Undocumented in seed*), and related terms from CLI and runtime contexts (with honest verification notes).

| Key | Type | Default | What it does | Verified at |
|---|---|---|---|---|
| `id` | string | *mandatory* | Unique identifier for the harness row. Used to key catalog entries, references in `[places.*] allow_harness`, acceptance records, and CLI invocation targets (`cowbell new <id>`). | `(verified: cowbell.py:767, 4120, 4330)` |
| `kind` | string | `id` | The underlying agent CLI binary or kind. When `command` is omitted, Cowbell searches `PATH` for this binary name. Also indexes preset tables such as `[lanes.<kind>]`. | `(verified: cowbell.py:767, 838, 4126, 2362)` |
| `title` | string | `""` (falls back to `id`) | Human-readable label displayed in interactive pickers, menus, process lists, and catalog tables. | `(verified: cowbell.py:383, 1699, 2020, 4055)` |
| `command` | string | `""` | Path to a custom wrapper script or executable binary. Tilde expansion (`~`) is applied. When specified, Cowbell treats the harness as a wrapper (`is_wrapper(h) == True`) instead of invoking `kind` directly from `PATH`. | `(verified: cowbell.py:773-774, 834, 838, 2362)` |
| `argv` | list[str] | *none (runtime)* | *Not a catalog configuration key (undocumented in seed).* In Cowbell, `argv` is dynamically constructed at launch by `build_argv` and recorded on live process inspection records; it is not parsed from `[[harness]]` blocks. | `(verified: cowbell.py:2161, 2283, 2621)` |
| `family` | string | `kind` | Grouping identifier used for classification and glyph mapping. *Undocumented in seed.* | `(verified: cowbell.py:768, 1698)` |
| `egress` | string | `"vendor"` | Network egress categorization for glyph display. Allowed values are `"vendor"` (`↑`), `"local"` (`⌂`), or `"mesh"` (`⌂`). *Undocumented in seed.* | `(verified: cowbell.py:769, 1698, 4128)` |
| `models` | list[str] | `[]` | List of supported model identifiers offered in the launch sheet. The first entry (`models[0]`) serves as the default model if none is specified. | `(verified: cowbell.py:771, 2180, 4018, 4132)` |
| `model_flag` | list[str] | `[]` | CLI flag prepended before the chosen model name when invoking the agent (e.g. `["--model"]` or `["-m"]`). | `(verified: cowbell.py:2125-2126, 2177-2178, 5134)` |
| `cycle_flag` | list[str] | `[]` | CLI flag used to pass a comma-separated list of all declared models for cycling support (e.g. `["--models"]`). *Undocumented in seed.* | `(verified: cowbell.py:2181-2182, 5122, 5264)` |
| `model_cycle` | — | — | *Not a TOML configuration key (undocumented in seed).* This is the user-interface display label in Cowbell's interactive editor (`_edit_row("model cycle", ...)`) for the `cycle_flag` property. | `(verified: cowbell.py:5122, 5262-5267)` |
| `effort_flag` | list[str] | `[]` | CLI flag tokens used to set reasoning effort. If a token contains `"{}"` (e.g. `["-c", "model_reasoning_effort={}"]`), `{}` is replaced in-place by the effort level; otherwise the level is appended as the subsequent token (e.g. `["--effort", "high"]`). | `(verified: cowbell.py:2138-2146, 4134-4136)` |
| `efforts` | list[str] | `[]` | Supported reasoning effort levels presented in the launch sheet (e.g. `["low", "medium", "high", "max"]`). An empty list indicates free-form string entry. | `(verified: cowbell.py:4137-4138)` |
| `effort` | string | `""` | Default reasoning effort level for this harness row (e.g. `"high"`). Cowbell catalog verification requires `effort_flag` to be set whenever `effort` is populated. | `(verified: cowbell.py:2169, 2179, 4142-4143, 4915)` |
| `session_id_flag` | string | `""` | CLI flag passed when Cowbell assigns a session UUID outside Herdr (e.g. `"--session-id"`). Enables standalone launch and later resumption in plain terminals. | `(verified: cowbell.py:2357-2359)` |
| `resume` | list[str] | `[]` | Arguments used to resume an existing session. If set to a subcommand like `["resume"]`, it is positioned before options (`codex resume <id>`); if ending with `"="` (e.g. `["--session="]`), the session id is concatenated; otherwise the session id is appended as a subsequent argument (`--resume <id>`). | `(verified: cowbell.py:772, 2172, 2202-2210, 4070)` |
| `resume_flag` | — | — | *Not found in loader.* The actual catalog field name is `resume` (a list of tokens). | `(verified: cowbell.py:772, 2202, 4070)` |
| `name_flag` | string | `""` | CLI flag passed to set the session's display name outside Herdr (e.g. `"--name"`). | `(verified: cowbell.py:2360-2361)` |
| `claim_flag` | string | `""` | CLI flag for agent role/persona claims (e.g. `"--agent"`). For Grok harnesses, this flag is passed only if `~/.grok/agents/<sitting>.md` exists. | `(verified: cowbell.py:2103-2115)` |
| `add_dir_flag` | string | `""` | Flag repeated once per additional directory granted to the agent workspace (e.g. `"--add-dir"`). | `(verified: cowbell.py:2149-2158, 4139-4141)` |
| `tools_allow_flag` | string | `""` | CLI flag used to specify permitted tools (e.g. `"--allowedTools"` or `"--tools"`). | `(verified: cowbell.py:2131-2132, 2186-2187, 5142-5148)` |
| `tools_deny_flag` | string | `""` | CLI flag used to specify forbidden tools (e.g. `"--disallowedTools"` or `"--disallowed-tools"`). | `(verified: cowbell.py:2133-2134, 2188-2189, 5142-5148)` |
| `tools_allow` | string | `""` | Preset tool allowance string configured directly on the harness row. Appended at launch when `tools_allow_flag` is present. *Undocumented in seed.* | `(verified: cowbell.py:2131, 4891, 4920, 5119)` |
| `tools_deny` | string | `""` | Preset tool denial string configured directly on the harness row. Appended at launch when `tools_deny_flag` is present. *Undocumented in seed.* | `(verified: cowbell.py:2133, 4891, 4922, 5120)` |
| `lane` | string | `""` (inherits `[defaults]`) | Default permissions tier preset for this harness (`"green"`, `"yellow"`, or `"red"`). Overrides `[defaults] lane` for this specific harness row. *Undocumented in seed.* | `(verified: cowbell.py:2127, 4130-4131, 4883, 4918)` |
| `system_prompt_flag` | string | `""` | CLI flag used to supply an extra system prompt file or text (e.g. `"--append-system-prompt-file"` or `"--append-system-prompt"`). Used when a seat briefing file is discovered or `system_prompt` is defined. | `(verified: cowbell.py:751, 2191-2195, 5278-5279)` |
| `seat_flag` | string | `""` | Deprecated alias for `system_prompt_flag` retained for backward compatibility with pre-0.3 catalogs. *Undocumented in seed.* | `(verified: cowbell.py:750-751)` |
| `system_prompt` | string | `""` | Static system prompt text or file path injected via `system_prompt_flag` on launch. *Undocumented in seed.* | `(verified: cowbell.py:2193-2195, 5123, 5273-5277)` |
| `provider` | string | `""` | Name of the backend model provider (e.g. `"openrouter"` or `"anthropic"`). *Undocumented in seed.* | `(verified: cowbell.py:2174-2176, 5019, 5121, 5253-5258)` |
| `provider_flag` | list[str] | `[]` | CLI flag tokens used to pass the `provider` name to the agent binary (e.g. `["--provider"]`). *Undocumented in seed.* | `(verified: cowbell.py:2175-2176, 5259-5260)` |
| `requires` | list[list[str]] | `[]` | List of command-line argument lists run sequentially in the host terminal prior to agent launch (e.g. verifying a daemon or local inference endpoint). The first non-zero exit code halts launch. A bare string, as the whole value or as an entry, is malformed: `catalog --check` reports it and a launch refuses it before any entry runs; it is never wrapped or split. | `(verified: cowbell.py:892-899, 4147-4150)` |
| `check` | list[str] | `[]` | Single argv command executed to evaluate harness acceptance. A bare string is malformed: `catalog --check` reports it and the check fails with the same rule; it is never wrapped or split. Results are recorded in `accept.json`. If unproven within the past 7 days, Cowbell executes this check prior to launching. | `(verified: cowbell.py:879-889, 901-910, 4092-4110, 4144-4146)` |
| `trust_tool` | string | `id` | Identifier queried against `trust_command` (`harness-trust`) to retrieve verification badges and security verdicts. Defaults to the harness `id`. | `(verified: cowbell.py:770, 1691, 1700, 3981, 4055)` |
| `unix_user` | string | `""` | Dedicated Unix username (`getpwnam`) under which the harness runs. When current UID differs, Cowbell prefixes execution with `agent-run <user> --`. Must be paired with a security wall (`nono_profile` or `wall = "door"`). | `(verified: cowbell.py:2415, 2514, 2524, 2548-2551)` |
| `wall` | string | `""` | Sandboxing model. The only permitted value is `"door"`, indicating that the harness executable establishes its own sandbox boundary. Mutually exclusive with `nono_profile`. | `(verified: cowbell.py:2514-2516, 2525, 2536)` |
| `nono_profile` | string | `""` | Absolute path to a root-owned `nono` JSON sandbox profile. Cowbell wraps execution with `nono run --profile <profile>`. | `(verified: cowbell.py:2514, 2525, 2563-2574)` |
| `nono_proxy_port` | integer | *none* | Loopback TCP port (1024–65535) passed via `--proxy-port` to the `nono` isolation wrapper. Requires `nono_profile`. *Undocumented in seed.* | `(verified: cowbell.py:2525, 2531-2534, 2572-2574)` |
| `cwd` | string | `""` | Absolute directory in which the harness must start when combined with `unix_user`. `nono`'s `--allow-cwd` flag grants access to this specific folder rather than the caller's directory. | `(verified: cowbell.py:2569-2571)` |

---

## Global & Defaults Field Context

While configured outside `[[harness]]` rows, the following keys in `[defaults]` govern how seat briefings, trust checks, and default permissions interact with harness execution:

| Key | Section | Type | Default | What it does | Verified at |
|---|---|---|---|---|---|
| `seat_file` | `[defaults]` | string | `"SEAT.md"` | Filename of the briefing document sought when walking upwards from the current directory towards `$HOME`. If located, its path is supplied to the harness via `system_prompt_flag`. | `(verified: cowbell.py:495, 499, 737, 745)` |
| `trust_command` | `[defaults]` | string | `"harness-trust"` | External executable invoked to obtain trust badges and evaluate security policies for `trust_tool`. | `(verified: cowbell.py:737, 745, 106)` |
| `session_history` | `[defaults]` | string | `"off"` | Governs session discovery from native agent data stores (`"off"`, `"on"`, or `"all"`). | `(verified: cowbell.py:104, 1500-1506)` |
| `lane` | `[defaults]` | string | `"yellow"` | Fallback permission tier (`"green"`, `"yellow"`, `"red"`) utilized when neither harness nor place defines one. | `(verified: cowbell.py:109, 4887)` |

---

## `[lanes.*]` Preset Reference

Permission presets ("lanes") define standard execution tiers across different agent kinds. When an agent is launched under a given lane, Cowbell looks up `cat["lanes"][harness["kind"]][lane]` and appends the mapped arguments to the command line.

### Preset Tier Table

| Key | Type | Default | What it does | Verified at |
|---|---|---|---|---|
| `green` | list[str] | `[]` | Read-only / planning tier. Flags passed to prevent modifications and restrict tool actions to analysis and reading. | `(verified: cowbell.py:764, 2128-2130, 2183-2185)` |
| `yellow` | list[str] | `[]` | Standard edit tier (Cowbell default). Flags passed to permit file modifications within the workspace while prompting on commands or external actions. | `(verified: cowbell.py:764, 2128-2130, 2183-2185)` |
| `red` | list[str] | `[]` | Unrestricted / bypass tier. Flags passed to disable interactive permission prompts and approval checks. | `(verified: cowbell.py:764, 2128-2130, 2183-2185)` |

### Seed Lane Mappings

The table below summarizes the flag mappings established in `harnesses.toml` for supported agent kinds:

| Kind | `green` (Plan / Read-only) | `yellow` (Edit / Workspace-write) | `red` (Bypass / Full-access) |
|---|---|---|---|
| `claude` | `["--permission-mode", "plan"]` | `["--permission-mode", "acceptEdits"]` | `["--permission-mode", "bypassPermissions"]` |
| `grok` | `["--permission-mode", "plan"]` | `["--permission-mode", "acceptEdits"]` | `["--always-approve"]` |
| `codex` | `["--sandbox", "read-only"]` | `["--sandbox", "workspace-write"]` | `["--dangerously-bypass-approvals-and-sandbox"]` |
| `pi` | `["--tools", "read"]` | `["--tools", "read,edit,write"]` | `[]` |
| `omp` | `["--approval-mode", "always-ask"]` | `["--approval-mode", "write"]` | `["--approval-mode", "yolo"]` |
