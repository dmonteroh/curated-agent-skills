# Node.js CLI Frameworks

## Commander.js (Recommended)

```javascript
#!/usr/bin/env node
import { Command } from 'commander';
import { version } from './package.json';

const program = new Command();

program
  .name('mycli')
  .description('My awesome CLI tool')
  .version(version);

program
  .command('init')
  .description('Initialize a new project')
  .option('-t, --template <type>', 'Project template', 'default')
  .option('-f, --force', 'Overwrite existing files')
  .action(async (options) => {
    console.log(`Initializing with template: ${options.template}`);
  });

program
  .command('deploy <environment>')
  .description('Deploy to environment')
  .option('--dry-run', 'Preview without executing')
  .action(async (environment, options) => {
    if (options.dryRun) {
      console.log(`Would deploy to: ${environment}`);
    } else {
      await deploy(environment);
    }
  });

const config = program.command('config').description('Manage configuration');

config
  .command('get <key>')
  .description('Get config value')
  .action((key) => console.log(getConfig(key)));

config
  .command('set <key> <value>')
  .description('Set config value')
  .action((key, value) => setConfig(key, value));

program.parse();
```

## Yargs (Alternative)

```javascript
#!/usr/bin/env node
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';

yargs(hideBin(process.argv))
  .command(
    'deploy <env>',
    'Deploy to environment',
    (yargs) => {
      return yargs
        .positional('env', {
          describe: 'Environment name',
          choices: ['dev', 'staging', 'prod'],
        })
        .option('force', {
          alias: 'f',
          type: 'boolean',
          description: 'Force deployment',
        });
    },
    async (argv) => {
      await deploy(argv.env, { force: argv.force });
    }
  )
  .middleware([(argv) => {
    if (!isConfigValid()) {
      throw new Error('Invalid config');
    }
  }])
  .demandCommand()
  .help()
  .parse();
```
