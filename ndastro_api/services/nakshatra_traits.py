"""Nakshatra timing, traits, and compatibility calculations.

Provides detailed nakshatra analysis including characteristics,
planetary rulers, muhurta timing, and compatibility assessments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

NAKSHATRA_COUNT = 27
NAKSHATRA_ARC_DEGREES = 360.0 / NAKSHATRA_COUNT
PADA_PER_NAKSHATRA = 4
PADA_ARC_DEGREES = NAKSHATRA_ARC_DEGREES / PADA_PER_NAKSHATRA

NAKSHATRA_NAMES = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishtha",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]

NAKSHATRA_LORDS = [
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
]

NAKSHATRA_DEITIES = [
    "Ashwini Kumaras",
    "Yama",
    "Agni",
    "Brahma",
    "Soma",
    "Rudra",
    "Aditi",
    "Brihaspati",
    "Serpents",
    "Pitris",
    "Bhaga",
    "Aryaman",
    "Savitar",
    "Tvashtar",
    "Vayu",
    "Indra-Agni",
    "Mitra",
    "Indra",
    "Nirrti",
    "Apah",
    "Vishvedevas",
    "Vishnu",
    "Vasus",
    "Varuna",
    "Aja Ekapada",
    "Ahirbudhnya",
    "Pushan",
]

# Nakshatra gunas (qualities)
NAKSHATRA_GANAS = [
    "Deva",
    "Manushya",
    "Rakshasa",
    "Manushya",
    "Deva",
    "Manushya",
    "Deva",
    "Deva",
    "Rakshasa",
    "Rakshasa",
    "Manushya",
    "Manushya",
    "Deva",
    "Rakshasa",
    "Deva",
    "Rakshasa",
    "Deva",
    "Rakshasa",
    "Rakshasa",
    "Manushya",
    "Manushya",
    "Deva",
    "Rakshasa",
    "Rakshasa",
    "Manushya",
    "Manushya",
    "Deva",
]

# Nakshatra types (fixed, movable, dual)
NAKSHATRA_TYPES = [
    "Movable",
    "Fixed",
    "Dual",
    "Fixed",
    "Dual",
    "Movable",
    "Movable",
    "Movable",
    "Fixed",
    "Fixed",
    "Fixed",
    "Fixed",
    "Movable",
    "Dual",
    "Movable",
    "Fixed",
    "Fixed",
    "Fixed",
    "Fixed",
    "Dual",
    "Fixed",
    "Movable",
    "Dual",
    "Movable",
    "Dual",
    "Fixed",
    "Dual",
]


class NakshatraGana(str, Enum):
    """Nakshatra gana classification."""

    DEVA = "Deva"
    MANUSHYA = "Manushya"
    RAKSHASA = "Rakshasa"


class NakshatraType(str, Enum):
    """Nakshatra movement type."""

    FIXED = "Fixed"
    MOVABLE = "Movable"
    DUAL = "Dual"


@dataclass
class NakshatraTraits:
    """Nakshatra characteristics and traits."""

    index: int
    name: str
    lord: str
    deity: str
    gana: NakshatraGana
    type: NakshatraType
    symbol: str
    meaning: str
    qualities: list[str] = field(default_factory=list)
    activities: list[str] = field(default_factory=list)


@dataclass
class NakshatraPosition:
    """Nakshatra position for a longitude."""

    longitude: float
    nakshatra_index: int
    nakshatra_name: str
    pada: int
    degrees_in_nakshatra: float
    degrees_in_pada: float
    lord: str
    traits: NakshatraTraits


@dataclass
class NakshatraCompatibility:
    """Nakshatra compatibility analysis."""

    nakshatra1: int
    nakshatra2: int
    name1: str
    name2: str
    kuta_score: float
    compatibility_level: str
    description: str


def get_nakshatra_from_longitude(longitude: float) -> int:
    """Get nakshatra index (1-27) from longitude."""
    normalized = longitude % 360.0
    index = int(normalized / NAKSHATRA_ARC_DEGREES) + 1
    return min(max(1, index), NAKSHATRA_COUNT)


def get_pada_from_longitude(longitude: float) -> int:
    """Get pada (1-4) within nakshatra from longitude."""
    normalized = longitude % 360.0
    nakshatra_degree = normalized % NAKSHATRA_ARC_DEGREES
    pada = int(nakshatra_degree / PADA_ARC_DEGREES) + 1
    return min(max(1, pada), PADA_PER_NAKSHATRA)


def get_nakshatra_traits(nakshatra_index: int) -> NakshatraTraits:
    """Get detailed traits for a nakshatra."""
    if not 1 <= nakshatra_index <= NAKSHATRA_COUNT:
        msg = f"Invalid nakshatra index: {nakshatra_index}"
        raise ValueError(msg)

    idx = nakshatra_index - 1
    name = NAKSHATRA_NAMES[idx]

    # Additional traits by nakshatra
    symbols_and_meanings = {
        1: ("Horse's head", "Swift action, healing"),
        2: ("Yoni", "Creative power, fertility"),
        3: ("Razor/Flame", "Sharpness, purification"),
        4: ("Chariot/Cart", "Growth, abundance"),
        5: ("Deer's head", "Curiosity, gentleness"),
        6: ("Teardrop", "Intensity, transformation"),
        7: ("House", "Return, restoration"),
        8: ("Wheel/Circle", "Nourishment, support"),
        9: ("Serpent", "Wisdom, kundalini"),
        10: ("Throne", "Ancestral power, authority"),
        11: ("Bed/Hammock", "Rest, pleasure"),
        12: ("Helping hand", "Service, cooperation"),
        13: ("Pearl/Hand", "Skill, dexterity"),
        14: ("Coral/Pearl", "Art, creativity"),
        15: ("Coral", "Independence, freedom"),
        16: ("Triumphal arch", "Achievement, balance"),
        17: ("Lotus", "Friendship, devotion"),
        18: ("Umbrella/Earring", "Leadership, protection"),
        19: ("Elephant tusk", "Roots, foundation"),
        20: ("Elephant tusk", "Victory, invincibility"),
        21: ("Vishvedevas", "Universal, all-encompassing"),
        22: ("Ear", "Learning, listening"),
        23: ("Drum", "Rhythm, prosperity"),
        24: ("Circles", "Healing, hundred stars"),
        25: ("Sword", "Intense transformation"),
        26: ("Twins", "Support, duality"),
        27: ("Fish/Drum", "Nourishment, journey's end"),
    }

    symbol, meaning = symbols_and_meanings.get(nakshatra_index, ("Unknown", "Unknown"))

    return NakshatraTraits(
        index=nakshatra_index,
        name=name,
        lord=NAKSHATRA_LORDS[idx],
        deity=NAKSHATRA_DEITIES[idx],
        gana=NakshatraGana(NAKSHATRA_GANAS[idx]),
        type=NakshatraType(NAKSHATRA_TYPES[idx]),
        symbol=symbol,
        meaning=meaning,
    )


def calculate_nakshatra_position(longitude: float) -> NakshatraPosition:
    """Calculate complete nakshatra position for a longitude.

    Args:
        longitude: Sidereal longitude in degrees [0, 360).

    Returns:
        NakshatraPosition with full details.

    """
    nakshatra_index = get_nakshatra_from_longitude(longitude)
    pada = get_pada_from_longitude(longitude)

    normalized = longitude % 360.0
    degrees_in_nakshatra = normalized % NAKSHATRA_ARC_DEGREES
    degrees_in_pada = degrees_in_nakshatra % PADA_ARC_DEGREES

    traits = get_nakshatra_traits(nakshatra_index)

    return NakshatraPosition(
        longitude=longitude,
        nakshatra_index=nakshatra_index,
        nakshatra_name=traits.name,
        pada=pada,
        degrees_in_nakshatra=degrees_in_nakshatra,
        degrees_in_pada=degrees_in_pada,
        lord=traits.lord,
        traits=traits,
    )


def calculate_nakshatra_compatibility(
    nakshatra1: int,
    nakshatra2: int,
) -> NakshatraCompatibility:
    """Calculate compatibility between two nakshatras.

    Uses simplified Kuta system.

    Args:
        nakshatra1: First nakshatra index (1-27).
        nakshatra2: Second nakshatra index (1-27).

    Returns:
        NakshatraCompatibility with score and description.

    """
    if not (1 <= nakshatra1 <= NAKSHATRA_COUNT) or not (1 <= nakshatra2 <= NAKSHATRA_COUNT):
        msg = "Invalid nakshatra indices"
        raise ValueError(msg)

    name1 = NAKSHATRA_NAMES[nakshatra1 - 1]
    name2 = NAKSHATRA_NAMES[nakshatra2 - 1]

    # Simplified Dina Kuta (distance compatibility)
    distance = abs(nakshatra2 - nakshatra1)
    dina_score = 3.0 if distance not in {0, 9, 18} else 0.0

    # Gana Kuta (temperament compatibility)
    gana1 = NAKSHATRA_GANAS[nakshatra1 - 1]
    gana2 = NAKSHATRA_GANAS[nakshatra2 - 1]
    if gana1 == gana2:
        gana_score = 6.0
    elif (gana1 == "Deva" and gana2 == "Manushya") or (gana1 == "Manushya" and gana2 == "Deva"):
        gana_score = 5.0
    else:
        gana_score = 0.0

    # Total Kuta score (simplified)
    kuta_score = dina_score + gana_score
    max_score = 9.0

    # Determine compatibility level
    if kuta_score >= 7.0:  # noqa: PLR2004
        level = "Excellent"
    elif kuta_score >= 5.0:  # noqa: PLR2004
        level = "Good"
    elif kuta_score >= 3.0:  # noqa: PLR2004
        level = "Average"
    else:
        level = "Poor"

    description = f"Compatibility: {kuta_score}/{max_score} - {gana1} + {gana2}."

    return NakshatraCompatibility(
        nakshatra1=nakshatra1,
        nakshatra2=nakshatra2,
        name1=name1,
        name2=name2,
        kuta_score=kuta_score,
        compatibility_level=level,
        description=description,
    )
