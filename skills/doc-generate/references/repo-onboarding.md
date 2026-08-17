# Repo Onboarding Playbook

Signal tables and artifact outlines for documenting a repository nobody has documented yet. The pass that uses them is "Onboarding pass for an unfamiliar repo" in `SKILL.md`.

## Reconnaissance signals

Resolve each family as a glob query and open a file only where its signal is ambiguous. The patterns are starting points per ecosystem, not a closed list: a family missing from the results means "not detected by these patterns", never "absent".

| Signal family | What it answers | Patterns to glob |
| --- | --- | --- |
| Package manifest | Language, dependency set, declared scripts | `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `requirements*.txt`, `pom.xml`, `build.gradle*`, `Gemfile`, `composer.json`, `mix.exs`, `pubspec.yaml`, `*.csproj` |
| Framework fingerprint | Which framework owns routing and lifecycle | Root framework configs (`next.config.*`, `nuxt.config.*`, `angular.json`, `vite.config.*`, `astro.config.*`), a Django `settings.py`, a Flask app factory, a FastAPI `main.py`, a Rails `config/application.rb`, a Spring `application.{yml,properties}` |
| Entry point | Where execution actually starts | `main.*`, `index.*`, `app.*`, `server.*`, `cmd/`, `src/main/`, plus the container `CMD`/`ENTRYPOINT` and the manifest's declared start script |
| Directory shape | The mental model of the repo | The top two directory levels, excluding vendored and generated trees (`node_modules/`, `vendor/`, `.git/`, `dist/`, `build/`, `target/`, `__pycache__/`) |
| Config and tooling | The rules the repo already enforces | Linter and formatter configs, `tsconfig.json`, `Makefile`, `Dockerfile`, `docker-compose*`, CI workflow directories, `.env.example` |
| Test layout | Where a newcomer's first test goes | `tests/`, `test/`, `__tests__/`, `*_test.go`, `*.spec.*`, `*.test.*`, and runner configs (`pytest.ini`, `jest.config.*`, `vitest.config.*`, `go.mod` test tooling) |

Interpreting the results:

- A manifest declares intent; the code declares behavior. Where they disagree, the code is the evidence and the disagreement is itself worth a line in the guide.
- Two or more manifests at different depths means a workspace or monorepo — map the members before describing the repo as one application.
- A framework fingerprint with no matching code (a config file for a framework nothing imports) is dead configuration, not a stack fact.

## Convention signals

Detect what the repo already does, not what it should do. Sample several instances per convention and record the dominant form; a single example is an anecdote.

| Convention | Read it from |
| --- | --- |
| File and symbol naming | Existing filenames per directory (kebab-case, camelCase, PascalCase, snake_case) and the exported symbol names inside them |
| Test naming | The suffix existing tests actually use, and whether tests sit beside sources or in a parallel tree |
| Error handling | Two or three handlers: thrown exceptions, returned error values, result types, or error codes |
| Dependency wiring | Whether collaborators are injected or imported directly at the point of use |
| Async style | Callbacks, promises and `async`/`await`, channels, actors, or blocking calls |
| Branch naming | Recent branch names in the repository |
| Commit style | Recent commit subjects: type prefixes, ticket identifiers, mood, subject length |
| Integration style | Whether history is linear (squash or rebase) or carries merge commits |

Git history is the only one of these that can be unavailable. Check before sampling: if `git rev-parse --is-shallow-repository` prints `true`, or the repository has no commits, the last three rows cannot be established. Record "git history unavailable or too shallow to detect conventions" and move on — a convention inferred from one commit is a guess wearing evidence's clothes.

## Onboarding guide outline

- **Overview** — what the project does and who it serves, in a few sentences.
- **Tech stack** — a table of layer, technology, and version constraint (language, framework, datastore, data-access layer, test tooling, CI).
- **Architecture** — the pattern (single service, monorepo, service split, serverless), the front-end/back-end boundary if there is one, and the interface style actually served (REST, GraphQL, RPC, events).
- **Key entry points** — path to what it owns, one line each: the request entry, the data-model source of truth, the build and runtime config.
- **Directory map** — top-level directory to purpose, skipping any directory whose name already says it.
- **Request lifecycle** — the traced path (method: `references/architecture-documentation.md`).
- **Conventions** — the established rows from the table above, with the unestablished ones named as unestablished.
- **Common tasks** — the real commands, lifted from the manifest's scripts, `Makefile` targets, or CI steps, never invented: dev server, tests, lint, migrations, production build.
- **Where to look** — an intent-to-location table, so a newcomer's first change starts in the right file.

Example rows for the last table, from a repository whose signals resolved to a JavaScript web application:

| I want to... | Look at... |
| --- | --- |
| Add an HTTP endpoint | `src/api/` — one file per route, registered in `src/api/index.ts` |
| Add a database table | `db/schema.prisma` — the data-model source of truth |
| Add a test | `tests/` mirroring the source path |

## Agent-instruction file outline

Many repositories keep a root-level instruction file that agents load before every task. Its name varies by project and by toolchain, so detect the file the project already uses rather than assuming one; if none exists, confirm the name the project wants before creating it.

Sections worth carrying, each populated from detected evidence rather than from convention:

- **Stack** — the same summary as the guide, compressed to what changes how code is written.
- **Code style** — the detected naming and structural conventions, stated as rules.
- **Testing** — the command that runs tests, the file convention new tests must match, and the coverage command if one is configured.
- **Build and run** — dev, build, and lint commands as they are actually invoked.
- **Project structure** — the directory-to-purpose map, trimmed to non-obvious entries.
- **Conventions** — commit style, integration style, and error-handling expectations, omitting any row the git check could not establish.

Retention test for every line: would a competent engineer joining this project already do this without being told? Then it does not earn a line. The file is loaded before every task, so its length is paid repeatedly.
