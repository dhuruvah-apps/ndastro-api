"""Ashtakavarga (8-point strength) calculation utility.

Implements the Ashtakavarga system - a planetary support/opposition analysis.
Determines which houses receive planetary strength and which are afflicted.

Two types:
1. Sarva Ashtakavarga (SAV) - Comprehensive strength of all 12 houses
2. Bhinna Ashtakavarga (BAV) - Individual planet strength maps

Each planet owns 8 houses and contributes 0-8 points per house based on:
- Its own position (exaltation, own sign, etc.)
- Other planets' aspects and conjunctions
- Benefic/malefic relationships
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# Constants
RASI_COUNT = 12
HOUSES_PER_PLANET = 8
MAX_AVG_POINTS = 8  # Maximum points per house per planet
STRONG_HOUSE_THRESHOLD = 30  # 30+ points = strong
WEAK_HOUSE_THRESHOLD = 20  # <20 points = weak
VERY_STRONG_THRESHOLD = 40
MODERATE_HOUSE_THRESHOLD = 20
WEAK_POINTS_THRESHOLD = 10
AVG_VERY_STRONG_THRESHOLD = 6
AVG_STRONG_THRESHOLD = 5
AVG_MODERATE_THRESHOLD = 3


class AshtakavargaStrength(str, Enum):
    """Strength classification for houses."""

    VERY_STRONG = "very_strong"  # 40+ points
    STRONG = "strong"  # 30-39 points
    MODERATE = "moderate"  # 20-29 points
    WEAK = "weak"  # 10-19 points
    VERY_WEAK = "very_weak"  # <10 points


def _apply_aspect_and_conjunction_points(
    house_points: int,
    aspecting: list[str],
    conjunct: list[str],
) -> int:
    """Apply points from aspects and conjunctions."""
    adjusted = house_points

    for aspecting_planet in aspecting:
        if aspecting_planet in BENEFIC_PLANETS:
            adjusted += 1
        elif aspecting_planet in MALEFIC_PLANETS:
            adjusted = max(0, adjusted - 1)

    for conjunct_planet in conjunct:
        if conjunct_planet in BENEFIC_PLANETS:
            adjusted += 1
        elif conjunct_planet in MALEFIC_PLANETS:
            adjusted = max(0, adjusted - 1)

    return adjusted


def _apply_dignity_points(
    house_points: int,
    planet: str,
    context: AshtakavargaContext,
) -> int:
    """Apply exaltation/own rasi/debilitation modifiers."""
    adjusted = house_points

    if context.exalted_planets and planet in context.exalted_planets:
        adjusted += 1

    if context.own_rasi_planets and planet in context.own_rasi_planets:
        adjusted += 1

    if context.debilitated_planets and planet in context.debilitated_planets:
        adjusted = max(0, adjusted - 2)

    return adjusted


# Planet houses (which 8 houses each planet rules in SAV)
# Based on classical Parasara system
PLANET_HOUSES = {
    "sun": {1, 2, 3, 5, 6, 8, 10, 11},
    "moon": {1, 2, 3, 4, 6, 8, 9, 12},
    "mars": {1, 2, 3, 6, 8, 10, 11, 12},
    "mercury": {1, 2, 4, 5, 7, 8, 9, 10},
    "jupiter": {2, 5, 7, 9, 10, 11, 12},  # 7 houses, completing with Sun
    "venus": {1, 2, 3, 4, 5, 7, 9, 11},
    "saturn": {3, 6, 8, 10, 11, 12},  # 6 houses
    "rahu": {1, 2, 4, 5, 7, 8, 10},  # 7 houses
    "kethu": {3, 6, 9, 10, 11, 12},  # 6 houses
}

# Benefic and malefic planets for SAV
BENEFIC_PLANETS = {"jupiter", "venus", "mercury", "moon"}
MALEFIC_PLANETS = {"mars", "saturn", "sun", "rahu", "kethu"}


@dataclass
class BhinnaAshtakavarga:
    """Bhinna Ashtakavarga: Individual planet's strength map."""

    planet: str
    points_per_house: dict[int, int] = field(default_factory=dict)  # {house: points}
    total_points: int = 0
    average_per_house: float = 0.0


