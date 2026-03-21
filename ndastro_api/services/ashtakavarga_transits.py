"""Ashtakavarga Transit Predictions Module.

Combines Ashtakavarga (natal strength of houses) with current transits
to generate highly accurate, weighted predictions. When a planet transits
through a house, the effect is amplified or diminished based on the natal
Ashtakavarga points in that house.

Key Concept:
- High Ashtakavarga points (30+) + Beneficial transit = Very Favorable
- Low Ashtakavarga points (<20) + Challenging transit = Very Challenging
- This gives a 2D analysis: natal potential × current activation
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# Thresholds for Ashtakavarga points
SAV_VERY_STRONG = 40
SAV_STRONG = 30
SAV_MODERATE = 20
SAV_WEAK = 10

# Transit timing categories
SLOW_PLANETS = {"jupiter", "saturn", "rahu", "kethu"}
MEDIUM_PLANETS = {"mars", "venus"}
FAST_PLANETS = {"sun", "moon", "mercury"}


class TransitPredictionStrength(str, Enum):
    """Overall prediction strength combining SAV + transit."""

    EXCELLENT = "excellent"  # Strong SAV + beneficial transit
    VERY_GOOD = "very_good"  # Good SAV + beneficial transit
    GOOD = "good"  # Moderate SAV + beneficial
    NEUTRAL = "neutral"  # Balanced or mixed
    CHALLENGING = "challenging"  # Weak SAV or challenging transit
    DIFFICULT = "difficult"  # Weak SAV + challenging transit
    VERY_DIFFICULT = "very_difficult"  # Very weak SAV + malefic transit


class LifeAreaFocus(str, Enum):
    """Life areas affected by house transits."""

    SELF_HEALTH = "self_health"  # House 1
    WEALTH_FAMILY = "wealth_family"  # House 2
    COURAGE_SIBLINGS = "courage_siblings"  # House 3
    HOME_MOTHER = "home_mother"  # House 4
    CHILDREN_CREATIVITY = "children_creativity"  # House 5
    ENEMIES_HEALTH = "enemies_health"  # House 6
    PARTNERSHIP_MARRIAGE = "partnership_marriage"  # House 7
    TRANSFORMATION_OCCULT = "transformation_occult"  # House 8
    FORTUNE_DHARMA = "fortune_dharma"  # House 9
    CAREER_STATUS = "career_status"  # House 10
    GAINS_INCOME = "gains_income"  # House 11
    LOSS_SPIRITUALITY = "loss_spirituality"  # House 12


@dataclass
class AshtakavargaTransitPrediction:
    """Complete prediction for a house transit with SAV weighting."""

    house: int
    transiting_planet: str
    sav_points: int
    sav_strength: str  # "very_strong", "strong", "moderate", "weak", "very_weak"
    transit_nature: str  # "beneficial", "neutral", "challenging"
    prediction_strength: TransitPredictionStrength
    life_area: LifeAreaFocus
    duration_category: str  # "slow", "medium", "fast"
    primary_effects: list[str]
    recommendations: list[str]
    timing_notes: str


@dataclass
class AshtakavargaTransitReport:
    """Complete report of all transit predictions."""

    predictions: list[AshtakavargaTransitPrediction]
    most_favorable_houses: list[int]
    most_challenging_houses: list[int]
    key_recommendations: list[str]
    overall_period_assessment: str


# Benefic and malefic planet classifications
BENEFIC_PLANETS = {"jupiter", "venus", "mercury", "moon"}
MALEFIC_PLANETS = {"saturn", "mars", "rahu", "kethu", "sun"}

# House to life area mapping
HOUSE_TO_LIFE_AREA = {
    1: LifeAreaFocus.SELF_HEALTH,
    2: LifeAreaFocus.WEALTH_FAMILY,
    3: LifeAreaFocus.COURAGE_SIBLINGS,
    4: LifeAreaFocus.HOME_MOTHER,
    5: LifeAreaFocus.CHILDREN_CREATIVITY,
    6: LifeAreaFocus.ENEMIES_HEALTH,
    7: LifeAreaFocus.PARTNERSHIP_MARRIAGE,
    8: LifeAreaFocus.TRANSFORMATION_OCCULT,
    9: LifeAreaFocus.FORTUNE_DHARMA,
    10: LifeAreaFocus.CAREER_STATUS,
    11: LifeAreaFocus.GAINS_INCOME,
    12: LifeAreaFocus.LOSS_SPIRITUALITY,
}

# Planet-house effect matrix (basic transit effects)
PLANET_HOUSE_EFFECTS = {
    "jupiter": {
        "beneficial_houses": {1, 2, 5, 7, 9, 10, 11},
        "neutral_houses": {3, 4, 8},
        "challenging_houses": {6, 12},
    },
    "saturn": {
        "beneficial_houses": {3, 6, 10, 11},
        "neutral_houses": {2, 8, 12},
        "challenging_houses": {1, 4, 5, 7, 9},
    },
    "mars": {
        "beneficial_houses": {3, 6, 10, 11},
        "neutral_houses": {2, 8},
        "challenging_houses": {1, 4, 5, 7, 9, 12},
    },
    "venus": {
        "beneficial_houses": {1, 2, 4, 5, 7, 9, 11, 12},
        "neutral_houses": {3, 8, 10},
        "challenging_houses": {6},
    },
    "mercury": {
        "beneficial_houses": {1, 2, 4, 5, 6, 9, 10},
        "neutral_houses": {3, 7, 8, 11, 12},
        "challenging_houses": set(),
    },
    "sun": {
        "beneficial_houses": {1, 3, 10, 11},
        "neutral_houses": {2, 4, 5, 9},
        "challenging_houses": {6, 7, 8, 12},
    },
    "moon": {
        "beneficial_houses": {1, 2, 3, 4, 7, 10, 11},
        "neutral_houses": {5, 9},
        "challenging_houses": {6, 8, 12},
    },
    "rahu": {
        "beneficial_houses": {3, 6, 10, 11},
        "neutral_houses": {2, 8, 12},
        "challenging_houses": {1, 4, 5, 7, 9},
    },
    "kethu": {
        "beneficial_houses": {3, 6, 12},
        "neutral_houses": {8, 9},
        "challenging_houses": {1, 2, 4, 5, 7, 10, 11},
    },
}


def classify_sav_strength(sav_points: int) -> str:
    """Classify Sarva Ashtakavarga strength level.

    Args:
        sav_points: Total SAV points for a house (0-56 typically)

    Returns:
        Strength classification string

    """
    if sav_points >= SAV_VERY_STRONG:
        return "very_strong"
    if sav_points >= SAV_STRONG:
        return "strong"
    if sav_points >= SAV_MODERATE:
        return "moderate"
    if sav_points >= SAV_WEAK:
        return "weak"
    return "very_weak"


def determine_transit_nature(planet: str, house: int) -> str:
    """Determine if a planet's transit through a house is beneficial/neutral/challenging.

    Args:
        planet: Transiting planet name
        house: House number (1-12)

    Returns:
        "beneficial", "neutral", or "challenging"

    """
    effects = PLANET_HOUSE_EFFECTS.get(planet, {})
    beneficial = effects.get("beneficial_houses", set())
    challenging = effects.get("challenging_houses", set())

    if house in beneficial:
        return "beneficial"
    if house in challenging:
        return "challenging"
    return "neutral"


def calculate_prediction_strength(
    sav_points: int,
    transit_nature: str,
) -> TransitPredictionStrength:
    """Calculate overall prediction strength from SAV + transit.

    Args:
        sav_points: Sarva Ashtakavarga points in the house
        transit_nature: "beneficial", "neutral", or "challenging"

    Returns:
        TransitPredictionStrength enum value

    """
    sav_strength = classify_sav_strength(sav_points)

    # Matrix of combinations
    if transit_nature == "beneficial":
        if sav_strength in {"very_strong", "strong"}:
            return TransitPredictionStrength.EXCELLENT
        if sav_strength == "moderate":
            return TransitPredictionStrength.VERY_GOOD
        if sav_strength == "weak":
            return TransitPredictionStrength.GOOD
        return TransitPredictionStrength.NEUTRAL

    if transit_nature == "challenging":
        if sav_strength in {"very_weak", "weak"}:
            return TransitPredictionStrength.VERY_DIFFICULT
        if sav_strength == "moderate":
            return TransitPredictionStrength.DIFFICULT
        if sav_strength == "strong":
            return TransitPredictionStrength.CHALLENGING
        return TransitPredictionStrength.NEUTRAL

    # Neutral transit
    if sav_strength in {"very_strong", "strong"}:
        return TransitPredictionStrength.GOOD
    if sav_strength == "moderate":
        return TransitPredictionStrength.NEUTRAL
    return TransitPredictionStrength.CHALLENGING


def get_duration_category(planet: str) -> str:
    """Get transit duration category based on planet speed.

    Args:
        planet: Planet name

    Returns:
        "slow", "medium", or "fast"

    """
    if planet in SLOW_PLANETS:
        return "slow"
    if planet in MEDIUM_PLANETS:
        return "medium"
    return "fast"


def generate_primary_effects(
    planet: str,
    house: int,
    sav_strength: str,
    transit_nature: str,
) -> list[str]:
    """Generate primary effects description for the transit.

    Args:
        planet: Transiting planet
        house: House number
        sav_strength: SAV strength classification
        transit_nature: beneficial/neutral/challenging

    Returns:
        List of primary effect descriptions

    """
    effects = []

    # House-specific themes
    house_themes = {
        1: "self, health, vitality, appearance, new beginnings",
        2: "wealth, family, speech, food, values, possessions",
        3: "courage, siblings, communication, short travels, skills",
        4: "home, mother, property, emotional peace, vehicles",
        5: "children, creativity, education, romance, speculation",
        6: "enemies, disease, debts, service, competition, daily work",
        7: "marriage, partnerships, business, public image, spouse",
        8: "transformation, longevity, occult, inheritance, sudden events",
        9: "fortune, father, dharma, higher learning, long travels",
        10: "career, status, authority, reputation, achievements",
        11: "gains, income, friends, aspirations, elder siblings",
        12: "loss, expenses, foreign lands, spirituality, isolation, sleep",
    }

    house_theme = house_themes.get(house, "this life area")

    # Base effect description
    if transit_nature == "beneficial":
        effects.append(f"{planet.title()} favorably activates {house_theme}")
    elif transit_nature == "challenging":
        effects.append(f"{planet.title()} creates challenges in {house_theme}")
    else:
        effects.append(f"{planet.title()} neutrally influences {house_theme}")

    # SAV modulation
    if sav_strength in {"very_strong", "strong"}:
        effects.append(f"House has strong foundation ({sav_strength}) to handle events")
    elif sav_strength in {"weak", "very_weak"}:
        effects.append(f"House foundation is {sav_strength}, requiring extra caution")

    # Planet-specific interpretations
    planet_effects = {
        "jupiter": "expansion, wisdom, optimism, growth opportunities",
        "saturn": "discipline, delays, hard work, karmic lessons, maturity",
        "mars": "energy, action, competition, courage, potential conflicts",
        "venus": "harmony, pleasure, relationships, comforts, artistic expression",
        "mercury": "intellect, communication, business, learning, adaptability",
        "sun": "confidence, authority, ego, vitality, leadership",
        "moon": "emotions, mind, fluctuations, intuition, nurturing",
        "rahu": "ambition, unconventional, obsession, sudden changes, material desires",
        "kethu": "spirituality, detachment, past-life, losses, enlightenment",
    }

    planet_quality = planet_effects.get(planet, "planetary influence")
    effects.append(f"Emphasizes: {planet_quality}")

    return effects


def generate_recommendations(
    planet: str,
    house: int,
    prediction_strength: TransitPredictionStrength,
    duration_category: str,
) -> list[str]:
    """Generate actionable recommendations for the transit period.

    Args:
        planet: Transiting planet
        house: House number
        prediction_strength: Overall prediction strength
        duration_category: slow/medium/fast

    Returns:
        List of recommendations

    """
    recommendations = []

    # Duration-based planning
    if duration_category == "slow":
        recommendations.append(f"Long-term transit ({planet}): Plan major actions for this entire period (1+ years)")
    elif duration_category == "medium":
        recommendations.append(f"Medium-term transit ({planet}): Best to act within 1-6 months window")
    else:
        recommendations.append(f"Short-term transit ({planet}): Act quickly, effects pass within weeks")

    # Strength-based actions
    if prediction_strength in {TransitPredictionStrength.EXCELLENT, TransitPredictionStrength.VERY_GOOD}:
        recommendations.append("Excellent timing! Initiate important projects in this life area")
        recommendations.append("Expect support and favorable outcomes")
    elif prediction_strength == TransitPredictionStrength.GOOD:
        recommendations.append("Favorable period but requires effort. Take calculated actions")
    elif prediction_strength in {TransitPredictionStrength.CHALLENGING, TransitPredictionStrength.DIFFICULT}:
        recommendations.append("Exercise caution. Delay major decisions if possible")
        recommendations.append("Focus on damage control and patience")
    elif prediction_strength == TransitPredictionStrength.VERY_DIFFICULT:
        recommendations.append("Very challenging period. Avoid new initiatives")
        recommendations.append("Strengthen foundations, seek expert guidance, practice patience")

    # House-specific recommendations
    house_recommendations = {
        1: ["Focus on health and self-care", "Good time for personal growth initiatives"],
        2: ["Monitor finances carefully", "Family time important"],
        3: ["Enhance communication skills", "Connect with siblings"],
        4: ["Attend to home matters", "Spend time with mother"],
        5: ["Creative projects favored", "Children's education focus"],
        6: ["Health checkups advisable", "Address pending conflicts"],
        7: ["Relationship attention needed", "Business partnerships review"],
        8: ["Insurance and estate planning", "Study occult sciences if interested"],
        9: ["Spiritual practices beneficial", "Consider higher education or travel"],
        10: ["Career advancement opportunities", "Public speaking or visibility"],
        11: ["Networking important", "Financial goals achievable"],
        12: ["Meditation and retreat helpful", "Foreign connections possible"],
    }

    house_recs = house_recommendations.get(house, [])
    recommendations.extend(house_recs[:2])  # Add top 2 house recommendations

    return recommendations


def generate_timing_notes(planet: str, duration_category: str) -> str:
    """Generate timing-specific notes.

    Args:
        planet: Transiting planet
        duration_category: slow/medium/fast

    Returns:
        Timing guidance string

    """
    durations = {
        "jupiter": "~1 year per house (13 months)",
        "saturn": "~2.5 years per house",
        "rahu": "~1.5 years per house",
        "kethu": "~1.5 years per house",
        "mars": "~1.5-2 months per house",
        "venus": "~1 month per house (variable)",
        "sun": "~1 month per house",
        "moon": "~2.25 days per house",
        "mercury": "~3 weeks per house (variable with retrogrades)",
    }

    base_duration = durations.get(planet, "Variable duration")

    if duration_category == "slow":
        return f"{base_duration}. Long-lasting effects - plan accordingly. Peak effects in middle third of transit."
    if duration_category == "medium":
        return f"{base_duration}. Moderate duration - take action in first half. Monitor retrograde periods."
    return f"{base_duration}. Brief effects - act immediately for best results. Effects fade quickly."


def predict_ashtakavarga_transit(
    planet: str,
    house: int,
    sav_points: int,
) -> AshtakavargaTransitPrediction:
    """Generate complete prediction for a single transit.

    Args:
        planet: Transiting planet name
        house: House number (1-12)
        sav_points: Sarva Ashtakavarga points for that house

    Returns:
        Complete AshtakavargaTransitPrediction object

    """
    sav_strength = classify_sav_strength(sav_points)
    transit_nature = determine_transit_nature(planet, house)
    prediction_strength = calculate_prediction_strength(sav_points, transit_nature)
    duration_category = get_duration_category(planet)
    life_area = HOUSE_TO_LIFE_AREA[house]

    primary_effects = generate_primary_effects(planet, house, sav_strength, transit_nature)
    recommendations = generate_recommendations(planet, house, prediction_strength, duration_category)
    timing_notes = generate_timing_notes(planet, duration_category)

    return AshtakavargaTransitPrediction(
        house=house,
        transiting_planet=planet,
        sav_points=sav_points,
        sav_strength=sav_strength,
        transit_nature=transit_nature,
        prediction_strength=prediction_strength,
        life_area=life_area,
        duration_category=duration_category,
        primary_effects=primary_effects,
        recommendations=recommendations,
        timing_notes=timing_notes,
    )


def generate_ashtakavarga_transit_report(
    transit_houses: dict[str, int],
    sav_scores: dict[int, int],
) -> AshtakavargaTransitReport:
    """Generate comprehensive report for all current transits.

    Args:
        transit_houses: Dict mapping planet names to current house numbers
        sav_scores: Dict mapping house numbers (1-12) to SAV points

    Returns:
        Complete AshtakavargaTransitReport

    """
    predictions = []

    # Generate prediction for each transit
    for planet, house in transit_houses.items():
        sav_points = sav_scores.get(house, 25)  # Default moderate if not provided
        prediction = predict_ashtakavarga_transit(planet, house, sav_points)
        predictions.append(prediction)

    # Analyze to find most favorable/challenging
    sorted_by_strength = sorted(
        predictions,
        key=lambda p: list(TransitPredictionStrength).index(p.prediction_strength),
    )

    favorable = [
        p.house
        for p in predictions
        if p.prediction_strength in {TransitPredictionStrength.EXCELLENT, TransitPredictionStrength.VERY_GOOD, TransitPredictionStrength.GOOD}
    ]

    challenging = [
        p.house
        for p in predictions
        if p.prediction_strength
        in {
            TransitPredictionStrength.CHALLENGING,
            TransitPredictionStrength.DIFFICULT,
            TransitPredictionStrength.VERY_DIFFICULT,
        }
    ]

    # Generate key recommendations (top 3-5)
    key_recs = []
    if sorted_by_strength:
        best = sorted_by_strength[0]
        if best.prediction_strength in {TransitPredictionStrength.EXCELLENT, TransitPredictionStrength.VERY_GOOD}:
            key_recs.append(
                f"Excellent opportunity in House {best.house} ({best.life_area.value}) - "
                f"{best.transiting_planet.title()} transit with strong foundation"
            )

    if len(sorted_by_strength) > 1:
        worst = sorted_by_strength[-1]
        if worst.prediction_strength in {
            TransitPredictionStrength.DIFFICULT,
            TransitPredictionStrength.VERY_DIFFICULT,
        }:
            key_recs.append(
                f"Caution needed in House {worst.house} ({worst.life_area.value}) - {worst.transiting_planet.title()} challenging weak foundation"
            )

    # Count slow planet transits for long-term planning
    slow_transits = [p for p in predictions if p.duration_category == "slow"]
    if slow_transits:
        key_recs.append(f"{len(slow_transits)} slow planet transit(s) - Long-term effects (1-2+ years)")

    # Overall assessment
    excellent_count = sum(1 for p in predictions if p.prediction_strength == TransitPredictionStrength.EXCELLENT)
    difficult_count = sum(
        1 for p in predictions if p.prediction_strength in {TransitPredictionStrength.DIFFICULT, TransitPredictionStrength.VERY_DIFFICULT}
    )

    if excellent_count > difficult_count:
        overall = "Favorable period overall. Multiple opportunities for growth and success."
    elif difficult_count > excellent_count:
        overall = "Challenging period requiring patience and careful planning. Focus on strengthening foundations."
    else:
        overall = "Mixed period with both opportunities and challenges. Selective action recommended."

    return AshtakavargaTransitReport(
        predictions=predictions,
        most_favorable_houses=favorable[:5],  # Top 5
        most_challenging_houses=challenging[:5],
        key_recommendations=key_recs,
        overall_period_assessment=overall,
    )
