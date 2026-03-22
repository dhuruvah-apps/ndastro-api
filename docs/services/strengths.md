# Planetary Strengths

The strengths module implements four classical Jyotish strength systems. Each quantifies a planet's power from a different angle.

---

## 1. Shadbala (Six-Fold Strength)

Shadbala measures six independent sources of planetary power, each contributing up to 30 points. Combined, they give a total score (Rupa/Virupas) and a percentage.

### `calculate_shadbala`

```python
calculate_shadbala(context: ShadbalaPlanetContext) -> dict
```

Computes all six Balas and returns their scores.

**Return keys:**

| Key | Description | Range |
|-----|-------------|-------|
| `sthana_bala` | Positional strength | 0–30 |
| `dig_bala` | Directional strength | 0–30 |
| `kala_bala` | Temporal strength | 0–30 |
| `paksha_bala` | Lunar phase strength | 0–30 |
| `chesta_bala` | Motional strength | 0–30 |
| `drishti_bala` | Aspectual strength | 0–30 |
| `total_shadbala` | Sum of all six | 0–180 |
| `shadbala_percentage` | As percentage of maximum | 0–100 |

### Individual Bala Functions

#### `calculate_sthana_bala`
```python
calculate_sthana_bala(
    planet_code: str,
    rasi_number: int,
    *,
    retrograde: bool
) -> float
```
Positional strength based on sign placement (exaltation, own sign, moolatrikona, friend, enemy, debilitation) and retrograde status.

#### `calculate_dig_bala`
```python
calculate_dig_bala(planet_code: str, house_number: int) -> float
```
Directional strength — each planet is strongest in a specific kendra house:

| Planet | Strongest House |
|--------|----------------|
| Sun, Mars | 10th (south) |
| Moon, Venus | 4th (north) |
| Saturn | 7th (west) |
| Jupiter, Mercury | 1st (east) |

#### `calculate_kala_bala`
```python
calculate_kala_bala(planet_code: str, *, night: bool) -> float
```
Temporal strength — some planets are stronger by day (`night=False`), others by night.

| Stronger by Day | Stronger by Night |
|----------------|------------------|
| Sun, Jupiter, Venus | Moon, Mars, Saturn |
| Mercury (neutral) | — |

#### `calculate_paksha_bala`
```python
calculate_paksha_bala(planet_code: str, moon_phase: float) -> float
```
Lunar phase strength (Sukla/Krishna Paksha). The Moon and Jupiter are stronger in the bright half; Mars and Saturn in the dark half.

#### `calculate_chesta_bala`
```python
calculate_chesta_bala(
    planet_code: str,
    *,
    retrograde: bool,
    avg_speed: float
) -> float
```
Motional strength — retrograde planets and planets moving faster than average receive higher scores.

#### `calculate_drishti_bala`
```python
calculate_drishti_bala(
    other_planets: list[tuple[str, bool]]
) -> float
```
Aspectual strength from planets aspecting this planet. Each tuple is `(planet_code, is_benefic)`.

---

## 2. Vimshopaka Bala (20-Point Strength)

Measures dignity across multiple divisional charts (vargas). The maximum score is 20 points.

### `compute_vimshopaka_bala`

```python
compute_vimshopaka_bala(
    planet_longitudes: dict[str, float],
    *,
    scheme: str = "shodasavarga"
) -> VimshopakaBalaReport
```

### Schemes

| Scheme | Vargas Used | Notes |
|--------|------------|-------|
| `shadvarga` | D1, D2, D3, D9, D12, D30 | 6 charts |
| `saptavarga` | D1–D9 + D12, D30 | 7 charts |
| `dasavarga` | 10 charts | Classical set |
| `shodasavarga` | All 16 vargas D1–D60 | Most comprehensive (default) |

### Dignity Scores

| Dignity | Score |
|---------|-------|
| `EXALTATION` | 20 |
| `MOOLATRIKONA` | 18 |
| `OWN_SIGN` | 15 |
| `GREAT_FRIEND` | 12 |
| `FRIEND` | 10 |
| `NEUTRAL` | 7.5 |
| `ENEMY` | 5 |
| `GREAT_ENEMY` | 2.5 |
| `DEBILITATION` | 2 |

### Strength Labels

| Score Range | Label |
|-------------|-------|
| ≥ 18 | PARIJATA |
| ≥ 16 | UTTAMA |
| ≥ 13 | GOPURA |
| ≥ 10 | SIMHASANA |
| ≥ 6 | PARAVATA |
| ≥ 4 | DEVALOKA |
| ≥ 2 | BHOOLOKA |
| < 2 | NARAKA |

---

## 3. Bhava Strength (House Strength)

Scores each bhava (house) by combining occupant planets, lord dignity, aspects, and optionally Ashtakavarga points.

### `calculate_bhava_strength`

```python
calculate_bhava_strength(
    context: BhavaStrengthContext,
    weights: BhavaStrengthWeights = DEFAULT_WEIGHTS
) -> BhavaStrengthSummary
```

### Default Weights

| Factor | Default Weight |
|--------|---------------|
| Benefic occupant | +2.0 |
| Malefic occupant | −2.0 |
| Lord exalted | +3.0 |
| Lord debilitated | −3.0 |
| Benefic aspect | +1.0 |
| Malefic aspect | −1.0 |
| Ashtakavarga multiplier | 0.5 |

---

## 4. Aspect Strength

Calculates the strength of planetary aspects within the natal chart.

### `calculate_aspects_with_strength`

```python
calculate_aspects_with_strength(
    planet_longitudes: dict[str, float]
) -> AspectStrengthReport
```

### Aspect Types

| Type | Orb |
|------|-----|
| `CONJUNCTION` | 0° |
| `OPPOSITION` | 180° |
| `TRINE` | 120° |
| `SQUARE` | 90° |
| `SEXTILE` | 60° |
| `SEVENTH` | 210°/150° — full-sign 7th house aspect |

### Special Aspects

Certain planets cast full aspects to non-standard houses (in addition to the 7th):

| Planet | Special Houses Aspected |
|--------|------------------------|
| Mars | 4th and 8th |
| Jupiter | 5th and 9th |
| Saturn | 3rd and 10th |

### `AspectStrengthReport`

| Field | Type | Description |
|-------|------|-------------|
| `aspects` | `list[Aspect]` | All detected aspects |
| `strongest_aspect` | `Aspect | None` | Highest-strength aspect |
| `total_aspects` | `int` | Count of aspects found |
