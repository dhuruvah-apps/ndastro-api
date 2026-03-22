# Quick Start

## Hosted API

The ndastro-api is publicly hosted on Render and available immediately — no local setup required.

**Base URL**: [https://ndastro-api.onrender.com](https://ndastro-api.onrender.com)

| Resource | URL |
|----------|-----|
| Interactive Docs (Swagger UI) | [https://ndastro-api.onrender.com/docs#/](https://ndastro-api.onrender.com/docs#/) |
| ReDoc | [https://ndastro-api.onrender.com/redoc](https://ndastro-api.onrender.com/redoc) |
| OpenAPI JSON | [https://ndastro-api.onrender.com/openapi.json](https://ndastro-api.onrender.com/openapi.json) |

!!! tip "Try it in the browser"
    Open the [Swagger UI](https://ndastro-api.onrender.com/docs#/) to explore and call every endpoint interactively without writing any code.

!!! note "Cold starts"
    The hosted instance runs on Render's free tier and may take 30–60 seconds to respond after a period of inactivity (cold start). Subsequent requests are fast.

---

## Local Development Setup

Follow these steps to run the API on your own machine.

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)

### 1. Clone the repository

```sh
git clone https://github.com/jaganathan-eswaran/ndastro-api.git
cd ndastro-api
```

### 2. Install dependencies

```sh
poetry install
```

### 3. Configure environment

Copy the example environment file and fill in the required values:

```sh
cp .env.example .env
```

At minimum, set `SECRET_KEY`:

```sh
# Generate a secure key
openssl rand -hex 32
```

See [Environment Variables](../configuration/environment.md) for the full reference.

### 4. Set up the database

```sh
poetry run pre-start
poetry run db-migrate
poetry run init-data
```

### 5. Run the API server

```sh
uvicorn ndastro_api.main:app --reload
```

The API will be available at:

- **API base**: [http://localhost:8000](http://localhost:8000)
- **Interactive docs**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

---

## Running Tests

```sh
pytest --envfile .\ndastro_api\.env.test
```

For verbose output:

```sh
pytest -v
```

For coverage:

```sh
pytest --cov=ndastro_api --cov-report=term-missing
```

---

## Making Your First Request

Once the API is running (hosted or local), try fetching planetary positions:

```sh
curl "https://ndastro-api.onrender.com/api/v1/astro/planets?lat=13.08&lon=80.27&dateandtime=2000-01-01T10:30:00"
```

Or via the interactive docs — click **Authorize** in Swagger UI if using authenticated endpoints.

See the [API Reference](../api/overview.md) for a full list of endpoints.
