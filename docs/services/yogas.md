# Yogas

Yogas are planetary combinations in Vedic astrology that produce specific life outcomes. The system covers three layers of yoga analysis:

1. **Nitya Yoga** — daily lunar-solar combination (27 yogas)
2. **Pancha Mahapurusha & Other Planetary Yogas** — natal chart combinations
3. **Extended Yogas** — nine additional classical combinations

---

## Nitya Yoga

The Nitya Yoga is calculated from the combined longitude of the Sun and Moon divided into 27 equal segments of 13°20′.

### `calculate_nitya_yoga`

```python
calculate_nitya_yoga(
    sun_longitude: float,
    moon_longitude: float
) -> NityaYogaResult
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `sun_longitude` | `float` | Sidereal Sun longitude (0–360°) |
| `moon_longitude` | `float` | Sidereal Moon longitude (0–360°) |

**Returns:** `NityaYogaResult` with `number` (1–27), `name`, and `description`.

### `get_nitya_yoga_name`

```python
get_nitya_yoga_name(number: int) -> str
```

Returns the Sanskrit name for a nitya yoga number (1–27).

### The 27 Nitya Yogas

| # | Name | Nature |
|---|------|--------|
| 1 | Vishkambha | Inauspicious |
| 2 | Preeti | Auspicious |
| 3 | Ayushman | Auspicious |
| 4 | Saubhagya | Auspicious |
| 5 | Shobhana | Auspicious |
| 6 | Atiganda | Inauspicious |
| 7 | Sukarma | Auspicious |
| 8 | Dhriti | Auspicious |
| 9 | Shoola | Inauspicious |
| 10 | Ganda | Inauspicious |
| 11 | Vriddhi | Auspicious |
| 12 | Dhruva | Auspicious |
| 13 | Vyaghata | Inauspicious |
| 14 | Harshana | Auspicious |
| 15 | Vajra | Mixed |
| 16 | Siddhi | Auspicious |
| 17 | Vyatipata | Very Inauspicious |
| 18 | Variyan | Inauspicious |
| 19 | Parigha | Inauspicious |
| 20 | Shiva | Auspicious |
| 21 | Siddha | Auspicious |
| 22 | Sadhya | Auspicious |
| 23 | Shubha | Auspicious |
| 24 | Shukla | Auspicious |
| 25 | Brahma | Auspicious |
| 26 | Indra | Auspicious |
| 27 | Vaidhriti | Very Inauspicious |

---

## Planetary Yogas

Planetary yogas evaluate natal chart configurations. They require a `PlanetaryYogaContext` that holds all planet positions, signs, and house placements.

### Pancha Mahapurusha Yogas

Five "Great Person" yogas formed when a non-luminous planet (Mars, Mercury, Jupiter, Venus, Saturn) occupies its own sign or exaltation sign in a kendra (house 1, 4, 7, or 10):

| Yoga | Planet | Sign/Exaltation |
|------|--------|----------------|
| **Ruchaka** | Mars | Aries / Scorpio (own) or Capricorn (exalted) |
| **Bhadra** | Mercury | Gemini / Virgo (own) or Virgo (exalted) |
| **Hamsa** | Jupiter | Sagittarius / Pisces (own) or Cancer (exalted) |
| **Malavya** | Venus | Taurus / Libra (own) or Pisces (exalted) |
| **Sasa** | Saturn | Capricorn / Aquarius (own) or Libra (exalted) |

### Gajakesari Yoga

Jupiter in a kendra from the Moon (houses 1, 4, 7, or 10 from Moon's position). Produces wisdom, wealth, and renown.

---

## Extended Yogas

### `evaluate_extended_yogas`

```python
evaluate_extended_yogas(
    context: PlanetaryYogaContext
) -> list[YogaRuleResult]
```

Evaluates nine additional classical yogas. Returns **only the yogas that are present** in the chart (empty list if none qualify).

Each `YogaRuleResult` includes: `name`, `present` (always `True`), `description`, and `strength`.

### The Nine Extended Yogas

| Yoga | Key Combination | Effect |
|------|----------------|--------|
| **Lakshmi Yoga** | Venus + lagna lord in angle/trine, strong | Wealth, luxury, fortune |
| **Saraswati Yoga** | Jupiter, Venus, Mercury in kendras/trikonas | Learning, creativity, eloquence |
| **Budha-Aditya (Strong)** | Sun + Mercury conjunct, Mercury not combust | Intelligence, analytical skill |
| **Parvata Yoga** | 6th and 8th lords weak or absent, lagna strong | Fame, prosperity |
| **Kahala Yoga** | 4th + 9th lords strong and connected | Courage, commanding nature |
| **Chamara Yoga** | Lagna lord exalted in angle, Jupiter aspectting | Respect, leadership |
| **Sankha Yoga** | 5th + 6th lords in mutual angles | Charitable, humanitarian |
| **Matsya Yoga** | Multiple planets in 4th/8th with Lagna strong | Intuitive, deep insight |
| **Vasumathi Yoga** | Benefics in Upachaya houses (3, 6, 10, 11) | Accumulated wealth, enterprise |

---

## `PlanetaryYogaContext`

The shared context object passed to yoga evaluation functions:

| Field | Type | Description |
|-------|------|-------------|
| `planets` | `list[Planet]` | Full planet list with positions |
| `ascendant` | `Planet` | Lagna planet object |
| `house_cusps` | `list[float]` | House cusp longitudes |
| `ayanamsa` | `int` | Ayanamsa used for computation |
