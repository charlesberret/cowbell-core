# Cowbell acceptance results

Copy this file to `docs/uat/RESULTS-YYYY-MM-DD-<name>.md` and fill that copy.
Leave this template blank.

Version under test (`cowbell --version`):

Machine (OS, Python, `pipx --version`):

| # | Scenario | Tester | Date | Pass/fail | Notes |
| --- | --- | --- | --- | --- | --- |
| 01 | [stranger install](01-stranger-install.md) | | | | |
| 02 | [python 3.9 trap](02-python-39.md) | | | | |
| 03 | [empty directory](03-empty-directory.md) | | | | |
| 04 | [one agent installed](04-one-agent.md) | | | | |
| 05 | [several agents, several running](05-several-agents.md) | | | | |
| 06 | [`new` with flags](06-new-flags.md) | | | | |
| 07 | [`status` and `catalog`](07-status-catalog.md) | | | | |
| 08 | [`reconcile --dry-run`](08-reconcile-dry-run.md) | | | | |
| 09 | [keyboard and mouse](09-keyboard-mouse.md) | | | | |
| 10 | [no herdr binary](10-no-herdr.md) | | | | |
| 11 | [unix_user place](11-unix-user.md) | | | | |
| 12 | [uninstall](12-uninstall.md) | | | | |

Pass/fail is `pass` or `fail`. Copy any **UNCLEAR** line from the scenario into Notes.
