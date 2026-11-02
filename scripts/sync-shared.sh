#!/usr/bin/env bash
# Copy each skill in shared/skills/ into every domain plugin (code, work).
#
# shared/skills/<skill>/ is the only copy to edit. The copies under
# plugins/<domain>/skills/<skill>/ exist because a plugin can only ship
# files inside its own directory. scripts/validate.sh fails if a copy
# drifts from its source, so run this after every edit to shared/skills/.
#
# Usage: scripts/sync-shared.sh   (from anywhere inside the repo)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DOMAINS=(code work)

for src in shared/skills/*/; do
  skill="$(basename "$src")"
  for domain in "${DOMAINS[@]}"; do
    dest="plugins/$domain/skills/$skill"
    rm -rf "$dest"
    mkdir -p "$(dirname "$dest")"
    cp -R "${src%/}" "$dest"
    echo "synced: $dest"
  done
done
