# Plugin Architecture

```
mycli/
├── core/                      # Core functionality
├── plugins/
│   ├── aws/                  # Plugin: AWS integration
│   │   ├── package.json
│   │   └── index.js
│   └── github/               # Plugin: GitHub integration
│       ├── package.json
│       └── index.js
└── plugin-loader.js          # Discovery & loading
```

Plugin discovery:

1. Check `~/.mycli/plugins/`
2. Check `node_modules/mycli-plugin-*`
3. Check `MYCLI_PLUGIN_PATH` env var
