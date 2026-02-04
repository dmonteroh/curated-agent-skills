# Pattern: Privacy by Design/Default

Use this reference to translate privacy-by-design requirements into concrete controls.

## Minimization Checklist

- Collect only fields required for the stated purpose.
- Separate optional data into distinct flows with explicit opt-in.
- Avoid copying personal data into analytics unless required.

## Default Settings

- Default to the least intrusive setting (e.g., analytics off).
- Require affirmative action to enable optional processing.
- Provide an easy way to withdraw or change preferences.

## Access, Logging, and Security

- Enforce least-privilege access with reviewable roles.
- Mask or redact sensitive fields in logs and exports.
- Encrypt data in transit and at rest where appropriate.

## Pseudonymization Patterns

- Replace direct identifiers with stable pseudonyms for analytics.
- Store re-identification keys in a separate system with stricter access.

## DPIA Triggers (Common)

- Large-scale processing of special categories.
- Systematic monitoring or profiling.
- Use of new technologies with unclear risk profiles.
