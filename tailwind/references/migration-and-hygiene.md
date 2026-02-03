# Migration + Hygiene Checklist

Use this when upgrading Tailwind, introducing plugins, or refactoring class strategy.

## Before changing anything

- Identify where class names are generated (templates, MDX, runtime strings).
- Confirm the build pipeline (PostCSS/Vite/Next/etc.) and where Tailwind config is loaded from.

## After changes

- Confirm no missing classes in production build output.
- Confirm `darkMode` behavior and tokens render correctly.
- Confirm safelist patterns do not explode CSS size.

## Codebase hygiene

- Prefer semantic token classes instead of raw palette usage in app code.
- Centralize component class contracts (avoid per-callsite reinvention).
- Document any non-obvious plugin or safelist decisions in the repo.

