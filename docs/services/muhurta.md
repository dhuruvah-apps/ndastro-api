# Muhurta (Electional Astrology)

Muhurta is the Vedic system of selecting auspicious time windows for important activities. The `muhurta_advanced` module identifies inauspicious periods to avoid (Durmuhurta, Varjyam) and auspicious ones to seek (Amrita Kala, Kala).

---

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `MINUTES_PER_MUHURTA` | 48 | Each muhurta is 48 minutes long (1/30th of a day) |
| Total muhurtas per day | 30 | A full day (24h) has 30 muhurtas |

---

## `MuhurtaQuality` Enum

| Value | Meaning |
|-------|---------|
| `EXCELLENT` | Best for all activities |
| `GOOD` | Suitable for most activities |
| `AVERAGE` | Neutral, proceed with care |
| `POOR` | Avoid if possible |
| `INAUSPICIOUS` | Strongly avoid |

---

## Functions

### `get_durmuhurtas`

```python
get_durmuhurtas(sunrise: datetime) -> list[DurmuhurtaWindow]
```

Returns the Durmuhurta windows for the day — inauspicious 48-minute periods that should be avoided for starting new activities.

**Algorithm:** Durmuhurtas occur at muhurta indices `[6, 14, 23, 28]` from sunrise. Each window starts at `sunrise + (index × 48 minutes)` and lasts 48 minutes.

**Returns:** List of `DurmuhurtaWindow`:

| Field | Type | Description |
|-------|------|-------------|
| `start` | `datetime` | Window start time |
| `end` | `datetime` | Window end time |
| `name` | `str` | Name of the Durmuhurta |
| `weekday_name` | `str` | Weekday this applies to |
| `quality` | `MuhurtaQuality` | Always `INAUSPICIOUS` |

---

### `get_varjyam_windows`

```python
get_varjyam_windows(
    tithi: int,
    nakshatra: int,
    tithi_end_time: datetime
) -> list[VarjyamWindow]
```

Returns Varjyam (inauspicious) windows based on the nakshatra–tithi combination. Varjyam periods are derived from 12 classical nakshatra pairs that produce harmful combinations on specific tithis.

**Returns:** List of `VarjyamWindow`:

| Field | Type | Description |
|-------|------|-------------|
| `start` | `datetime` | Window start time |
| `end` | `datetime` | Window end time |
| `nakshatra` | `int` | Triggering nakshatra |
| `tithi` | `int` | Triggering tithi |
| `quality` | `MuhurtaQuality` | Always `INAUSPICIOUS` |

---

### `get_amrita_kala_windows`

```python
get_amrita_kala_windows(
    weekday: int,
    nakshatra: int,
    sunrise: datetime,
    sunset: datetime
) -> tuple[list[AmritaKalaWindow], list[KalaWindow]]
```

Returns both Amrita Kala (nectar period — very auspicious) and Kala (specific planetary period) windows.

**Returns:** `(amrita_windows, kala_windows)` — two separate lists.

**`AmritaKalaWindow`:**

| Field | Type | Description |
|-------|------|-------------|
| `start` | `datetime` | Window start |
| `end` | `datetime` | Window end |
| `quality` | `MuhurtaQuality` | `EXCELLENT` |
| `ruling_planet` | `str` | Planet governing this window |

**`KalaWindow`:**

| Field | Type | Description |
|-------|------|-------------|
| `start` | `datetime` | Window start |
| `end` | `datetime` | Window end |
| `quality` | `MuhurtaQuality` | `GOOD` or `EXCELLENT` |
| `name` | `str` | Kala name |

---

## Typical Muhurta Workflow

For a given day, the sequence of analysis is:

1. Calculate `sunrise` and `sunset` using the sunrise-sunset API endpoint.
2. Get Panchanga data (`tithi`, `nakshatra`, `vara`) for the day.
3. Call `get_durmuhurtas(sunrise)` → avoid these windows.
4. Call `get_varjyam_windows(tithi, nakshatra, tithi_end_time)` → avoid these windows.
5. Call `get_amrita_kala_windows(weekday, nakshatra, sunrise, sunset)` → prefer these windows.
6. Schedule the activity in an Amrita Kala or Kala window that does not overlap with Durmuhurta or Varjyam.

---

## Integration with Abhijit Muhurta

The `panchanga` module's `get_abhijit_muhurta` (see [Nakshatra & Panchanga](nakshatra_panchanga.md)) provides the midday auspicious window. Abhijit combined with Amrita Kala produces the most powerful timing.

!!! note "Wednesday Exception"
    Abhijit Muhurta is traditionally not used on Wednesdays as it is considered inauspicious for that weekday.
