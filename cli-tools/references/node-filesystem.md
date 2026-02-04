# Node.js File System Helpers

```javascript
import fs from 'fs-extra';
import { globby } from 'globby';
import path from 'path';

// Copy with template
await fs.copy('templates/app', targetDir, {
  filter: (src) => !src.includes('node_modules'),
});

// Read/write JSON
const config = await fs.readJson('config.json');
await fs.writeJson('output.json', data, { spaces: 2 });

// Ensure directory exists
await fs.ensureDir('dist/assets');

// Find files
const files = await globby(['src/**/*.ts', '!src/**/*.test.ts']);
```
