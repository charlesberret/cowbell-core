# 11 · `unix_user` place

Not run in this pack. The privilege run is a separate pack: two Unix
accounts, `sudo` or `agent-run`, and optional `nono`. This scenario only
points at it.

## Precondition

You do not create another Unix account, do not install `nono`, and do not
run `sudo` for this scenario.

## Steps

1. Read this file and stop.
2. When `scripts/uat/privilege/run.sh` and `docs/uat/11-privilege.md` exist,
   that is the pack to run. Do not run it as part of this sheet.
3. On this sheet, mark 11 `pass` only to record that you stopped here. If
   you ran the privilege commands anyway, mark `fail` and say so.

## Expected

No cowbell command is run for this scenario. There is no output and no exit
code.

The strings below are `unix_confine` and `cmd_new` in `cowbell.py`. They are
what the other pack should see. They were read from the source, not produced
by a two-account run:

- With `unix_user` set and the process not already that user, the command is
  prefixed with `agent-run <user> --` when `agent-run` is on `PATH`, otherwise
  `sudo -u <user> --`.
- `require_uid` with no `unix_user` raises
  `cowbell: refused — no unix_user for <path>; set [places.*] unix_user or use agent-run <uid> -- …`.
- A name `getpwnam` does not know raises
  `cowbell: unix_user '<name>' is not on this host`.
- `nono_profile` wraps the inner command as
  `nono run --silent --profile <path> --allow-cwd --`.
  If `nono` is missing:
  `cowbell: nono is not on PATH (needed for this place)`.
- If neither `agent-run` nor `sudo` is on `PATH`:
  `cowbell: cannot drop to unix user '<name>' (agent-run is not installed and sudo is not on PATH)`.
- A harness the place does not allow is refused before that drop, with the
  scenario 06 line:
  `cowbell: <id> may not start in place <name> (allowed: …)`.

The `getpwnam` refusal was also hit on this machine by the unit test
`LaunchSheet.test_a_saved_harness_launches_like_its_source`, which calls
`spec_command` on a catalog whose user is `guest`. This host has no `guest`
account, and the test ended in
`SystemExit: cowbell: unix_user 'guest' is not on this host`. That is not a
substitute for the privilege pack.

## Pass / fail

```
[ ] pass
[ ] fail

Tester:
Date:
```

## Notes

`scripts/uat/privilege/` and `docs/uat/11-privilege.md` are not in this tree.
If they are still missing, Notes say so. The row can still be `pass` for
this scenario, because the step is to stop.
