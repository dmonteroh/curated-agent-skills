# Clean Architecture - Project Structure

## Project Layout

```
Solution.sln
├── src/
│   ├── Domain/                    # Core business logic
│   │   ├── Entities/
│   │   ├── ValueObjects/
│   │   ├── Exceptions/
│   │   └── Interfaces/
│   ├── Application/               # Use cases, CQRS handlers
│   │   ├── Common/
│   │   ├── Products/
│   │   │   ├── Commands/
│   │   │   └── Queries/
│   │   └── DependencyInjection.cs
│   ├── Infrastructure/            # External concerns
│   │   ├── Persistence/
│   │   ├── Identity/
│   │   └── DependencyInjection.cs
│   └── WebApi/                    # API layer
│       ├── Endpoints/
│       ├── Filters/
│       └── Program.cs
└── tests/
```

## Domain Layer

```csharp
// Domain/Entities/Product.cs
namespace Domain.Entities;

public class Product
{
    public int Id { get; private set; }
    public string Name { get; private set; } = string.Empty;
    public string Description { get; private set; } = string.Empty;
    public decimal Price { get; private set; }
    public int CategoryId { get; private set; }
    public Category Category { get; private set; } = null!;
    public DateTime CreatedAt { get; private set; }
    public DateTime? UpdatedAt { get; private set; }

    private Product() { }

    public static Product Create(string name, string description, decimal price, int categoryId)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new DomainException("Product name is required");

        if (price <= 0)
            throw new DomainException("Product price must be greater than zero");

        return new Product
        {
            Name = name,
            Description = description,
            Price = price,
            CategoryId = categoryId,
            CreatedAt = DateTime.UtcNow
        };
    }

    public void Update(string name, string description, decimal price)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new DomainException("Product name is required");

        if (price <= 0)
            throw new DomainException("Product price must be greater than zero");

        Name = name;
        Description = description;
        Price = price;
        UpdatedAt = DateTime.UtcNow;
    }
}

// Domain/Exceptions/DomainException.cs
namespace Domain.Exceptions;

public class DomainException : Exception
{
    public DomainException(string message) : base(message) { }
}
```
