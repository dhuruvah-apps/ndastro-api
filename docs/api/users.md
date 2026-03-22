# Users API

Base path: `/api/v1/users`

All user endpoints require authentication. Superuser privileges are needed for create, delete, and tier-update operations.

---

## Create User

```
POST /api/v1/users/
```

**Auth**: Superuser required

**Request body** (JSON):

```json
{
  "username": "jane",
  "email": "jane@example.com",
  "name": "Jane Doe",
  "password": "securepassword",
  "is_superuser": false
}
```

**Response** `201 Created`:

```json
{
  "id": 2,
  "username": "jane",
  "email": "jane@example.com",
  "name": "Jane Doe",
  "is_superuser": false,
  "is_active": true,
  "created_at": "2024-01-15T10:00:00"
}
```

---

## List Users

```
GET /api/v1/users/
```

Returns a paginated list of users.

**Query parameters**:

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | `integer` | `1` | Page number |
| `items_per_page` | `integer` | `10` | Items per page |

**Response** `200 OK`:

```json
{
  "items": [...],
  "total": 50,
  "total_count": 50,
  "has_more": true,
  "page": 1,
  "items_per_page": 10
}
```

---

## Get User

```
GET /api/v1/users/{username}
```

**Path parameter**: `username`

**Response** `200 OK`: `UserRead` object (same as Create response).

---

## Update User

```
PATCH /api/v1/users/{username}
```

Updates a user's own profile. Superusers can update any user.

**Path parameter**: `username`

**Request body** (JSON, all fields optional):

```json
{
  "email": "new@example.com",
  "name": "New Name",
  "password": "newpassword"
}
```

**Response** `200 OK`:

```json
{
  "message": "User updated successfully."
}
```

---

## Soft-Delete User

```
DELETE /api/v1/users/{username}
```

**Auth**: Superuser required

Marks the user as deleted (`is_deleted=true`, sets `deleted_at`). The user record is retained in the database.

**Response** `200 OK`:

```json
{
  "message": "User deleted successfully."
}
```

---

## Hard-Delete User

```
DELETE /api/v1/users/db_user/{username}
```

**Auth**: Superuser required

Permanently removes the user record from the database.

**Response** `200 OK`:

```json
{
  "message": "User permanently deleted."
}
```

---

## Get User Tier

```
GET /api/v1/users/{username}/tier
```

Returns the tier assigned to a user.

**Response** `200 OK`:

```json
{
  "tier_id": 1,
  "name": "free",
  "created_at": "2024-01-01T00:00:00"
}
```

Returns `null` if the user has no tier assigned.

---

## Update User Tier

```
PATCH /api/v1/users/{username}/tier
```

**Auth**: Superuser required

**Request body** (JSON):

```json
{
  "tier_id": 2
}
```

**Response** `200 OK`:

```json
{
  "message": "User tier updated successfully."
}
```
