# Debug Trace Runbook

When cowbell starts slowly or an agent launch hesitates, the opt-in launch trace records millisecond-precision timing for every startup phase. Tracing is completely off by default so regular launches incur zero disk writes. When enabled, cowbell appends timed events to a private state log covering herdr IPC calls, session history scans, trust checks, canonical name resolution, process scans, UI frame assembly, shell readiness waits, requirement verification, acceptance checks, and process execution. (verified: cowbell.py:73-75; CHANGELOG.md:8-9)

## Quick Start

Enable tracing for a single run using `--debug`:

```bash
cowbell --debug
```
(verified: cowbell.py:27, 6444-6454)

Or enable tracing across commands using the environment variable:

```bash
export COWBELL_DEBUG=1
cowbell
```
(verified: cowbell.py:27, 107)

Follow the trace in real time:

```bash
tail -f "${XDG_STATE_HOME:-$HOME/.local/state}/cowbell/debug.log"
```
(verified: cowbell.py:146, 265-270)

Override the log path directly:

```bash
COWBELL_DEBUG=1 COWBELL_DEBUG_LOG=/tmp/cowbell-debug.log cowbell
```
(verified: cowbell.py:142-144)

## Enabling and Precedence

Tracing can be activated via CLI flags or environment variables:

1. **CLI Flag (`--debug`):** Passing `--debug` before `--` forces tracing on for that invocation, even if `COWBELL_DEBUG` is unset or empty. The flag is stripped from cowbell's arguments before subcommands or options are evaluated. Any `--debug` occurring *after* `--` is preserved untouched as an argument for the launched harness or subcommand. (verified: cowbell.py:105-106, 6444-6454, 6458)
2. **Environment Variable (`COWBELL_DEBUG`):** Tracing is active when `COWBELL_DEBUG` is set to any recognized truthy string: `"1"`, `"true"`, `"yes"`, `"on"`, or `"verbose"` (case-insensitive, whitespace-trimmed). Any other value leaves tracing disabled. (verified: cowbell.py:76, 107)

### Log Destination

The active log path is determined in order of precedence:

1. `COWBELL_DEBUG_LOG`: If set and non-empty, cowbell expands `~` and writes directly to this path. (verified: cowbell.py:142-144)
2. `COWBELL_STATE_DIR`: If set, cowbell writes to `$COWBELL_STATE_DIR/debug.log`. (verified: cowbell.py:146, 266-270)
3. `XDG_STATE_HOME`: If set, cowbell writes to `$XDG_STATE_HOME/cowbell/debug.log`. (verified: cowbell.py:146, 267-270)
4. Default state directory: Cowbell writes to `~/.local/state/cowbell/debug.log`. (verified: cowbell.py:146, 267-270)

The enclosing directory is automatically created if it does not already exist. (verified: cowbell.py:156, 269)

## File Safety and Operational Guarantees

Tracing is designed to never compromise privacy, consume unbounded disk space, or interrupt launches:

- **Private Permissions (0600):** The log file is created and set to permission mode `0600` (`-rw-------`), ensuring only the file owner can read or write trace records. (verified: cowbell.py:160)
- **1 MB Single Rotation:** Before opening or appending to the log file, cowbell checks its size against `DEBUG_LOG_MAX = 1_000_000` bytes (1 MB). If the file exceeds 1 MB, it is atomically replaced with a single backup named `debug.log.1`. Older backups are discarded; rotation never creates multiple numbered files. (verified: cowbell.py:77, 157-158)
- **Silent Failure:** If any write or flush fails with an `OSError` (such as a read-only filesystem or a full disk), cowbell sets an internal flag (`self._dead = True`) and silently disables all subsequent logging for the remainder of the process. Debugging errors are suppressed so tracing never breaks or aborts an agent launch. (verified: cowbell.py:93, 103-104, 138-139)
- **Bounded Lengths:** Each output line is capped at 2,000 characters. In addition, each field value has newlines replaced with spaces, leading and trailing whitespace trimmed, and is truncated to 300 characters. Field values containing whitespace or double quotes are quoted with double quotes. (verified: cowbell.py:84-89, 136)

### Privacy

