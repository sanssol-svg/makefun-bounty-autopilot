#!/usr/bin/env bash
# Submit ONE make.fun bounty end-to-end using the makefun CLI.
#
# This is a REFERENCE driver. The full auto-submit pipeline also records an
# agent "transcript" (the coding session) which make.fun requires for the
# `thinking_reproduces` / `thinking_revised` gates. See README.md.
#
# Prerequisites (all OUTSIDE this repo — never commit them):
#   - makefun CLI (makefun.mjs) from a bounty kit, on your PATH
#   - keypair at ~/.makefun/keypair.json
#   - credentials at ~/.makefun/credentials (created by `makefun connect`)
#
# Usage:
#   ./submit_one.sh <competition-slug> <source-dir> <title>
set -euo pipefail

SLUG="${1:?competition slug required}"
SOURCE="${2:?source dir required}"
TITLE="${3:?title required}"

KEYPAIR="$HOME/.makefun/keypair.json"
DRAND="https://api.drand.sh"

echo "▶ init $SLUG in $SOURCE"
cd "$SOURCE"
makefun init --competition "$SLUG" --keypair "$KEYPAIR" --drand-relay "$DRAND"

echo "▶ (record agent coding session here — see README)"

echo "▶ bundle transcripts"
makefun bundle --repo "$SOURCE" --session "$SESSION_DB" \
  --session-id "$SESSION_ID" --no-discover --out /tmp/bundle.tar.gz

echo "▶ check (do NOT skip this — it catches a bad transcript before submit)"
makefun check --repo "$SOURCE" --transcripts /tmp/bundle.tar.gz

echo "▶ submit"
makefun submit --competition "$SLUG" --source "$SOURCE" \
  --commit "$(git -C "$SOURCE" rev-parse HEAD)" \
  --bundle /tmp/bundle.tar.gz --title "$TITLE" --keypair "$KEYPAIR"
