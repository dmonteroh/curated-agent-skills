# Cloud-Native - Graceful Shutdown

```csharp
builder.Services.Configure<HostOptions>(options =>
{
    options.ShutdownTimeout = TimeSpan.FromSeconds(30);
});

public class DataProcessingService : BackgroundService
{
    private readonly ILogger<DataProcessingService> _logger;

    public DataProcessingService(ILogger<DataProcessingService> logger)
    {
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Data processing service starting");

        try
        {
            while (!stoppingToken.IsCancellationRequested)
            {
                await ProcessDataAsync(stoppingToken);
                await Task.Delay(TimeSpan.FromMinutes(5), stoppingToken);
            }
        }
        catch (OperationCanceledException)
        {
            _logger.LogInformation("Data processing service is stopping");
        }
    }

    private async Task ProcessDataAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Processing data batch");
        await Task.Delay(1000, cancellationToken);
    }

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Data processing service stopping");
        await base.StopAsync(cancellationToken);
        _logger.LogInformation("Data processing service stopped");
    }
}
```
