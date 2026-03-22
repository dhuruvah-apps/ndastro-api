# Planetary Positions

The `position` service computes sidereal planetary positions using the Swiss Ephemeris. It returns detailed data for all nine Jyotish planets (Navagrahas) plus the lunar nodes.

---

## Functions

### `get_sidereal_planet_positions`

```python
get_sidereal_planet_positions(
    lat: float,
    lon: float,
    given_time: datetime,
    ayanamsa: int = 1
) -> list[Planet]
```

Returns sidereal positions for all Jyotish planets at the given time and location.

**Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `lat` | `float` | Geographic latitude in decimal degrees |
| `lon` | `float` | Geographic longitude in decimal degrees |
| `given_time` | `datetime` | UTC datetime for the computation |
| `ayanamsa` | `int` | Ayanamsa code (default `1` = Lahiri) |

**Returns:** `list[Planet]` — one entry per planet (see Planet model below).

---

### `get_sidereal_ascendant_position`

```python
get_sidereal_ascendant_position(
    given_time: datetime,
    lat: float,
    lon: float,
    ayanamsa: int = 1
) -> Planet
```

Computes the sidereal ascendant (Lagna) for the given birth time and place.

---

### `get_nakshatra_and_pada`

```python
get_nakshatra_and_pada(longitude: float) -> tuple[NakshatraCode, int]
```

Determines the nakshatra and pada (quarter) for a given ecliptic longitude.

| Return | Type | Description |
|--------|------|-------------|
| `NakshatraCode` | `str` | 3-letter nakshatra code (e.g. `"ASW"`, `"BHA"`) |
| `int` | — | Pada number: 1–4 |

---

### `get_planet_sign_and_degree`

```python
get_planet_sign_and_degree(planet_longitude: float) -> tuple[Rasis, Angle]
```

Converts an ecliptic longitude into a zodiac sign and degree within that sign.

---

### `get_planet_house_position`

```python
get_planet_house_position(
    ascendant_longitude: float,
    planet_longitude: float
) -> Houses
```

Calculates the house (bhava) number (1–12) of a planet relative to the ascendant.

---

## Planet Model

Each `Planet` object returned carries the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Planet name (e.g. `"Sun"`, `"Moon"`) |
| `code` | `str` | Short code (e.g. `"SU"`, `"MO"`, `"LA"`) |
| `longitude` | `float` | Ecliptic longitude in decimal degrees (0–360) |
| `latitude` | `float` | Ecliptic latitude |
| `speed` | `float` | Daily motion in degrees |
| `retrograde` | `bool` | `true` if planet is retrograde |
| `rasi` | `str` | Zodiac sign name |
| `rasi_number` | `int` | Sign number 1–12 (Aries = 1) |
| `degree_in_rasi` | `float` | Degrees within the current sign (0–30) |
| `house` | `int` | Bhava number 1–12 |
| `nakshatra` | `str` | Nakshatra name |
| `nakshatra_code` | `str` | 3-letter nakshatra code |
| `nakshatra_pada` | `int` | Pada 1–4 |

---

## Planets Covered

| Code | Planet | Sanskrit |
|------|--------|---------|
| `SU` | Sun | Surya |
| `MO` | Moon | Chandra |
| `MA` | Mars | Mangala |
| `ME` | Mercury | Budha |
| `JU` | Jupiter | Guru |
| `VE` | Venus | Shukra |
| `SA` | Saturn | Shani |
| `RA` | Rahu (North Node) | — |
| `KE` | Ketu (South Node) | — |
| `LA` | Ascendant | Lagna |

---

## Ayanamsa Codes

| Code | Name | Notes |
|------|------|-------|
| `1` | Lahiri | Most common in Indian astrology (default) |
| `3` | Raman | B.V. Raman ayanamsa |
| `5` | Krishnamurti (KP) | Used in KP astrology |
