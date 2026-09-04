#!/usr/bin/env bash
# Render, then publish ONLY an explicit allowlist of paths.
#
# Why an allowlist: .gitignore is itself a published file, so anything named in
# it is visible on GitHub. Private exclusions live in .git/info/exclude (local
# only), and this script never uses `git add -A` on the whole tree. Nothing
# reaches the remote unless it is named in PUBLISH below.
#
# Usage:  ./tools/publish.sh "what changed"
set -euo pipefail
cd "$(dirname "$0")/.."
MSG="${1:-Update coursework website}"

PUBLISH=(
  _quarto.yml
  index.qmd
  about.qmd
  styles.css
  .gitignore
  ISSS626-GAA.Rproj
  Hands-on_Ex
  _freeze
  _site
  tools
)

# Anything matching these must never be staged, whatever else happens.
DENY='(^|/)(CLAUDE\.md|_notes/|\.env|.*\.Rhistory|.*\.RData|Rplots\.pdf|\.DS_Store)$'

echo "→ rendering…"
quarto render >/dev/null

echo "→ staging allowlist…"
git reset -q                       # clear the index; start from nothing
for p in "${PUBLISH[@]}"; do
  [ -e "$p" ] && git add -A -- "$p"
done

echo "→ checking for anything that must not be published…"
if git diff --cached --name-only | grep -aE "$DENY"; then
  echo "ABORTED: a denied path was staged (listed above)."
  git reset -q
  exit 1
fi

echo
echo "Files in this commit:"
git diff --cached --name-status | sed 's/^/  /'
echo
echo "  total: $(git diff --cached --name-only | wc -l | tr -d ' ') files"
