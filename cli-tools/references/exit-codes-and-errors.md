# Exit Codes & Error Messages

## Exit Codes

Standard POSIX exit codes:

```javascript
const EXIT_CODES = {
  SUCCESS: 0,
  GENERAL_ERROR: 1,
  MISUSE: 2,              // Invalid arguments
  PERMISSION_DENIED: 77,
  NOT_FOUND: 127,
  SIGINT: 130,            // Ctrl+C
};
```

## Error Handling Pattern

```text
Error: Config file not found at /path/to/config.yml

Tried locations:
  • ./mycli.config.yml
  • ~/.myclirc
  • /etc/mycli/config.yml

Run 'mycli init' to create a config file, or use --config to specify location.
```
