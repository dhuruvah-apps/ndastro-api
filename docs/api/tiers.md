# Tiers API

Base path: `/api/v1/tiers`

Tiers control access levels and feature availability per user. All tier endpoints require authentication.

---

## Create Tier

```
POST /api/v1/tiers/
```

**Auth**: Superuser required

**Request body** (JSON):

```json
{
  "name": "premium"
}
```

**Response** `201 Created`:

```json
{
  "id": 2,
  "name": "premium",
  "created_at": "2024-01-15T10:00:00"
}
```

---

## List Tiers

```
GET /api/v1/tiers/
```

**Query parameters**:

| Param | Type | Default |
|-------|------|---------|
| `page` | `integer` | `1` |
| `items_per_page` | `integer` | `10` |

**Response** `200 OK`: Paginated list of `TierRead` objects.

---

## Get Tier

```
GET /api/v1/tiers/{name}
```

**Path parameter**: `name` — tier name (e.g., `free`, `premium`)

**Response** `200 OK`:

```json
{
  "id": 1,
  "name": "free",
  "created_at": "2024-01-01T00:00:00"
}
```

---

## Update Tier

```
PATCH /api/v1/tiers/{name}
```

**Auth**: Superuser required

**Path parameter**: `name`

**Request body** (JSON):

```json
{
  "name": "standard"
}
```

**Response** `200 OK`:

```json
{
  "message": "Tier updated successfully."
}
```

---

## Delete Tier

```
DELETE /api/v1/tiers/{name}
```

**Auth**: Superuser required

**Response** `200 OK`:

```json
{
  "message": "Tier deleted successfully."
}
```
