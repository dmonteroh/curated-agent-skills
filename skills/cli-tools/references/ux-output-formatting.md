# Output Formatting

## Tables

```
Good:
┌─────────────┬──────────┬──────────┐
│ Environment │ Status   │ Updated  │
├─────────────┼──────────┼──────────┤
│ production  │ ✓ Active │ 2h ago   │
│ staging     │ ✓ Active │ 5m ago   │
│ development │ ✗ Down   │ 1d ago   │
└─────────────┴──────────┴──────────┘

Minimal (for scripting):
Environment  Status  Updated
production   Active  2h ago
staging      Active  5m ago
development  Down    1d ago

JSON (for programmatic use):
[
  {"env": "production", "status": "active", "updated": "2h ago"},
  {"env": "staging", "status": "active", "updated": "5m ago"}
]
```

## Lists

```
Bulleted:
Features:
  • TypeScript support
  • Hot reload
  • Auto-formatting

Numbered:
Steps to deploy:
  1. Build application
  2. Run tests
  3. Deploy to server
  4. Verify deployment

Tree:
my-app/
├── src/
│   ├── components/
│   └── utils/
├── tests/
└── package.json
```
