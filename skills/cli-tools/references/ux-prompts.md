# Interactive Prompts

## Prompt Types

```
Text Input:
  Project name: my-awesome-app
  ↑ Clear label

Select (Single Choice):
  ? Select environment: (Use arrow keys)
  ❯ development
    staging
    production

Checkbox (Multiple Choice):
  ? Select features: (Press space to select, enter to confirm)
  ◉ TypeScript
  ◯ ESLint
  ◉ Prettier
  ◯ Jest

Confirmation:
  ? Deploy to production? (y/N)
  ↑ Default is No (safer)

Password:
  ? Enter password: ********
  ↑ Masked input
```

## Prompt Guidelines

```
DO:
✓ Show keyboard hints ("Use arrow keys", "Press space")
✓ Provide sensible defaults (pre-select common choices)
✓ Allow skipping with Ctrl+C
✓ Validate input immediately
✓ Show preview/summary before final action

DON'T:
✗ Require interaction in CI/CD environments
✗ Ask obvious questions (confirm every action)
✗ Hide what will happen next
✗ Make users repeat information
```
