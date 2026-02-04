# Cloud-Native - Caching and Observability

## Distributed Caching with Redis

```csharp
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = builder.Configuration.GetConnectionString("Redis");
    options.InstanceName = "MyApp_";
});

public class CachedProductService
{
    private readonly IProductService _productService;
    private readonly IDistributedCache _cache;
    private readonly ILogger<CachedProductService> _logger;

    public CachedProductService(
        IProductService productService,
        IDistributedCache cache,
        ILogger<CachedProductService> logger)
    {
        _productService = productService;
        _cache = cache;
        _logger = logger;
    }

    public async Task<Product?> GetByIdAsync(int id, CancellationToken cancellationToken = default)
    {
        var cacheKey = $"product_{id}";

        var cachedData = await _cache.GetStringAsync(cacheKey, cancellationToken);
        if (cachedData is not null)
        {
            _logger.LogInformation("Cache hit for product {ProductId}", id);
            return JsonSerializer.Deserialize<Product>(cachedData);
        }

        _logger.LogInformation("Cache miss for product {ProductId}", id);
        var product = await _productService.GetByIdAsync(id, cancellationToken);

        if (product is not null)
        {
            var options = new DistributedCacheEntryOptions
            {
                AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(10)
            };

            await _cache.SetStringAsync(
                cacheKey,
                JsonSerializer.Serialize(product),
                options,
                cancellationToken);
        }

        return product;
    }
}
```

## OpenTelemetry Observability

```csharp
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;
using OpenTelemetry.Metrics;

var otlpEndpoint = builder.Configuration["Telemetry:OtlpEndpoint"];

builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource.AddService("MyApp"))
    .WithTracing(tracing =>
    {
        tracing.AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation()
            .AddEntityFrameworkCoreInstrumentation();

        if (!string.IsNullOrWhiteSpace(otlpEndpoint))
        {
            tracing.AddOtlpExporter(options =>
            {
                options.Endpoint = new Uri(otlpEndpoint);
            });
        }
    })
    .WithMetrics(metrics => metrics
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddRuntimeInstrumentation()
        .AddPrometheusExporter());

app.MapPrometheusScrapingEndpoint();
```
