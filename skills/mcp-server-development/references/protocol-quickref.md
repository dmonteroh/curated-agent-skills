# MCP Protocol Quick Reference (JSON-RPC 2.0)

This is a compact reference so you don't have to open long specs mid-task.

## Message shapes (JSON-RPC 2.0)

- Request:
  - `jsonrpc: \"2.0\"`
  - `id`
  - `method`
  - `params` (optional)
- Response:
  - `jsonrpc: \"2.0\"`
  - `id`
  - `result` (success) OR `error` (failure)

## Lifecycle (typical)

1) Client connects (stdio/HTTP/SSE)
2) Client sends `initialize` -> server responds with capabilities
3) Client sends `notifications/initialized`
4) Normal operation:
   - `tools/list`, `tools/call`
   - `resources/list`, `resources/read`, subscriptions if supported
   - `prompts/list`, `prompts/get` if you provide prompts
5) Shutdown/close

## Core method families (mental map)

- Tools:
  - `tools/list`
  - `tools/call`
- Resources:
  - `resources/list`
  - `resources/read`
  - subscribe/unsubscribe (if supported)
- Prompts:
  - `prompts/list`
  - `prompts/get`

## Error handling guidance

- Return structured, actionable errors.
- Keep error messages short by default; include a “hint” for next steps when possible.

