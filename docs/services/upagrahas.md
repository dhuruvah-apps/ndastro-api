# Upagrahas (Shadow Planets)

Upagrahas are derived (calculated) points in the horoscope — they have no physical body but exert powerful influences. The system includes 11 upagrahas, all derived mathematically from the Sun's position.

---

## Overview

Upagrahas fall into two groups:

- **Sun-Based (Day/Night Upagrahas)**: 5 upagrahas derived from the Sun's daily arc
- **Ascending/Descending Nodes Group**: 6 additional shadow points

All 11 are computed from `sun_longitude` using fixed angular offsets applied to the Sun's arc in the chart.

---

## The 11 Upagrahas

| Code | Name | Nature | Significations |
|------|------|--------|----------------|
| `DHUMA` | Dhuma | Malefic | Smoke, pollution, hidden enemies |
| `VYATIPAATA` | Vyatipaata | Very malefic | Sudden reversals, accidents |
| `PARIVESHA` | Parivesha | Malefic | Obstacles, delays, blockages |
| `INDRACHAAPA` | Indrachaapa | Malefic | Broken promises, betrayal |
| `UPAKETU` | Upaketu | Malefic | Separation, detachment |
| `KAALA` | Kaala (Kala Vela) | Malefic | Time restrictions, karma from past |
| `MRITYU` | Mrityu | Very malefic | Death-like suffering, severe difficulties |
| `ARTHA_PRAHARAKA` | Artha Praharaka | Malefic | Financial losses, theft |
| `YAMAGHANTAKA` | Yamaghantaka | Malefic | Danger, Yama (death) afflictions |
| `GULIKA` | Gulika (Mandi) | Malefic | Poison, chronic illness, misfortune |
| `MAANDI` | Mandi | Very malefic | Chronic malaise, obstructions (alternate name for Gulika in some traditions) |

---

## Functions

### `calculate_sun_based_upagrahas`

```python
calculate_sun_based_upagrahas(sun_longitude: float) -> dict[str, float]
```

Computes all upagraha longitudes from the Sun's position using fixed angular offsets.

**Returns:** `dict[UpagrahaType, float]` — upagraha type → ecliptic longitude (0–360°).

### `get_sun_based_upagraha_details`

```python
get_sun_based_upagraha_details(
    upagraha_type: str,
    longitude: float
) -> Upagraha
```

Returns the full `Upagraha` object for a given type and computed longitude.

### `get_all_sun_based_upagrahas`

```python
get_all_sun_based_upagrahas(sun_longitude: float) -> list[Upagraha]
```

Computes all 11 upagrahas and returns them as a list of `Upagraha` objects.

### `get_upagraha_interpretation`

```python
get_upagraha_interpretation(upagraha: Upagraha) -> str
```

Returns a human-readable interpretation based on the upagraha's type, sign placement, and house position.

---

## `Upagraha` Model

| Field | Type | Description |
|-------|------|-------------|
| `type` | `str` | `UpagrahaType` code |
| `name` | `str` | Sanskrit name |
| `longitude` | `float` | Ecliptic longitude (0–360°) |
| `rasi_number` | `int` | Sign (1–12) |
| `rasi_name` | `str` | Sign name |
| `degree_in_rasi` | `float` | Degree within the sign (0–30) |
| `house` | `int` | House (1–12) relative to natal lagna |
| `nakshatra` | `str` | Nakshatra name |
| `nakshatra_pada` | `int` | Pada (1–4) |
| `nature` | `str` | `"malefic"`, `"very malefic"`, etc. |

---

## Computation Derivation

Upagrahas are computed from the Sun's position using traditional formulas. The key derived points:

| Upagraha | Derivation Formula |
|----------|--------------------|
| Dhuma | `Sun + 133°20′` |
| Vyatipaata | `360° − Dhuma` |
| Parivesha | `Vyatipaata + 180°` |
| Indrachaapa | `360° − Parivesha` |
| Upaketu | `Indrachaapa + 16°40′` |
| Gulika/Mandi | Derived from Saturn's day/night arc segments |

---

## House Placement Effects

Upagrahas are particularly significant in:

| House | Effect of Upagraha Placement |
|-------|------------------------------|
| 1st | Health issues, inauspicious omens at birth |
| 2nd | Financial losses, speech difficulties |
| 4th | Domestic troubles, property disputes |
| 7th | Relationship strife, partner difficulties |
| 8th | Chronic illness, accidents, longevity concerns |
| 10th | Career obstacles, public reputation damage |
| 12th | Spiritual affliction, hidden suffering |

Upagrahas in the 3rd, 6th, or 11th houses generally cause fewer problems as malefic energy can be channeled outward.

---

## Gulika (Mandi) Special Importance

Gulika (also called Mandi) is the most significant upagraha:

- Considered a secondary Rahu in effect
- Its house position shows chronic areas of misfortune
- Its sign lord's placement modifies the expression
- Conjunctions of Gulika with planets severely afflict those planets' significations

!!! tip "Practical Note"
    In natal chart analysis, always check if any planet is conjunct Gulika within 10°. Such planets require careful Dasha timing analysis.
