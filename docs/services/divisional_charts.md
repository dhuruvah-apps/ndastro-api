# Divisional Charts (Vargas)

Divisional charts (Vargas) are derived charts created by subdividing each zodiac sign. They reveal specific domains of life with greater precision than the Rasi chart alone.

---

## Overview

Each divisional chart is computed by dividing the 30° of a sign into equal or unequal segments, then assigning each segment to a sign of the zodiac according to classical rules. The result is a new "chart" where each planet has a modified sign placement.

---

## `VargaType` Enum

| Value | Division | Name | Life Domain |
|-------|----------|------|-------------|
| `D1` | 1 | Rasi | Overall life (main chart) |
| `D2` | 2 | Hora | Wealth and resources |
| `D3` | 3 | Drekkana | Siblings and courage |
| `D4` | 4 | Chaturthamsa | Fortune and property |
| `D7` | 7 | Saptamsa | Children and progeny |
| `D9` | 9 | Navamsa | Marriage and dharma |
| `D10` | 10 | Dasamsa | Career and profession |
| `D12` | 12 | Dwadasamsa | Parents |
| `D16` | 16 | Shodasamsa | Vehicles and comforts |
| `D20` | 20 | Vimshamsa | Spiritual life |
| `D24` | 24 | Chaturvimshamsa | Education and learning |
| `D27` | 27 | Saptavimshamsa | Strengths and weaknesses |
| `D30` | 30 | Trimshamsa | Misfortunes and evils |
| `D40` | 40 | Khavedamsa | Maternal heritage |
| `D45` | 45 | Akshavedamsa | Paternal heritage |
| `D60` | 60 | Shastiamsa | Past life karma (most sensitive) |

---

## Functions

### `get_varga_rasi`

```python
get_varga_rasi(longitude: float, division: int) -> int
```

Generic function to compute the varga sign for any integer division.

**Formula:** `floor(longitude / (30 / division)) % 12 + 1`

This is the simple proportional method — use `get_varga_rasi_with_rules` for classical accuracy.

### `get_varga_rasi_with_rules`

```python
get_varga_rasi_with_rules(longitude: float, varga: VargaType) -> int
```

Applies the classical Parasara rules for each varga division. For most vargas, sign assignment depends on:

- Whether the base rasi is odd (Vishama) or even (Sama) — determines the counting direction
- Special rules (e.g. D9 Navamsa cycles through the three nakshatras of each sign)
- For D60: Each degree (0.5°) maps to a specific fixed rasi sequence

**Returns:** Sign number 1–12.

### `compute_varga_chart`

```python
compute_varga_chart(
    longitudes: dict[str, float],
    varga: VargaType
) -> VargaChart
```

Computes an entire divisional chart for all planets.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `longitudes` | `dict[str, float]` | Planet code → sidereal longitude |
| `varga` | `VargaType` | The divisional chart to compute |

**Returns:** `VargaChart` with:

| Field | Type | Description |
|-------|------|-------------|
| `varga_type` | `VargaType` | Which division was computed |
| `planet_signs` | `dict[str, int]` | Planet code → varga sign (1–12) |
| `division` | `int` | Numeric division factor |

---

## Classical Sign Assignment (D9 Navamsa)

The Navamsa is the most important divisional chart. Each sign's 30° is divided into 9 Navamsas of 3°20′ each. Counting starts from:

| Base Rasi Type | Navamsa Starts From |
|---------------|---------------------|
| Fire signs (Aries, Leo, Sagittarius) | Aries (1) |
| Earth signs (Taurus, Virgo, Capricorn) | Capricorn (10) |
| Air signs (Gemini, Libra, Aquarius) | Libra (7) |
| Water signs (Cancer, Scorpio, Pisces) | Cancer (4) |

---

## Classical Sign Assignment (D2 Hora)

| Odd Sign | Even Sign |
|----------|-----------|
| First half (0–15°) → Leo | First half (0–15°) → Cancer |
| Second half (15–30°) → Cancer | Second half (15°–30°) → Leo |

---

## Vargottama

A planet is **Vargottama** when it occupies the same sign in both the D1 (Rasi) and D9 (Navamsa) charts. This greatly strengthens the planet:

- Occurs when a planet is in the first 3°20′ of a sign (Navamsa 1 = Rasi 1 within that triplicity)
- Vargottama planets give their significations more fully and reliably

---

## Usage Example

```python
from ndastro_api.services.divisional_charts import compute_varga_chart, VargaType

# Get D9 Navamsa chart
d9 = compute_varga_chart(
    longitudes={"SU": 45.3, "MO": 120.7, "MA": 210.1, ...},
    varga=VargaType.D9
)

# Check Jupiter's navamsa sign
print(d9.planet_signs["JU"])  # e.g. 5 (Leo)
```
