# Error Messages

## Good Error Messages

```
Pattern: [Context] → [Problem] → [Solution]

Example 1: File not found
✗ Error: Config file not found

Searched locations:
  • ./mycli.config.yml
  • ~/.config/mycli/config.yml
  • /etc/mycli/config.yml

Solutions:
  • Run 'mycli init' to create a config file
  • Use --config to specify a different location
  • Check file permissions

Example 2: Validation error
✗ Error: Invalid environment 'prod'

Expected one of:
  • development
  • staging
  • production

Did you mean 'production'?

Example 3: Permission error
✗ Error: Permission denied writing to /etc/mycli/config.yml

This operation requires elevated permissions.

Try:
  • Run with sudo: sudo mycli config set key value
  • Use user config: mycli config set --user key value
  • Check file permissions: ls -la /etc/mycli/config.yml
```

## Error Message Guidelines

```
DO:
✓ Be specific ("Port 3000 already in use" not "Port unavailable")
✓ Show context ("in file config.yml, line 42")
✓ Suggest solutions ("Try running 'mycli fix'")
✓ Use plain language ("File not found" not "ENOENT")

DON'T:
✗ Show stack traces to users (save for --debug)
✗ Use jargon ("EACCES: permission denied")
✗ Leave users stuck ("Invalid input" with no explanation)
✗ Be vague ("Something went wrong")
```
