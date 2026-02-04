# Clean Architecture - API Integration

## Minimal API Endpoints

```csharp
// WebApi/Endpoints/ProductEndpoints.cs
using Application.Products.Commands.CreateProduct;
using Application.Products.Queries.GetProducts;
using MediatR;

namespace WebApi.Endpoints;

public static class ProductEndpoints
{
    public static IEndpointRouteBuilder MapProductEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/products")
            .WithTags("Products")
            .WithOpenApi();

        group.MapGet("/", async (
            [AsParameters] GetProductsQuery query,
            ISender sender) =>
        {
            var result = await sender.Send(query);
            return Results.Ok(result);
        });

        group.MapPost("/", async (
            CreateProductCommand command,
            ISender sender) =>
        {
            var product = await sender.Send(command);
            return Results.Created($"/api/products/{product.Id}", product);
        });

        return app;
    }
}
```

## Quick Reference

| Pattern | Purpose |
|---------|---------|
| `IRequest<T>` | MediatR command/query interface |
| `IRequestHandler<TReq, TRes>` | Handler implementation |
| `IPipelineBehavior<,>` | Cross-cutting concerns |
| `IValidator<T>` | FluentValidation interface |
| `ISender` | MediatR sender for endpoints |
| Domain entities | Business logic and invariants |
| Application layer | Use cases and orchestration |
| Infrastructure | External dependencies |
