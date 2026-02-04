# Status Messages & Debug Modes

## Real-time Updates

```
Multi-step process:
✓ Dependencies installed (2.3s)
✓ Application built (8.1s)
⠋ Running tests... (current)
⏳ Deploying... (pending)
⏳ Verifying... (pending)

Updates:
⠋ Installing dependencies...
  → npm install
✓ Dependencies installed (2.3s)

⠋ Building application...
  → webpack build
✓ Application built (8.1s)
  → Output: dist/ (2.4 MB)
```

## Summary/Completion

```
✓ Deployment complete!

Summary:
  Environment:  production
  Version:      v1.2.3
  Duration:     2m 34s
  Deployed:     YYYY-MM-DD HH:MM UTC

Next steps:
  • View logs: mycli logs production
  • Monitor:   mycli status production
  • Rollback:  mycli rollback production

URL: https://app.example.com
```

## Debugging & Verbose Mode

```
Normal mode (default):
✓ Deployed to production (2m 34s)

Verbose mode (--verbose):
[10:30:12] Starting deployment...
[10:30:13] Loading config from ./mycli.config.yml
[10:30:14] Connecting to production server...
[10:30:15] Uploading files (124 files, 2.4 MB)...
[10:30:28] Running post-deploy hooks...
[10:32:46] ✓ Deployment complete

Debug mode (--debug):
[DEBUG] Config loaded: {env: 'production', ...}
[DEBUG] SSH connection established: user@host
[DEBUG] Executing: rsync -avz ./dist/ user@host:/var/www/
[DEBUG] Output: sending incremental file list...
[DEBUG] Exit code: 0
✓ Deployed to production (2m 34s)

Usage:
# Normal: concise output
mycli deploy production

# Verbose: detailed steps
mycli deploy production --verbose

# Debug: everything including internals
DEBUG=* mycli deploy production
```
