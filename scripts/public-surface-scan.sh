#!/bin/sh
# Public-surface scan. Exit 0 when the tree is clean, 1 when a denylist token
# remains. Usage: public-surface-scan.sh [root]
#
# Default root is the repo (the parent of this script). The denylist is
# assembled at runtime so this file is not itself a hit. When the scan root
# contains tests/fixtures/public-surface, that corpus is skipped; pass the
# clean or dirty fixture as root to scan it. Generated trees (.git,
# .ruff_cache, __pycache__, dist) are skipped so a local run matches a
# checkout.
#
# Search is grep -rnE (extended regular expressions, no \b: word edges are
# [^A-Za-z0-9_]). The allowlist in public-surface-allow.txt is applied with
# Python re, which is what lets a product word be exempt without dropping
# the rest of the line.
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
ALLOW=$SCRIPT_DIR/public-surface-allow.txt

if [ "${1:-}" ]; then
  ROOT=$(CDPATH= cd -- "$1" && pwd)
else
  ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
fi

if [ ! -f "$ALLOW" ]; then
  echo "public-surface: missing allowlist $ALLOW" >&2
  exit 2
fi

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "public-surface: python is required to apply the allowlist" >&2
  exit 2
fi

# Fragments are quoted apart so the source text is not a denylist match.
wb='(^|[^A-Za-z0-9_])'
we='([^A-Za-z0-9_]|$)'
p_users="/Users""/"
p_home="/home""/[a-z]+"
p_tilde_cloud="~/clo""ud"
p_cloud_sync="cloud/s""ync"
p_git_projects="git-pro""jects"
p_hosts="avi""cenna|hes""iod|fic""ino|poly""tonic|relay""tower|ana""ximander|enco""smic|do""lan"
p_ips="10\\.100\\.0""\\.|100\\.64\\.0""\\.|192\\.168""\\."
p_house="Major""domo|club""house|agent-""deck|World ""Zero|brain""trust|Is""runa|Ket""tle|tetra""fold|Xan""adu|majordomo-""inbox|CLAUDE-""base|constitu""tion|handoff""-"
p_linear="${wb}(LAB|SYS|OFC|DSK)-[0-9]+${we}"
p_sk="sk-[A-Za-z0-9]""{10,}"
p_xox="xo""xb-"
p_ghp="ghp_[A-Za-z0-9]""{20,}"
p_key="BEGIN [A-Z ]""*PRIVATE KEY"

pattern="${p_users}|${p_home}|${p_tilde_cloud}|${p_cloud_sync}|${p_git_projects}|${p_hosts}|${p_ips}|${p_house}|${p_linear}|${p_sk}|${p_xox}|${p_ghp}|${p_key}"

hits=$(mktemp)
patfile=$(mktemp)
trap 'rm -f "$hits" "$patfile"' EXIT INT TERM
printf '%s' "$pattern" > "$patfile"

cd "$ROOT"
# --exclude-dir=public-surface skips the fixture corpus when this root
# contains it. Scanning the corpus itself (its root is clean/ or dirty/)
# does not exclude those files.
set +e
grep -rnE -I \
  --exclude-dir=.git \
  --exclude-dir=.ruff_cache \
  --exclude-dir=__pycache__ \
  --exclude-dir=dist \
  --exclude-dir=public-surface \
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
import re
import sys

allow_path, pat_path, hits_path = sys.argv[1:]
pattern = open(pat_path, encoding="utf-8").read()
try:
    forbidden = re.compile(pattern)
except re.error as exc:
    print(f"public-surface: bad denylist: {exc}", file=sys.stderr)
    sys.exit(2)

exempt = []
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
  # Command substitution ate the final newline; put it back for the log.
  printf '%s\n' "$kept"
  printf 'public-surface: %s hit(s)\n' "$(printf '%s\n' "$kept" | grep -c .)" >&2
  exit 1
fi

echo "public-surface: clean"
exit 0
