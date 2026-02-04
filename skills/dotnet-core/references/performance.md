# .NET Performance Notes

- Avoid blocking on async (`.Result`, `.Wait()`).
- Use pooled objects for hot paths (`ArrayPool<T>`).
- Cache compiled regex and expensive serializers.
- Use `IAsyncEnumerable<T>` for streaming.
