"""Upagrahas (Sub-planets) calculation utility.

Implements the 11 Upagrahas as defined by Sage Parasara.
These are mathematical points that do not correspond to physical bodies.
All houses occupied by Upagrahas are spoiled by their malefic nature.

Two types:
1. Sun-based Upagrahas (5): Dhuma, Vyatipaata, Parivesha, Indrachaapa, Upaketu
2. Time-based Upagrahas (6): Kaala, Mrityu, Artha Praharaka, Yamaghantaka, Gulika, Maandi
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

# Constants for sun-based upagrahas
DHUMA_OFFSET = 133 + 20 / 60  # 133°20'
VYATIPAATA_OFFSET = 360.0
PARIVESHA_OFFSET = 180.0
INDRACHAAPA_OFFSET = 360.0
UPAKETU_OFFSET = 16 + 40 / 60  # 16°40'

# Day/night division constants
DIVISION_PARTS = 8
FULL_CIRCLE = 360.0
RASI_COUNT = 12  # Total number of rasis


class UpagrahaType(str, Enum):
    """Type of Upagraha."""

    DHUMA = "dhuma"
    VYATIPAATA = "vyatipaata"
    PARIVESHA = "parivesha"
    INDRACHAAPA = "indrachaapa"
    UPAKETU = "upaketu"
    KAALA = "kaala"
    MRITYU = "mrityu"
    ARTHA_PRAHARAKA = "artha_praharaka"
    YAMAGHANTAKA = "yamaghantaka"
    GULIKA = "gulika"
    MAANDI = "maandi"


class PlanetRuler(str, Enum):
    """Planets that rule day/night divisions (ordered by weekday sequence)."""

    SUN = "sun"
    MOON = "moon"
    MARS = "mars"
    MERCURY = "mercury"
    JUPITER = "jupiter"
    VENUS = "venus"
    SATURN = "saturn"
    LORDLESS = "lordless"


# Ruling planets for 8 parts of daytime on each weekday
# Index 0 = Sunday, 1 = Monday, etc.
DAY_RULERS = [
    [
        PlanetRuler.SUN,
        PlanetRuler.MOON,
        PlanetRuler.MARS,
        PlanetRuler.MERCURY,
        PlanetRuler.JUPITER,
        PlanetRuler.VENUS,
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
    ],  # Sunday
    [
        PlanetRuler.MOON,
        PlanetRuler.MARS,
        PlanetRuler.MERCURY,
        PlanetRuler.JUPITER,
        PlanetRuler.VENUS,
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
        PlanetRuler.SUN,
    ],  # Monday
    [
        PlanetRuler.MARS,
        PlanetRuler.MERCURY,
        PlanetRuler.JUPITER,
        PlanetRuler.VENUS,
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
        PlanetRuler.SUN,
        PlanetRuler.MOON,
    ],  # Tuesday
    [
        PlanetRuler.MERCURY,
        PlanetRuler.JUPITER,
        PlanetRuler.VENUS,
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
        PlanetRuler.SUN,
        PlanetRuler.MOON,
        PlanetRuler.MARS,
    ],  # Wednesday
    [
        PlanetRuler.JUPITER,
        PlanetRuler.VENUS,
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
        PlanetRuler.SUN,
        PlanetRuler.MOON,
        PlanetRuler.MARS,
        PlanetRuler.MERCURY,
    ],  # Thursday
    [
        PlanetRuler.VENUS,
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
        PlanetRuler.SUN,
        PlanetRuler.MOON,
        PlanetRuler.MARS,
        PlanetRuler.MERCURY,
        PlanetRuler.JUPITER,
    ],  # Friday
    [
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
        PlanetRuler.SUN,
        PlanetRuler.MOON,
        PlanetRuler.MARS,
        PlanetRuler.MERCURY,
        PlanetRuler.JUPITER,
        PlanetRuler.VENUS,
    ],  # Saturday
]

# Ruling planets for 8 parts of nighttime on each weekday
NIGHT_RULERS = [
    [
        PlanetRuler.JUPITER,
        PlanetRuler.VENUS,
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
        PlanetRuler.SUN,
        PlanetRuler.MOON,
        PlanetRuler.MARS,
        PlanetRuler.MERCURY,
    ],  # Sunday
    [
        PlanetRuler.VENUS,
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
        PlanetRuler.SUN,
        PlanetRuler.MOON,
        PlanetRuler.MARS,
        PlanetRuler.MERCURY,
        PlanetRuler.JUPITER,
    ],  # Monday
    [
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
        PlanetRuler.SUN,
        PlanetRuler.MOON,
        PlanetRuler.MARS,
        PlanetRuler.MERCURY,
        PlanetRuler.JUPITER,
        PlanetRuler.VENUS,
    ],  # Tuesday
    [
        PlanetRuler.SUN,
        PlanetRuler.MOON,
        PlanetRuler.MARS,
        PlanetRuler.MERCURY,
        PlanetRuler.JUPITER,
        PlanetRuler.VENUS,
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
    ],  # Wednesday
    [
        PlanetRuler.MOON,
        PlanetRuler.MARS,
        PlanetRuler.MERCURY,
        PlanetRuler.JUPITER,
        PlanetRuler.VENUS,
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
        PlanetRuler.SUN,
    ],  # Thursday
    [
        PlanetRuler.MARS,
        PlanetRuler.MERCURY,
        PlanetRuler.JUPITER,
        PlanetRuler.VENUS,
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
        PlanetRuler.SUN,
        PlanetRuler.MOON,
    ],  # Friday
    [
        PlanetRuler.MERCURY,
        PlanetRuler.JUPITER,
        PlanetRuler.VENUS,
        PlanetRuler.SATURN,
        PlanetRuler.LORDLESS,
        PlanetRuler.SUN,
        PlanetRuler.MOON,
        PlanetRuler.MARS,
    ],  # Saturday
]


@dataclass
class Upagraha:
    """Upagraha position and details."""

    name: UpagrahaType
    longitude: float  # 0-360 degrees
    rasi_number: int  # 1-12
    rasi_name: str  # Sign name (Aries, Taurus, etc.)
    degree_in_rasi: float  # 0-30 degrees
    ruling_planet: str | None = None  # For time-based upagrahas


def _normalize_longitude(longitude: float) -> float:
    """Normalize longitude to 0-360 range."""
    normalized = longitude % FULL_CIRCLE
    return normalized if normalized >= 0 else normalized + FULL_CIRCLE


def calculate_sun_based_upagrahas(sun_longitude: float) -> dict[UpagrahaType, float]:
    """Calculate 5 Sun-based Upagrahas from Sun's longitude.

    Args:
        sun_longitude: Sun's tropical longitude (0-360 degrees)

    Returns:
        Dictionary mapping UpagrahaType to longitude (0-360)

    """
    # Step 1: Calculate Dhuma
    dhuma = _normalize_longitude(sun_longitude + DHUMA_OFFSET)

    # Step 2: Calculate Vyatipaata (opposite of Dhuma)
    vyatipaata = _normalize_longitude(VYATIPAATA_OFFSET - dhuma)

    # Step 3: Calculate Parivesha (180° from Vyatipaata)
    parivesha = _normalize_longitude(vyatipaata + PARIVESHA_OFFSET)

    # Step 4: Calculate Indrachaapa (opposite of Parivesha)
    indrachaapa = _normalize_longitude(INDRACHAAPA_OFFSET - parivesha)

    # Step 5: Calculate Upaketu (from Indrachaapa)
    upaketu = _normalize_longitude(indrachaapa + UPAKETU_OFFSET)

    return {
        UpagrahaType.DHUMA: dhuma,
        UpagrahaType.VYATIPAATA: vyatipaata,
        UpagrahaType.PARIVESHA: parivesha,
        UpagrahaType.INDRACHAAPA: indrachaapa,
        UpagrahaType.UPAKETU: upaketu,
    }


def _get_day_or_night_ruling_planets(birth_datetime: datetime, *, is_day: bool) -> list[PlanetRuler]:
    """Get ruling planets for 8 parts of day or night.

    Args:
        birth_datetime: Birth date and time
        is_day: True for daytime, False for nighttime

    Returns:
        List of 8 PlanetRuler enums (one for each part)

    """
    weekday = birth_datetime.weekday()  # 0=Monday, 6=Sunday
    # Convert to weekday index (0=Sunday, 1=Monday, etc.)
    weekday_idx = (weekday + 1) % 7

    rulers = DAY_RULERS if is_day else NIGHT_RULERS
    return rulers[weekday_idx]


def _get_upagraha_ruling_planet(upagraha_type: UpagrahaType, weekday_idx: int, *, is_day: bool) -> PlanetRuler | None:
    """Get which planet rules a specific upagraha.

    Args:
        upagraha_type: Type of time-based upagraha
        weekday_idx: Weekday index (0=Sunday)
        is_day: True for daytime, False for nighttime

    Returns:
        PlanetRuler that rules this upagraha

    """
    # Map upagrahas to their ruling planet positions
    upagraha_positions = {
        UpagrahaType.KAALA: 4,  # Sun's part (5th position, 0-indexed = 4)
        UpagrahaType.MRITYU: 1,  # Mars's part (2nd position)
        UpagrahaType.ARTHA_PRAHARAKA: 2,  # Mercury's part (3rd position)
        UpagrahaType.YAMAGHANTAKA: 3,  # Jupiter's part (4th position, but for night?)
        UpagrahaType.GULIKA: 5,  # Saturn's part (6th position)
        UpagrahaType.MAANDI: 5,  # Saturn's part (6th position, at beginning)
    }

    if upagraha_type not in upagraha_positions:
        return None

    position = upagraha_positions[upagraha_type]
    rulers = DAY_RULERS if is_day else NIGHT_RULERS
    return rulers[weekday_idx][position]


def get_sun_based_upagraha_details(
    upagraha_type: UpagrahaType,
    longitude: float,
) -> Upagraha:
    """Convert upagraha longitude to Upagraha dataclass with rasi details.

    Args:
        upagraha_type: Type of sun-based upagraha
        longitude: Upagraha longitude (0-360)

    Returns:
        Upagraha dataclass with all details

    """
    # Calculate rasi number (0-11, convert to 1-12)
    rasi_number = int(longitude // 30) + 1
    rasi_number = min(rasi_number, RASI_COUNT)

    # Calculate degree within rasi (0-30)
    degree_in_rasi = longitude % 30

    # Rasi names in order
    rasi_names = [
        "aries",
        "taurus",
        "gemini",
        "cancer",
        "leo",
        "virgo",
        "libra",
        "scorpio",
        "sagittarius",
        "capricorn",
        "aquarius",
        "pisces",
    ]
    rasi_name = rasi_names[rasi_number - 1]

    return Upagraha(
        name=upagraha_type,
        longitude=longitude,
        rasi_number=rasi_number,
        rasi_name=rasi_name,
        degree_in_rasi=degree_in_rasi,
    )


def get_all_sun_based_upagrahas(sun_longitude: float) -> list[Upagraha]:
    """Get all 5 Sun-based Upagrahas with complete details.

    Args:
        sun_longitude: Sun's tropical longitude (0-360)

    Returns:
        List of 5 Upagraha objects

    """
    sun_based = calculate_sun_based_upagrahas(sun_longitude)

    upagrahas = []
    for upagraha_type, longitude in sun_based.items():
        upagraha = get_sun_based_upagraha_details(upagraha_type, longitude)
        upagrahas.append(upagraha)

    return upagrahas


def get_upagraha_interpretation(upagraha: Upagraha) -> str:
    """Get interpretation of an Upagraha in its rasi.

    Args:
        upagraha: Upagraha object with all details

    Returns:
        Interpretation string

    """
    interpretations = {
        UpagrahaType.DHUMA: "Very malefic. Spoils the house and brings obstruction.",
        UpagrahaType.VYATIPAATA: "Malefic. Causes loss and discord.",
        UpagrahaType.PARIVESHA: "Malefic. Brings suffering and hardship.",
        UpagrahaType.INDRACHAAPA: "Malefic. Causes impediments and obstacles.",
        UpagrahaType.UPAKETU: "Malefic. Creates instability and disturbances.",
        UpagrahaType.KAALA: "Malefic like Sun. Brings loss and obstruction.",
        UpagrahaType.MRITYU: "Malefic like Mars. Creates danger and hardship.",
        UpagrahaType.ARTHA_PRAHARAKA: "Malefic like Mercury. Causes loss of wealth.",
        UpagrahaType.YAMAGHANTAKA: "Malefic like Jupiter. Causes religious obstacles.",
        UpagrahaType.GULIKA: "Malefic like Saturn. Brings delays and suffering.",
        UpagrahaType.MAANDI: "Malefic like Saturn. Brings stagnation and blockage.",
    }

    base_meaning = interpretations.get(upagraha.name, "Malefic point")
    return f"{base_meaning} In {upagraha.rasi_name} ({upagraha.degree_in_rasi:.1f}°)"
