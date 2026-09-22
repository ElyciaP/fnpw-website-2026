#!/usr/bin/env bash
# Bring the WordPress side up to date with the static build.
#
# Run from the repo root whenever you have changed global.css, main.js or any
# project page:
#   bash wp/tools/sync.sh
#
# Then commit in GitHub Desktop, and re-run the project import in Local.
set -euo pipefail
cd "$(dirname "$0")/../.."

cp assets/css/global.css wp/themes/fnpw-2026/assets/css/global.css
cp assets/js/main.js     wp/themes/fnpw-2026/assets/js/main.js
echo "Copied global.css and main.js into the theme"

python3 wp/tools/build_project_bundle.py
