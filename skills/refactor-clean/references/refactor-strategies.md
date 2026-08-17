# Incremental Refactor Strategies

Use these tactics to keep diffs small and behavior stable.

## High-Impact, Low-Risk Moves

- Rename for clarity before structural changes.
- Extract constants for repeated literals.
- Extract helper functions for duplicate logic.
- Encapsulate fields or config behind accessors.

## Method Extraction Example

```
# Before
def process_order(order):
    # 50 lines of validation
    # 30 lines of calculation
    # 40 lines of notification

# After
def process_order(order):
    validate_order(order)
    total = calculate_order_total(order)
    send_order_notifications(order, total)
```

## Class Decomposition Example

```
class UserService:
    def __init__(self, validator, repository, email_service, logger):
        self.validator = validator
        self.repository = repository
        self.email_service = email_service
        self.logger = logger

    def create_user(self, data):
        self.validator.validate(data)
        user = self.repository.save(data)
        self.email_service.send_welcome_email(user)
        self.logger.log_creation(user)
        return user
```

## Mechanical and Bulk Rewrites

- Preview before applying. Run a codemod, structural pattern rewrite, or bulk rename in dry-run mode and read the **entire** match set, not a sample. The unexpected matches are the finding: narrow the pattern and preview again rather than applying and cleaning up afterwards.
- Prefer a tool-verified rename — a language server's or an IDE's rename — over a textual search-and-replace. It follows the symbol rather than the string, so it leaves an unrelated identifier of the same name alone, and it fails loudly when the rename is not valid.
- One transformation per step, and keep the preview output with the step so a reviewer can see what the pattern matched.

## Splitting an Oversized Module

- Split by responsibility, not by size: name the distinct concepts the file owns, then give each one its own file.
- Name each new file after the concept it owns. Never `utils`, `helpers`, or `common`; never a token split (`foo_1`, `foo_2`) that leaves two halves of one idea in two files.
- Present the split plan before executing it. A split changes every importer, which makes it the least revertible move in this reference.
- This skill sets no line-count threshold, and a file's length is a signal rather than a defect — the defect is the number of responsibilities. If a project defines a size ceiling, it is that project's chosen convention; measure it as pure LOC (non-blank, non-comment lines) so the count does not move with formatting or comment volume.

## Safe Refactor Checklist

- Preserve public interfaces unless explicitly approved.
- Keep each change reviewable and revertible.
- Avoid mixing refactors with behavior changes.
- Prefer composition over inheritance for new structure.
