"""Shadbala (Six Strengths) calculation utility.

Implements the classical Vedic method to calculate planetary strength
across six dimensions: Sthana, Dig, Kala, Paksha, Chesta, and Drishti.
"""

from __future__ import annotations

from dataclasses import dataclass

from ndastro_api.core.utils.data_loader import astro_data

# Maximum Shadbala points (in Virupas, where 60 Virupas = 1 Rupa)
MAX_STHANA_BALA = 30.0
MAX_DIG_BALA = 15.0
MAX_KALA_BALA = 15.0
MAX_PAKSHA_BALA = 15.0
MAX_CHESTA_BALA = 15.0
MAX_DRISHTI_BALA = 15.0
MAX_SHADBALA = 90.0
HALF_LUNAR_CYCLE = 90.0


@dataclass
class ShadbalaPlanetContext:
    """Context for shadbala calculation."""

    planet_code: str
    rasi_number: int
    house_number: int
    is_retrograde: bool  # type: ignore[misc]
    is_night: bool  # type: ignore[misc]
    moon_phase: float
    avg_speed: float
    aspecting_planets: list[tuple[str, bool]] | None = None


def _get_sign_strength(planet_code: str, rasi_name: str, rasi_ruler: str) -> float:
    """Get sign strength for a planet in a specific rasi."""
    planet = astro_data.get_planet_by_code(planet_code)
    if not planet:
        return 0.0

    # Check sign positions in priority order
    sign_strength_map = [
        (rasi_name in planet.own_signs, 30.0),
        (planet.exaltation and rasi_name == planet.exaltation.sign, 25.0),
        (planet.moolatrikona and rasi_name == planet.moolatrikona.sign, 20.0),
        (planet.debilitation and rasi_name == planet.debilitation.sign, 0.0),
    ]
    for condition, strength in sign_strength_map:
        if condition:
            return strength

    # Check ruler relationships
    ruler_strength_map = [
        (rasi_ruler in planet.natural_friends, 15.0),
        (rasi_ruler in planet.natural_neutrals, 5.0),
        (rasi_ruler in planet.natural_enemies, 0.0),
    ]
    for condition, strength in ruler_strength_map:
        if condition:
            return strength
    return 5.0


def calculate_sthana_bala(
    planet_code: str,
    rasi_number: int,
    *,
    retrograde: bool,
) -> float:
    """Calculate Sthana Bala (Positional Strength).

    Strength based on planet's sign position and rulership.

    Args:
        planet_code: Planet code (e.g., 'sun', 'mercury')
        rasi_number: Rasi number (1-12, Aries=1 to Pisces=12)
        retrograde: Whether planet is retrograde

    Returns:
        Sthana Bala points (0-30)

    """
    rasi = astro_data.get_rasi_by_number(rasi_number)
    if not rasi:
        return 0.0

    bala = _get_sign_strength(planet_code, rasi.name, rasi.ruler)

    # Retrograde reduces Sthana Bala by 10%
    if retrograde and planet_code not in ["rahu", "kethu"]:
        bala *= 0.9

    return max(0.0, bala)


def calculate_dig_bala(planet_code: str, house_number: int) -> float:
    """Calculate Dig Bala (Directional Strength).

    Strength based on favourable house positions.

    Args:
        planet_code: Planet code
        house_number: House number (1-12)

    Returns:
        Dig Bala points (0-15)

    """
    if planet_code not in ["sun", "moon", "mercury", "venus", "mars barycenter", "jupiter barycenter", "saturn barycenter"]:
        return 0.0

    # Directional strength by house
    # Sun strongest in 10th (Leo natural house = South)
    # Mars strongest in 10th (South)
    # Jupiter strongest in 1st (East)
    # Mercury strongest in 1st (East)
    # Venus strongest in 4th (West)
    # Moon strongest in 4th (West)
    # Saturn strongest in 7th (West)

    dig_strength = {
        "sun": {10: 15.0, 7: 14.0, 4: 8.0, 1: 0.0},
        "moon": {4: 15.0, 1: 14.0, 10: 8.0, 7: 0.0},
        "mercury": {1: 15.0, 10: 14.0, 4: 8.0, 7: 0.0},
        "venus": {4: 15.0, 1: 14.0, 7: 8.0, 10: 0.0},
        "mars barycenter": {10: 15.0, 1: 14.0, 4: 8.0, 7: 0.0},
        "jupiter barycenter": {1: 15.0, 4: 14.0, 10: 8.0, 7: 0.0},
        "saturn barycenter": {7: 15.0, 4: 14.0, 1: 8.0, 10: 0.0},
    }

    strength_map = dig_strength.get(planet_code, {})
    return float(strength_map.get(house_number, 0.0))


