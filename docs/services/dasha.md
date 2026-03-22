# Dasha System (Vimsottari)

The Vimsottari Dasha is the primary planetary period system in Jyotish. It assigns 120 years across 9 planets based on the Moon's nakshatra at birth. Each planet rules a Maha Dasha (major period) which is further subdivided into Bhukti (sub-period), Antara (sub-sub), and Pratyantara (sub-sub-sub).

---

## Planet Periods

| Planet | Maha Dasha Duration |
|--------|-------------------|
| Ketu | 7 years |
| Venus | 20 years |
| Sun | 6 years |
| Moon | 10 years |
| Mars | 7 years |
| Rahu | 18 years |
| Jupiter | 16 years |
| Saturn | 19 years |
| Mercury | 17 years |
| **Total** | **120 years** |

---

## `DasaLevel` Enum

| Value | Level |
|-------|-------|
| `MAHA` | Major period (~years) |
| `BHUKTI` | Sub-period (~months) |
| `ANTARA` | Sub-sub-period (~weeks) |
| `PRATYANTARA` | Sub-sub-sub-period (~days) |

---

## Functions

### `get_nakshatra_ruler`

```python
get_nakshatra_ruler(nakshatra_number: int) -> str
```

Returns the planet code that rules the given nakshatra (1–27). The sequence of rulers repeats the 9-planet cycle in the order: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury.

### `calculate_dasa_start_planet_and_fraction`

```python
calculate_dasa_start_planet_and_fraction(
    nakshatra_number: int,
    nakshatra_pada: int
) -> tuple[str, float]
```

Determines the ruling planet of the first Maha Dasha after birth and the fraction of that period already elapsed at birth (based on which pada the Moon occupied within its nakshatra).

### `calculate_current_dasa_period`

```python
calculate_current_dasa_period(
    birth_date: date,
    current_date: date,
    birth_nakshatra: int
) -> DasaPeriod
```

Computes the currently running dasha period at `current_date`.

**Returns:** `DasaPeriod` with fields:

| Field | Type | Description |
|-------|------|-------------|
| `maha_dasha` | `str` | Current Maha Dasha planet code |
| `bhukti` | `str` | Current Bhukti planet code |
| `antara` | `str` | Current Antara planet code |
| `maha_start` | `date` | Maha Dasha start date |
| `maha_end` | `date` | Maha Dasha end date |
| `bhukti_start` | `date` | Bhukti start date |
| `bhukti_end` | `date` | Bhukti end date |

### `get_dasa_sequence_from_planet`

```python
get_dasa_sequence_from_planet(
    planet: str,
    levels: int = 1
) -> list[tuple[str, float]]
```

Returns the ordered sequence of sub-period planets and their duration (as a fraction of the parent period) starting from the given planet.

- `levels=1` returns Bhukti sequence within a Maha Dasha.
- `levels=2` returns Antara sequence.

### `calculate_dasa_change_dates`

```python
calculate_dasa_change_dates(
    birth_date: date,
    birth_nakshatra: int,
    future_years: int = 10
) -> list[dict]
```

Projects all Maha Dasha and Bhukti transitions for the next `future_years` years from today. Useful for predictive timeline generation.

**Returns:** List of dicts with `planet`, `level`, `start_date`, `end_date`.

### `get_dasa_interpretation`

```python
get_dasa_interpretation(planet: str, level: DasaLevel) -> str
```

Returns a narrative interpretation string for a planet's Dasha at the given level (Maha / Bhukti / Antara).

---

## Sequence Example

For a native born with Moon in **Rohini** (nakshatra 4, ruled by Moon):

```
Moon Maha Dasha → Mars Bhukti → Jupiter Antara → ...
```

The fraction elapsed at birth is derived from how deep into Rohini the Moon is (0–13°20′ span).

---

## `DasaPeriod` Model

```python
@dataclass
class DasaPeriod:
    maha_dasha: str       # e.g. "MO"
    bhukti: str           # e.g. "MA"
    antara: str           # e.g. "JU"
    maha_start: date
    maha_end: date
    bhukti_start: date
    bhukti_end: date
    antara_start: date
    antara_end: date
```
