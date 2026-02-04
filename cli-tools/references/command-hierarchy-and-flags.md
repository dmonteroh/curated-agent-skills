# Command Hierarchy & Flags

## Command Hierarchy

```
mycli                           # Root command
├── init [options]              # Simple command
├── config
│   ├── get <key>               # Nested subcommand
│   ├── set <key> <value>
│   └── list
├── deploy [environment]        # Command with args
│   ├── --dry-run               # Flag
│   ├── --force
│   └── --config <file>         # Option with value
└── plugins
    ├── install <name>
    ├── list
    └── remove <name>
```

## Flag Conventions

```bash
# Boolean flags (presence = true)
mycli deploy --force --dry-run

# Short + long forms
mycli -v --verbose
mycli -c config.yml --config config.yml

# Required vs optional
mycli deploy <env>              # Positional (required)
mycli deploy --env production   # Flag (optional)

# Multiple values
mycli install pkg1 pkg2 pkg3    # Variadic args
mycli --exclude node_modules --exclude .git
```
