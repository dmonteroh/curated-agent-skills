# Feedback Guidelines

## Principles

- Specific and actionable feedback with clear outcomes.
- Code-focused, not person-focused.
- Balanced: highlight strengths and critical issues.
- Prioritized by severity and impact.

## Feedback structure

1) Observation: what is seen in the diff.
2) Impact: why it matters (risk, reliability, security).
3) Suggestion: concrete fix or alternative.

## Example phrasing

```
Observation: The retry loop never caps attempts.
Impact: Under outage conditions it may overwhelm downstream services.
Suggestion: Add exponential backoff and a max retry count.
```

## Handling disagreement

- Ask for intent or constraints before reasserting a recommendation.
- Offer a validation path (benchmark, test, or smaller change).
