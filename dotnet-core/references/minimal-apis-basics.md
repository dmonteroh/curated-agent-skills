# Minimal APIs - Basics

## Basic Endpoint Patterns

```csharp
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.MapGet("/api/products", async (IProductService service) =>
{
    var products = await service.GetAllAsync();
    return Results.Ok(products);
});

app.MapGet("/api/products/{id:int}", async (int id, IProductService service) =>
{
    var product = await service.GetByIdAsync(id);
    return product is not null
        ? Results.Ok(product)
        : Results.NotFound();
});

app.MapPost("/api/products", async (
    [FromBody] CreateProductRequest request,
    IProductService service) =>
{
    var product = await service.CreateAsync(request);
    return Results.Created($"/api/products/{product.Id}", product);
})
.WithName("CreateProduct")
.Produces<ProductResponse>(StatusCodes.Status201Created)
.ProducesValidationProblem();

app.MapPut("/api/products/{id:int}", async (
    int id,
    [FromBody] UpdateProductRequest request,
    IProductService service) =>
{
    var success = await service.UpdateAsync(id, request);
    return success ? Results.NoContent() : Results.NotFound();
});

app.MapDelete("/api/products/{id:int}", async (int id, IProductService service) =>
{
    await service.DeleteAsync(id);
    return Results.NoContent();
});

app.Run();
```

## Route Groups

```csharp
var api = app.MapGroup("/api")
    .WithOpenApi()
    .RequireAuthorization();

var products = api.MapGroup("/products")
    .WithTags("Products");

products.MapGet("/", GetAllProducts);
products.MapGet("/{id:int}", GetProductById);
products.MapPost("/", CreateProduct);
products.MapPut("/{id:int}", UpdateProduct);
products.MapDelete("/{id:int}", DeleteProduct);

static async Task<IResult> GetAllProducts(IProductService service)
{
    var products = await service.GetAllAsync();
    return Results.Ok(products);
}

static async Task<IResult> GetProductById(int id, IProductService service)
{
    var product = await service.GetByIdAsync(id);
    return product is not null ? Results.Ok(product) : Results.NotFound();
}
```