The log may contain paths and flag names from harness configuration. It is written mode 0600 and only when `COWBELL_DEBUG` (or `--debug`/`COWBELL_DEBUG_LOG`) is set. It should not be shared unreviewed. The log path is opened without following a symlink and must be a regular file; anything else turns tracing off for that run.

**What is masked.** Command lines in `start`, `requires`, `exec`, `spawn`, `raise` and `herdr` events keep the executable's basename and flag names. Masked as `***`: every word you typed after `--` in `cowbell new`, every word after a literal `--`, the value of a flag whose name has a part like `key`, `token`, `secret`, `pass`, `password`, `auth`, `bearer`, `prompt` or `instruction` (`--api-key`, `--system-prompt`; a flag such as `--dangerously-bypass-approvals-and-sandbox` is not one), and every `NAME=value` word. A bare `--` is never taken as a flag's value. The herdr `pane run` event is built from the masked argv, not from the packed launch line.

**What is not masked (stated limit).** Free text is masked only where it has a credential shape: `sk-…`/`pk-…` keys, `ghp_…`-style tokens, `Bearer …`, `user:pass@` in a URL, `NAME=value` with a sensitive name, and a sensitive flag with its value. The last line a harness `check` prints (the `check` event's `detail`) and herdr's error text (`err` on a failed `herdr` event) can hold any other word a tool chose to print, and those words are written as they are. A secret with no recognizable shape in that output reaches the log. Do not point a `check` at a command that prints one, and treat the log as sensitive.

The same limit applies inside command lines: sensitivity is judged by the flag's name, so the value of a single-letter flag (`-p`, `-u`, `-H`, `--cookie`) is logged as it is. Put secrets only behind flags whose names name them.

## Trace Line Format and Event Reference

Every trace entry is written as a single line with space-separated columns:

```text
<ISO-8601-UTC-TIMESTAMP>  <ELAPSED-SECONDS>s  <KIND>  <FIELD1>=<VAL1> <FIELD2>=<VAL2> ...
```
(verified: cowbell.py:126-128)

- **Timestamp:** UTC ISO 8601 string with millisecond resolution, ending in `Z` (for example, `2026-11-13T18:17:18.781Z`). (verified: cowbell.py:127)
- **Elapsed Seconds:** Elapsed seconds since the trace instance was initialized, formatted to three decimal places and right-aligned to 8 characters (for example, `   0.042s`). (verified: cowbell.py:100, 128)
- **Kind:** Name of the operation or phase being logged. (verified: cowbell.py:128)
- **Fields:** Key-value pairs detailing phase parameters, elapsed sub-millisecond durations (`ms=`), counts, return codes, and identifiers. Empty and `None` fields are omitted. (verified: cowbell.py:126)

### Event Kinds

| Kind | Trigger and Meaning | Emitted Fields | Verified Source |
|---|---|---|---|
| `start` | CLI invocation initialization or native agent start retry on busy shell | `argv`, `cwd` (at startup); `pane`, `attempt`, `busy` (on retry) | cowbell.py:3072, 6460 |
| `host` | Runtime host environment context detected (picker/direct mode, herdr availability) | `mode`, `herdr` (0 or 1) | cowbell.py:6395 |
| `frame` | Render cycle for the interactive picker UI frame | `ms`, `history_ms`, `registry_ms`, `live`, `cold`, `startable` | cowbell.py:6209-6210 |
| `history` | Session history scan for prior agent conversations | `store` (`"claude"`, `"grok"`, or `"as-user"`), `ms`, `files`, `hit`, `miss`, `user`, `rc` | cowbell.py:1321, 1400, 1464 |
| `trust` | Advisory reach/privilege evaluation for a tool | `tool`, `ms`, `verdict`, `rc`, `err` | cowbell.py:1557, 1563, 1566, 1569 |
| `names` | Canonical name computation across unpinned sessions | `ms`, `reads` | cowbell.py:1679 |
| `ps` | Census of live agent processes scanned outside herdr | `ms`, `scanned`, `agents`, `ps` | cowbell.py:2342 |
| `herdr` | IPC request to the herdr terminal harness socket | `ms`, `argv`, `rc`, `err`, `bytes` | cowbell.py:2798, 2801, 2805, 2809, 2815, 2817, 2821, 2823 |
| `shell` | Polling for shell process readiness inside a newly allocated pane | `pane`, `ms`, `polls`, `ready` | cowbell.py:3054 |
| `requires` | Execution of a harness `requires` pre-launch command | `harness`, `cmd` | cowbell.py:895 |
| `check` | Execution of a harness acceptance `check` command | `harness`, `ok`, `detail` | cowbell.py:907 |
| `raise` | Multi-phase agent raise lifecycle inside herdr | `phase` (`"begin"`, `"pane"`, `"fail"`, `"done"`), `harness`, `agent`, `name`, `resume`, `how`, `pane`, `ms`, `mode`, `cmd` | cowbell.py:3085-3086, 3110, 3128, 3161 |
| `exec` | Direct process handover (`os.execv`) replacing cowbell in the current terminal | `harness`, `cmd` | cowbell.py:2649 |
| `spawn` | Detached or background agent process spawn | `harness`, `pid`, `cmd` | cowbell.py:2687 |

## Reading a Slow Start: Worked Example

Below is a trace excerpt showing a slow startup where cowbell took 1.485 seconds before rendering its first picker frame:

```text
2026-11-13T18:00:00.001Z     0.000s  start    argv="(default)" cwd=/workspace/project
2026-11-13T18:00:00.003Z     0.002s  host     mode=picker herdr=1
2026-11-13T18:00:00.018Z     0.017s  herdr    ms=14 rc=0 argv="api snapshot" bytes=4096
2026-11-13T18:00:00.045Z     0.044s  ps       ms=26 scanned=180 agents=2 ps=1
2026-11-13T18:00:00.210Z     0.209s  history  store=claude ms=164 files=48 hit=12 miss=36
2026-11-13T18:00:00.215Z     0.214s  names    ms=4 reads=2
2026-11-13T18:00:01.465Z     1.464s  trust    tool=claude ms=1250 verdict=unknown rc=1
2026-11-13T18:00:01.486Z     1.485s  frame    ms=1468 history_ms=164 registry_ms=1295 live=2 cold=1 startable=4
```

### Diagnosing the Delay

1. **Locate the time leap:** Scan the elapsed seconds column (`0.000s` -> `0.214s` -> `1.464s`). A jump of 1.250 seconds occurred between `names` and `trust`.
2. **Identify the responsible phase:** The `trust` line records `ms=1250 tool=claude verdict=unknown rc=1` (verified: cowbell.py:1566). The external trust validation tool hesitated before exiting with return code 1.
3. **Inspect cache performance:** On the `history` line, `store=claude ms=164 files=48 hit=12 miss=36` shows that 36 session files required cold parsing from disk. Subsequent frames will benefit from cache hits (verified: cowbell.py:1313-1321).
4. **Correlate with frame totals:** The `frame` summary line reports `ms=1468 history_ms=164 registry_ms=1295`. This confirms that 1,295 ms of the 1,468 ms frame render duration was spent during registry creation (which includes the 1,250 ms trust evaluation). (verified: cowbell.py:6206-6210)

## Contributor Reference: The `Trace.event` Argument Trap

When adding or updating trace instrumentation in `cowbell.py`, be careful of the method signature of `Trace.event`:

```python
def event(self, kind: str, **fields) -> None:
    if not self.enabled():
        return
    ...
```
(verified: cowbell.py:123-125)

### The Trap

The first positional argument to `Trace.event` is named `kind`, which designates the trace event type (such as `"start"`, `"herdr"`, or `"raise"`).

If a caller attempts to pass the agent or harness kind as a keyword argument named `kind=`:

```python
# BROKEN: causes TypeError!
trace.event("raise", phase="begin", kind=h.get("kind", ""))
```

Python's function call mechanism detects multiple values for parameter `kind` and immediately raises:

```text
TypeError: Trace.event() got multiple values for argument 'kind'
```

### Critical Consequence

Because Python performs parameter binding **before** entering the function body, this `TypeError` is raised even when tracing is disabled (`trace.enabled() == False`). A buggy trace call will crash regular, untraced launches for all users. (verified: cowbell.py:123-124)

### Correct Practice

To record the underlying agent type on an event, use an alternate keyword name such as `agent=`:

```python
# CORRECT: passes the harness kind as agent=
trace.event("raise", phase="begin", harness=h.get("id", ""), agent=h.get("kind", ""),
            name=name, resume=1 if resume_id else 0)
```
(verified: cowbell.py:3085-3086)
