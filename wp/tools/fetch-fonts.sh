#!/usr/bin/env bash
# Self-host the FNPW variable fonts.
#
# Run this from a normal terminal on your Mac, in the repo root:
#   bash wp/tools/fetch-fonts.sh
#
# It downloads Sora, Figtree and Caveat as variable woff2 files into the theme.
# Once they are present the theme stops calling Google Fonts, which is worth a
# measurable amount on the mobile performance score.
set -euo pipefail

DEST="wp/themes/fnpw-2026/assets/fonts"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
mkdir -p "$DEST"

fetch() {
  local family="$1" axis="$2" out="$3"
  local css url
  css=$(curl -fsS -A "$UA" "https://fonts.googleapis.com/css2?family=${family}:${axis}&display=swap")
  # Google returns several subsets. Take the one marked /* latin */, which is
  # the one with ordinary English letters in it.
  url=$(printf '%s' "$css" | awk '/\/\* latin \*\//{f=1} f' | grep -o 'https://[^)]*\.woff2' | head -1)
  if [ -z "$url" ]; then
    echo "Could not resolve a woff2 URL for ${family}" >&2
    return 1
  fi
  curl -fsS -o "${DEST}/${out}" "$url"
  echo "  ${out}  $(wc -c < "${DEST}/${out}" | tr -d ' ') bytes"
}

echo "Fetching fonts into ${DEST}"
fetch "Sora"    "wght@100..800" "sora-variable.woff2"
fetch "Figtree" "wght@300..900" "figtree-variable.woff2"
fetch "Caveat"  "wght@400..700" "caveat-variable.woff2"
echo "Done. Commit these files."
