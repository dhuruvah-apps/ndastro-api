# Health & Metrics API

These endpoints do not require authentication and can be used for health checks, monitoring, and uptime probes.

---

## Health Check

```
GET /health-check
```

Returns the API and database connectivity status.

**Response** `200 OK` (healthy):

```json
{
  "status": "healthy"
}
```

**Response** `200 OK` (degraded):

```json
{
  "status": "unhealthy"
}
```

!!! note
    The endpoint always returns HTTP `200`. Check the `status` field to determine health — this avoids load-balancer false-positive failures.

---

## System Metrics

```
GET /metrics
```

Returns real-time system resource usage for the host running the API.

**Response** `200 OK`:

```json
{
  "cpu_percent": 12.5,
  "memory_percent": 45.3,
  "disk_usage": 60.1
}
```

| Field | Type | Description |
|-------|------|-------------|
| `cpu_percent` | `float` | CPU usage percentage (0–100) |
| `memory_percent` | `float` | RAM usage percentage (0–100) |
| `disk_usage` | `float` | Disk usage percentage (0–100) |

!!! info "Azure Use Case"
    These metrics can be scraped by Azure Monitor or a custom Application Insights integration to track host-level resource pressure without needing Azure VM diagnostics extensions.
