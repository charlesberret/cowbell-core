# Join requires-check into local main

## Decision

Local main is the merge of `requires-check` into the icon-font line. Both `36a18eb` and `a173bfc` are in its history. The font commits that count are `313527f` and `a173bfc`. (verified: `git show -s --format='%h %p' cb790ca` → parents `a173bfc 12dd4d5`; `git merge-base --is-ancestor` of each of `36a18eb`, `a173bfc`, `313527f` against `main` → all exit 0)

**Not decided:** a push of local main, a vendor into the plugin checkout, and a 0.3.3 cut.

## Decided by

The sprint director, 2026-11-12, under the goal picked at kickoff: "Picker refuses a stale harness." The merge order is the sprint review of that night. This is not a separate ruling on a push. DRAFT — needs maintainer check: decision attribution (who decided, the goal, the date) is a social fact, not checkable from the tree.

## Force

snapshot

## Context

`requires-check` at `36a18eb` had `requires`, `check`, and `cowbell accept`. Local main at `a173bfc` had the icon-font work and did not contain `36a18eb`. The two lines diverged at `865e7d5`. The picked goal required both commits on local main, with the picker mark, the README, the seed note, a green suite, and a workflow. (verified: `git merge-base 36a18eb a173bfc` → `865e7d52af0e1af6e6f108d7401a34a36cb4299d`; `git show 36a18eb:cowbell.py` carries `requires` (:887), `check` (:874/:900), `cmd_accept` (:3894), `cmd == "accept"` (:6320); `git merge-base --is-ancestor 36a18eb a173bfc` → exit 1, not contained; `git log -1 a173bfc` → "docs: changelog for the icon font fallback") DRAFT — needs maintainer check: the picked goal and its required pieces.

## Options set aside

- Cherry-pick `36a18eb` onto main. A cherry-pick is a new commit, so `36a18eb` itself would not be an ancestor of main. (verified: `git log -1 36a18eb` → "feat: requires and check on harness rows"; `git merge-base --is-ancestor 36a18eb a173bfc` → exit 1, it was not on the pre-merge line; the cherry-pick-is-a-new-commit clause is git semantics)
- Revive `886eca84` and `367653b1`. Those font commits had been reset off `requires-check`. The font that counts was already on main as `313527f` and `a173bfc`. (verified: `git merge-base --is-ancestor 886eca84 36a18eb` → exit 1, `367653b1` → exit 1 — both off `requires-check`; `git log -1 886eca84` → "feat: icon font fallback and `cowbell font install`" and `git log -1 367653b1` → "docs: changelog for the icon font fallback", the same subjects `313527f`/`a173bfc` carry; `313527f` and `a173bfc` are ancestors of `main` → exit 0)
- Leave the lines unjoined. The goal required both commits on local main. DRAFT — needs maintainer check: goal attribution.

## Consequences

Local main is `cb790ca` (`Merge branch 'requires-check'`), which contains `12dd4d5` (`feat: show a stale check on the picker`). The changelog keeps four Unreleased bullets: the icon font, then requires/check, then the debug trace, then save-as. `cowbell.py` and the tests auto-merged. The suite on that main was `Ran 384 tests in 51.463s` then `OK`. (verified: `git log -1 cb790ca` → "Merge branch 'requires-check'"; `git merge-base --is-ancestor 12dd4d5 cb790ca` → exit 0; `CHANGELOG.md` Unreleased has exactly four bullets in the stated order; `git show --cc cb790ca` → combined diffs only on `CHANGELOG.md` and `README.md`, none on `cowbell.py` or `tests/test_cowbell.py` — consistent with auto-merge; stale clause: the `main` tip has since moved to `962f715` — `git log --oneline cb790ca..main` lists 3 later commits) DRAFT — needs maintainer check: the recorded suite output "Ran 384 tests in 51.463s" then "OK" is a historical log line, not re-checkable.

Local main is ahead of origin and behind it by the two commits that were already on origin. A push was not done. The plugin checkout was not vendored. (verified: `git rev-list --left-right --count origin/main...main` → `2 18` — ahead 18, behind 2; the two origin commits are `a973cbb` and `4a3288d` per `git log --oneline main..origin/main`; ahead 18 confirms still unpushed) DRAFT — needs maintainer check: "The plugin checkout was not vendored" refers to a checkout outside this tree.

## Revisit when

Someone is about to push local main, or those two origin commits need to come into this line.
