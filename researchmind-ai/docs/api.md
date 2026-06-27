# API Reference

Base URL: `http://localhost:8000`

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

## System

### GET `/health`

Returns service health.

Response `200`:

```json
{
  "status": "ok",
  "service": "ResearchMind AI",
  "environment": "development"
}
```

### GET `/metrics`

Returns runtime counters and latency metrics.

Response `200`:

```json
{
  "uptime_seconds": 120.4,
  "request_count": 42,
  "error_count": 0,
  "average_latency_ms": 18.7,
  "path_counts": {},
  "status_counts": {},
  "agent_runs": {},
  "agent_failures": {}
}
```

## Authentication

### POST `/auth/register`

Request:

```json
{
  "email": "researcher@example.com",
  "full_name": "Researcher One",
  "password": "StrongPass123"
}
```

Response `201`: user profile.  
Status codes: `201`, `409`, `422`.

### POST `/auth/login`

Request:

```json
{
  "email": "researcher@example.com",
  "password": "StrongPass123"
}
```

Response `200`:

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer"
}
```

Status codes: `200`, `401`, `403`, `422`.

### POST `/auth/refresh`

Request:

```json
{
  "refresh_token": "<refresh_token>"
}
```

Response `200`: new token pair.  
Status codes: `200`, `401`, `422`.

### POST `/auth/logout`

Revokes the bearer token when present.

Response `200`:

```json
{
  "message": "Logged out successfully"
}
```

### GET `/auth/profile`

Response `200`: authenticated user profile.  
Status codes: `200`, `401`.

## Research

### POST `/research/start`

Starts the autonomous research workflow.

Request:

```json
{
  "title": "Agentic AI Research",
  "query": "Agentic AI in scientific research",
  "depth": 2,
  "citation_style": "APA"
}
```

Response `201`:

```json
{
  "id": 1,
  "title": "Agentic AI Research",
  "query": "Agentic AI in scientific research",
  "status": "completed",
  "created_at": "2026-06-27T00:00:00",
  "updated_at": "2026-06-27T00:00:30"
}
```

Status codes: `201`, `401`, `422`, `500`.

### GET `/research/history`

Returns research history for the authenticated user.

Status codes: `200`, `401`.

### GET `/research/{id}`

Returns project detail, latest state, report, execution logs, and agent executions.

Status codes: `200`, `401`, `404`.

### DELETE `/research/{id}`

Deletes a project owned by the authenticated user.

Response `200`:

```json
{
  "message": "Research project deleted"
}
```

Status codes: `200`, `401`, `404`.

## Reports

### GET `/report/{id}`

Returns report metadata, markdown, HTML, PDF path, and citations.

Status codes: `200`, `401`, `404`.

### GET `/report/{id}/pdf`

Downloads the generated PDF.

Status codes: `200`, `401`, `404`.

### GET `/report/{id}/markdown`

Returns markdown as `text/markdown`.

Status codes: `200`, `401`, `404`.

## Memory

### POST `/memory/store`

Request:

```json
{
  "content": "Agentic AI systems coordinate specialized agents.",
  "project_id": 1,
  "metadata": {
    "source": "manual-note"
  }
}
```

Response `201`:

```json
{
  "message": "Memory stored"
}
```

Status codes: `201`, `401`, `422`.

### GET `/memory/search?q=agentic&limit=5`

Searches user-scoped ChromaDB memory.

Response `200`:

```json
{
  "results": ["Agentic AI systems coordinate specialized agents."]
}
```

Status codes: `200`, `401`, `422`.

### DELETE `/memory/clear`

Clears user memory from SQLite and ChromaDB.

Status codes: `200`, `401`.
