# 11 · `unix_user` place

Not run in this pack. The privilege checks are QA-C6 (LAB-632).

## Precondition

A place with `unix_user` is configured only as the README describes it. You
do not create the other Unix account, do not install `nono`, and do not run
`sudo` for this scenario.

## Steps

1. Read this file and stop.
2. Open QA-C6 (LAB-632) and run that pack when it exists:
   `scripts/uat/privilege/run.sh` in its container, and the macOS steps in
   `docs/uat/11-privilege.md`.
3. Do not copy those results into this scenario's box. QA-C6 has its own
   PASS/FAIL lines. On this sheet, mark 11 as `pass` only to record that you
   did not run the privilege pack here, and point Notes at the QA-C6 result.
   If you did run it by mistake, mark `fail` and say so.

## Expected

No cowbell command is run. There is no output and no exit code.

What this scenario is pointing at, from the code, so the pointer is not a
guess:

- `unix_confine` drops to the place's `unix_user` (`getpwnam`). If the
  process is not already that user, the command is prefixed with
  `agent-run <user> --` when `agent-run` is on `PATH`, otherwise
  `sudo -u <user> --`.
- `require_uid` with no `unix_user` raises
  `cowbell: refused — no unix_user for <path>; set [places.*] unix_user or use agent-run <uid> -- …`.
- A `unix_user` that is not on the host raises
  `cowbell: unix_user '<name>' is not on this host`.
- `nono_profile` wraps the command as
  `nono run --silent --profile <path> --allow-cwd --` inside the uid drop.
  If `nono` is not on `PATH`:
  `cowbell: nono is not on PATH (needed for this place)`.
- If neither `agent-run` nor `sudo` is on `PATH`:
  `cowbell: cannot drop to unix user '<name>' (agent-run is not installed and sudo is not on PATH)`.
- A harness the place does not allow is refused before that drop. The
  message is the one in scenario 06:
  `cowbell: <id> may not start in place <name> (allowed: …)`.

Those strings are `unix_confine` and `cmd_new` in `cowbell.py`. QA-C6 is
where they are executed on a machine with two uids. This file does not
execute them.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

QA-C6's own writeup is `docs/uat/11-privilege.md` plus
`scripts/uat/privilege/`. Neither is part of this pack. If that path is
still missing, Notes say "QA-C6 pack not in the tree yet" and the row is
`pass` for *this* scenario (the pointer was followed by not running it).
