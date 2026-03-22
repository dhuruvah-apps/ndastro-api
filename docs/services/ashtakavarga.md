# Ashtakavarga

Ashtakavarga is a Vedic technique that assigns benefic points (0 or 1) to each house from each planet's position. The aggregate scores reveal house strength and guide transit predictions.

---

## Overview

- **Bhinnashtakavarga (BAV)**: Individual 8×12 contribution table for each of the 7 planets + Ascendant (8 contributors).
- **Sarvashtakavarga (SAV)**: Sum of all BAV tables — total benefic points per house (0–56 per house).
- Maximum possible SAV points per house: **56** (8 contributors × 7 planets).

---

## Core Functions

### `calculate_sarva_ashtakavarga`

```python
calculate_sarva_ashtakavarga(
    context: AshtakavargaContext
) -> SarvaAshtakavarga
```

Computes the full Sarvashtakavarga from the chart context.

**Returns:** `SarvaAshtakavarga` — dict-like object with SAV points for houses 1–12 and the individual BAV tables.

### `get_house_strength_classification`

```python
get_house_strength_classification(points: int) -> AshtakavargaStrength
```

Classifies the SAV score of a single house.

| SAV Points | Classification |
|-----------|----------------|
| 40 or more | `VERY_STRONG` |
| 30–39 | `STRONG` |
| 25–29 | `MODERATE` |
| 20–24 | `WEAK` |
| Below 20 | `VERY_WEAK` |

### `get_ashtakavarga_interpretation`

```python
get_ashtakavarga_interpretation(
    house: int,
    points: int,
    strength: AshtakavargaStrength
) -> str
```

Returns a human-readable interpretation string for a house's SAV score and strength classification. The text is house-specific (e.g. house 2 vs house 10 get different narratives).

---

## `AshtakavargaStrength` Enum

| Value | SAV Range |
|-------|-----------|
| `VERY_STRONG` | ≥ 40 |
| `STRONG` | 30–39 |
| `MODERATE` | 25–29 |
| `WEAK` | 20–24 |
| `VERY_WEAK` | < 20 |

---

## Transit Predictions (Ashtakavarga Transits)

The `ashtakavarga_transits` module extends the core with transit-specific scoring.

### `classify_sav_strength`

```python
classify_sav_strength(sav_points: int) -> str
```

Maps SAV transit points (0–56) to a verbal strength label.

| Range | Label |
|-------|-------|
| ≥ 40 | `"very strong"` |
| ≥ 30 | `"strong"` |
| ≥ 20 | `"moderate"` |
| ≥ 10 | `"weak"` |
| < 10 | `"very weak"` |

### `determine_transit_nature`

```python
determine_transit_nature(planet: str, house: int) -> str
```

Returns `"beneficial"`, `"neutral"`, or `"challenging"` based on classical rules for which houses are favourable for each transiting planet.

**Classical transit favourability (selected):**

| Planet | Beneficial Houses |
|--------|-----------------|
| Sun | 3, 6, 10, 11 |
| Moon | 1, 3, 6, 7, 10, 11 |
| Mars | 3, 6, 11 |
| Mercury | 2, 4, 6, 8, 10, 11 |
| Jupiter | 2, 5, 7, 9, 11 |
| Venus | 1, 2, 3, 4, 5, 8, 9, 11, 12 |
| Saturn | 3, 6, 11 |

### `calculate_prediction_strength`

```python
calculate_prediction_strength(
    planet: str,
    house: int,
    sav_points: int,
    is_retrograde: bool = False
) -> TransitPredictionStrength
```

Combines SAV score, classical transit nature, and retrograde modifier to produce a composite `TransitPredictionStrength` result.

---

## `AshtakavargaContext`

| Field | Type | Description |
|-------|------|-------------|
| `planets` | `list[Planet]` | Full sidereal planet list |
| `ascendant` | `Planet` | Ascendant (Lagna) |
| `ayanamsa` | `int` | Ayanamsa code used |

---

## `SarvaAshtakavarga` Model

| Field | Type | Description |
|-------|------|-------------|
| `sav` | `dict[int, int]` | House → SAV points mapping (houses 1–12) |
| `bav` | `dict[str, dict[int, int]]` | Planet code → house → BAV points |
| `total` | `int` | Sum of all SAV points (should equal 337 for a complete chart) |
