# Cloud-Native - Configuration and Logging

## Configuration Management

```csharp
// appsettings.json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=MyApp;Integrated Security=true;"
  },
  "JwtSettings": {
    "Secret": "",
    "Issuer": "MyApp",
    "Audience": "MyAppUsers",
    "ExpirationMinutes": 60
  },
  "Features": {
    "EnableSwagger": true,
    "EnableMetrics": true
  }
}

public class ApplicationSettings
{
    public const string SectionName = "ApplicationSettings";

    public required string ApplicationName { get; init; }
    public required int MaxRequestSize { get; init; }
    public required bool EnableCaching { get; init; }
}

builder.Services.Configure<ApplicationSettings>(
    builder.Configuration.GetSection(ApplicationSettings.SectionName));

public class MyService
{
    private readonly ApplicationSettings _settings;

    public MyService(IOptions<ApplicationSettings> options)
    {
        _settings = options.Value;
    }
}

builder.Configuration
    .AddJsonFile("appsettings.json", optional: false)
    .AddJsonFile($"appsettings.{builder.Environment.EnvironmentName}.json", optional: true)
    .AddEnvironmentVariables()
    .AddUserSecrets<Program>(optional: true);
```

## Structured Logging

```csharp
using Serilog;
using Serilog.Events;

builder.Host.UseSerilog((context, configuration) =>
{
    configuration
        .MinimumLevel.Information()
        .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
        .MinimumLevel.Override("Microsoft.Hosting.Lifetime", LogEventLevel.Information)
        .Enrich.FromLogContext()
        .Enrich.WithMachineName()
        .Enrich.WithEnvironmentName()
        .WriteTo.Console(outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}")
        .WriteTo.File(
            "logs/app-.log",
            rollingInterval: RollingInterval.Day,
            outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj}{NewLine}{Exception}");
});

public class ProductService
{
    private readonly ILogger<ProductService> _logger;

    public ProductService(ILogger<ProductService> logger)
    {
        _logger = logger;
    }

    public async Task<Product> CreateAsync(CreateProductRequest request)
    {
        _logger.LogInformation(
            "Creating product {ProductName} with price {Price}",
            request.Name,
            request.Price);

        try
        {
            var product = Product.Create(request.Name, request.Description, request.Price, request.CategoryId);

            _logger.LogInformation(
                "Product {ProductId} created successfully",
                product.Id);

            return product;
        }
        catch (Exception ex)
        {
            _logger.LogError(
                ex,
                "Failed to create product {ProductName}",
                request.Name);
            throw;
        }
    }
}
```
