#!/usr/bin/env bash
# Render the whole site, commit everything, push. Vercel redeploys itself.
# Usage:  ./tools/publish.sh "what changed"
set -e
cd "$(dirname "$0")/.."
MSG="${1:-Update coursework website}"

echo "→ rendering…"
quarto render

echo "→ committing…"
git add -A
if git diff --cached --quiet; then
  echo "  nothing to commit"
else
  git commit -q -m "$MSG"
fi

echo "→ pushing…"
git push -q

echo
echo "done. live in ~1 min:"
echo "  https://isss626-gaa.vercel.app/"