@dataclass
class SarvaAshtakavarga:
    """Sarva Ashtakavarga: Overall strength of all houses."""

    points_per_house: dict[int, int] = field(default_factory=dict)  # {house: total_points}
    bhinna_maps: dict[str, BhinnaAshtakavarga] = field(default_factory=dict)
    strong_houses: list[int] = field(default_factory=list)  # 30+ points
    weak_houses: list[int] = field(default_factory=list)  # <20 points
    moderate_houses: list[int] = field(default_factory=list)  # 20-29 points


@dataclass
class AshtakavargaContext:
    """Context for Ashtakavarga calculations."""

    planets_in_houses: dict[str, int]  # {planet: house_number}
    planets_in_rasis: dict[str, str]  # {planet: rasi_name}
    aspecting_planets: dict[str, list[str]]  # {planet: [aspecting_planets]}
    conjunct_planets: dict[str, list[str]]  # {planet: [conjunct_planets]}
    exalted_planets: list[str] | None = None
    own_rasi_planets: list[str] | None = None
    debilitated_planets: list[str] | None = None


def _calculate_planet_ashtakavarga(
    planet: str,
    context: AshtakavargaContext,
) -> BhinnaAshtakavarga:
    """Calculate Bhinna Ashtakavarga for a single planet.

    Args:
        planet: Planet name
        context: AshtakavargaContext with placement details

    Returns:
        BhinnaAshtakavarga with point distribution

    """
    points_per_house: dict[int, int] = {}

    # Get the houses ruled by this planet
    ruled_houses = PLANET_HOUSES.get(planet, set())

    for house in range(1, RASI_COUNT + 1):
        house_points = 0

        # If planet owns this house, it examines it
        if house not in ruled_houses:
            points_per_house[house] = 0
            continue

        if context.planets_in_houses.get(planet) == house:
            house_points += 1

        aspecting = context.aspecting_planets.get(planet, [])
        conjunct = context.conjunct_planets.get(planet, [])

        house_points = _apply_aspect_and_conjunction_points(
            house_points,
            aspecting,
            conjunct,
        )
        house_points = _apply_dignity_points(house_points, planet, context)

        # Cap at maximum
        house_points = min(house_points, MAX_AVG_POINTS)
        points_per_house[house] = house_points

    total_points = sum(points_per_house.values())
    avg = total_points / len(ruled_houses) if ruled_houses else 0.0

    return BhinnaAshtakavarga(
        planet=planet,
        points_per_house=points_per_house,
        total_points=total_points,
        average_per_house=avg,
    )


def calculate_sarva_ashtakavarga(
    context: AshtakavargaContext,
) -> SarvaAshtakavarga:
    """Calculate Sarva Ashtakavarga (overall house strength).

    Args:
        context: AshtakavargaContext with planet placements

    Returns:
        SarvaAshtakavarga with comprehensive strength analysis

    """
    sav = SarvaAshtakavarga()

    # 1. Calculate Bhinna Ashtakavarga for each planet
    planets = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "kethu"]

    for planet in planets:
        bhinna = _calculate_planet_ashtakavarga(planet, context)
        sav.bhinna_maps[planet] = bhinna

    # 2. Sum points for each house from all planets
    for house in range(1, RASI_COUNT + 1):
        house_total = 0

        for bhinna in sav.bhinna_maps.values():
            house_total += bhinna.points_per_house.get(house, 0)

        sav.points_per_house[house] = house_total

    # 3. Classify houses by strength
    for house, points in sav.points_per_house.items():
        if points >= STRONG_HOUSE_THRESHOLD:
            sav.strong_houses.append(house)
        elif points < WEAK_HOUSE_THRESHOLD:
            sav.weak_houses.append(house)
        else:
            sav.moderate_houses.append(house)

    sav.strong_houses.sort()
    sav.weak_houses.sort()
    sav.moderate_houses.sort()

    return sav


