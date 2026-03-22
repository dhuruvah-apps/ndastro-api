# Nakshatra & Panchanga

This page covers two related services:

- **`nakshatra_traits`** — lookup of nakshatra properties and compatibility
- **`panchanga`** — traditional five-limb Vedic daily almanac (tithi, vara, nakshatra, yoga, karana) plus muhurta windows

---

## Nakshatra Traits

### Overview

The 27 nakshatras (lunar mansions) divide the zodiac into 13°20′ segments. Each nakshatra has 4 padas (quarters) of 3°20′.

### Functions

#### `get_nakshatra_from_longitude`

```python
get_nakshatra_from_longitude(longitude: float) -> int
```

Returns the nakshatra index (1–27) for a given ecliptic longitude.

#### `get_pada_from_longitude`

```python
get_pada_from_longitude(longitude: float) -> int
```

Returns the pada (1–4) within the nakshatra for a given ecliptic longitude.

#### `get_nakshatra_traits`

```python
get_nakshatra_traits(nakshatra_index: int) -> NakshatraTraits
```

Returns the complete traits object for the given nakshatra (index 1–27).

#### `calculate_nakshatra_position`

```python
calculate_nakshatra_position(longitude: float) -> NakshatraPosition
```

Combines the nakshatra index, pada, and degree-within-nakshatra into a single result.

#### `calculate_nakshatra_compatibility`

```python
calculate_nakshatra_compatibility(
    nakshatra1: int,
    nakshatra2: int
) -> NakshatraCompatibility
```

Calculates the compatibility score between two nakshatras based on classical Guna Milan.

Raises `ValueError` if either nakshatra index is out of range (1–27).

---

### `NakshatraTraits` Model

| Field | Type | Description |
|-------|------|-------------|
| `index` | `int` | Nakshatra number 1–27 |
| `name` | `str` | Sanskrit name (e.g. `"Ashwini"`) |
| `symbol` | `str` | Visual symbol |
| `deity` | `str` | Ruling deity |
| `ruling_planet` | `str` | Graha lord |
| `gana` | `NakshatraGana` | Energy type |
| `type` | `NakshatraType` | Movability type |
| `qualities` | `list[str]` | Key character traits |

### Enumerations

#### `NakshatraGana`
| Value | Meaning |
|-------|---------|
| `DEVA` | Divine (benefic nature) |
| `MANUSHYA` | Human (mixed nature) |
| `RAKSHASA` | Demonic (rajasic/challenging nature) |

#### `NakshatraType`
| Value | Meaning |
|-------|---------|
| `FIXED` | Sthira — good for permanent activities |
| `MOVABLE` | Chara — good for travel, change |
| `DUAL` | Dwishwabhava — mixed |

---

### The 27 Nakshatras

| # | Name | Ruler | Gana |
|---|------|-------|------|
| 1 | Ashwini | Ketu | Deva |
| 2 | Bharani | Venus | Manushya |
| 3 | Krittika | Sun | Rakshasa |
| 4 | Rohini | Moon | Manushya |
| 5 | Mrigashira | Mars | Deva |
| 6 | Ardra | Rahu | Manushya |
| 7 | Punarvasu | Jupiter | Deva |
| 8 | Pushya | Saturn | Deva |
| 9 | Ashlesha | Mercury | Rakshasa |
| 10 | Magha | Ketu | Rakshasa |
| 11 | Purva Phalguni | Venus | Manushya |
| 12 | Uttara Phalguni | Sun | Manushya |
| 13 | Hasta | Moon | Deva |
| 14 | Chitra | Mars | Rakshasa |
| 15 | Swati | Rahu | Deva |
| 16 | Vishakha | Jupiter | Rakshasa |
| 17 | Anuradha | Saturn | Deva |
| 18 | Jyeshtha | Mercury | Rakshasa |
| 19 | Mula | Ketu | Rakshasa |
| 20 | Purva Ashadha | Venus | Manushya |
| 21 | Uttara Ashadha | Sun | Manushya |
| 22 | Shravana | Moon | Deva |
| 23 | Dhanishtha | Mars | Rakshasa |
| 24 | Shatabhisha | Rahu | Rakshasa |
| 25 | Purva Bhadrapada | Jupiter | Manushya |
| 26 | Uttara Bhadrapada | Saturn | Manushya |
| 27 | Revati | Mercury | Deva |

---

## Panchanga

The five limbs (*pancha + anga*) of the Vedic almanac for a given day:

| Limb | Meaning |
|------|---------|
| **Tithi** | Lunar day (30 per lunar month) |
| **Vara** | Weekday with planetary ruler |
| **Nakshatra** | Moon's nakshatra |
| **Yoga** | Nitya yoga (see [Yogas](yogas.md)) |
| **Karana** | Half-tithi (11 types) |

### Functions

#### `get_tithi_number`

```python
get_tithi_number(sun_longitude: float, moon_longitude: float) -> int
```

Returns the tithi number (1–30) based on the elongation of the Moon from the Sun.

#### `get_tithi_result`

```python
get_tithi_result(tithi_number: int) -> TithiResult
```

Returns the name, lord, nature, and auspiciousness of the given tithi.

#### `get_karana_result`

```python
get_karana_result(sun_longitude: float, moon_longitude: float) -> KaranaResult
```

Returns the current karana (one of 11 types) for the given planetary positions.

#### `get_vara_number_from_weekday`

```python
get_vara_number_from_weekday(weekday: int) -> int
```

Converts a Python `datetime.weekday()` value (0=Monday) to a Vara number (1=Sunday…7=Saturday). Raises `MissingWeekdayError` if the input is invalid.

#### `get_vara_result`

```python
get_vara_result(vara_number: int) -> VaraResult
```

Returns the vara name, ruling planet, and general auspiciousness.

#### `get_vara_result_from_datetime`

```python
get_vara_result_from_datetime(dt: datetime) -> VaraResult
```

Convenience wrapper — extracts the weekday from a datetime and returns the vara result. Raises `MissingTimezoneError` if `dt` is naive (no timezone info).

#### `get_day_segments`

```python
get_day_segments(sunrise: datetime, sunset: datetime) -> list[DaySegment]
```

Divides the daytime period (sunrise → sunset) into 8 equal segments (each one-eighth of the daytime arc). Returns segment start/end times and the ruling planet.

#### `get_night_segments`

```python
get_night_segments(sunset: datetime, next_sunrise: datetime) -> list[NightSegment]
```

Divides the nighttime period (sunset → next sunrise) into 8 equal segments.

#### `get_abhijit_muhurta`

```python
get_abhijit_muhurta(
    sunrise: datetime,
    sunset: datetime,
    *,
    exclude_wednesday: bool = True
) -> AbhijitMuhurta | None
```

Computes the Abhijit muhurta window — the auspicious midday period. Returns `None` on Wednesdays when `exclude_wednesday=True` (classical rule).

---

### Error Types

| Exception | Raised When |
|-----------|-------------|
| `MissingWeekdayError` | Invalid weekday passed to `get_vara_number_from_weekday` |
| `MissingTimezoneError` | Naive datetime passed to `get_vara_result_from_datetime` |
