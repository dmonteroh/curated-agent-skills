# Progress Indicators

## When to Use What

```
Determinate (known total):
  [████████████░░░░░░░░] 60% (3/5 files)
  Use: File operations, downloads, batch processing

Indeterminate (unknown duration):
  ⠋ Loading...
  Use: API calls, database queries, waiting for external services

Multi-step:
  ✓ Dependencies installed
  ⠋ Building application...
  ⏳ Running tests...
  Use: Multi-phase operations (build, deploy, etc.)
```

## Progress Bar Best Practices

```
Good:
[████████████░░░░░░░░] 60% | 120/200 MB | 2.4 MB/s | ETA: 33s
↑ Visual     ↑ Percent  ↑ Progress  ↑ Rate     ↑ Time

Components:
- Visual bar (20-40 chars)
- Percentage (when known)
- Current/total (with units)
- Speed/rate (when applicable)
- ETA (estimated time remaining)

Bad:
Processing... (no feedback)
60% (no context)
[████████████████████████████████████████] (too wide)
```

## Spinner Styles

```
⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏   Dots (elegant, low-key)
⣾ ⣽ ⣻ ⢿ ⡿ ⣟ ⣯ ⣷        Blocks (bold, attention)
◐ ◓ ◑ ◒                  Circle (classic)
▖ ▘ ▝ ▗                  Corners (minimal)
⠁ ⠂ ⠄ ⡀ ⢀ ⠠ ⠐ ⠈        Line (subtle)

Choose based on:
- Terminal compatibility (stick to ASCII for Windows)
- Branding (match tool personality)
- Context (subtle for background, bold for main task)
```
