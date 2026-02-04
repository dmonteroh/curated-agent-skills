# Node.js Terminal Output

## Chalk

```javascript
import chalk from 'chalk';

// Basic colors
console.log(chalk.blue('Info: ') + 'Starting deployment...');
console.log(chalk.green('Success: ') + 'Deployment complete');
console.log(chalk.yellow('Warning: ') + 'Deprecated flag used');
console.log(chalk.red('Error: ') + 'Deployment failed');

// Styles
console.log(chalk.bold.underline('Important'));
console.log(chalk.dim('Less important'));

// Templates
const success = chalk.green.bold;
const error = chalk.red.bold;
console.log(success('✓') + ' Build successful');
console.log(error('✗') + ' Build failed');

// Disable colors for CI
const log = {
  info: (msg) => console.log(chalk.blue('ℹ'), msg),
  success: (msg) => console.log(chalk.green('✔'), msg),
  warn: (msg) => console.log(chalk.yellow('⚠'), msg),
  error: (msg) => console.log(chalk.red('✖'), msg),
};

// Auto-detects TTY and CI environments
```
