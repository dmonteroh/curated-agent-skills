# CI Workflows and CLI Tooling

## Requirements

- CI runner with git history access.
- A changelog generator such as `git-cliff` or equivalent.
- Network access if downloading binaries during the job.
- `curl` and `tar` available in the runner image for download/install steps.
- Release credentials stored as CI secrets if publishing notes.

## Example: GitHub Actions with git-cliff

```yaml
name: Release Notes

on:
  workflow_dispatch:
  push:
    tags:
      - 'v*'

jobs:
  release-notes:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Install git-cliff
        run: |
          curl -sSL https://github.com/orhun/git-cliff/releases/download/vX.Y.Z/git-cliff-vX.Y.Z-x86_64-unknown-linux-gnu.tar.gz \
            | tar -xz --strip-components=1
          sudo mv git-cliff /usr/local/bin/git-cliff
      - name: Generate release notes
        run: git-cliff -c cliff.toml -o RELEASE_NOTES.md
      - name: Upload notes artifact
        uses: actions/upload-artifact@v4
        with:
          name: release-notes
          path: RELEASE_NOTES.md
```

Usage

- Add `cliff.toml` to the repository with section mappings.
- Use the tag-based trigger to produce notes per release.

Verification

- Run `git-cliff -c cliff.toml --unreleased` locally to preview output.
- Confirm the workflow artifact contains the generated notes.

## Example: GitLab CI with commitizen + git-cliff

```yaml
release_notes:
  stage: release
  image: alpine:3.20
  script:
    - apk add --no-cache git curl tar
    - curl -sSL https://github.com/orhun/git-cliff/releases/download/vX.Y.Z/git-cliff-vX.Y.Z-x86_64-unknown-linux-gnu.tar.gz \
        | tar -xz --strip-components=1
    - ./git-cliff -c cliff.toml -o RELEASE_NOTES.md
  artifacts:
    paths:
      - RELEASE_NOTES.md
  rules:
    - if: '$CI_COMMIT_TAG'
```

Usage

- Ensure tags are pushed to trigger the job.
- Store release credentials (if used) in protected variables.

Verification

- Run the job on a test tag and inspect `RELEASE_NOTES.md`.

## Common pitfalls

- Shallow clones omit earlier tags and produce incomplete notes.
- Missing secrets cause publish steps to fail silently.
- Mixing manual edits into generated notes introduces drift.