def get_house_strength_classification(points: int) -> AshtakavargaStrength:
    """Classify house strength by point total.

    Args:
        points: Total Ashtakavarga points for the house

    Returns:
        AshtakavargaStrength classification

    """
    if points >= VERY_STRONG_THRESHOLD:
        return AshtakavargaStrength.VERY_STRONG
    if points >= STRONG_HOUSE_THRESHOLD:
        return AshtakavargaStrength.STRONG
    if points >= MODERATE_HOUSE_THRESHOLD:
        return AshtakavargaStrength.MODERATE
    if points >= WEAK_POINTS_THRESHOLD:
        return AshtakavargaStrength.WEAK
    return AshtakavargaStrength.VERY_WEAK


def get_ashtakavarga_interpretation(
    house: int,
    points: int,
    strength: AshtakavargaStrength,
) -> str:
    """Get interpretation of Ashtakavarga for a house.

    Args:
        house: House number (1-12)
        points: Total Ashtakavarga points
        strength: Strength classification

    Returns:
        Interpretation string

    """
    house_meanings = {
        1: "Self, appearance, personality, vitality",
        2: "Wealth, family, speech, food",
        3: "Siblings, courage, communication, short journeys",
        4: "Mother, home, property, peace of mind",
        5: "Children, creativity, intellect, romance",
        6: "Enemies, debts, health issues, service",
        7: "Spouse, partnerships, business, relationships",
        8: "Longevity, inheritance, secrets, transformation",
        9: "Father, luck, philosophy, long journeys, religion",
        10: "Career, reputation, status, authority",
        11: "Income, gains, friendships, aspirations",
        12: "Losses, expenses, isolation, liberation",
    }

    meaning = house_meanings.get(house, f"House {house}")

    strength_descriptions = {
        AshtakavargaStrength.VERY_STRONG: f"EXCELLENT support ({points} pts). {meaning} will flourish.",
        AshtakavargaStrength.STRONG: f"Good support ({points} pts). {meaning} will succeed with effort.",
        AshtakavargaStrength.MODERATE: f"Fair support ({points} pts). {meaning} will have mixed results.",
        AshtakavargaStrength.WEAK: f"Low support ({points} pts). {meaning} faces challenges.",
        AshtakavargaStrength.VERY_WEAK: f"Very poor support ({points} pts). {meaning} highly afflicted.",
    }

    return strength_descriptions.get(strength, f"House {house}: {points} points")


def get_bhinna_planet_interpretation(
    planet: str,
    points: list[int],
) -> str:
    """Get interpretation of a planet's Bhinna Ashtakavarga.

    Args:
        planet: Planet name
        points: List of points for each house (8 values)

    Returns:
        Interpretation string

    """
    total = sum(points)
    avg = total / len(points) if points else 0

    if avg >= AVG_VERY_STRONG_THRESHOLD:
        strength = "Very strong"
    elif avg >= AVG_STRONG_THRESHOLD:
        strength = "Strong"
    elif avg >= AVG_MODERATE_THRESHOLD:
        strength = "Moderate"
    else:
        strength = "Weak"

    return f"{planet.upper()} Ashtakavarga: {strength} ({total} total pts, avg {avg:.1f}/8)"


def get_strong_houses_for_activities(sav: SarvaAshtakavarga) -> dict[str, list[int]]:
    """Get optimal houses for various activities based on SAV.

    Args:
        sav: SarvaAshtakavarga with strength analysis

    Returns:
        Dictionary mapping activity to favorable houses

    """
    strong = sav.strong_houses
    moderate = sav.moderate_houses

    favorable = strong if strong else moderate

    return {
        "business_ventures": [h for h in favorable if h in {1, 5, 10, 11}],
        "marriage_events": [h for h in favorable if h in {2, 7}],
        "buying_property": [h for h in favorable if h in {4}],
        "education": [h for h in favorable if h in {3, 5, 9}],
        "health_matters": [h for h in favorable if h not in {6, 8, 12}],
        "spiritual_pursuits": [h for h in favorable if h in {8, 9, 12}],
    }
