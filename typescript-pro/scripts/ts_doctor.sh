#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"

have() { command -v "$1" >/dev/null 2>&1; }

say() { printf '%s\n' "$*"; }

say "TypeScript Doctor (read-only scan)"

if have rg; then
  RG=rg
else
  RG=grep
fi

# Detect tsconfig(s)
if [ -f "$ROOT/tsconfig.json" ]; then
  say "- Found tsconfig: $ROOT/tsconfig.json"
else
  say "- No tsconfig.json at repo root (scan may be incomplete)."
fi

# Common risky patterns
say ""
say "Suspicious patterns (if any):"
if [ "$RG" = "rg" ]; then
  rg -n --hidden --glob '!**/node_modules/**' --glob '!**/dist/**' --glob '!**/build/**' \
    "\\bany\\b|@ts-ignore|@ts-nocheck" "$ROOT" || true
else
  grep -R -n "\bany\b" "$ROOT" 2>/dev/null || true
  grep -R -n "@ts-ignore" "$ROOT" 2>/dev/null || true
  grep -R -n "@ts-nocheck" "$ROOT" 2>/dev/null || true
fi

say ""
say "Suggested commands to run (if available):"
cat <<'CMDS'
- tsc --noEmit
- tsc --noEmit --extendedDiagnostics
- eslint .
CMDS

say ""
say "TSConfig flags worth reviewing:"
if [ -f "$ROOT/tsconfig.json" ]; then
  if [ "$RG" = "rg" ]; then
    rg -n '"strict"\s*:\s*true|"skipLibCheck"\s*:\s*true|"noUncheckedIndexedAccess"\s*:\s*true|"exactOptionalPropertyTypes"\s*:\s*true' "$ROOT/tsconfig.json" || true
  else
    grep -n '"strict"' "$ROOT/tsconfig.json" 2>/dev/null || true
  fi
else
  say "- (no root tsconfig.json)"
fi
