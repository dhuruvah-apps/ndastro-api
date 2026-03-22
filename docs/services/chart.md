# Chart Generation

The `chart_utils` service generates South Indian-style horoscope charts as SVG strings. Charts are rasi-based (sign-fixed squares) and include all planetary positions and birth metadata.

---

## Functions

### `generate_south_indian_chart_svg`

```python
generate_south_indian_chart_svg(
    kattams_data: list[KattamDisplayData],
    birth_details: BirthDetails
) -> str
```

Produces a complete South Indian chart as an SVG string ready to embed in HTML or save as a `.svg` file.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `kattams_data` | `list[KattamDisplayData]` | Planetary occupants for each of the 12 houses |
| `birth_details` | `BirthDetails` | Name, date, time and place labels for the centre box |

**Returns:** `str` — a self-contained SVG document.

---

## Data Models

### `BirthDetails`

Metadata displayed in the centre info box of the chart.

| Field | Type | Description |
|-------|------|-------------|
| `name_abbr` | `str` | Short name or initials of the native |
| `date` | `str` | Birth date label (e.g. `"01-Jan-2000"`) |
| `time` | `str` | Birth time label (e.g. `"10:30 AM"`) |
| `place` | `str` | Birth place label (e.g. `"Chennai, India"`) |

### `KattamDisplayData`

Describes what to render in a single house cell (kattam).

| Field | Type | Description |
|-------|------|-------------|
| `house_number` | `int` | House number 1–12 |
| `rasi_name` | `str` | Zodiac sign occupying this house |
| `planets` | `list[str]` | Planet codes/labels to display (e.g. `["SU", "MO(R)"]`) |

---

## South Indian Layout

The chart uses a fixed 4×4 grid. The centre 2×2 cells form the info box. The 12 house cells are arranged clockwise from the top-left corner:

```
┌──────┬──────┬──────┬──────┐
│  12  │   1  │   2  │   3  │
├──────┼──────┼──────┼──────┤
│  11  │ INFO │ INFO │   4  │
├──────┼ BOX  ┼ BOX  ┼──────┤
│  10  │ INFO │ INFO │   5  │
├──────┼──────┼──────┼──────┤
│   9  │   8  │   7  │   6  │
└──────┴──────┴──────┴──────┘
```

- **Sign-fixed**: Each cell represents a fixed zodiac sign that never moves.
- **Rasi 1 (Aries)** always occupies the top-left corner cell (cell position 1 in the layout; house number changes depending on the ascendant).
- The ascendant (Lagna) cell is highlighted or labeled to indicate the 1st house.

---

## Internal Helpers

| Function | Description |
|----------|-------------|
| `process_rasi_data` | Maps planet longitudes to their rasi (sign) numbers |
| `calculate_planet_positions` | Converts raw `Planet` list to `KattamDisplayData` format |
| `draw_chart_borders` | Renders the outer grid lines in SVG |
| `render_center_text` | Writes the `BirthDetails` fields into the centre box |
| `render_house_and_planets` | Writes the rasi label and planet codes into each house cell |

---

## API Endpoint

The `/api/v1/astro/chart` endpoint calls `generate_south_indian_chart_svg` directly and returns the SVG with `Content-Type: image/svg+xml`.

```http
GET /api/v1/astro/chart?lat=13.08&lon=80.27&dateandtime=2000-01-01T10:30:00
```

Embed directly in HTML:

```html
<img src="/api/v1/astro/chart?lat=13.08&lon=80.27&dateandtime=2000-01-01T10:30:00"
     alt="Birth Chart" />
```

Or as an inline SVG by fetching the response body:

```html
<div id="chart-container"></div>
<script>
  fetch('/api/v1/astro/chart?lat=13.08&lon=80.27&dateandtime=2000-01-01T10:30:00')
    .then(r => r.text())
    .then(svg => document.getElementById('chart-container').innerHTML = svg);
</script>
```
