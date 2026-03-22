# Authentication API

Base path: `/api/v1/auth`

---

## Login

```
POST /api/v1/auth/login
```

Authenticates a user and returns access and refresh tokens.

**Request body** (form data):

| Field | Type | Description |
|-------|------|-------------|
| `username` | `string` | Username or email |
| `password` | `string` | User password |

**Response** `200 OK`:

```json
{
  "username": "john",
  "access_token": {
    "token": "<jwt>",
    "expires_in": 604800,
    "token_type": "bearer"
  },
  "refresh_token": {
    "token": "<jwt>",
    "expires_in": 31536000,
    "token_type": "bearer"
  }
}
```

!!! note
    `expires_in` values are in **seconds**. Access token defaults to 10080 min (7 days); refresh token defaults to 365 days.

---

## OAuth2 Token (Swagger UI)

```
POST /api/v1/auth/token
```

Standard OAuth2 password flow endpoint for use with the Swagger UI `Authorize` button.

**Request body** (form data — `application/x-www-form-urlencoded`):

| Field | Type |
|-------|------|
| `username` | `string` |
| `password` | `string` |

**Response**:

```json
{
  "access_token": "<jwt>",
  "expires_in": 604800,
  "token_type": "bearer"
}
```

---

## Refresh Token

```
POST /api/v1/auth/refresh
```

Exchanges a refresh token for new access and refresh tokens. Requires authentication.

**Request body** (JSON):

```json
{
  "token": "<refresh_jwt>",
  "expires_in": 31536000,
  "token_type": "bearer"
}
```

**Response** `200 OK`: Same structure as [Login](#login).

---

## Get Current User

```
GET /api/v1/auth/me
```

Returns the currently authenticated user's profile.

**Headers**: `Authorization: Bearer <access_token>`

**Response** `200 OK`:

```json
{
  "id": 1,
  "username": "john",
  "email": "john@example.com",
  "name": "John Doe",
  "is_superuser": false,
  "is_active": true
}
```

---

## Password Recovery

```
POST /api/v1/auth/password-recovery/{email}
```

Sends a password recovery email to the specified address.

**Path parameter**: `email` — the registered email address.

**Response** `200 OK`:

```json
{
  "message": "Password recovery email sent."
}
```

!!! info
    Email sending must be enabled via the `EMAILS_ENABLED=true` environment variable and a configured SMTP server.

---

## Logout

```
POST /api/v1/auth/logout
```

Blacklists the current access and refresh tokens, invalidating the session.

**Headers**: `Authorization: Bearer <access_token>`

The refresh token is read from the `refresh_token` HTTP-only cookie.

**Response** `200 OK`:

```json
{
  "message": "Logged out successfully."
}
```
