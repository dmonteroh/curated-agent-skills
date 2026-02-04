# EF Core - Performance and Reference

## Performance Optimization

```csharp
private static readonly Func<ApplicationDbContext, int, Task<Product?>> _getProductById =
    EF.CompileAsyncQuery((ApplicationDbContext context, int id) =>
        context.Products
            .Include(p => p.Category)
            .FirstOrDefault(p => p.Id == id));

public async Task<Product?> GetByIdOptimizedAsync(int id)
{
    return await _getProductById(_context, id);
}

public async Task<List<Order>> GetOrdersWithItemsAsync(
    CancellationToken cancellationToken = default)
{
    return await _context.Orders
        .Include(o => o.OrderItems)
            .ThenInclude(oi => oi.Product)
        .AsSplitQuery()
        .ToListAsync(cancellationToken);
}

public async Task AddRangeAsync(
    List<Product> products,
    CancellationToken cancellationToken = default)
{
    await _context.Products.AddRangeAsync(products, cancellationToken);
    await _context.SaveChangesAsync(cancellationToken);
}

public async Task<List<ProductSalesReport>> GetProductSalesReportAsync(
    int year,
    CancellationToken cancellationToken = default)
{
    return await _context.Database
        .SqlQuery<ProductSalesReport>(
            $@"SELECT p.Id, p.Name, SUM(oi.Quantity) as TotalSold, SUM(oi.Quantity * oi.UnitPrice) as Revenue
               FROM Products p
               INNER JOIN OrderItems oi ON p.Id = oi.ProductId
               INNER JOIN Orders o ON oi.OrderId = o.Id
               WHERE YEAR(o.CreatedAt) = {year}
               GROUP BY p.Id, p.Name
               ORDER BY Revenue DESC")
        .ToListAsync(cancellationToken);
}
```

## Quick Reference

| Pattern | Usage |
|---------|-------|
| `AsNoTracking()` | Read-only queries for better performance |
| `Include()` | Eager loading related entities |
| `ThenInclude()` | Loading nested relationships |
| `AsSplitQuery()` | Prevent cartesian explosion |
| `FirstOrDefaultAsync()` | Get single or null |
| `ToListAsync()` | Execute query and get list |
| `AddAsync()` | Add entity to context |
| `Update()` | Mark entity as modified |
| `Remove()` | Mark entity for deletion |
| `SaveChangesAsync()` | Persist changes to database |
