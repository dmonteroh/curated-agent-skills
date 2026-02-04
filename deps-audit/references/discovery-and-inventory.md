# Dependency discovery and inventory

Use this reference to identify dependency manifests and produce a minimal inventory.

## Inputs

- Repo root path.
- Any repo-specific locations to include or exclude.

## Manifest detection checklist

- Node: `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`.
- Python: `pyproject.toml`, `poetry.lock`, `Pipfile.lock`, `requirements.txt`.
- Go: `go.mod`, `go.sum`.
- Rust: `Cargo.toml`, `Cargo.lock`.
- Java: `pom.xml`, `build.gradle`, `build.gradle.kts`.
- Ruby: `Gemfile`, `Gemfile.lock`.

## Steps and outputs

1) Locate manifests and lockfiles.
- Output: list of detected ecosystems with evidence paths.

2) Prefer lockfiles as the source of truth.
- Output: note which lockfiles will be used for version accuracy.

3) Identify dependency scope.
- Output: runtime vs dev/test dependency notes when available.

## Decision points

- If no manifests are found, stop and report "no dependency evidence found".
- If only manifests are found without lockfiles, note reduced precision.

## Pitfalls to avoid

- Mixing multiple package managers without noting which lockfile wins.
- Treating vendored code as dependency evidence without validation.
