# Prasna (Vedic Horary Astrology)

Prasna Shastra is the classical Vedic system of **predicting what a person came to ask about** before they speak.
At the exact moment of arrival, the Lagna (ascendant), Moon, 7th lord, and dominant planet collectively
encode the nature of the unspoken query.

The `prasna` service applies six classical rules to score all 12 houses of the chart, then returns the
top-3 predicted topics, each with a full analytical paragraph.

The public result dataclasses live in `ndastro_api.core.models.prasna`.

---

## API Endpoint

| Method | Path | Summary |
|--------|------|---------|
| `GET` | `/api/v1/prasna/query-topic` | Predict the topic of an unspoken query from the current chart |

---

## `GET /api/v1/prasna/query-topic`

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `lat` | `float` | ✓ | Geographic latitude of the questioner |
| `lon` | `float` | ✓ | Geographic longitude of the questioner |
| `dateandtime` | `string` | — | ISO 8601 datetime of the query (defaults to current UTC) |
| `ayanamsa` | `string` | — | Ayanamsa system (default `lahiri`) |

### Response Shape

```json
{
  "datetime_utc": "2026-07-19T08:30:00+00:00",
  "chart": { ...PrasnaChartSnapshot... },
  "topics": [ ...PrasnaTopicResult × 3... ],
  "disclaimer": "Prasna Shastra is an indicative classical system..."
}
```

### `PrasnaChartSnapshot` Fields

| Field | Type | Description |
|-------|------|-------------|
| `lagna_sign_number` | `int` | Ascending sign 1–12 at query time |
| `lagna_sign_name` | `string` | e.g. `Leo` |
| `lagna_lord_code` | `string` | Planet code of the Lagna lord (e.g. `SU`) |
| `lagna_lord_house` | `int` | House (1–12) where the Lagna lord is placed |
| `moon_sign_number` | `int` | Moon's sign 1–12 |
| `moon_sign_name` | `string` | e.g. `Aquarius` |
| `moon_house` | `int` | Moon's whole-sign house (1–12) |
| `moon_nakshatra_number` | `int` | Nakshatra 1–27 |
| `moon_nakshatra_name` | `string` | e.g. `Shatabhisha` |
| `moon_nakshatra_lord_code` | `string` | Lord of Moon's nakshatra |
| `seventh_lord_code` | `string` | Planet code of the 7th house lord |
| `seventh_lord_house` | `int` | House where 7th lord is placed |
| `strongest_planet_code` | `string` | Most dignified planet in the chart |
| `strongest_planet_house` | `int` | House where the strongest planet sits |
| `strongest_planet_sign_name` | `string` | Sign of the strongest planet |

### `PrasnaTopicResult` Fields

| Field | Type | Description |
|-------|------|-------------|
| `rank` | `int` | 1 = most likely, 3 = third most likely |
| `topic` | `string` | Short label, e.g. `"Marriage & Partnership"` |
| `confidence` | `float` | Normalised score 0.0–1.0 |
| `primary_house` | `int` | House (1–12) that drives this prediction |
| `primary_indicator` | `string` | One-sentence classical rule trigger |
| `paragraph` | `string` | Full Prasna analysis with reasoning |

---

## The Six Classical Prasna Rules

The service scores each house (1–12) by applying the following rules in order of weight:

| # | Rule | Weight | Classical Basis |
|---|------|--------|----------------|
| 1 | **Moon's house** | 3.0 | Moon = mind; the house it occupies shows the questioner's preoccupation |
| 2 | **7th lord's house** | 2.0 | The 7th represents "what you came about" — the object of the query |
| 3 | **Lagna lord's house** | 2.0 | The Lagna lord reflects the self and its primary concern |
| 4 | **Strongest planet's house** | 1.5 | The most dignified planet activates its house's significations |
| 5 | **Most occupied house** | 0.7/planet | Where planets cluster, energy focuses |
| 6 | **Moon's nakshatra lord's house** | 1.0 | Fine-grained nakshatra-level indicator |

Additionally, planets in Kendra houses (1, 4, 7, 10) add a small boost (0.3 per planet) to those houses.

All house scores are normalised to 0–1 before ranking. The top-3 houses become the topic predictions.

---

## House → Topic Mapping

| House | Short Label | Typical Query Subject |
|-------|-------------|----------------------|
| 1 | Health & Self | Your health, body, appearance, or a deeply personal matter |
| 2 | Wealth & Family | Money, savings, pending income, family finances, or an asset |
| 3 | Communication & Siblings | A sibling, short journey, agreement, document, or decision requiring courage |
| 4 | Home, Property & Mother | Land, a house, a vehicle, your mother, or an educational institution |
| 5 | Children & Creativity | A child, romantic relationship, creative project, or investment |
| 6 | Enemies, Debt & Disease | A health problem, a debt, an enemy, or a legal dispute |
| 7 | Marriage & Partnership | A spouse, business partner, or significant agreement with another |
| 8 | Crisis, Secrets & Transformation | An inheritance, sudden event, hidden matter, or major life change |
| 9 | Fortune, Dharma & Long Journeys | Luck, religion, a long journey, your father, or guidance on the right path |
| 10 | Career & Status | Your career, a job matter, a promotion, or dealings with authority |
| 11 | Gains & Desires | Pending income, a fulfilled wish, or a friendship/network matter |
| 12 | Loss, Foreign & Spiritual | An expense, a loss, foreign travel, hospitalisation, or a spiritual question |

