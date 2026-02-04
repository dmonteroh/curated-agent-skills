# Color Usage

## Semantic Colors

```
Red:     Errors, failures, destructive actions
Yellow:  Warnings, deprecations, non-critical issues
Green:   Success, completion, positive feedback
Blue:    Information, hints, neutral messages
Cyan:    Commands, code, technical details
Magenta: Highlights, special items
Gray:    Less important, metadata, timestamps

Examples:
✓ Success: Deployment complete
✗ Error: File not found
⚠ Warning: Deprecated flag --old-flag
ℹ Info: Using cache from ~/.mycli/cache
```

## When to Disable Colors

```javascript
// Detect non-TTY output (piped to file, etc.)
const noColor = !process.stdout.isTTY ||
                process.env.NO_COLOR ||
                process.env.CI === 'true';

if (noColor) {
  // Disable colors
}
```

## Color Accessibility

```
- Don't rely on color alone (use symbols too)
- Provide high contrast (test with various terminals)
- Support color blindness (red/green alternatives)

Good:
✓ Build successful (green)
✗ Build failed (red)
↑ Symbols work without color

Bad:
Success (only color, no symbol)
Failed (only color, no symbol)
```
