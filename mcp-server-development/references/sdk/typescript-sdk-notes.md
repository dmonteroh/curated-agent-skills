# TypeScript MCP SDK Notes (Practical)

Use this as a “things I always forget” checklist.

## Defaults

- Use strict schemas (Zod `.strict()`).
- Ensure output is stable and concise by default.
- Avoid `any`; keep tool inputs/outputs typed.

## Safety

- Log to stderr (or logger sink) if using stdio transport; do not pollute stdout if stdout is protocol transport.
- Ensure tool calls have timeouts/retry behavior only where safe (don’t retry destructive calls blindly).

## Testing

- Add at least one end-to-end scenario per high-value tool (happy path + one failure).
- Validate large-list tools with pagination and caps to avoid token blowups.

