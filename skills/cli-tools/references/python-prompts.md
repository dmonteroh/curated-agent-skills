# Python Interactive Prompts

## questionary

```python
import questionary

# Text input
name = questionary.text(
    "Project name:",
    default="my-project",
    validate=lambda x: len(x) > 0 or "Name required"
).ask()

# Select from list
environment = questionary.select(
    "Select environment:",
    choices=["development", "staging", "production"],
    default="development"
).ask()

# Checkbox (multi-select)
features = questionary.checkbox(
    "Select features:",
    choices=[
        questionary.Choice("TypeScript", checked=True),
        questionary.Choice("ESLint", checked=True),
        questionary.Choice("Prettier", checked=True),
        questionary.Choice("Jest", checked=False),
    ]
).ask()

# Confirmation
confirmed = questionary.confirm(
    "Deploy to production?",
    default=False
).ask()

if confirmed:
    deploy()

# Password
password = questionary.password("Enter password:").ask()
```
