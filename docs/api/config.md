# Engine Configuration API

Base path: `/api/v1/config`

This endpoint exposes the server-wide ndastro-engine calculation defaults. It is read-only — the global configuration is set at startup via environment variables and cannot be mutated via HTTP. For per-request overrides, see the `node_type` and `position_reference` query parameters on the [Astrology endpoints](astro.md#per-request-calculation-overrides).

---

## Get Current Engine Settings

```
GET /api/v1/config
```

Returns the active engine calculation settings. Useful for debugging, client-side adaptation, and verifying which defaults the server is using.

**Authentication**: Required (Bearer token)

**Query parameters**: None

**Response** `200 OK`:

```json
{
  "position_reference": "geocentric",
  "node_type": "true",
  "ayanamsa_delta": 0.0,
  "dasa_year_length": 365.25,
  "apply_nutation": true,
  "apply_aberration": true,
  "apply_grav_deflection": true,
  "sunrise_definition": "geometric"
}
```

**Response fields**:

| Field | Type | Description |
|-------|------|-------------|
| `position_reference` | `string` | `geocentric` or `topocentric` — how planet positions are computed |
| `node_type` | `string` | `true` (osculating, JHora-compatible) or `mean` (IAU polynomial) |
| `ayanamsa_delta` | `float` | Additional degrees added to the computed ayanamsa value |
| `dasa_year_length` | `float` | Year length in days used for Vimsottari dasha period calculations |
| `apply_nutation` | `bool` | Whether nutation corrections are applied via Skyfield |
| `apply_aberration` | `bool` | Whether stellar aberration is applied |
| `apply_grav_deflection` | `bool` | Whether gravitational deflection of light is applied |
| `sunrise_definition` | `string` | `geometric` (centre of Sun at horizon) or `disc_centre` |

---

## Setting Overrides

The global settings shown by this endpoint are configured at startup from `NDASTRO_*` environment variables. They cannot be changed at runtime via HTTP.

Clients that need a specific `node_type` or `position_reference` for individual requests can pass those as query parameters directly on the calculation endpoints, without affecting other users:

```
GET /api/v1/astro/planets?node_type=mean&position_reference=topocentric
GET /api/v1/astro/lunar-nodes?node_type=mean
```

See [Per-Request Calculation Overrides](astro.md#per-request-calculation-overrides) for full details.

---

## Corresponding Engine Settings

The fields returned by this endpoint map directly to the `EngineSettings` dataclass in `ndastro-engine` and the `NDASTRO_*` environment variables described in the [ndastro-engine Configuration guide](https://dhuruvah-in.github.io/ndastro-core/guide/configuration/).
