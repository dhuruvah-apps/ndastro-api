"""Aspect strength calculation with orbs and weighted influences.

Provides detailed aspect analysis including orb-based strength modulation,
applying/separating aspects, and dignitary-adjusted influences.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class AspectType(str, Enum):
    """Standard Vedic aspects."""

    CONJUNCTION = "conjunction"
    OPPOSITION = "opposition"
    TRINE = "trine"
    SQUARE = "square"
    SEXTILE = "sextile"
    SEVENTH = "seventh"
    FOURTH_EIGHTH = "fourth_eighth"
    FIFTH_NINTH = "fifth_ninth"
    THIRD_TENTH = "third_tenth"


class AspectQuality(str, Enum):
    """Aspect influence quality."""

    BENEFIC = "benefic"
    NEUTRAL = "neutral"
    MALEFIC = "malefic"


# Standard aspect orbs (in degrees)
ASPECT_ORBS = {
    AspectType.CONJUNCTION: 10.0,
    AspectType.OPPOSITION: 8.0,
    AspectType.TRINE: 8.0,
    AspectType.SQUARE: 7.0,
    AspectType.SEVENTH: 8.0,
    AspectType.FOURTH_EIGHTH: 7.0,
    AspectType.FIFTH_NINTH: 8.0,
    AspectType.THIRD_TENTH: 6.0,
    AspectType.SEXTILE: 6.0,
}

# Aspect strength by planet (Graha Drishti)
SPECIAL_ASPECT_STRENGTHS = {
    "Mars": {7: 1.0, 4: 0.75, 8: 0.75},
    "Jupiter": {5: 1.0, 7: 1.0, 9: 1.0},
    "Saturn": {3: 1.0, 7: 1.0, 10: 1.0},
}

# Natural benefics and malefics
NATURAL_BENEFICS = ["Jupiter", "Venus", "Moon", "Mercury"]
NATURAL_MALEFICS = ["Saturn", "Mars", "Sun", "Rahu", "Ketu"]

MIN_ORB_STRENGTH = 0.1
MAX_ORB_STRENGTH = 1.0
FULL_CIRCLE = 360.0
HALF_CIRCLE = 180.0


@dataclass
class AspectDetails:
    """Detailed aspect information between two planets."""

    aspecting_planet: str
    aspected_planet: str
    aspect_type: AspectType
    orb: float
    max_orb: float
    orb_strength: float
    base_strength: float
    total_strength: float
    is_applying: bool
    quality: AspectQuality
    house_distance: int
    aspecting_longitude: float
    aspected_longitude: float


@dataclass
class AspectStrengthReport:
    """Complete aspect analysis for a chart."""

    aspects: list[AspectDetails]
    strongest_aspects: list[AspectDetails]
    benefic_aspects: list[AspectDetails]
    malefic_aspects: list[AspectDetails]


def _normalize_angle(angle: float) -> float:
    """Normalize angle to [0, 360)."""
    normalized = angle % FULL_CIRCLE
    return normalized if normalized >= 0 else normalized + FULL_CIRCLE


def _angular_distance(lon1: float, lon2: float) -> float:
    """Calculate shortest angular distance between two longitudes."""
    diff = abs(_normalize_angle(lon2) - _normalize_angle(lon1))
    return diff if diff <= HALF_CIRCLE else FULL_CIRCLE - diff


def _get_aspect_type_and_orb(
    house_distance: int,
    angular_distance: float,
) -> tuple[AspectType | None, float]:
    """Determine aspect type and orb based on house distance and angular separation."""
    aspect_configs = [
        (AspectType.CONJUNCTION, [1], 0.0),
        (AspectType.SEVENTH, [7], 180.0),
        (AspectType.FOURTH_EIGHTH, [4, 8], [90.0, 270.0]),
        (AspectType.FIFTH_NINTH, [5, 9], [120.0, 240.0]),
        (AspectType.TRINE, [5, 9], [120.0, 240.0]),
        (AspectType.SQUARE, [4, 10], [90.0, 270.0]),
        (AspectType.THIRD_TENTH, [3, 11], [60.0, 300.0]),
        (AspectType.SEXTILE, [3, 11], [60.0, 300.0]),
        (AspectType.OPPOSITION, [7], 180.0),
    ]

    for aspect_type, valid_houses, expected_angles in aspect_configs:
        if house_distance not in valid_houses:
            continue

        expected = expected_angles if isinstance(expected_angles, list) else [expected_angles]
        for angle in expected:
            orb = abs(angular_distance - angle)
            max_orb = ASPECT_ORBS.get(aspect_type, 8.0)
            if orb <= max_orb:
                return aspect_type, orb

    return None, 0.0


def _calculate_orb_strength(orb: float, max_orb: float) -> float:
    """Calculate strength modifier based on orb (1.0 exact, diminishes with distance)."""
    if max_orb <= 0:
        return MAX_ORB_STRENGTH
    ratio = orb / max_orb
    strength = MAX_ORB_STRENGTH - (ratio * (MAX_ORB_STRENGTH - MIN_ORB_STRENGTH))
    return max(MIN_ORB_STRENGTH, min(MAX_ORB_STRENGTH, strength))


def _get_base_strength(
    aspecting_planet: str,
    house_distance: int,
) -> float:
    """Get base strength for an aspect (considers special aspects)."""
    special = SPECIAL_ASPECT_STRENGTHS.get(aspecting_planet, {})
    return special.get(house_distance, 1.0)


def _get_aspect_quality(aspecting_planet: str) -> AspectQuality:
    """Determine if aspect is benefic or malefic based on planet nature."""
    if aspecting_planet in NATURAL_BENEFICS:
        return AspectQuality.BENEFIC
    if aspecting_planet in NATURAL_MALEFICS:
        return AspectQuality.MALEFIC
    return AspectQuality.NEUTRAL


def _is_applying_aspect(
    aspecting_lon: float,
    aspected_lon: float,
    aspecting_speed: float,
) -> bool:
    """Check if aspect is applying (getting closer) or separating."""
    # Positive speed means planet is moving forward
    # Aspect is applying if aspecting planet is behind and catching up
    if aspecting_speed <= 0:
        return False  # Retrograde simplification

    normalized_aspecting = _normalize_angle(aspecting_lon)
    normalized_aspected = _normalize_angle(aspected_lon)

    if normalized_aspecting < normalized_aspected:
        return aspecting_speed > 0
    return aspecting_speed < 0


def _house_distance(lon1: float, lon2: float) -> int:
    """Calculate house distance between two longitudes (1-12)."""
    rasi1 = int(_normalize_angle(lon1) / 30.0) + 1
    rasi2 = int(_normalize_angle(lon2) / 30.0) + 1

    distance = rasi2 - rasi1
    if distance < 0:
        distance += 12
    return distance if distance > 0 else 12


def calculate_aspects_with_strength(
    planet_longitudes: dict[str, float],
    *,
    planet_speeds: dict[str, float] | None = None,
    min_strength_threshold: float = 0.3,
) -> AspectStrengthReport:
    """Calculate detailed aspect strengths between all planets.

    Args:
        planet_longitudes: Sidereal longitudes [0, 360) for each planet.
        planet_speeds: Optional daily motion in degrees (for applying/separating).
        min_strength_threshold: Minimum total strength to include in report.

    Returns:
        AspectStrengthReport with detailed aspect analysis.

    """
    aspects: list[AspectDetails] = []

    if planet_speeds is None:
        planet_speeds = {}

    planets = list(planet_longitudes.keys())

    for i, planet1 in enumerate(planets):
        lon1 = planet_longitudes[planet1]
        speed1 = planet_speeds.get(planet1, 1.0)

        for planet2 in planets[i + 1 :]:
            lon2 = planet_longitudes[planet2]

            angular_dist = _angular_distance(lon1, lon2)
            house_dist = _house_distance(lon1, lon2)

            aspect_type, orb = _get_aspect_type_and_orb(house_dist, angular_dist)
            if not aspect_type:
                continue

            max_orb = ASPECT_ORBS.get(aspect_type, 8.0)
            orb_strength = _calculate_orb_strength(orb, max_orb)
            base_strength = _get_base_strength(planet1, house_dist)
            total_strength = base_strength * orb_strength

            if total_strength < min_strength_threshold:
                continue

            is_applying = _is_applying_aspect(lon1, lon2, speed1)
            quality = _get_aspect_quality(planet1)

            aspect = AspectDetails(
                aspecting_planet=planet1,
                aspected_planet=planet2,
                aspect_type=aspect_type,
                orb=orb,
                max_orb=max_orb,
                orb_strength=orb_strength,
                base_strength=base_strength,
                total_strength=total_strength,
                is_applying=is_applying,
                quality=quality,
                house_distance=house_dist,
                aspecting_longitude=lon1,
                aspected_longitude=lon2,
            )

            aspects.append(aspect)

    # Sort and categorize aspects
    strongest = sorted(aspects, key=lambda a: a.total_strength, reverse=True)[:5]
    benefic = [a for a in aspects if a.quality == AspectQuality.BENEFIC]
    malefic = [a for a in aspects if a.quality == AspectQuality.MALEFIC]

    return AspectStrengthReport(
        aspects=aspects,
        strongest_aspects=strongest,
        benefic_aspects=benefic,
        malefic_aspects=malefic,
    )


def get_planet_aspects(
    report: AspectStrengthReport,
    planet: str,
) -> Sequence[AspectDetails]:
    """Get all aspects involving a specific planet."""
    return [a for a in report.aspects if planet in (a.aspecting_planet, a.aspected_planet)]


def get_applying_aspects(report: AspectStrengthReport) -> Sequence[AspectDetails]:
    """Get all applying (exact-bound) aspects."""
    return [a for a in report.aspects if a.is_applying]
