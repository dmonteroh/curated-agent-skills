# Configuration Precedence

Priority order (highest to lowest):

1. **Command-line flags** - Explicit user intent
2. **Environment variables** - Runtime context
3. **Config files (project)** - `.myclirc`, `mycli.config.js`
4. **Config files (user)** - `~/.myclirc`, `~/.config/mycli/config.yml`
5. **Config files (system)** - `/etc/mycli/config.yml`
6. **Defaults** - Hard-coded sensible defaults

```javascript
// Example config resolution
const config = {
  ...systemDefaults,
  ...loadSystemConfig(),
  ...loadUserConfig(),
  ...loadProjectConfig(),
  ...loadEnvVars(),
  ...parseCliFlags(),
};
```
