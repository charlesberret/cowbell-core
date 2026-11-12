#!/usr/bin/env bash
# Fail if tracked public files carry house-local paths or coordination junk.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "public-surface-scan: not a git checkout" >&2
  exit 1
fi

mapfile -t files < <(git ls-files)
if ((${#files[@]} == 0)); then
  echo "public-surface-scan: no tracked files" >&2
  exit 1
fi

fail=0
report() {
  echo "public-surface-scan: $*" >&2
  fail=1
}

pat='/Users/[^/[:space:]]+|\.coordination/|\.inbox/|HANDOFF[^[:space:]]*\.md|LAB-[0-9]+'

for f in "${files[@]}"; do
  [[ -f "$f" ]] || continue
  case "$f" in
    scripts/public-surface-scan.sh | .gitignore) continue ;;
  esac
  hits="$(grep -nE "$pat" "$f" 2>/dev/null || true)"
  if [[ -n "$hits" ]]; then
    while IFS= read -r line; do
      report "$f: $line"
    done <<<"$hits"
  fi
done

if ((fail)); then
  exit 1
fi
echo "public-surface-scan: ok (${#files[@]} tracked files)"
exit 0
