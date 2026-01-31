#!/usr/bin/env bash
set -euo pipefail

# Read-only, best-effort audit for common Tailwind misconfigurations.
# Run inside an app repo that uses Tailwind.

if ! command -v rg >/dev/null 2>&1; then
  echo "error: ripgrep (rg) not found; install rg or run equivalent searches." >&2
  exit 1
fi

echo "Tailwind audit (read-only)"
echo

config_candidates=$(
  rg -n --files --hidden --glob '!*node_modules/*' --glob '!*.min.*' \
    | rg -n '(tailwind\\.config\\.(js|cjs|mjs|ts)|postcss\\.config\\.(js|cjs|mjs|ts))$' \
    || true
)

if [[ -z "${config_candidates}" ]]; then
  echo "- tailwind config: not found (ok if config is non-standard)"
else
  echo "- config candidates:"
  echo "${config_candidates}" | sed 's/^/  - /'
fi

echo
echo "Heuristics:"

rg -n "content\\s*:\\s*\\[" --hidden --glob '!*node_modules/*' . >/dev/null 2>&1 \
  && echo "- content globs: present" \
  || echo "- content globs: NOT detected (risk: purge/missing styles)"

rg -n "safelist\\s*:" --hidden --glob '!*node_modules/*' . >/dev/null 2>&1 \
  && echo "- safelist: present (review scope for CSS bloat)" \
  || echo "- safelist: not detected (ok unless classes are dynamic)"

rg -n "darkMode\\s*:\\s*['\\\"]class['\\\"]" --hidden --glob '!*node_modules/*' . >/dev/null 2>&1 \
  && echo "- darkMode: class strategy detected" \
  || echo "- darkMode: class strategy not detected (ok; ensure strategy is intentional)"

rg -n "colors\\s*:\\s*\\{[^}]*ui\\s*:" --hidden --glob '!*node_modules/*' . >/dev/null 2>&1 \
  && echo "- semantic ui color namespace: detected" \
  || echo "- semantic ui color namespace: not detected (ok; but consider semantic tokens)"

echo
echo "If styles disappear in production:"
echo "- confirm content paths include all templates (and any UI library templates)"
echo "- confirm class names are not generated dynamically without safelist"

