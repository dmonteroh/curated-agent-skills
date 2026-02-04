# Authentication - Authorization and Current User

## Authorization Policies

```csharp
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy =>
        policy.RequireRole("Admin"));

    options.AddPolicy("UserOrAdmin", policy =>
        policy.RequireRole("User", "Admin"));

    options.AddPolicy("RequireEmailVerified", policy =>
        policy.RequireClaim("email_verified", "true"));
});

app.MapGet("/api/admin/users", GetAllUsers)
    .RequireAuthorization("AdminOnly");

app.MapGet("/api/profile", GetProfile)
    .RequireAuthorization();

app.MapPost("/api/products", CreateProduct)
    .RequireAuthorization("AdminOnly");
```

## Current User Service

```csharp
// Application/Common/Interfaces/ICurrentUserService.cs
namespace Application.Common.Interfaces;

public interface ICurrentUserService
{
    int? UserId { get; }
    string? Email { get; }
    bool IsAuthenticated { get; }
    bool IsInRole(string role);
}

// Infrastructure/Services/CurrentUserService.cs
using System.Security.Claims;
using Microsoft.AspNetCore.Http;

namespace Infrastructure.Services;

public class CurrentUserService : ICurrentUserService
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public CurrentUserService(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    public int? UserId
    {
        get
        {
            var userIdClaim = _httpContextAccessor.HttpContext?.User?
                .FindFirstValue(ClaimTypes.NameIdentifier);

            return int.TryParse(userIdClaim, out var userId) ? userId : null;
        }
    }

    public string? Email =>
        _httpContextAccessor.HttpContext?.User?.FindFirstValue(ClaimTypes.Email);

    public bool IsAuthenticated =>
        _httpContextAccessor.HttpContext?.User?.Identity?.IsAuthenticated ?? false;

    public bool IsInRole(string role) =>
        _httpContextAccessor.HttpContext?.User?.IsInRole(role) ?? false;
}

builder.Services.AddHttpContextAccessor();
builder.Services.AddScoped<ICurrentUserService, CurrentUserService>();
```

## Quick Reference

| Pattern | Usage |
|---------|-------|
| `RequireAuthorization()` | Endpoint requires authentication |
| `RequireAuthorization("Policy")` | Endpoint requires specific policy |
| `AllowAnonymous()` | Allow unauthenticated access |
| `RequireRole("Admin")` | Require specific role |
| `ICurrentUserService` | Access current user info |
