# Node.js Progress Indicators

## Ora

```javascript
import ora from 'ora';

// Simple spinner
const spinner = ora('Loading...').start();
await doWork();
spinner.succeed('Done!');

// Update text
const updating = ora('Starting...').start();
updating.text = 'Processing...';
await process();
updating.text = 'Finalizing...';
await finalize();
updating.succeed('Complete!');

// Different states
updating.start('Installing dependencies...');
// ... work
updating.succeed('Dependencies installed');
// or
updating.fail('Installation failed');
// or
updating.warn('Some packages skipped');
// or
updating.info('Using cached packages');

// Multiple spinners
const spinners = {
  api: ora('Deploying API...').start(),
  web: ora('Deploying web app...').start(),
  db: ora('Running migrations...').start(),
};

await Promise.all([
  deployApi().then(() => spinners.api.succeed()),
  deployWeb().then(() => spinners.web.succeed()),
  runMigrations().then(() => spinners.db.succeed()),
]);
```

## cli-progress

```javascript
import cliProgress from 'cli-progress';

// Single progress bar
const bar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);
bar.start(100, 0);

for (let i = 0; i <= 100; i++) {
  await processItem(i);
  bar.update(i);
}

bar.stop();

// Multi-progress
const multibar = new cliProgress.MultiBar({
  clearOnComplete: false,
  hideCursor: true,
});

const bar1 = multibar.create(100, 0, { task: 'API' });
const bar2 = multibar.create(100, 0, { task: 'Web' });

await Promise.all([
  processApi(bar1),
  processWeb(bar2),
]);

multibar.stop();
```
