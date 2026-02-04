# Core Concepts

## Keep a Changelog Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [Unreleased]

### Added
- New feature X

## [1.2.0] - YYYY-MM-DD

### Added
- User profile avatars
- Dark mode support

### Changed
- Improved loading performance by 40%

### Deprecated
- Old authentication API (use v2)

### Removed
- Legacy payment gateway

### Fixed
- Login timeout issue (#123)

### Security
- Updated dependencies for CVE-XXXX-YYYY

[Unreleased]: <compare-url>/v1.2.0...HEAD
[1.2.0]: <compare-url>/v1.1.0...v1.2.0
```

## Conventional Commits

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

| Type | Description | Changelog Section |
|------|-------------|-------------------|
| `feat` | New feature | Added |
| `fix` | Bug fix | Fixed |
| `docs` | Documentation | (usually excluded) |
| `style` | Formatting | (usually excluded) |
| `refactor` | Code restructure | Changed |
| `perf` | Performance | Changed |
| `test` | Tests | (usually excluded) |
| `chore` | Maintenance | (usually excluded) |
| `ci` | CI changes | (usually excluded) |
| `build` | Build system | (usually excluded) |
| `revert` | Revert commit | Removed |

## Semantic Versioning

```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes (feat! or BREAKING CHANGE)
MINOR: New features (feat)
PATCH: Bug fixes (fix)
```
