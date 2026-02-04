# Help Text Design

## Command Help Structure

```
USAGE
  mycli <command> [options]

COMMANDS
  init         Initialize a new project
  deploy       Deploy to environment
  config       Manage configuration
  plugins      Manage plugins

OPTIONS
  -h, --help     Show help
  -v, --version  Show version
  --config FILE  Config file path

Run 'mycli <command> --help' for more information on a command.

EXAMPLES
  # Initialize a new project
  mycli init my-app

  # Deploy to production
  mycli deploy production --dry-run
```

## Subcommand Help

```
USAGE
  mycli deploy <environment> [options]

ARGUMENTS
  environment    Target environment (required)
                 Values: development, staging, production

OPTIONS
  -c, --config <file>    Config file path
                         Default: ./mycli.config.yml

  -f, --force            Skip confirmation prompts
                         Use with caution in production

  -d, --dry-run          Preview changes without executing
                         Shows what would happen

  -v, --verbose          Show detailed output
                         Includes debug information

EXAMPLES
  # Deploy to production (with confirmation)
  mycli deploy production

  # Preview staging deployment
  mycli deploy staging --dry-run

  # Use custom config
  mycli deploy production --config ./prod.yml

  # Force deploy without prompts
  mycli deploy production --force
```
