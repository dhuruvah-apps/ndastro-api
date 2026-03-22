# Environment Variables

All configuration is managed via environment variables (loaded from an `.env` file or the host environment). The application uses [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for validation.

---

## Application Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_NAME` | `string` | `"ND Astro Rest API"` | Application display name |
| `APP_DESCRIPTION` | `string` | — | API description shown in Swagger UI |
| `APP_VERSION` | `string` | — | API version string |
| `FRONTEND_HOST` | `string` | `"ndastro-ui.onrender.com"` | Primary frontend hostname for CORS |
| `FRONTENDADMIN_HOST` | `string` | `"ndastro-pwd-mgnt.onrender.com"` | Admin frontend hostname for CORS |
| `CORS_ORIGINS` | `list[string]` | `["*"]` | Allowed CORS origins |
| `TOKEN_TYPE` | `string` | `"bearer"` | OAuth2 token type |
| `ENVIRONMENT` | `string` | `"local"` | Runtime environment: `local`, `test`, `staging`, `production` |

---

## Security & JWT

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SECRET_KEY` | `string` | *(required)* | JWT signing secret — must be set in production |
| `ALGORITHM` | `string` | `"HS256"` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `int` | `10080` | Access token lifetime in minutes (7 days) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `int` | `365` | Refresh token lifetime in days |

!!! danger "Production Required"
    `SECRET_KEY` **must** be set to a strong random value in production. Generate one with:
    ```bash
    openssl rand -hex 32
    ```

---

## Database

`DATABASE_TYPE` selects the active database backend: `sqlite` (default), `postgres`, or `mysql`.

### SQLite (default)

| Variable | Default |
|----------|---------|
| `SQLITE_URI` | `"./ndastro_api/resources/data/ndastro_app.db"` |
| `SQLITE_SYNC_PREFIX` | `"sqlite:///"` |
| `SQLITE_ASYNC_PREFIX` | `"sqlite+aiosqlite:///"` |

### PostgreSQL

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `POSTGRES_USER` | `string` | `"postgres"` | DB username |
| `POSTGRES_PASSWORD` | `string` | `"postgres"` | DB password |
| `POSTGRES_SERVER` | `string` | `"localhost"` | DB host |
| `POSTGRES_PORT` | `int` | `5432` | DB port |
| `POSTGRES_DB` | `string` | `"postgres"` | Database name |
| `POSTGRES_URL` | `string` | — | Full connection string (overrides individual fields) |

### MySQL

| Variable | Type | Default |
|----------|------|---------|
| `MYSQL_USER` | `string` | `"username"` |
| `MYSQL_PASSWORD` | `string` | `"password"` |
| `MYSQL_SERVER` | `string` | `"localhost"` |
| `MYSQL_PORT` | `int` | `5432` |
| `MYSQL_DB` | `string` | `"dbname"` |
| `MYSQL_URL` | `string` | — |

---

## First Admin User

| Variable | Default | Description |
|----------|---------|-------------|
| `ADMIN_NAME` | `"admin"` | Display name for the initial superuser |
| `ADMIN_EMAIL` | `"admin@dapps.com"` | Email for the initial superuser |
| `ADMIN_USERNAME` | `"admin"` | Username for the initial superuser |
| `ADMIN_PASSWORD` | `""` | Password — **must be set before running `init-data`** |

---

## Email (SMTP)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `EMAILS_ENABLED` | `bool` | `false` | Enable email sending |
| `EMAILS_FROM_NAME` | `string` | `"ND Astro by DApps"` | Sender display name |
| `EMAILS_FROM_EMAIL` | `string` | `"ndastro@dhuruvah.in"` | Sender address |
| `SMTP_HOST` | `string` | `"smtppro.zoho.in"` | SMTP server host |
| `SMTP_PORT` | `int` | `465` | SMTP port |
| `SMTP_SSL` | `bool` | `true` | Use SSL |
| `SMTP_TLS` | `bool` | `false` | Use TLS (STARTTLS) |
| `SMTP_USER` | `string` | — | SMTP username |
| `SMTP_PASSWORD` | `string` | — | SMTP password |
| `EMAIL_RESET_TOKEN_EXPIRE_HOURS` | `int` | `24` | Password reset token validity |

---

## Admin Panel

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CRUD_ADMIN_ENABLED` | `bool` | `true` | Enable the admin UI at `/admin` |
| `CRUD_ADMIN_MOUNT_PATH` | `string` | `"/admin"` | Admin panel URL path |
| `CRUD_ADMIN_ALLOWED_IPS_LIST` | `list[string]` | — | IP allowlist for admin access |
| `CRUD_ADMIN_MAX_SESSIONS` | `int` | `10` | Max concurrent admin sessions |
| `CRUD_ADMIN_SESSION_TIMEOUT` | `int` | `1440` | Admin session timeout (minutes) |
| `SESSION_SECURE_COOKIES` | `bool` | `true` | Require HTTPS for session cookies |

---

## Client Caching

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CLIENT_CACHE_MAX_AGE` | `int` | `60` | `Cache-Control: max-age` value (seconds) |

---

## Minimal Production `.env` Example

```dotenv
ENVIRONMENT=production
DATABASE_TYPE=postgres

SECRET_KEY=<generate-with-openssl-rand-hex-32>

POSTGRES_USER=ndastro
POSTGRES_PASSWORD=<strong-password>
POSTGRES_SERVER=<db-host>
POSTGRES_DB=ndastro_db

ADMIN_EMAIL=admin@yourdomain.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong-admin-password>

EMAILS_ENABLED=true
SMTP_HOST=smtppro.zoho.in
SMTP_PORT=465
SMTP_SSL=true
SMTP_USER=ndastro@yourdomain.com
SMTP_PASSWORD=<smtp-password>

FRONTEND_HOST=yourdomain.com
CORS_ORIGINS=["https://yourdomain.com"]
```
