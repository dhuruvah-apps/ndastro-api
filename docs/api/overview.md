# API Reference Overview

**ndastro-api** is a RESTful API built with [FastAPI](https://fastapi.tiangolo.com/). All endpoints are grouped under the `/api/v1` prefix.

## Base URL

```
https://<your-domain>/api/v1
```

The interactive Swagger UI is available at:

```
https://<your-domain>/api/v1/docs
```

## Authentication

Most endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Tokens are obtained via [`POST /api/v1/auth/login`](auth.md#login).

## All Endpoints

| Method | Path | Auth | Summary |
|--------|------|------|---------|
| `POST` | `/api/v1/auth/token` | No | OAuth2 token (Swagger UI) |
| `POST` | `/api/v1/auth/login` | No | Login → tokens |
| `POST` | `/api/v1/auth/refresh` | Yes | Rotate tokens |
| `GET` | `/api/v1/auth/me` | Yes | Current user |
| `POST` | `/api/v1/auth/password-recovery/{email}` | No | Password recovery |
| `POST` | `/api/v1/auth/logout` | Yes | Logout |
| `POST` | `/api/v1/users/` | Superuser | Create user |
| `GET` | `/api/v1/users/` | Yes | List users |
| `GET` | `/api/v1/users/{username}` | Yes | Get user |
| `PATCH` | `/api/v1/users/{username}` | Yes | Update user |
| `DELETE` | `/api/v1/users/{username}` | Superuser | Soft-delete user |
| `DELETE` | `/api/v1/users/db_user/{username}` | Superuser | Hard-delete user |
| `GET` | `/api/v1/users/{username}/tier` | Yes | Get user tier |
| `PATCH` | `/api/v1/users/{username}/tier` | Superuser | Update user tier |
| `POST` | `/api/v1/tiers/` | Superuser | Create tier |
| `GET` | `/api/v1/tiers/` | Yes | List tiers |
| `GET` | `/api/v1/tiers/{name}` | Yes | Get tier |
| `PATCH` | `/api/v1/tiers/{name}` | Superuser | Update tier |
| `DELETE` | `/api/v1/tiers/{name}` | Superuser | Delete tier |
| `GET` | `/api/v1/astro/lunar-nodes` | Tier-based | Rahu & Kethu positions (`node_type` override) |
| `GET` | `/api/v1/astro/planets` | Tier-based | All planet positions (`node_type`, `position_reference` overrides) |
| `GET` | `/api/v1/astro/ascendant` | Tier-based | Ascendant position |
| `GET` | `/api/v1/astro/sunrise-sunset` | Tier-based | Sunrise & sunset |
| `GET` | `/api/v1/astro/kattams` | Tier-based | 12-house kattam chart |
| `GET` | `/api/v1/astro/chart` | Tier-based | SVG chart image |
| `GET` | `/api/v1/astro/panchanga` | Tier-based | Full panchanga with timing windows |
| `GET` | `/api/v1/muhurta` | Tier-based | Single-day muhurta analysis (Durmuhurta, Varjyam, Amrita Kala) |
| `GET` | `/api/v1/muhurta/auspicious-range` | Tier-based | Best dates in a range for a life event (70 event types, 5-formula scoring) |
| `GET` | `/api/v1/prasna/query-topic` | Tier-based | Predict the topic of an unspoken query (Prasna Shastra, 6-rule chart analysis) |
| `GET` | `/api/v1/location/search` | Tier-based | Geocode free-form text → lat, lon, timezone |
| `GET` | `/health-check` | No | API health status |
| `GET` | `/metrics` | No | System metrics |
| `GET` | `/api/v1/config` | Yes | Active engine calculation settings |

## Response Format

### Success

All successful responses follow standard HTTP status codes:

- `200 OK` — successful read/update
- `201 Created` — successful creation

### Error

```json
{
  "detail": "Error message here"
}
```

Custom application errors (from business logic):

```json
{
  "error": "Error message here"
}
```

### Common HTTP Error Codes

| Code | Meaning |
|------|---------|
| `400` | Bad request / invalid input |
| `401` | Unauthorized — missing or invalid token |
| `403` | Forbidden — insufficient permissions |
| `404` | Resource not found |
| `409` | Conflict — duplicate resource |
| `429` | Rate limit exceeded |
| `500` | Internal server error |

## Pagination

List endpoints accept `page` and `items_per_page` query parameters and return:

```json
{
  "items": [...],
  "total": 100,
  "total_count": 100,
  "has_more": true,
  "page": 1,
  "items_per_page": 10
}
```