---

## Planet Dignity — Strength Calculation

The strongest planet is identified using classical dignity scores:

| Placement | Score |
|-----------|-------|
| Exaltation sign | 3.0 |
| Own sign | 2.5 |
| Friendly sign | 2.0 |
| Neutral sign | 1.5 |
| Enemy sign | 0.8 |
| Debilitation sign | 0.25 |

**Exaltation / Debilitation signs:**

| Planet | Exaltation | Debilitation |
|--------|-----------|--------------|
| Sun | Aries | Libra |
| Moon | Taurus | Scorpio |
| Mars | Capricorn | Cancer |
| Mercury | Virgo | Pisces |
| Jupiter | Cancer | Capricorn |
| Venus | Pisces | Virgo |
| Saturn | Libra | Aries |

---

## Result Models (`ndastro_api.core.models.prasna`)

### `PrasnaResult`

Top-level return type from `analyse_prasna_query`.

| Field | Type | Description |
|-------|------|-------------|
| `datetime_utc` | `str` | ISO 8601 UTC datetime of the query |
| `chart` | `PrasnaChartSnapshot` | Key chart elements |
| `topics` | `tuple[PrasnaTopicResult, ...]` | 3 ranked predictions |

### `PrasnaChartSnapshot`

Immutable snapshot of the key indicators — see [chart fields](#prasnachartsnapshot-fields) above.

### `PrasnaTopicResult`

One ranked prediction — see [topic fields](#prasnatopicresult-fields) above.

---

## Service Function

```python
from ndastro_api.services.prasna import analyse_prasna_query

result = analyse_prasna_query(
    lat=12.971667,
    lon=77.593611,
    dt=datetime.now(timezone.utc),
    ayanamsa_system="lahiri",   # default
)
```

Returns a `PrasnaResult`. The function uses `get_planet_position` and `get_ascendent_position`
from `ndastro_engine` and applies whole-sign houses throughout.

---

## Usage Example

```
GET /api/v1/prasna/query-topic?lat=12.971667&lon=77.593611
```

**Typical response (abridged):**

```json
{
  "datetime_utc": "2026-07-19T08:30:00+00:00",
  "chart": {
    "lagna_sign_name": "Leo",
    "lagna_lord_code": "SU",
    "lagna_lord_house": 1,
    "moon_sign_name": "Aquarius",
    "moon_house": 7,
    "moon_nakshatra_name": "Shatabhisha",
    "moon_nakshatra_lord_code": "RA",
    "seventh_lord_code": "SA",
    "seventh_lord_house": 7,
    "strongest_planet_code": "JU",
    "strongest_planet_house": 5,
    "strongest_planet_sign_name": "Sagittarius"
  },
  "topics": [
    {
      "rank": 1,
      "topic": "Marriage & Partnership",
      "confidence": 0.82,
      "primary_house": 7,
      "primary_indicator": "Moon occupies the 7th house",
      "paragraph": "At the moment of this query, Leo rises as the Lagna with Sun as its lord, now placed in the 1st house. The Moon — representing the mind and its preoccupations — occupies Aquarius in the 7th house, within the nakshatra Shatabhisha whose lord is Rahu. Classically, the 7th lord (Saturn) reveals what the questioner came about; here it resides in the 7th house. The strongest planet in this chart is Jupiter in Sagittarius (the 5th house). The dominant Prasna indicator here is: Moon occupies the 7th house. Taken together, these classical signs point with strong conviction toward a relationship — marriage, a business partner, or an agreement with another person. You appear to have come with a question about another person — a spouse, a life partner, a business associate, or a significant agreement or negotiation involving someone else."
    },
    ...
  ],
  "disclaimer": "Prasna Shastra is an indicative classical system..."
}
```

!!! note "Disclaimer"
    Prasna Shastra predictions are based on classical house-scoring rules applied at the moment of query.
    They are indicative, not definitive. Always interpret results in the context of the full chart and
    with guidance from a qualified Vedic astrologer.

!!! tip "Surprise Effect"
    The endpoint is designed so that the API caller can show the **rank-1 topic** to the questioner
    *before* the questioner has stated their concern — the classical Prasna astrologer's signature move.
    The `paragraph` field explains the full reasoning chain so the caller can narrate it naturally.
