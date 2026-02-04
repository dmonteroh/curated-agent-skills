# Node.js Packaging & Testing

## Package.json Setup

```json
{
  "name": "mycli",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "mycli": "./bin/cli.js"
  },
  "files": [
    "bin/",
    "lib/",
    "templates/"
  ],
  "engines": {
    "node": ">=18.0.0"
  },
  "dependencies": {
    "commander": "^11.0.0",
    "inquirer": "^9.0.0",
    "chalk": "^5.0.0",
    "ora": "^7.0.0"
  }
}
```

## Testing CLIs

```javascript
import { execaCommand } from 'execa';
import { describe, it, expect } from 'vitest';

describe('mycli', () => {
  it('shows version', async () => {
    const { stdout } = await execaCommand('node bin/cli.js --version');
    expect(stdout).toMatch(/\d+\.\d+\.\d+/);
  });

  it('shows help', async () => {
    const { stdout } = await execaCommand('node bin/cli.js --help');
    expect(stdout).toContain('Usage:');
  });

  it('handles invalid command', async () => {
    await expect(
      execaCommand('node bin/cli.js invalid')
    ).rejects.toThrow();
  });
});
```
