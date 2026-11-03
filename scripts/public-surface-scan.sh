#!/bin/sh
# Public-surface scan. Exit 0 when the tree is clean, 1 when a denylist token
# remains. Usage: public-surface-scan.sh [root]
#
# Generic patterns only live in this file: home-directory prefixes, ~/cloud,
# RFC1918 and CGNAT addresses, Linear-style issue ids, token shapes, and
# private-key headers. Project-specific terms are not stored here. Set
# PUBLIC_SURFACE_TERMS to a file of extra extended regexes (one per line) or
# to the regex text itself (a CI secret). When that variable is unset, only
# the generic patterns run.
#
# The default scan skips this script and tests/fixtures/public-surface so the
# pattern list and the fixture corpus are not hits. Pass a fixture directory
# as root to scan it.
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
ALLOW=$SCRIPT_DIR/public-surface-allow.txt

if [ "${1:-}" ]; then
  ROOT=$(CDPATH= cd -- "$1" && pwd)
else
  ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
fi

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "public-surface: python is required to apply the allowlist" >&2
  exit 2
fi

octet='(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])'
# Edges are written out. BSD grep has no \b.
edge='(^|[^A-Za-z0-9_])'
end='([^0-9]|$)'
# 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, and 100.64.0.0/10.
p_rfc10="${edge}10(\\.${octet}){3}${end}"
p_rfc172="${edge}172\\.(1[6-9]|2[0-9]|3[0-1])(\\.${octet}){2}${end}"
p_rfc192="${edge}192\\.168(\\.${octet}){2}${end}"
p_cgnat="${edge}100\\.(6[4-9]|[7-9][0-9]|1[0-1][0-9]|12[0-7])(\\.${octet}){2}${end}"
p_issue='(^|[^A-Za-z0-9_])[A-Z][A-Z0-9]{1,9}-[0-9]+([^A-Za-z0-9_]|$)'
p_sk='sk-[A-Za-z0-9]{10,}'
p_xox='xoxb-'
p_ghp='ghp_[A-Za-z0-9]{20,}'
p_key='BEGIN [A-Z ]*PRIVATE KEY'

pattern="/Users/|/home/|~/cloud|${p_rfc10}|${p_rfc172}|${p_rfc192}|${p_cgnat}|${p_issue}|${p_sk}|${p_xox}|${p_ghp}|${p_key}"

# Extra terms: a path to a regex file, or the regex text (CI secret).
created_extra=""
if [ -n "${PUBLIC_SURFACE_TERMS:-}" ]; then
  if [ -f "$PUBLIC_SURFACE_TERMS" ]; then
    extra_src=$PUBLIC_SURFACE_TERMS
  else
    extra_src=$(mktemp)
    created_extra=$extra_src
    printf '%s\n' "$PUBLIC_SURFACE_TERMS" > "$extra_src"
  fi
  extra=$(awk '
    /^[[:space:]]*#/ || /^[[:space:]]*$/ { next }
    { if (s) s = s "|" $0; else s = $0 }
    END { print s }
  ' "$extra_src")
  if [ -n "$extra" ]; then
    pattern="${pattern}|${extra}"
  fi
fi

hits=$(mktemp)
patfile=$(mktemp)
trap 'rm -f "$hits" "$patfile" ${created_extra:+"$created_extra"}' EXIT INT TERM
printf '%s' "$pattern" > "$patfile"

cd "$ROOT"
set +e
grep -rnE -I \
  --exclude-dir=.git \
  --exclude-dir=.ruff_cache \
  --exclude-dir=__pycache__ \
  --exclude-dir=dist \
  --exclude-dir=public-surface \
  --exclude=public-surface-scan.sh \
  -e "$pattern" . > "$hits"
status=$?
set -e
if [ "$status" -eq 1 ]; then
  : # no matches
elif [ "$status" -ne 0 ]; then
  echo "public-surface: grep failed ($status)" >&2
  exit "$status"
fi

kept=$($PY - "$ALLOW" "$patfile" "$hits" <<'PY'
import os
import re
import sys

allow_path, pat_path, hits_path = sys.argv[1:]
pattern = open(pat_path, encoding="utf-8").read()
try:
    forbidden = re.compile(pattern)
except re.error as exc:
    print(f"public-surface: bad pattern: {exc}", file=sys.stderr)
    sys.exit(2)

exempt = []
if os.path.isfile(allow_path):
    for raw in open(allow_path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            exempt.append(re.compile(line))
        except re.error as exc:
            print(f"public-surface: bad allowlist regex {line!r}: {exc}", file=sys.stderr)
            sys.exit(2)

kept = []
for raw in open(hits_path, encoding="utf-8"):
    if raw.count(":") < 2:
        body = raw
        prefix = ""
    else:
        path, lineno, body = raw.split(":", 2)
        prefix = f"{path}:{lineno}:"
    body = body.rstrip("\n")
    stripped = body
    for cre in exempt:
        stripped = cre.sub("", stripped)
    if forbidden.search(stripped):
        kept.append(f"{prefix}{body}\n")

sys.stdout.write("".join(sorted(kept)))
PY
)

if [ -n "$kept" ]; then
  printf '%s\n' "$kept"
  printf 'public-surface: %s hit(s)\n' "$(printf '%s\n' "$kept" | grep -c .)" >&2
  exit 1
fi

echo "public-surface: clean"
exit 0
