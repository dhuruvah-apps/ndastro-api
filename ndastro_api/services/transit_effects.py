"""Transit effects analysis - detailed interpretation of planetary transits.

Provides in-depth transit analysis including house-by-house interpretations,
retrograde effects, conjunction impacts, and timing significance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TransitImpact(str, Enum):
    """Impact level of a transit."""

    VERY_FAVORABLE = "very_favorable"
    FAVORABLE = "favorable"
    NEUTRAL = "neutral"
    CHALLENGING = "challenging"
    VERY_CHALLENGING = "very_challenging"


class TransitDuration(str, Enum):
    """Duration classification of transit."""

    BRIEF = "brief"  # < 1 month
    SHORT = "short"  # 1-3 months
    MEDIUM = "medium"  # 3-6 months
    LONG = "long"  # 6-12 months
    EXTENDED = "extended"  # > 12 months


@dataclass
class TransitInterpretation:
    """Interpretation for a specific transit."""

    transiting_planet: str
    natal_house: int
    natal_planet: str | None
    impact: TransitImpact
    duration: TransitDuration
    description: str
    themes: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class TransitEffect:
    """Complete transit effect analysis."""

    planet: str
    current_house: int
    is_retrograde: bool
    interpretations: list[TransitInterpretation] = field(default_factory=list)
    overall_impact: TransitImpact = TransitImpact.NEUTRAL


# House-by-house transit interpretations
HOUSE_TRANSIT_THEMES = {
    1: {
        "themes": ["Self, identity, appearance, vitality"],
        "jupiter": ("Very favorable", "Growth in confidence, new beginnings, opportunities"),
        "saturn": ("Challenging", "Responsibility increases, self-discipline needed"),
        "mars": ("Energizing", "Increased energy and assertiveness"),
        "venus": ("Favorable", "Improved appearance, charm, social grace"),
        "mercury": ("Activating", "Mental clarity, communication skills enhanced"),
        "sun": ("Empowering", "Vitality and leadership strengthened"),
        "moon": ("Emotional", "Emotional sensitivity, mood fluctuations"),
    },
    2: {
        "themes": ["Finances, family, speech, values"],
        "jupiter": ("Favorable", "Financial growth, family harmony"),
        "saturn": ("Restrictive", "Financial caution needed, delayed income"),
        "mars": ("Active", "Aggressive speech, financial actions"),
        "venus": ("Enhancing", "Improved income, pleasant speech"),
    },
    3: {
        "themes": ["Communication, siblings, courage, skills"],
        "mercury": ("Favorable", "Enhanced communication, learning success"),
        "mars": ("Energizing", "Courageous actions, assertive communication"),
        "jupiter": ("Expanding", "New skills, supportive siblings"),
    },
    4: {
        "themes": ["Home, mother, property, emotional peace"],
        "moon": ("Empowering", "Emotional stability, mother's blessings"),
        "saturn": ("Heavy", "Responsibilities at home, property delays"),
        "venus": ("Harmonizing", "Domestic happiness, property gains"),
    },
    5: {
        "themes": ["Creativity, children, education, romance"],
        "jupiter": ("Very favorable", "Creative success, children's progress"),
        "venus": ("Romantic", "Romance flourishes, artistic expression"),
        "mercury": ("Intellectual", "Learning success, intelligent offspring"),
    },
    6: {
        "themes": ["Obstacles, enemies, health, service"],
        "saturn": ("Strengthening", "Overcomes enemies through persistence"),
        "mars": ("Combative", "Victory over opposition, health concerns"),
        "jupiter": ("Protective", "Reduces obstacles, health improvement"),
    },
    7: {
        "themes": ["Partnership, marriage, business, public"],
        "venus": ("Favorable", "Relationship harmony, business success"),
        "jupiter": ("Blessed", "Marriage prospects, partnership growth"),
        "saturn": ("Testing", "Relationship challenges, commitments"),
    },
    8: {
        "themes": ["Transformation, longevity, inheritance, occult"],
        "saturn": ("Transformative", "Deep changes, occult interests"),
        "mars": ("Intense", "Sudden changes, health vigilance"),
        "jupiter": ("Protective", "Reduces difficulties, inheritance gains"),
    },
    9: {
        "themes": ["Fortune, father, dharma, higher learning"],
        "jupiter": ("Most favorable", "Great fortune, spiritual growth"),
        "sun": ("Empowering", "Father's support, dharmic actions"),
        "mars": ("Activating", "Energy for dharma, distant travel"),
    },
    10: {
        "themes": ["Career, status, authority, public image"],
        "jupiter": ("Elevating", "Career advancement, recognition"),
        "saturn": ("Demanding", "Hard work pays off, authority increases"),
        "sun": ("Empowering", "Leadership roles, public recognition"),
    },
    11: {
        "themes": ["Gains, friends, aspirations, income"],
        "jupiter": ("Very favorable", "Income increases, goals achieved"),
        "venus": ("Beneficial", "Social pleasures, material gains"),
        "mercury": ("Networking", "Beneficial friendships, intellectual gains"),
    },
    12: {
        "themes": ["Loss, expenses, spirituality, foreign lands"],
        "jupiter": ("Spiritual", "Spiritual growth, beneficial expenses"),
        "saturn": ("Isolating", "Reduced activity, spiritual practices"),
        "venus": ("Pleasant", "Luxurious expenses, foreign pleasures"),
    },
}


def interpret_transit(
    planet: str,
    house: int,
    *,
    is_retrograde: bool = False,
) -> TransitInterpretation:
    """Generate interpretation for a transit.

    Args:
        planet: Transiting planet name.
        house: House number (1-12) where transit occurs.
        is_retrograde: Whether planet is retrograde.

    Returns:
        TransitInterpretation with themes and recommendations.

    """
    house_data = HOUSE_TRANSIT_THEMES.get(house, {})
    themes = house_data.get("themes", ["General life area"])

    planet_effect = house_data.get(planet.lower(), ("Neutral", "Standard transit effects apply"))
    base_impact, base_description = planet_effect

    # Adjust for retrograde
    if is_retrograde:
        base_description = f"Retrograde: {base_description} (review and revision period)"
        if "favorable" in base_impact.lower():
            impact = TransitImpact.NEUTRAL
        elif "challenging" in base_impact.lower():
            impact = TransitImpact.VERY_CHALLENGING
        else:
            impact = TransitImpact.NEUTRAL
    else:
        impact_map = {
            "very favorable": TransitImpact.VERY_FAVORABLE,
            "most favorable": TransitImpact.VERY_FAVORABLE,
            "favorable": TransitImpact.FAVORABLE,
            "challenging": TransitImpact.CHALLENGING,
            "neutral": TransitImpact.NEUTRAL,
        }
        impact = impact_map.get(base_impact.lower(), TransitImpact.NEUTRAL)

    # Determine duration based on planet
    duration_map = {
        "moon": TransitDuration.BRIEF,
        "sun": TransitDuration.BRIEF,
        "mercury": TransitDuration.SHORT,
        "venus": TransitDuration.SHORT,
        "mars": TransitDuration.MEDIUM,
        "jupiter": TransitDuration.LONG,
        "saturn": TransitDuration.EXTENDED,
        "rahu": TransitDuration.EXTENDED,
        "ketu": TransitDuration.EXTENDED,
    }
    duration = duration_map.get(planet.lower(), TransitDuration.MEDIUM)

    recommendations = _generate_recommendations(planet, house, impact)

    return TransitInterpretation(
        transiting_planet=planet,
        natal_house=house,
        natal_planet=None,
        impact=impact,
        duration=duration,
        description=base_description,
        themes=themes,
        recommendations=recommendations,
    )


def _generate_recommendations(planet: str, house: int, impact: TransitImpact) -> list[str]:
    """Generate recommendations based on transit."""
    recommendations = []

    if impact in (TransitImpact.VERY_FAVORABLE, TransitImpact.FAVORABLE):
        recommendations.append("Take initiative in related areas")
        recommendations.append("Make important decisions")
        if house in {1, 10}:
            recommendations.append("Start new projects or ventures")
    elif impact in (TransitImpact.CHALLENGING, TransitImpact.VERY_CHALLENGING):
        recommendations.append("Exercise patience and caution")
        recommendations.append("Avoid major decisions in this area")
        recommendations.append("Focus on maintaining rather than initiating")

    # Planet-specific recommendations
    if planet.lower() == "jupiter":
        recommendations.append("Pursue education and spiritual growth")
    elif planet.lower() == "saturn":
        recommendations.append("Embrace discipline and hard work")
    elif planet.lower() == "mars":
        recommendations.append("Channel energy productively")

    return recommendations


def analyze_transit_effects(
    transiting_planets: dict[str, int],
    *,
    retrograde_planets: list[str] | None = None,
) -> list[TransitEffect]:
    """Analyze effects of multiple transits.

    Args:
        transiting_planets: Dict of planet names to house numbers.
        retrograde_planets: List of retrograde planet names.

    Returns:
        List of TransitEffect for each planet.

    """
    if retrograde_planets is None:
        retrograde_planets = []

    effects: list[TransitEffect] = []

    for planet, house in transiting_planets.items():
        is_retro = planet in retrograde_planets
        interpretation = interpret_transit(planet, house, is_retrograde=is_retro)

        effect = TransitEffect(
            planet=planet,
            current_house=house,
            is_retrograde=is_retro,
            interpretations=[interpretation],
            overall_impact=interpretation.impact,
        )

        effects.append(effect)

    return effects
