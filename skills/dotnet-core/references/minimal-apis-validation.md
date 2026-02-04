# Minimal APIs - Validation and DI

## Filters and Validation

```csharp
using FluentValidation;

public record CreateProductRequest(
    string Name,
    string Description,
    decimal Price,
    int CategoryId
);

public class CreateProductValidator : AbstractValidator<CreateProductRequest>
{
    public CreateProductValidator()
    {
        RuleFor(x => x.Name)
            .NotEmpty()
            .MaximumLength(100);

        RuleFor(x => x.Price)
            .GreaterThan(0)
            .LessThan(1000000);

        RuleFor(x => x.CategoryId)
            .GreaterThan(0);
    }
}

public class ValidationFilter<T> : IEndpointFilter where T : class
{
    private readonly IValidator<T> _validator;

    public ValidationFilter(IValidator<T> validator)
    {
        _validator = validator;
    }

    public async ValueTask<object?> InvokeAsync(
        EndpointFilterInvocationContext context,
        EndpointFilterDelegate next)
    {
        var request = context.Arguments.OfType<T>().FirstOrDefault();
        if (request is null)
        {
            return Results.BadRequest("Invalid request");
        }

        var validationResult = await _validator.ValidateAsync(request);
        if (!validationResult.IsValid)
        {
            return Results.ValidationProblem(
                validationResult.ToDictionary());
        }

        return await next(context);
    }
}

builder.Services.AddValidatorsFromAssemblyContaining<Program>();

app.MapPost("/api/products", CreateProduct)
    .AddEndpointFilter<ValidationFilter<CreateProductRequest>>();
```

## Dependency Injection

```csharp
builder.Services.AddScoped<IProductService, ProductService>();
builder.Services.AddScoped<IProductRepository, ProductRepository>();

app.MapPost("/api/orders", async (
    CreateOrderRequest request,
    IOrderService orderService,
    IEmailService emailService,
    ILogger<Program> logger,
    CancellationToken ct) =>
{
    logger.LogInformation("Creating order for {CustomerId}", request.CustomerId);

    var order = await orderService.CreateAsync(request, ct);
    await emailService.SendOrderConfirmationAsync(order.Id, ct);

    return Results.Created($"/api/orders/{order.Id}", order);
});
```
