# Astrology API

Base path: `/api/v1/astro`

All astrology endpoints use **sidereal (nirayana)** positions with the Lahiri ayanamsa by default. Access may be gated by user tier.

## Common Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lat` | `float` | `12.971667` | Observer latitude (Bangalore) |
| `lon` | `float` | `77.593611` | Observer longitude |
| `ayanamsa` | `string` | `"lahiri"` | Ayanamsa system |
| `dateandtime` | `string` | Current UTC | ISO 8601 datetime string |

---

## Lunar Nodes

```
GET /api/v1/astro/lunar-nodes
```

Returns the sidereal positions of Rahu (North Node) and Ketu (South Node).

**Query parameters**: `dateandtime`

**Response** `200 OK`:

```json
[
  {
    "name": "rahu",
    "code": "RA",
    "nirayana_longitude": 12.34,
    "rasi_occupied": "Aries",
    "advanced_by": 12.34,
    "nakshatra": "Ashwini",
    "pada": 2
  },
  {
    "name": "kethu",
    "code": "KE",
    "nirayana_longitude": 192.34,
    "rasi_occupied": "Libra",
    "advanced_by": 12.34,
    "nakshatra": "Swati",
    "pada": 2
  }
]
```

---

## All Planet Positions

```
GET /api/v1/astro/planets
```

Returns sidereal positions for all 9 Vedic planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu).

**Query parameters**: `lat`, `lon`, `ayanamsa`, `dateandtime`

**Response** `200 OK`: Array of `Planet` objects.

**Planet object key fields**:

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Planet name (e.g., `"sun"`) |
| `code` | `string` | Short code (e.g., `"SU"`) |
| `nirayana_longitude` | `float` | Sidereal longitude (0–360°) |
| `rasi_occupied` | `string` | Zodiac sign (e.g., `"Aries"`) |
| `advanced_by` | `float` | Degrees advanced within the rasi |
| `nakshatra` | `string` | Nakshatra code |
| `pada` | `int` | Pada (1–4) |
| `is_retrograde` | `bool` | Whether planet is retrograde |
| `posited_at` | `string` | House number (1–12) |

---

## Ascendant

```
GET /api/v1/astro/ascendant
```

Returns the sidereal ascendant (Lagna) position.

**Query parameters**: `lat`, `lon`, `dateandtime`, `ayanamsa`

**Response** `200 OK`: Single `Planet` object representing the ascendant.

---

## Sunrise & Sunset

```
GET /api/v1/astro/sunrise-sunset
```

Returns the sunrise and sunset times for the given location and date.

**Query parameters**: `lat`, `lon`, `dateandtime`

**Response** `200 OK`:

```json
{
  "sunrise": "2024-01-15T06:30:00+05:30",
  "sunset": "2024-01-15T18:00:00+05:30"
}
```

---

## Kattam Chart (12 Houses)

```
GET /api/v1/astro/kattams
```

Returns the complete 12-house kattam chart with planet placements.

**Query parameters**: `lat`, `lon`, `ayanamsa`, `dateandtime`

**Response** `200 OK`: Array of 12 `KattamResponse` objects (sorted by house order starting from the ascendant rasi).

**KattamResponse fields**:

| Field | Type | Description |
|-------|------|-------------|
| `order` | `int` | House order (1–12, starting from ascendant) |
| `is_ascendant` | `bool` | Whether this is the ascendant house |
| `asc_longitude` | `float` | Ascendant longitude for the ascendant house |
| `owner` | `int` | Planet code that owns this rasi |
| `rasi` | `int` | Rasi number (1–12) |
| `house` | `int` | House number (1–12) |
| `planets` | `array` | List of planets placed in this house |

**Example**:

```json
[
  {
    "order": 1,
    "is_ascendant": true,
    "asc_longitude": 45.67,
    "owner": 3,
    "rasi": 2,
    "house": 1,
    "planets": [
      {
        "name": "sun",
        "code": "SU",
        "nirayana_longitude": 52.34,
        "advanced_by": 7.34,
        "nakshatra": "Rohini",
        "pada": 1
      }
    ]
  }
]
```

---

## SVG Chart Image

```
GET /api/v1/astro/chart
```

Generates and returns a South Indian astrology chart as an SVG image.

**Query parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lat` | `float` | `12.971667` | Latitude |
| `lon` | `float` | `77.593611` | Longitude |
| `ayanamsa` | `string` | `"lahiri"` | Ayanamsa |
| `dateandtime` | `string` | Current UTC | Birth datetime |
| `chart_type` | `string` | `"south-indian"` | Chart style (`south-indian`) |
| `name` | `string` | `null` | Person's name (shown in center) |
| `place` | `string` | `null` | Birth place (shown in center) |
| `lang` | `string` | `"en"` | Language code for labels |
| `tz` | `string` | `null` | Timezone string |

**Response** `200 OK`:

- Content-Type: `image/svg+xml`
- Body: SVG markup of the 4×4 South Indian chart grid

!!! tip
    The SVG can be embedded in HTML directly or saved as a `.svg` file.
