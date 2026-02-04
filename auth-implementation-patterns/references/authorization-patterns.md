# Authorization Patterns

## Role-Based Access Control (RBAC)

- Assign roles to users; roles map to permissions.
- Keep role checks centralized in middleware or policy layers.

## Permission-Based Access Control

- Use explicit permissions for granular access.
- Prefer policies like `resource:action` (e.g., `invoice:approve`).

## Resource Ownership

- Enforce ownership at the data access layer.
- Check `resource.ownerId === requester.id` where applicable.

## Policy Enforcement Points

- API gateway or middleware for coarse checks.
- Service/domain layer for sensitive business rules.
