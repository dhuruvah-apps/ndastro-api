# Avasthas (Planetary States)

Avasthas describe the experiential state of a planet in the natal chart. The system uses four independent dimensions, each providing a different lens on how a planet expresses its significations.

---

## Overview

| Avastha Type | Dimension | States |
|-------------|-----------|--------|
| **Age Avastha** | Stage of life | 5 |
| **Alertness Avastha** | Consciousness level | 3 |
| **Mood Avastha** | Emotional state | 15 |
| **Activity Avastha** | Mode of action | 12 |

---

## Age Avastha (Baala—Vridha)

Reflects the planet's "age" — how fully it can deliver its results.

### `calculate_age_avastha`

```python
calculate_age_avastha(
    degree_in_rasi: float,
    rasi_number: int
) -> tuple[AgeAvastha, float]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `degree_in_rasi` | `float` | Planet's degree within its sign (0–30) |
| `rasi_number` | `int` | Sign number 1–12 |

**Returns:** `(AgeAvastha, confidence_score)`

### `AgeAvastha` Values

| Value | Sanskrit | Degree Range | Meaning |
|-------|---------|--------------|---------|
| `SAISAVA` | Infant | 0–6° | Planet is very weak, unable to deliver |
| `KUMAARA` | Youth | 6–12° | Planet is growing, partial results |
| `YUVA` | Adult | 12–18° | Planet is at full strength |
| `VRIDDHA` | Old | 18–24° | Planet is weakening, declining results |
| `MRITA` | Dead | 24–30° | Planet gives no results |

---

## Alertness Avastha (Jaagrita—Sushupta)

Reflects whether the planet is "awake" to deliver its significations.

### `calculate_alertness_avastha`

```python
calculate_alertness_avastha(
    planet_code: str,
    rasi_name: str
) -> tuple[AlertnessAvastha, str]
```

**Returns:** `(AlertnessAvastha, description)`

### `AlertnessAvastha` Values

| Value | Sanskrit | Condition | Effect |
|-------|---------|-----------|--------|
| `JAAGRITA` | Awake | Planet in its own sign, exaltation, or moolatrikona | Full results delivered |
| `SWAPNA` | Dreaming | Planet in a friend's sign | Moderate results |
| `SUSHUPTA` | Deep sleep | Planet in enemy/debilitated sign | Minimal results |

---

## Mood Avastha (Dipta—Khala)

Describes the emotional/functional mood of a planet, producing 15 distinct states based on sign relationships.

### `calculate_mood_avastha`

```python
calculate_mood_avastha(
    context: AvasthaPlanetContext
) -> tuple[MoodAvastha, str]
```

**Returns:** `(MoodAvastha, narrative_description)`

### `MoodAvastha` Values (15 states)

| Value | Sanskrit | Trigger Conditions |
|-------|---------|-------------------|
| `DIPTA` | Radiant | Exalted |
| `SWASTHA` | Comfortable | Own sign |
| `MUDITA` | Joyful | Great friend's sign |
| `SHAANTA` | Peaceful | Friend's sign |
| `SHAKTA` | Capable | Neutral sign, strong |
| `PEEDITA` | Suffering | Aspected by malefic |
| `DEENA` | Miserable | Debilitated |
| `VIKALA` | Disabled | Combust |
| `KHALA` | Cruel | Enemy's sign |
| `KOPA` | Angry | Sign of great enemy |
| `SUSHUPTI` | Dreaming | Weak and aspected |
| `TRASHTA` | Frightened | Mutual aspects with malefics |
| `KAALA` | Time-worn | Old period ending |
| `SABHAYA` | Fearful | Eclipsed/combust with malefic |
| `VIGNA` | Obstructed | Multiple afflictions |

---

## Activity Avastha (Sayana—Netrapani)

Describes what the planet is "doing" — its mode of activity — using a classical Parasara formula.

### `calculate_activity_avastha`

```python
calculate_activity_avastha(
    context: ActivityAvasthaPlanetContext
) -> tuple[ActivityAvastha, ActivityStrength, str]
```

**Formula:** `(C × P × A) + M + G + L mod 12`

where C = chart factor, P = planet factor, A = ascendant factor, M = Moon factor, G = gender factor, L = lord factor.

### `ActivityAvastha` Values (12 states)

| Value | Sanskrit | General Meaning |
|-------|---------|----------------|
| `SAYANA` | Sleeping | Inactive, resting |
| `UPAVESANA` | Sitting | Contemplative |
| `NETRAPANI` | Hands to eyes | Sorrowful, weeping |
| `PRAKASHANA` | Displaying | Active, showing results |
| `GAMANA` | Moving | Travelling, dynamic |
| `AGAMANA` | Returning | Recovery, coming back |
| `SABHAA` | In assembly | Social, public role |
| `AAGAMA` | Approaching | Gaining, arriving |
| `BHOJANA` | Eating | Enjoyment, abundance |
| `NRTYA_LIPA` | Dancing | Creative, expressive |
| `KAUTUKA` | Curious | Exploration, learning |
| `NIDRAA` | Deep sleep | Completely dormant |

### `ActivityStrength` Values

| Value | Meaning |
|-------|---------|
| `STRONG` | Activity produces strong outcomes |
| `MODERATE` | Activity produces moderate outcomes |
| `WEAK` | Activity is suppressed |

---

## Context Objects

### `AvasthaPlanetContext`

| Field | Type | Description |
|-------|------|-------------|
| `planet_code` | `str` | Planet code (e.g. `"SU"`, `"MO"`) |
| `rasi_number` | `int` | Current sign 1–12 |
| `aspects` | `list[str]` | Codes of aspecting planets |
| `is_combust` | `bool` | Whether planet is combust |
| `is_retrograde` | `bool` | Whether planet is retrograde |

### `ActivityAvasthaPlanetContext`

Extends `AvasthaPlanetContext` with additional chart-level fields needed for the Parasara formula (chart factor, ascendant factor, Moon factor, etc.).
