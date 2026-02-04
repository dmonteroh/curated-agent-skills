# Session-Based Authentication

## Session Checklist

- Store session state server-side (DB, Redis, memory store).
- Use secure cookies: `httpOnly`, `secure`, `sameSite`.
- Rotate session identifiers after login or privilege change.
- Set idle and absolute timeouts.

## Example (Pseudocode)

```ts
app.use(session({
  secret: SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: { httpOnly: true, secure: true, sameSite: 'lax' },
}));
```

## CSRF Considerations

- Use CSRF tokens for state-changing requests.
- Validate origin and referer headers where feasible.
