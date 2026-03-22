# Longevity Analysis

The longevity module implements classical Jyotish methods to assess the approximate span of life (Ayu) for a native. Multiple techniques are applied and reconciled to produce a range estimate.

---

## Overview

Longevity determination uses:

1. **Three Pairs Method** (Pindayu, Nisargayu, Amsayu) — three classical formulae averaged
2. **Eighth Lord Method** — strength of the 8th house lord
3. **Maraka Identification** — planets capable of causing end of life
4. **Rudra Trishula** and **Maheswara pairs** — advanced refinement techniques

---

## Core Utility Functions

### `get_rasi_type`

```python
get_rasi_type(rasi: int) -> RasiType
```

Returns the movability type of a sign (1–12).

### `RasiType` Values

| Value | Signs |
|-------|-------|
| `MOVABLE` (Chara) | Aries (1), Cancer (4), Libra (7), Capricorn (10) |
| `FIXED` (Sthira) | Taurus (2), Leo (5), Scorpio (8), Aquarius (11) |
| `DUAL` (Dwiswabhava) | Gemini (3), Virgo (6), Sagittarius (9), Pisces (12) |

### `get_special_8th_house`

```python
get_special_8th_house(from_rasi: int) -> int
```

Returns the special 8th house rasi from a given sign, used in advanced longevity calculations.

### `get_rasi_lord`

```python
get_rasi_lord(rasi: int) -> str
```

Returns the planet code that rules the given rasi (1–12).

### `get_house_from_rasi`

```python
get_house_from_rasi(lagna_rasi: int, target_rasi: int) -> int
```

Computes the house number of `target_rasi` relative to `lagna_rasi`.

### `get_rasi_at_house`

```python
get_rasi_at_house(lagna_rasi: int, house: int) -> int
```

Returns the rasi that occupies a specific house number from the lagna.

### `get_trine_rasis`

```python
get_trine_rasis(from_rasi: int) -> list[int]
```

Returns the three trikona (trine) rasis counting from the given rasi (the 1st, 5th, and 9th from it).

---

## Analysis Dataclasses

### `MarakaIdentification`

Identifies planets that have maraka (life-ending) potential.

| Field | Type | Description |
|-------|------|-------------|
| `primary_marakas` | `list[str]` | Lords of the 2nd and 7th houses |
| `secondary_marakas` | `list[str]` | Planets associated with primary marakas |
| `functional_marakas` | `list[str]` | Saturn, Rahu, Ketu in key positions |
| `strongest_maraka` | `str | None` | Planet with highest maraka potential |
| `reasoning` | `str` | Explanation of the determination |

### `ThreePairsResult`

Contains results of the three classical longevity formulae:

| Field | Type | Description |
|-------|------|-------------|
| `pindayu` | `float` | Longevity from planetary years |
| `nisargayu` | `float` | Natural longevity (fixed planetary periods) |
| `amsayu` | `float` | Longevity from navamsa positions |
| `short_life` | `tuple[float, float]` | Range for short life (0–32 years) |
| `medium_life` | `tuple[float, float]` | Range for medium life (32–64 years) |
| `long_life` | `tuple[float, float]` | Range for long life (64–96 years) |
| `recommended_range` | `tuple[float, float]` | Final estimated range |
| `category` | `str` | `"short"`, `"medium"`, or `"long"` |

### `EighthLordMethodResult`

| Field | Type | Description |
|-------|------|-------------|
| `eighth_lord` | `str` | Planet ruling the 8th house |
| `eighth_lord_house` | `int` | House where 8th lord is placed |
| `eighth_lord_sign` | `int` | Sign where 8th lord is placed |
| `sign_type` | `RasiType` | Movable / Fixed / Dual |
| `estimated_years` | `float` | Estimated longevity from this method |
| `reasoning` | `str` | Explanation |

### `LongevityAnalysis`

Comprehensive result combining all methods:

| Field | Type | Description |
|-------|------|-------------|
| `three_pairs` | `ThreePairsResult` | Results of the three-formula method |
| `eighth_lord_method` | `EighthLordMethodResult` | 8th lord analysis |
| `marakas` | `MarakaIdentification` | Maraka planet identification |
| `final_range` | `tuple[float, float]` | Reconciled longevity estimate in years |
| `category` | `str` | Life span category |
| `notes` | `list[str]` | Classical qualifications and caveats |

---

## Three Pairs Life Length Rules

The classical system divides life into three spans based on the sign types of key planets:

| Lagna Type | Eighth Lord Type | 8th from Moon Type | Category | Years |
|-----------|-----------------|-------------------|----------|-------|
| Movable | Movable | Any | Short | 0–32 |
| Fixed | Fixed | Any | Long | 64–96 |
| Dual | Dual | Any | Medium | 32–64 |
| Mixed | Mixed | Mixed | Medium | 32–64 |

!!! note "Classical Caveat"
    Longevity calculations are treated as directional estimates in modern practice. They identify vulnerable periods rather than fixed death dates. Planets like Saturn, Rahu, and Ketu as marakas can modify the timing significantly.
