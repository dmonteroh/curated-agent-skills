# Python MCP SDK Notes (Practical)

Use this as a compact checklist for real implementations.

## Validation

- Use Pydantic models for tool inputs (strict where possible).
- Validate early and return actionable errors.

## Transport/logging

- For stdio transport: keep protocol on stdout; log to stderr.

## Error handling

- Normalize errors into a stable shape with a short message and a next-step hint.
- Avoid dumping upstream payloads unless explicitly requested.

## Testing

- Add at least one end-to-end scenario per high-value tool.
- Verify pagination caps and truncation behavior for large data.

