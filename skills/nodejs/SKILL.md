---
name: nodejs
description: "Use when building production-ready Node.js backend services with Express or Fastify, covering API design, middleware, authentication, error handling, and database integration."
metadata:
  category: language
---
# Node.js Backend Patterns

Provides guidance for building scalable, maintainable Node.js backend applications with modern frameworks, architectural patterns, and operational best practices.

## Use this skill when

- Building REST APIs, GraphQL backends, or RPC services with Node.js
- Designing backend architecture, middleware, or error handling patterns
- Implementing authentication, authorization, or request validation
- Integrating Node.js services with databases, queues, or caches
- Planning operational readiness (logging, metrics, health checks)

## Do not use this skill when

- The request is unrelated to Node.js backend development
- The task focuses on frontend-only code, mobile apps, or infrastructure provisioning
- The user explicitly needs a non-Node.js runtime (Go, Python, Java, etc.)

## Required inputs

- Target framework (Express, Fastify, or unspecified)
- Service scope (API type, endpoints, or core responsibilities)
- Data sources (databases, caches, queues) and constraints
- Auth requirements (JWT, sessions, API keys, etc.)
- Operational constraints (deployment target, runtime limits)

## Instructions

1. Confirms goals, constraints, and missing inputs.
   - Output: a short scope summary and any clarification questions.
2. Selects the architecture and framework approach.
   - Decision point: if simplicity or broad compatibility is needed, pick Express; if performance or schema-driven validation is critical, pick Fastify.
   - Output: a recommended stack and rationale.
3. Defines the API contract and data model.
   - Decision point: if clients need flexible querying, choose GraphQL; if they need stable HTTP contracts, choose REST; if internal service calls dominate, choose RPC.
   - Output: endpoint list, request/response shapes, and data entities.
4. Plans middleware, auth, validation, and error handling.
   - Output: middleware sequence, auth strategy, and error response format.
5. Plans integrations and operational readiness.
   - Decision point: if work is long-running or retriable, use a queue; if latency is critical, keep it synchronous and cache where appropriate.
   - Output: integration checklist and observability requirements.
6. Provides implementation guidance and verification steps.
   - Output: ordered build steps and exact checks or tests to run.

## Common pitfalls

- Omitting input validation or returning inconsistent error shapes
- Mixing business logic into controllers instead of services/modules
- Hardcoding secrets or environment-specific values
- Forgetting graceful shutdown for database/queue connections

## Examples

**Example 1: REST API**

Input:
“Design a Node.js REST API for an order service with JWT auth.”

Output (summary):
- Recommend Fastify with schema validation
- Provide endpoint list for orders and authentication
- Outline middleware order, error format, and verification steps

**Example 2: Background jobs**

Input:
“Add a queue worker for email notifications in an Express app.”

Output (summary):
- Propose a worker process and shared job schema
- Identify required config and retry policy
- Provide step-by-step integration checklist

## Output contract

Response includes these sections:
- Summary
- Decisions (framework, API style, integrations)
- Implementation steps
- Risks & pitfalls
- Verification
- References (if used)

## References

- See `references/README.md` for detailed patterns and examples.
