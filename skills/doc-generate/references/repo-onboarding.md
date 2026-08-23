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
| In-file declaration order | The top of two or three files in the same layer: whether imports, type declarations, main logic, helpers, and exports appear in a fixed sequence |
| Where cross-cutting utilities live | Whether shared helpers — formatters, interceptors, middleware, validation — sit in a common location or beside their first caller, and where a new one would go |

Git history is the only one of these that can be unavailable. Check before sampling: if `git rev-parse --is-shallow-repository` prints `true`, or the repository has no commits, the branch, commit, and integration rows cannot be established. Record "git history unavailable or too shallow to detect conventions" and move on — a convention inferred from one commit is a guess wearing evidence's clothes.

### A near-even split is a conflict, not a dominant form

The sampling rule above assumes one form dominates. Where none does, writing down "the dominant form" invents a consensus the repository does not have, and the invented rule then gets enforced on every later change.

- **Lopsided split — resolve to the majority without asking.** The suppression rule is a minority that is both a small fraction of instances and a small absolute count: under 5% *and* fewer than 10 occurrences. Both figures are chosen defaults with no measurement behind them, and the pairing carries more weight than either number — 4% of a 300-file repo is 12 occurrences and does not auto-suppress. In a small repository, three instances against two is not a majority.
- **Near-even split, or two forms that mean different things on a dimension the code depends on — raise it.** Record the conflict and put it to a human, carrying a real path on each side and the cost of leaving both in place.
- **One conflict per question, answered before the next is asked.** Stacking several into one message converts a decision into a form to fill in, and the answers come back thinner than the evidence deserves.
- **A conflict has more than two answers.** Beyond "follow A" and "follow B", the answer may be that the repository is mid-migration and one side is the direction of travel, or a rule neither form matches. Record which it was: a migration is a different fact from a convention, and filing one as the other freezes a transition into a permanent rule.

### Record the rejected form, not only the winner

Every convention decided against a real alternative earns an explicit "do not" line naming what lost. A file that records only what to do leaves the losing pattern free to come back through the next contributor, and hands the next pass the same conflict with no memory that it was already settled. This is the half of convention capture that silence loses.

### Name real exemplar files

State each convention alongside a real file that demonstrates it and one line on what that file demonstrates. A rule with an in-repo example is checkable and can be imitated; a rule without one is prose, and a reader who reads it differently has nothing to check against. Choose files that are current and typical rather than the largest or the oldest, and say what to copy: the structure, not the defects. An exemplar is chosen for the convention it shows, and is not warranted correct in any other respect.

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
- **Exemplar files** — a handful of real paths, each with the single thing it demonstrates. This is the section that makes the rest checkable.
- **Do not** — the rejected alternative for each convention that was decided against one, stated as the pattern not to introduce.

Retention test for every line: would a competent engineer joining this project already do this without being told? Then it does not earn a line. The file is loaded before every task, so its length is paid repeatedly.

### Stamp the derivation, and append on re-run

Record in the file the commit the conventions were read from and what was sampled to reach them. A later pass compares against that stamp instead of re-deriving from nothing: read what changed since, check the new code against the recorded rules, and where something has genuinely moved, append a dated entry rather than overwriting the line it supersedes.

The reason a rule changed lives nowhere else. Current text alone cannot say whether a rule was never questioned or was argued to a conclusion twice, and a pass that overwrites silently will re-propose the form the last one rejected. Where the repository has no usable history, say so in the stamp rather than leaving it out — an unstamped file cannot be re-run incrementally, and the next pass has to start from scratch and re-ask every question.
