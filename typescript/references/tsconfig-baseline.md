# TSConfig Baseline

This is a baseline you can adapt. Some flags are intentionally left as "consider" because they can be disruptive in legacy code.

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022"],

    "module": "ESNext",
    "moduleResolution": "Bundler",

    "strict": true,

    "noUncheckedIndexedAccess": false,
    "exactOptionalPropertyTypes": false,

    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,

    "declaration": false,
    "sourceMap": true,
    "incremental": true
  }
}
```

## Notes

- `moduleResolution` depends on your runtime (Node vs bundler). If you are using Node ESM, consider `moduleResolution: "NodeNext"`.
- `skipLibCheck: true` is often worth it for speed; disable only if you must validate third-party `.d.ts`.
- Turn on stricter flags (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`) when the codebase is ready.
