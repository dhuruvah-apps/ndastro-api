"""Vimsottari Dasa calculation utility.

Implements Vimsottari Dasa - the primary predictive timing system in Vedic astrology.
Divides the 120-year life span into 9 periods corresponding to planets (including nodes).

Structure:
- Maha Dasa (major periods): 9 planets x varying years = 120 years total
- Bhukti Dasa (sub-periods): Each major period subdivided among 9 planets
- Antara Dasa (minor periods): Each sub-period subdivided among 9 planets
- Pratyantara Dasa (finest periods): Further subdivision
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date

# Constants
NAKSHATRA_COUNT = 27
PLANET_COUNT = 9

# Vimsottari Dasa planet periods (in years)
# Total = 120 years
DASA_YEARS = {
    "sun": 6,
    "moon": 10,
    "mars": 7,
    "mercury": 17,
    "jupiter": 16,
    "venus": 20,
    "saturn": 19,
    "rahu": 18,
    "kethu": 7,
}

# Order of planets in dasa sequence
DASA_SEQUENCE = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "kethu"]

# Total dasa cycle
TOTAL_DASA_YEARS = 120

# Nakshatras and their ruling planets
NAKSHATRA_RULERS = {
    1: "kethu",  # Aswini
    2: "venus",  # Bharani
    3: "sun",  # Krittika
    4: "moon",  # Rohini
    5: "mars",  # Mrigashira
    6: "mercury",  # Ardra
    7: "jupiter",  # Punarvasu
    8: "saturn",  # Pushya
    9: "mercury",  # Aslesha
    10: "venus",  # Magha
    11: "sun",  # Purva Phalguni
    12: "moon",  # Uttara Phalguni
    13: "mars",  # Hasta
    14: "mercury",  # Chitra
    15: "jupiter",  # Svati
    16: "saturn",  # Vishakha
    17: "venus",  # Anuradha
    18: "sun",  # Jyeshtha
    19: "moon",  # Mula
    20: "mars",  # Purva Ashadha
    21: "mercury",  # Uttara Ashadha
    22: "jupiter",  # Abhijit
    23: "saturn",  # Sravana
    24: "venus",  # Dhanistha
    25: "sun",  # Shatabhisha
    26: "moon",  # Purva Bhadrapada
    27: "mars",  # Uttara Bhadrapada
    28: "mercury",  # Revati
}


class DasaLevel(str, Enum):
    """Level of dasa subdivision."""

    MAHA = "maha"  # Major period (largest)
    BHUKTI = "bhukti"  # Sub-period
    ANTARA = "antara"  # Minor period
    PRATYANTARA = "pratyantara"  # Finest subdivision


@dataclass
class DasaPeriod:
    """Single dasa period with start/end dates and ruling planet."""

    level: DasaLevel
    planet: str  # Ruling planet
    duration_years: float  # Full period duration in years
    start_date: date
    end_date: date
    percentage_complete: float = 0.0  # 0-100% of the period that has elapsed


@dataclass
class VimsottariDasaContext:
    """Context for Vimsottari Dasa calculations."""

    birth_date: datetime
    birth_nakshatra: int  # 1-27, or fractional for precise position
    nakshatra_pada: float  # 0.0-4.0 (quarter of nakshatra)
    is_child: bool = False  # Is native a child at current date?


def get_nakshatra_ruler(nakshatra_number: int) -> str:
    """Get the ruling planet for a nakshatra.

    Args:
        nakshatra_number: Nakshatra number (1-27)

    Returns:
        Planet name that rules this nakshatra

    """
    # Constrain to valid range
    constrained_number = max(1, min(nakshatra_number, NAKSHATRA_COUNT))
    return NAKSHATRA_RULERS.get(constrained_number, "sun")


def calculate_dasa_start_planet_and_fraction(nakshatra_number: int, nakshatra_pada: float) -> tuple[str, float]:
    """Calculate starting dasa planet and fraction based on birth nakshatra.

    Args:
        nakshatra_number: Birth nakshatra (1-27)
        nakshatra_pada: Quarter within nakshatra (0.0-4.0)

    Returns:
        Tuple of (starting_planet, fraction_of_dasa_completed)

    """
    ruler = get_nakshatra_ruler(nakshatra_number)

    # Calculate fraction: nakshatra pada (0-4) / 4 * planet_years / total_years
    # More precise: position in nakshatra determines starting point in planet's dasa
    fraction_in_nakshatra = nakshatra_pada / 4.0
    planet_years = DASA_YEARS[ruler]
    fraction_of_dasa = fraction_in_nakshatra * (planet_years / TOTAL_DASA_YEARS)

    return ruler, fraction_of_dasa


def calculate_current_dasa_period(birth_date: datetime, current_date: datetime, birth_nakshatra: int) -> DasaPeriod:
    """Calculate current Maha Dasa period for a given date.

    Args:
        birth_date: Native's birth date
        current_date: Date to calculate dasa for
        birth_nakshatra: Birth nakshatra (1-27)

    Returns:
        DasaPeriod showing current Maha Dasa

    """
    starting_planet, fraction_in_dasa = calculate_dasa_start_planet_and_fraction(
        birth_nakshatra,
        2.0,  # Assuming mid-nakshatra for now
    )

    # Calculate time elapsed
    days_elapsed = (current_date.date() - birth_date.date()).days
    years_elapsed = days_elapsed / 365.25

    # Account for fraction already in dasa at birth
    dasa_period_length = DASA_YEARS[starting_planet]
    years_into_first_dasa = fraction_in_dasa * dasa_period_length
    total_years_from_start = years_into_first_dasa + years_elapsed

    # Which dasa are we in?
    cumulative_years = 0.0
    dasa_start_index = DASA_SEQUENCE.index(starting_planet)

    for i in range(PLANET_COUNT):  # Cycle through all 9 planets
        planet_idx = (dasa_start_index + i) % 9
        planet = DASA_SEQUENCE[planet_idx]
        planet_duration = DASA_YEARS[planet]

        if cumulative_years + planet_duration > total_years_from_start:
            # This is our current dasa
            current_dasa_planet = planet
            years_into_dasa = total_years_from_start - cumulative_years
            percentage = (years_into_dasa / planet_duration) * 100

            # Calculate start and end dates for this dasa
            dasa_start = birth_date + timedelta(days=cumulative_years * 365.25)
            dasa_end = dasa_start + timedelta(days=planet_duration * 365.25)

            return DasaPeriod(
                level=DasaLevel.MAHA,
                planet=current_dasa_planet,
                duration_years=planet_duration,
                start_date=dasa_start.date(),
                end_date=dasa_end.date(),
                percentage_complete=percentage,
            )

        cumulative_years += planet_duration

    # Fallback (shouldn't reach here)
    return DasaPeriod(
        level=DasaLevel.MAHA,
        planet=starting_planet,
        duration_years=DASA_YEARS[starting_planet],
        start_date=birth_date.date(),
        end_date=(birth_date + timedelta(days=365.25 * DASA_YEARS[starting_planet])).date(),
    )


def get_dasa_sequence_from_planet(planet: str, levels: int = 1) -> list[tuple[str, float]]:
    """Get dasa sequence starting from a given planet.

    Args:
        planet: Starting planet name
        levels: How many planets in sequence to return (1-9)

    Returns:
        List of (planet, years) tuples in dasa sequence

    """
    if planet not in DASA_SEQUENCE:
        return []

    start_idx = DASA_SEQUENCE.index(planet)
    sequence = []

    for i in range(min(levels, PLANET_COUNT)):
        idx = (start_idx + i) % PLANET_COUNT
        p = DASA_SEQUENCE[idx]
        sequence.append((p, DASA_YEARS[p]))

    return sequence


def calculate_dasa_change_dates(birth_date: datetime, birth_nakshatra: int, future_years: int = 10) -> list[dict]:
    """Calculate all major dasa change dates from birth forward.

    Args:
        birth_date: Native's birth date
        birth_nakshatra: Birth nakshatra (1-27)
        future_years: How many years into the future to calculate

    Returns:
        List of dicts with dasa change information

    """
    starting_planet, fraction_in_dasa = calculate_dasa_start_planet_and_fraction(birth_nakshatra, 2.0)

    start_idx = DASA_SEQUENCE.index(starting_planet)
    first_dasa_duration = DASA_YEARS[starting_planet] * (1 - fraction_in_dasa)

    changes = []
    cumulative_years = first_dasa_duration

    changes.append(
        {
            "planet": starting_planet,
            "start_date": birth_date.date(),
            "duration_years": first_dasa_duration,
            "end_date": (birth_date + timedelta(days=first_dasa_duration * 365.25)).date(),
            "order": 0,
        }
    )

    for i in range(1, PLANET_COUNT):
        idx = (start_idx + i) % 9
        planet = DASA_SEQUENCE[idx]
        duration = DASA_YEARS[planet]

        dasa_start = birth_date + timedelta(days=cumulative_years * 365.25)
        dasa_end = dasa_start + timedelta(days=duration * 365.25)

        if cumulative_years > future_years * 365.25:
            break

        changes.append(
            {
                "planet": planet,
                "start_date": dasa_start.date(),
                "duration_years": duration,
                "end_date": dasa_end.date(),
                "order": i,
            }
        )

        cumulative_years += duration

    return changes


def get_dasa_interpretation(planet: str, level: DasaLevel) -> str:
    """Get interpretation of a dasa period by planet.

    Args:
        planet: Planet name
        level: Dasa level (Maha, Bhukti, etc.)

    Returns:
        Interpretation string

    """
    interpretations = {
        "sun": "Authority, leadership, ego. Support from father/government.",
        "moon": "Emotions, mind, comfort. Family matters, travel.",
        "mars": "Energy, action, conflict. Courage, competition, accidents.",
        "mercury": "Intellect, communication, business. Studies, commerce.",
        "jupiter": "Luck, expansion, spirituality. Wealth, children, success.",
        "venus": "Pleasure, relationships, comfort. Marriage, arts, luxury.",
        "saturn": "Discipline, hard work, delays. Lessons, karma, suffering.",
        "rahu": "Unconventional, obsessions, growth. Ambition, deception.",
        "kethu": "Spirituality, detachment, isolation. Losses, enlightenment.",
    }

    base_meaning = interpretations.get(planet, "Dasa period")
    level_modifier = f" ({level.value.upper()})"

    return base_meaning + level_modifier