def calculate_kala_bala(planet_code: str, *, night: bool) -> float:
    """Calculate Kala Bala (Temporal Strength).

    Strength based on day/night rulership.

    Args:
        planet_code: Planet code
        night: True if birth time is at night

    Returns:
        Kala Bala points (0-15)

    """
    # Diurnal planets (stronger during day)
    diurnal_planets = ["sun", "mars barycenter", "jupiter barycenter"]
    # Nocturnal planets (stronger at night)
    nocturnal_planets = ["moon", "venus", "mercury"]

    if planet_code in diurnal_planets:
        return 0.0 if night else 15.0
    if planet_code in nocturnal_planets:
        return 15.0 if night else 0.0
    if planet_code == "saturn barycenter":
        return 7.5
    return 0.0


def calculate_paksha_bala(planet_code: str, moon_phase: float) -> float:
    """Calculate Paksha Bala (Lunar Fortnight Strength).

    Strength based on Moon's waxing/waning phase.

    Args:
        planet_code: Planet code
        moon_phase: Moon phase (0-180 degrees, where 0-90 is waxing, 90-180 is waning)

    Returns:
        Paksha Bala points (0-15)

    """
    # Benefics stronger during waxing phase (bright fortnight)
    benefics = ["mercury", "jupiter barycenter", "venus", "moon"]
    # Malefics stronger during waning phase (dark fortnight)
    malefics = ["sun", "mars barycenter", "saturn barycenter"]

    is_waxing = moon_phase < HALF_LUNAR_CYCLE

    if planet_code in benefics:
        return 15.0 if is_waxing else 0.0
    if planet_code in malefics:
        return 15.0 if not is_waxing else 0.0
    return 0.0


def calculate_chesta_bala(
    planet_code: str,
    *,
    retrograde: bool,
    avg_speed: float,
) -> float:
    """Calculate Chesta Bala (Motional Strength).

    Strength based on planet's speed relative to average.

    Args:
        planet_code: Planet code
        retrograde: Whether planet is retrograde
        avg_speed: Average daily speed in degrees

    Returns:
        Chesta Bala points (0-15)

    """
    if retrograde or planet_code in ["rahu", "kethu"]:
        return 0.0

    # Simplified: faster planets have higher chesta bala
    avg_speeds = {
        "sun": 1.0,
        "moon": 13.0,
        "mercury": 1.0,
        "venus": 1.0,
        "mars barycenter": 0.5,
        "jupiter barycenter": 0.08,
        "saturn barycenter": 0.03,
    }

    base_speed = avg_speeds.get(planet_code, 1.0)
    if avg_speed >= base_speed * 0.95:
        return 15.0
    if avg_speed >= base_speed * 0.85:
        return 10.0
    return 5.0


def calculate_drishti_bala(
    other_planets: list[tuple[str, bool]],
) -> float:
    """Calculate Drishti Bala (Aspect Strength).

    Strength gained/lost from other planet aspects.

    Args:
        other_planets: List of (planet_code, is_benefic) tuples

    Returns:
        Drishti Bala points (0-15, can be negative)

    """
    bala = 0.0

    for _other_code, is_benefic in other_planets:
        # Simplified: benefic aspects add strength, malefic subtract
        if is_benefic:
            bala += 2.5
        else:
            bala -= 2.5

    return max(-7.5, min(15.0, bala))


def calculate_shadbala(context: ShadbalaPlanetContext) -> dict[str, float]:
    """Calculate complete Shadbala (Six Strengths) for a planet.

    Args:
        context: ShadbalaPlanetContext containing planet and contextual data

    Returns:
        Dictionary with individual balas and total shadbala

    """
    aspecting_planets = context.aspecting_planets if context.aspecting_planets else []

    sthana = calculate_sthana_bala(context.planet_code, context.rasi_number, retrograde=context.is_retrograde)
    dig = calculate_dig_bala(context.planet_code, context.house_number)
    kala = calculate_kala_bala(context.planet_code, night=context.is_night)
    paksha = calculate_paksha_bala(context.planet_code, context.moon_phase)
    chesta = calculate_chesta_bala(context.planet_code, retrograde=context.is_retrograde, avg_speed=context.avg_speed)
    drishti = calculate_drishti_bala(aspecting_planets)

    total = sthana + dig + kala + paksha + chesta + drishti

    return {
        "sthana_bala": max(0.0, sthana),
        "dig_bala": max(0.0, dig),
        "kala_bala": max(0.0, kala),
        "paksha_bala": max(0.0, paksha),
        "chesta_bala": max(0.0, chesta),
        "drishti_bala": max(-15.0, drishti),
        "total_shadbala": max(0.0, total),
        "shadbala_percentage": (max(0.0, total) / MAX_SHADBALA) * 100.0,
    }
