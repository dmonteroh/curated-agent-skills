# Minimal APIs - Responses and Error Handling

## Response Patterns

```csharp
public record ProductResponse(
    int Id,
    string Name,
    string Description,
    decimal Price,
    string CategoryName
);

app.MapGet("/api/products/{id:int}", async (int id, IProductService service) =>
{
    var product = await service.GetByIdAsync(id);
    return product is not null
        ? Results.Ok(product)
        : Results.NotFound(new { Message = "Product not found" });
})
.Produces<ProductResponse>(StatusCodes.Status200OK)
.Produces(StatusCodes.Status404NotFound);

public class PagedResult<T>
{
    public required List<T> Items { get; init; }
    public required int TotalCount { get; init; }
    public required int Page { get; init; }
    public required int PageSize { get; init; }
}

app.MapGet("/api/products", async (
    [AsParameters] PaginationParams pagination,
    IProductService service) =>
{
    var result = await service.GetPagedAsync(
        pagination.Page,
        pagination.PageSize);
    return Results.Ok(result);
})
.Produces<PagedResult<ProductResponse>>();

public record PaginationParams(int Page = 1, int PageSize = 10);
```

## Error Handling

```csharp
app.UseExceptionHandler(exceptionHandlerApp =>
{
    exceptionHandlerApp.Run(async context =>
    {
        var exceptionHandlerFeature =
            context.Features.Get<IExceptionHandlerFeature>();
        var exception = exceptionHandlerFeature?.Error;

        var problemDetails = new ProblemDetails
        {
            Status = StatusCodes.Status500InternalServerError,
            Title = "An error occurred",
            Detail = exception?.Message
        };

        context.Response.StatusCode = StatusCodes.Status500InternalServerError;
        await context.Response.WriteAsJsonAsync(problemDetails);
    });
});

public class ErrorHandlingFilter : IEndpointFilter
{
    private readonly ILogger<ErrorHandlingFilter> _logger;

    public ErrorHandlingFilter(ILogger<ErrorHandlingFilter> logger)
    {
        _logger = logger;
    }

    public async ValueTask<object?> InvokeAsync(
        EndpointFilterInvocationContext context,
        EndpointFilterDelegate next)
    {
        try
        {
            return await next(context);
        }
        catch (ValidationException ex)
        {
            _logger.LogWarning(ex, "Validation failed");
            return Results.ValidationProblem(ex.Errors.ToDictionary(
                e => e.PropertyName,
                e => new[] { e.ErrorMessage }
            ));
        }
        catch (NotFoundException ex)
        {
            _logger.LogWarning(ex, "Resource not found");
            return Results.NotFound(new { Message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception");
            return Results.Problem("An unexpected error occurred");
        }
    }
}
```

## Quick Reference

| Pattern | Usage |
|---------|-------|
| `Results.Ok(data)` | 200 with response body |
| `Results.Created(uri, data)` | 201 with location header |
| `Results.NoContent()` | 204 no response body |
| `Results.BadRequest()` | 400 validation error |
| `Results.NotFound()` | 404 resource not found |
| `Results.Unauthorized()` | 401 authentication required |
| `Results.Forbid()` | 403 authorization failed |
| `app.MapGroup()` | Group related endpoints |
| `.WithTags()` | OpenAPI tag grouping |
| `.Produces<T>()` | Document response type |
