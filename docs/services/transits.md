# Transits

The transit system evaluates the effects of current planetary positions on the natal chart. Two modules work together: `transits` (position mapping) and `transit_effects` (interpretation).

---

## Overview

Transit analysis compares **where planets are now** against **where they were at birth** to derive effects, timing themes, and intensity levels.

---

## Position Mapping (`transits` module)

### `get_rasi_index`

```python
get_rasi_index(longitude: float) -> int
```

Converts an ecliptic longitude (0–360°) to a rasi (sign) index (0–11, where 0 = Aries).

### `get_house_index`

```python
get_house_index(longitude: float, lagna_longitude: float) -> int
```

Computes the house number (1–12) a planet occupies relative to the ascending degree.

### `build_transit_positions`

```python
build_transit_positions(
    current_planets: list[Planet],
    natal_lagna_longitude: float
) -> dict[str, TransitPosition]
```

Maps each transiting planet to its current house and sign relative to the natal ascendant.

### `build_house_transits`

```python
build_house_transits(
    current_planets: list[Planet],
    natal_lagna_longitude: float
) -> dict[int, list[str]]
```

Returns a mapping of house number → list of transiting planet codes currently in that house.

### `calculate_transit_aspects`

```python
calculate_transit_aspects(
    current_planets: list[Planet]
) -> list[TransitAspect]
```

Calculates aspects currently formed between transiting planets.

### `calculate_aspects_to_natal_planets`

```python
calculate_aspects_to_natal_planets(
    current_planets: list[Planet],
    natal_planets: list[Planet]
) -> list[NatalTransitAspect]
```

Calculates aspects formed between current transiting positions and natal planet positions. Includes special Mars/Jupiter/Saturn aspects.

### `classify_transit_house`

```python
classify_transit_house(house: int) -> TransitHouseClass
```

Classifies the transit house by its functional category.

### `TransitHouseClass` Values

| Value | Houses | Meaning |
|-------|--------|---------|
| `KENDRA` | 1, 4, 7, 10 | Angular — strong and immediate effects |
| `TRIKONA` | 1, 5, 9 | Trinal — fortune and dharma |
| `DUSTHANA` | 6, 8, 12 | Difficult — challenges, obstacles, loss |
| `UPACHAYA` | 3, 6, 10, 11 | Growing — beneficial over time |
| `MARAKA` | 2, 7 | Marker of endings and transformation |
| `NORMAL` | 2, 3, 11 | General areas of life |

### `get_house_transit_interpretation`

```python
get_house_transit_interpretation(
    planet: str,
    house: int
) -> str
```

Returns the classical textual interpretation for a planet transiting a given house.

---

## Transit Effects (`transit_effects` module)

### `interpret_transit`

```python
interpret_transit(
    planet: str,
    house: int,
    *,
    is_retrograde: bool = False
) -> TransitInterpretation
```

Returns a structured interpretation for a single planet's transit through a given house.

**Returns:** `TransitInterpretation` with:

| Field | Type | Description |
|-------|------|-------------|
| `planet` | `str` | Planet code |
| `house` | `int` | Transit house (1–12) |
| `impact` | `TransitImpact` | Impact level |
| `theme` | `str` | Life area theme |
| `description` | `str` | Narrative description |
| `is_retrograde` | `bool` | Retrograde modifier applied |

### `analyze_transit_effects`

```python
analyze_transit_effects(
    transiting_planets: dict[str, int],
    *,
    retrograde_planets: set[str]
) -> list[TransitEffect]
```

Bulk analysis — evaluates the transit effects of all planets simultaneously.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `transiting_planets` | `dict[str, int]` | Planet code → current house number |
| `retrograde_planets` | `set[str]` | Set of planet codes currently retrograde |

---

## `TransitImpact` Enum

| Value | Meaning |
|-------|---------|
| `VERY_FAVORABLE` | Major positive outcomes |
| `FAVORABLE` | Positive, supportive |
| `NEUTRAL` | Neither positive nor negative |
| `CHALLENGING` | Obstacles and friction |
| `VERY_CHALLENGING` | Major disruption or difficulty |

---

## House Transit Themes

Each house area of life that transiting planets activate:

| House | Theme |
|-------|-------|
| 1 | Self, health, new beginnings |
| 2 | Finances, speech, family |
| 3 | Courage, siblings, communication |
| 4 | Home, mother, emotions |
| 5 | Children, creativity, education |
| 6 | Health, service, enemies |
| 7 | Partnerships, marriage, contracts |
| 8 | Transformation, longevity, hidden matters |
| 9 | Dharma, spirituality, father, travel |
| 10 | Career, authority, public reputation |
| 11 | Gains, networks, aspirations |
| 12 | Losses, liberation, foreign lands |

---

## Sample Usage Flow

```python
# 1. Get current planetary positions
current = get_sidereal_planet_positions(lat, lon, now, ayanamsa)

# 2. Map to houses relative to natal lagna
houses = build_transit_positions(current, natal_lagna_longitude=95.3)

# 3. Classify and interpret each
effects = analyze_transit_effects(
    transiting_planets={p.code: p.house for p in current},
    retrograde_planets={p.code for p in current if p.retrograde}
)
```
