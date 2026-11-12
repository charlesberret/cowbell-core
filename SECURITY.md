# Security

cowbell is a local CLI: it reads your catalog and agent session stores, spawns processes you choose, and can integrate with [herdr](https://github.com/herdrdev/herdr). It does not phone home. What matters for trust is what it can run as which user, and what it reads when building the Resume list.

## Privilege and confinement

### `unix_user` on a place or harness

When `[places.*] unix_user` or a harness row sets `unix_user`, launches in that place are meant to run as that Unix account, not as your interactive user.

- **Spawning agents:** `unix_confine` wraps the agent command. If you are not already that user, cowbell prefixes `agent-run <user> --` when that helper is on `PATH`, otherwise `sudo -u <user> --`. If neither exists, cowbell refuses rather than running privileged code as the wrong user.
- **Session-history discovery:** With `[defaults] session_history = "on"`, Resume can list sessions from each harness's store (`~/.claude/projects`, `~/.grok/sessions`, and similar). For a place with `unix_user`, discovery runs **as that launch user** (same `agent-run` / `sudo -u` boundary) so Resume never offers a session the confined process could not open. Only derived metadata (ids, times, titles) is read; transcript bodies are not loaded into cowbell.

`require_uid = true` on a place refuses to start if no `unix_user` is set.

### `nono_profile`

When a place (or defaults) sets `nono_profile`, the launch command is wrapped inside the uid drop as:

`nono run --silent --profile <path> --allow-cwd -- <agent …>`

`nono` must be on `PATH`. This is an optional extra confinement layer around the argv cowbell already built; cowbell does not ship `nono`.

### What this does not do

cowbell is not a sandbox. A harness row still runs whatever `command` or agent CLI you configured. Lanes and trust badges are advisory unless your catalog or external tools enforce harder rules.

## Data cowbell reads

- **Catalog and roster** under `~/.config/cowbell` and `~/.local/state/cowbell` (or `COWBELL_CONFIG_DIR` / `COWBELL_STATE_DIR`).
- **Optional trust helper** (`trust_command` in the catalog): cowbell invokes it with `subject`, `match`, and `badge` arguments; it must be a program you trust on your machine.
- **Session stores** only when `session_history` is enabled, as described above.

## Reporting a security issue

Please report suspected vulnerabilities privately:

1. Open a **[GitHub security advisory](https://github.com/charlesberret/cowbell-core/security/advisories/new)** for this repository, or
2. Email the maintainer via the contact on the GitHub profile linked from the repo.

Include steps to reproduce, your OS, Python version, and relevant catalog fragments (redact secrets). We will acknowledge receipt and aim to respond with a fix or assessment.

For general bugs that are not security-sensitive, use [GitHub Issues](https://github.com/charlesberret/cowbell-core/issues).
