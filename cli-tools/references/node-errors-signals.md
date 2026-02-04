# Node.js Error Handling & Signals

```javascript
import { Command } from 'commander';

program
  .command('deploy')
  .action(async () => {
    try {
      await deploy();
    } catch (error) {
      if (error.code === 'EACCES') {
        console.error(chalk.red('Permission denied'));
        console.error('Try running with sudo or check file permissions');
        process.exit(77);
      } else if (error.code === 'ENOENT') {
        console.error(chalk.red('File not found:'), error.path);
        process.exit(127);
      } else {
        console.error(chalk.red('Deployment failed:'), error.message);
        if (process.env.DEBUG) {
          console.error(error.stack);
        }
        process.exit(1);
      }
    }
  });

// Handle SIGINT (Ctrl+C)
process.on('SIGINT', () => {
  console.log('\nOperation cancelled');
  process.exit(130);
});
```
