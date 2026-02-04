# Man Page Format

```
NAME
    mycli-deploy - Deploy application to environment

SYNOPSIS
    mycli deploy <environment> [options]

DESCRIPTION
    Deploy application to the specified environment.
    Supports development, staging, and production environments.

OPTIONS
    -c, --config <file>
        Path to configuration file
        Default: ./mycli.config.yml

    -f, --force
        Skip all confirmation prompts
        Use with caution in production

    -d, --dry-run
        Preview deployment without executing
        Shows what would be deployed

EXAMPLES
    Deploy to production:
        mycli deploy production

    Preview staging deployment:
        mycli deploy staging --dry-run

SEE ALSO
    mycli-init(1), mycli-config(1), mycli-rollback(1)
```
