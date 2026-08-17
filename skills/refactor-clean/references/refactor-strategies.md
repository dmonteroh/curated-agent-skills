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
- Pick the matcher by what the question depends on. A syntax *shape* — every call of this form, every empty catch, every cast to a given type — wants a structural matcher, one that parses the pattern as code and matches it against the parse tree: an occurrence inside a comment or a string literal is then not a hit, and a reformatted or line-wrapped occurrence still is. File *bytes* — string contents, comments, license headers, filenames — want a text matcher, which is the only one that can express them. A question about *meaning* — what does this name refer to, can this call throw, is this the same symbol as that one — wants neither, and goes to the language server or type checker, the only tools that resolve a name to its definition. Choosing on habit is what lets a textual search-and-replace rewrite a string literal that merely spells the identifier. State which class the step needs, then use whatever the project already has that provides it — the dependency is on the matcher class, never on one particular tool being installed. Where nothing structural is available for the language at hand, fall back to a text matcher and read the full match set by hand: the discipline is what makes the rewrite safe, not the tool.
- A zero-match result is a claim to verify, not an answer. "No occurrences, nothing to migrate" from a structural matcher counts only once the pattern has been shown to parse, the language or dialect was set to the one the files are actually written in (a mixed-syntax file read under the wrong dialect parses to garbage and reports a clean codebase), and the pattern's own parse tree has been read against the target's. Do not retry with variations until one matches: each failure has a reason, and the reason is the finding. An unexpectedly *small* match set is the same signal as an unexpectedly large one. The same check governs the after-state — a post-rewrite search returning zero remaining occurrences proves the rewrite landed only if that identical search returned the occurrences before it ran. *(Authored: the before-and-after pairing is this library's addition; the source states only the pre-search validation.)*

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
