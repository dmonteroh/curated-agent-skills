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

## Safe Refactor Checklist

- Preserve public interfaces unless explicitly approved.
- Keep each change reviewable and revertible.
- Avoid mixing refactors with behavior changes.
- Prefer composition over inheritance for new structure.
