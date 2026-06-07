#!/usr/bin/env bash
# Quick scripted demo of DomainForge — great for asciinema or a manual screen
# recording. Runs the fast preset on two seed words and checks a handful of names.
set -euo pipefail

cd "$(dirname "$0")"

# Resolve a launcher that exists on this machine. Prefer the installed CLI
# (no Python prefix), then python3, then python — so this works whether or not
# `python` is aliased (modern macOS/Linux ship only `python3`).
if command -v domainforge >/dev/null 2>&1; then
  DF=(domainforge)
elif command -v python3 >/dev/null 2>&1; then
  DF=(python3 -m domainforge)
elif command -v python >/dev/null 2>&1; then
  DF=(python -m domainforge)
else
  echo "No domainforge / python3 / python found on PATH." >&2
  exit 1
fi

"${DF[@]}" --fast --base "rune,forge" --check 12 -y

echo
echo "Open the shortlist:  cat domainforge_out/shortlist.md"
