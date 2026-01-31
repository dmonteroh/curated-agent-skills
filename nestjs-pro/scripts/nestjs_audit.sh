#!/usr/bin/env bash
set -euo pipefail

# Read-only, best-effort audit for common NestJS hygiene issues.
# Run inside a NestJS project repo.

if ! command -v rg >/dev/null 2>&1; then
  echo "error: ripgrep (rg) not found; install rg or run equivalent searches." >&2
  exit 1
fi

echo "NestJS audit (read-only)"
echo

main_candidates=$(rg -n --files --hidden --glob '!*node_modules/*' --glob '!*.min.*' | rg -n '(main\\.(ts|js))$' || true)
if [[ -z "${main_candidates}" ]]; then
  echo "- main.ts: not found (ok if project differs)"
else
  echo "- main.ts candidates:"
  echo "${main_candidates}" | sed 's/^/  - /'
fi

echo
echo "Checks (best-effort):"

rg -n "new ValidationPipe\\(" --hidden --glob '!*node_modules/*' . >/dev/null 2>&1 \
  && echo "- ValidationPipe: found" \
  || echo "- ValidationPipe: NOT found (risk: DTO validation may not run globally)"

rg -n "useGlobalFilters\\(" --hidden --glob '!*node_modules/*' . >/dev/null 2>&1 \
  && echo "- Global filters: found" \
  || echo "- Global filters: not detected (ok if per-route, but ensure error shape is consistent)"

rg -n "useGlobalInterceptors\\(" --hidden --glob '!*node_modules/*' . >/dev/null 2>&1 \
  && echo "- Global interceptors: found" \
  || echo "- Global interceptors: not detected (ok, but ensure logging/serialization is intentional)"

rg -n "setGlobalPrefix\\(" --hidden --glob '!*node_modules/*' . >/dev/null 2>&1 \
  && echo "- Global prefix: found" \
  || echo "- Global prefix: not detected (ok if API is root-scoped)"

echo
echo "Next: inspect findings and decide if fixes belong in main bootstrap, modules, or per-route wiring."

