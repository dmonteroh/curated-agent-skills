# Performance & Versioning

## Performance Patterns

```javascript
// Lazy loading: don't load unused dependencies
if (command === 'deploy') {
  const deploy = require('./commands/deploy');
  await deploy.run();
}

// Caching: avoid repeated calls
const cache = new Cache('~/.mycli/cache', { ttl: 3600 });
let plugins = await cache.get('plugins');
if (!plugins) {
  plugins = await fetchPlugins();
  await cache.set('plugins', plugins);
}

// Async operations: avoid blocking
await Promise.all([
  validateConfig(),
  loadPlugins(),
  runPreflightChecks(),
]);
```

## Versioning & Updates

```javascript
// Check for updates (non-blocking)
checkForUpdates().then(update => {
  if (update.available) {
    console.log(`Update available: ${update.version}`);
    console.log('Run the package manager update command.');
  }
}).catch(() => {
  // Silently fail - don't interrupt user workflow
});

// Version compatibility
const MIN_NODE_VERSION = '18.0.0';
if (!semver.satisfies(process.version, `>=${MIN_NODE_VERSION}`)) {
  console.error(`mycli requires Node.js ${MIN_NODE_VERSION} or higher`);
  process.exit(1);
}
```
