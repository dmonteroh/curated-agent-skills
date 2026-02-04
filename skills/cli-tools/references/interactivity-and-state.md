# Interactivity & State

## Interactive vs Non-Interactive

```javascript
// Detect if running in CI/CD or non-TTY
const isCI = process.env.CI === 'true' || !process.stdout.isTTY;

if (isCI) {
  if (!options.environment) {
    throw new Error('--environment required in non-interactive mode');
  }
} else {
  const environment = await prompt({
    type: 'select',
    message: 'Select environment:',
    choices: ['development', 'staging', 'production'],
  });
}
```

## State Management

```
~/.mycli/
├── config.yml           # User configuration
├── cache/               # Cached data
│   ├── plugins.json
│   └── api-responses/
├── credentials.json     # Sensitive data (600 perms)
└── state.json           # Session state
```
