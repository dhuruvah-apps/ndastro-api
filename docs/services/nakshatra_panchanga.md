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

---

## Inauspicious Timing Windows

These functions compute the traditional inauspicious (and conditionally inauspicious) time windows for a given Vedic day. All accept timezone-aware `datetime` objects.

All functions return a `TimeWindow` dataclass:

```python
@dataclass
class TimeWindow:
    name: str
    start: datetime
    end: datetime
```

---

### `get_rahu_kalam`

```python
get_rahu_kalam(
    *,
    sunrise: datetime,
    sunset: datetime,
    weekday_index: int | None = None,
    date_value: datetime | None = None,
) -> TimeWindow
```

Returns the **Rahu Kalam** window — an inauspicious 90-minute period ruled by Rahu.

The daytime arc (sunrise→sunset) is divided into 8 equal segments. Rahu Kalam occupies a fixed segment per weekday:

| Day | Segment |
|-----|---------|
| Sunday | 8th |
| Monday | 2nd |
| Tuesday | 7th |
| Wednesday | 5th |
| Thursday | 6th |
| Friday | 4th |
| Saturday | 3rd |

Pass either `weekday_index` (Python `datetime.weekday()`, 0=Monday) or `date_value` (a timezone-aware datetime).

---

### `get_yamagandam`

```python
get_yamagandam(
    *,
    sunrise: datetime,
    sunset: datetime,
    weekday_index: int | None = None,
    date_value: datetime | None = None,
) -> TimeWindow
```

Returns the **Yama Ghantaka** window — the period associated with Yama (death), traditionally avoided for auspicious activities.

Segment per weekday:

| Day | Segment |
|-----|---------|
| Sunday | 5th |
| Monday | 4th |
| Tuesday | 3rd |
| Wednesday | 2nd |
| Thursday | 1st |
| Friday | 7th |
| Saturday | 6th |

---

### `get_gulika`

```python
get_gulika(
    *,
    sunrise: datetime,
    sunset: datetime,
    weekday_index: int | None = None,
    date_value: datetime | None = None,
) -> TimeWindow
```

Returns the **Gulika Kala** (Kuliga / Maandi) window — the period ruled by Saturn's son Gulika.

Segment per weekday:

| Day | Segment |
|-----|---------|
| Sunday | 7th |
| Monday | 6th |
| Tuesday | 5th |
| Wednesday | 4th |
| Thursday | 3rd |
| Friday | 2nd |
| Saturday | 1st |

---

### `get_durmuhurta`

```python
get_durmuhurta(
    *,
    sunrise: datetime,
    sunset: datetime,
    next_sunrise: datetime,
    weekday_index: int | None = None,
    date_value: datetime | None = None,
) -> list[TimeWindow]
```

Returns the **Durmuhurta** window(s) — inauspicious muhurta periods during the day.

- **Sunday, Wednesday, Saturday**: one window.
- **Monday, Thursday, Friday**: two windows.
- **Tuesday**: two windows; the second is measured from sunset using the **night** duration.
- Each window lasts `day_duration × 0.8 / 12` hours (approximately 48–52 minutes).

Offsets (fraction of day duration from sunrise, divided by 12):

| Day | Window 1 offset | Window 2 offset |
|-----|-----------------|-----------------|
| Sunday | 10.4 | — |
| Monday | 5.6 | 8.8 |
| Tuesday | 2.4 | 4.8 (from sunset) |
| Wednesday | 5.6 | — |
| Thursday | 4.0 | 8.8 |
| Friday | 2.4 | 6.4 |
| Saturday | 1.6 | — |

---

### `get_varjya`

```python
get_varjya(
    *,
    ref_dt: datetime,
    current_moon_lon: float,
    moon_lon_fn: Callable[[datetime], float],
) -> list[TimeWindow]
```

Returns the **Varjya** window(s) — an inauspicious period derived from the Moon's current nakshatra.

The function uses binary search (via `_find_start_time` / `_find_end_time`) to find the precise nakshatra entry and exit times, then applies the traditional factor:

```
varjya_start = nakshatra_entry + (factor / 24) × nakshatra_duration
varjya_duration = nakshatra_duration × 1.6 / 24
```

Factors are sourced from the classical *Panchangam Calculations* by Karanam Ramakumar.

- Most nakshatras produce **one** Varjya window.
- **Mula** (nakshatra 19) produces **two** windows (factors 8 and 22.4).

`moon_lon_fn` must be a callable `(datetime) -> float` that returns the Moon's sidereal longitude for an arbitrary time — used for the binary search iterations.

**Example**:

```python
from ndastro_engine.core import get_planet_position
from ndastro_engine.enums import Planets
from ndastro_engine.ayanamsa import get_ayanamsa
from ndastro_engine.utils import normalize_degree
from ndastro_api.services.panchanga import get_varjya

def moon_lon(t):
    ayan = get_ayanamsa(t, "true_lahiri")
    return normalize_degree(get_planet_position(Planets.MOON, lat, lon, t).longitude - ayan)

current = moon_lon(dt)
windows = get_varjya(ref_dt=dt, current_moon_lon=current, moon_lon_fn=moon_lon)
for w in windows:
    print(f"Varjya: {w.start} → {w.end}")
```
