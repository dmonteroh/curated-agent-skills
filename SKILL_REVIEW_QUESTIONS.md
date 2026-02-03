# Skill Review Questions

1. Which PDF should we use as the reference you mentioned? I couldn't locate any `.pdf` files in this repo.
2. For the token budget check, I set `soft_limit=110` (warning) and `hard_limit=120` (error). Are these thresholds acceptable, or do you want different numbers?
3. Should warnings (soft limit) be non-blocking as implemented, or do you want warnings to fail the audit as well?
4. Do you want the audit to **require** `tiktoken` (current behavior: exit with error if missing), or should it skip token checks if `tiktoken` isn't installed?
5. For the skill-by-skill review, do you want a specific order (e.g., by category, by recent changes, or highest-impact first)?
