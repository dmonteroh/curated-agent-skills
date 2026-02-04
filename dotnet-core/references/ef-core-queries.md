# EF Core - Query Patterns

```csharp
public async Task<List<Product>> GetProductsByCategoryAsync(
    int categoryId,
    CancellationToken cancellationToken = default)
{
    return await _context.Products
        .AsNoTracking()
        .Include(p => p.Category)
        .Where(p => p.CategoryId == categoryId)
        .OrderBy(p => p.Name)
        .ToListAsync(cancellationToken);
}

public async Task<PagedResult<Product>> GetPagedProductsAsync(
    int page,
    int pageSize,
    CancellationToken cancellationToken = default)
{
    var query = _context.Products
        .AsNoTracking()
        .Include(p => p.Category);

    var totalCount = await query.CountAsync(cancellationToken);

    var items = await query
        .Skip((page - 1) * pageSize)
        .Take(pageSize)
        .ToListAsync(cancellationToken);

    return new PagedResult<Product>(items, totalCount, page, pageSize);
}

public async Task<List<ProductDto>> GetProductDtosAsync(
    CancellationToken cancellationToken = default)
{
    return await _context.Products
        .AsNoTracking()
        .Select(p => new ProductDto(
            p.Id,
            p.Name,
            p.Description,
            p.Price,
            p.Category.Name))
        .ToListAsync(cancellationToken);
}

public async Task<List<Product>> GetProductsBySpecificationAsync(
    Expression<Func<Product, bool>> predicate,
    CancellationToken cancellationToken = default)
{
    return await _context.Products
        .AsNoTracking()
        .Where(predicate)
        .ToListAsync(cancellationToken);
}

public async Task<decimal> GetTotalRevenueAsync(
    int year,
    CancellationToken cancellationToken = default)
{
    return await _context.Orders
        .AsNoTracking()
        .Where(o => o.CreatedAt.Year == year && o.Status == OrderStatus.Completed)
        .SelectMany(o => o.OrderItems)
        .SumAsync(oi => oi.Quantity * oi.UnitPrice, cancellationToken);
}
```
