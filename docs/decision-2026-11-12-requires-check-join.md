# Join requires-check into local main

## Decision

Local main is the merge of `requires-check` into the icon-font line. Both `36a18eb` and `a173bfc` are in its history. The font commits that count are `313527f` and `a173bfc`. (verified: `git show -s --format='%h %p' cb790ca` → parents `a173bfc 12dd4d5`; `git merge-base --is-ancestor` of each of `36a18eb`, `a173bfc`, `313527f` against `main` → all exit 0)

**Not decided:** a push of local main and a 0.3.3 cut.

## Decided by

Maintainer review, 2026-11-12, unifying the requires/check capability with the icon-font branch.

## Force

snapshot

## Context

`requires-check` at `36a18eb` had `requires`, `check`, and `cowbell accept`. Local main at `a173bfc` had the icon-font work and did not contain `36a18eb`. The two lines diverged at `865e7d5`. Both features were required on main alongside the picker mark, README updates, seed catalog notes, a green test suite, and CI workflow. (verified: `git merge-base 36a18eb a173bfc` → `865e7d52af0e1af6e6f108d7401a34a36cb4299d`; `git show 36a18eb:cowbell.py` carries `requires` (:887), `check` (:874/:900), `cmd_accept` (:3894), `cmd == "accept"` (:6320); `git merge-base --is-ancestor 36a18eb a173bfc` → exit 1, not contained; `git log -1 a173bfc` → "docs: changelog for the icon font fallback")

## Options set aside

- Cherry-pick `36a18eb` onto main. A cherry-pick is a new commit, so `36a18eb` itself would not be an ancestor of main. (verified: `git log -1 36a18eb` → "feat: requires and check on harness rows"; `git merge-base --is-ancestor 36a18eb a173bfc` → exit 1, it was not on the pre-merge line; the cherry-pick-is-a-new-commit clause is git semantics)
- Revive `886eca84` and `367653b1`. Those font commits had been reset off `requires-check`. The font that counts was already on main as `313527f` and `a173bfc`. (verified: `git merge-base --is-ancestor 886eca84 36a18eb` → exit 1, `367653b1` → exit 1 — both off `requires-check`; `git log -1 886eca84` → "feat: icon font fallback and `cowbell font install`" and `git log -1 367653b1` → "docs: changelog for the icon font fallback", the same subjects `313527f`/`a173bfc` carry; `313527f` and `a173bfc` are ancestors of `main` → exit 0)
- Leave the lines unjoined. Maintaining separate feature lines would leave requires/check and icon fonts disconnected in releases.

## Consequences

Local main is `cb790ca` (`Merge branch 'requires-check'`), which contains `12dd4d5` (`feat: show a stale check on the picker`). The changelog keeps four Unreleased bullets: the icon font, then requires/check, then the debug trace, then save-as. `cowbell.py` and the tests auto-merged. The suite on that main was `Ran 384 tests in 51.463s` then `OK`. (verified: `git log -1 cb790ca` → "Merge branch 'requires-check'"; `git merge-base --is-ancestor 12dd4d5 cb790ca` → exit 0; `CHANGELOG.md` Unreleased has exactly four bullets in the stated order; `git show --cc cb790ca` → combined diffs only on `CHANGELOG.md` and README.md, none on `cowbell.py` or `tests/test_cowbell.py` — consistent with auto-merge; stale clause: the `main` tip has since moved to `962f715` — `git log --oneline cb790ca..main` lists 3 later commits)

Before the second merge, local main was ahead 22 of origin/main and behind 2 (`git rev-list --left-right --count origin/main...main` → `2 22`). The two origin commits were `a973cbb` (docs/errors.md error-message catalog) and `4a3288d` (seed-catalog tests). A push was not yet done.

## Revisit when

Someone is about to push local main, or those two origin commits need to come into this line.

## Addendum 2026-11-13

The two origin commits (`a973cbb` docs/errors.md error-message catalog and `4a3288d` seed-catalog tests) were brought into local main via merge `327769f` and completed in `d110a53`. Following this sync merge:
- Behind count is 0 (`git rev-list --left-right --count origin/main...main` now shows 0 left; local main is ahead 24, behind 0).
- The test suite is green: `Ran 394 tests in 40.153s` (`OK (skipped=1)`). (TODO for builder: verify final test count and timing on commit).
- Both history lines are unified into a single line ready for the 0.3.3 release candidate.
