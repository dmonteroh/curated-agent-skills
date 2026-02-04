# Diagram Patterns

Use diagrams when a flow has multiple branches, async steps, or layered components.

## Flowchart (control flow)

```mermaid
flowchart TD
    A[Entry point] --> B{Decision}
    B -->|Yes| C[Happy path]
    B -->|No| D[Fallback]
    C --> E[Exit]
    D --> E
```

## Sequence (request lifecycle)

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant DB
    Client->>API: Request
    API->>DB: Read
    DB-->>API: Rows
    API-->>Client: Response
```

## Class diagram (data model or APIs)

```mermaid
classDiagram
    class Service {
        +execute(request)
        -validate(request)
    }
    class Repository {
        +find(id)
        +save(entity)
    }
    Service --> Repository
```

## Selection tips

- Prefer flowcharts for branching control flow.
- Prefer sequence diagrams for async or multi-service interactions.
- Prefer class diagrams for object relationships or stable APIs.
