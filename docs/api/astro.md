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

**Query parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dateandtime` | `string` | Current UTC | ISO 8601 datetime string |
| `node_type` | `string` | *(server default)* | `true` — osculating (JHora-compatible); `mean` — IAU polynomial. Overrides the server setting for this request only. |

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

**Query parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lat` | `float` | `12.971667` | Observer latitude |
| `lon` | `float` | `77.593611` | Observer longitude |
| `ayanamsa` | `string` | `"lahiri"` | Ayanamsa system |
| `dateandtime` | `string` | Current UTC | ISO 8601 datetime string |
| `node_type` | `string` | *(server default)* | `true` or `mean` — overrides server node type for this request only. |
| `position_reference` | `string` | *(server default)* | `geocentric` or `topocentric` — overrides server position reference for this request only. |

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
| `posited_at` | `string` | House number (01–12) |

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

---

## Panchanga

```
GET /api/v1/astro/panchanga
```

Returns the complete five-limb Vedic panchanga for the given location and datetime, including precise start/end times for each element and all inauspicious timing windows.

**Query parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lat` | `float` | `12.971667` | Observer latitude |
| `lon` | `float` | `77.593611` | Observer longitude |
| `ayanamsa` | `string` | `"lahiri"` | Ayanamsa system |
| `dateandtime` | `string` | Current UTC | ISO 8601 datetime string |
| `activity` | `string` | `null` | Optional activity to check auspiciousness for (e.g. `"marriage"`, `"travel"`) |

**Response** `200 OK`:

```json
{
  "tithi_name": "Navami",
  "tithi_number": 9,
  "tithi_start": "2026-05-23T23:01:00Z",
  "tithi_end": "2026-05-24T22:31:00Z",
  "karana_name": "Balava",
  "karana_number": 2,
  "karana_start": "2026-05-24T10:54:00Z",
  "karana_end": "2026-05-24T22:31:00Z",
  "vara_name": "Bhanu",
  "vara_number": 1,
  "vara_start": "2026-05-24T00:22:00Z",
  "vara_end": "2026-05-25T00:22:00Z",
  "yoga_name": "Harshana",
  "yoga_number": 14,
  "yoga_start": "2026-05-23T22:11:00Z",
  "yoga_end": "2026-05-24T21:52:00Z",
  "muhurta_rating": 0.72,
  "auspicious_for": ["general", "travel"],
  "inauspicious_for": [],
  "interpretations": {
    "tithi": "Navami is good for bold actions...",
    "vara": "Sunday is ruled by the Sun..."
  },
  "nakshatra_compatibility": {
    "friendly": ["Ashwini", "Bharani"],
    "neutral": ["Krittika"]
  },
  "activity_support": null,
  "sunrise": "2026-05-24T00:22:00Z",
  "sunset": "2026-05-24T13:07:00Z",
  "moonrise": "2026-05-24T07:36:00Z",
  "moonset": "2026-05-24T20:02:00Z",
  "rahu_kalam": {
    "start": "2026-05-24T11:32:00Z",
    "end": "2026-05-24T13:07:00Z"
  },
  "gulika_kala": {
    "start": "2026-05-24T09:57:00Z",
    "end": "2026-05-24T11:32:00Z"
  },
  "yama_ghantaka": {
    "start": "2026-05-24T06:47:00Z",
    "end": "2026-05-24T08:22:00Z"
  },
  "durmuhurta": [
    {
      "start": "2026-05-24T11:25:00Z",
      "end": "2026-05-24T12:16:00Z"
    }
  ],
  "varjya": [
    {
      "start": "2026-05-24T04:51:00Z",
      "end": "2026-05-24T06:30:00Z"
    }
  ]
}
```

**`PanchangaResponse` fields**:

| Field | Type | Description |
|-------|------|-------------|
| `tithi_name` | `string` | Tithi name (e.g. `"Navami"`) |
| `tithi_number` | `int` | Tithi number (1–30) |
| `tithi_start` | `datetime\|null` | UTC datetime when the tithi begins |
| `tithi_end` | `datetime\|null` | UTC datetime when the tithi ends |
| `karana_name` | `string` | Karana name |
| `karana_number` | `int` | Karana number |
| `karana_start` | `datetime\|null` | UTC datetime when the karana begins |
| `karana_end` | `datetime\|null` | UTC datetime when the karana ends |
| `vara_name` | `string` | Vedic weekday name |
| `vara_number` | `int` | Vara number (1=Sunday … 7=Saturday) |
| `vara_start` | `datetime\|null` | Sunrise of current Vedic day |
| `vara_end` | `datetime\|null` | Sunrise of next Vedic day |
| `yoga_name` | `string` | Nitya yoga name |
| `yoga_number` | `int` | Yoga number (1–27) |
| `yoga_start` | `datetime\|null` | UTC datetime when the yoga begins |
| `yoga_end` | `datetime\|null` | UTC datetime when the yoga ends |
| `muhurta_rating` | `float\|null` | Overall muhurta quality score (0–1) |
| `auspicious_for` | `string[]` | Activity categories favoured today |
| `inauspicious_for` | `string[]` | Activity categories to avoid today |
| `interpretations` | `object` | Textual interpretation per element |
| `nakshatra_compatibility` | `object` | Nakshatra groups by compatibility |
| `activity_support` | `object\|null` | Tithi/vara/yoga support for the requested activity |
| `sunrise` | `datetime\|null` | Sunrise time (UTC) |
| `sunset` | `datetime\|null` | Sunset time (UTC) |
| `moonrise` | `datetime\|null` | Moonrise time (UTC) |
| `moonset` | `datetime\|null` | Moonset time (UTC) |
| `rahu_kalam` | `TimeRange\|null` | Rahu Kalam window |
| `gulika_kala` | `TimeRange\|null` | Gulika Kala window |
| `yama_ghantaka` | `TimeRange\|null` | Yama Ghantaka window |
| `durmuhurta` | `TimeRange[]` | Durmuhurta window(s) — 1 or 2 per day |
| `varjya` | `TimeRange[]` | Varjya window(s) for the current nakshatra |

**`TimeRange` object**:

| Field | Type | Description |
|-------|------|-------------|
| `start` | `datetime` | Window start (UTC) |
| `end` | `datetime` | Window end (UTC) |

**`ActivitySupportResponse` object** (present when `activity` parameter is supplied):

| Field | Type | Description |
|-------|------|-------------|
| `activity` | `string` | The activity queried |
| `tithi_support` | `bool` | Whether the tithi supports the activity |
| `karana_support` | `bool` | Whether the karana supports the activity |
| `vara_support` | `bool` | Whether the vara supports the activity |
| `yoga_support` | `bool` | Whether the yoga supports the activity |
| `inauspicious_flags` | `string[]` | Active inauspicious periods that overlap |

!!! note
    All times are returned in UTC. Inauspicious periods (`rahu_kalam`, `gulika_kala`, `yama_ghantaka`, `durmuhurta`, `varjya`) are computed only when both sunrise and sunset are available for the location. Mula nakshatra produces two `varjya` windows.

---

## Per-Request Calculation Overrides

The `node_type` and `position_reference` query parameters on `/lunar-nodes` and `/planets` let a client temporarily override the server's default engine settings **for that single request only**. No other concurrent request is affected.

| Parameter | Endpoints | Values | Effect |
|-----------|-----------|--------|--------|
| `node_type` | `lunar-nodes`, `planets` | `true`, `mean` | `true` — osculating nodes (JHora-compatible); `mean` — IAU polynomial |
| `position_reference` | `planets` | `geocentric`, `topocentric` | How planet positions are computed |

When omitted, the server's configured default is used (check `GET /api/v1/config` to see the active defaults).

**Example — request mean nodes for a single call:**

```
GET /api/v1/astro/lunar-nodes?dateandtime=2024-01-15T06:00:00Z&node_type=mean
```

**Example — request topocentric positions with mean nodes:**

```
GET /api/v1/astro/planets?lat=13.08&lon=80.27&dateandtime=2024-01-15T06:00:00Z&node_type=mean&position_reference=topocentric
```
