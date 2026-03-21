"""Longevity Calculations (Ay us) - Vedic Astrology.

Based on P.V.R. Narasimha Rao's Vedic Astrology: An Integrated Approach
Chapter 14: Topics Related to Longevity

This module implements various longevity determination techniques including:
- Maraka (killer) planets and houses identification
- Rudra, Trishoola, Maheswara calculations
- Method of Three Pairs for longevity category
- Eighth Lord Method

ETHICAL NOTE: This knowledge should NEVER be misused to scare clients.
Astrologers should only gently caution clients and suggest remedial measures.
"""

from dataclasses import dataclass
from enum import Enum

# ============================================================================
# CONSTANTS
# ============================================================================

# House numbers
HOUSE_1_SELF = 1
HOUSE_2_WEALTH = 2
HOUSE_3_COURAGE = 3
HOUSE_4_HOME = 4
HOUSE_5_CHILDREN = 5
HOUSE_6_ENEMIES = 6
HOUSE_7_PARTNERSHIP = 7
HOUSE_8_LONGEVITY = 8
HOUSE_9_FORTUNE = 9
HOUSE_10_CAREER = 10
HOUSE_11_GAINS = 11
HOUSE_12_LOSS = 12

# Rasi (sign) numbers 1-12 (Aries to Pisces)
RASI_ARIES = 1
RASI_TAURUS = 2
RASI_GEMINI = 3
RASI_CANCER = 4
RASI_LEO = 5
RASI_VIRGO = 6
RASI_LIBRA = 7
RASI_SCORPIO = 8
RASI_SAGITTARIUS = 9
RASI_CAPRICORN = 10
RASI_AQUARIUS = 11
RASI_PISCES = 12

TOTAL_RASIS = 12


# ============================================================================
# ENUMS
# ============================================================================


class LongevityCategory(str, Enum):
    """Longevity categories per Parasara."""

    SHORT_LIFE = "short_life"  # 0-36 years (Alpayu)
    MIDDLE_LIFE = "middle_life"  # 36-72 years (Madhyayu)
    LONG_LIFE = "long_life"  # 72-108 years (Purnayu)


class RasiType(str, Enum):
    """Rasi nature by zodiac sign type."""

    MOVABLE = "movable"  # Chara: Aries, Cancer, Libra, Capricorn
    FIXED = "fixed"  # Sthira: Taurus, Leo, Scorpio, Aquarius
    DUAL = "dual"  # Dvisvabhava: Gemini, Virgo, Sagittarius, Pisces


class HouseCategory(str, Enum):
    """House position categories for 8th lord method."""

    QUADRANT = "quadrant"  # Kendra: 1, 4, 7, 10 from reference
    PANAPHARA = "panaphara"  # 2, 5, 8, 11 from reference
    APOKLIMA = "apoklima"  # 3, 6, 9, 12 from reference


class MarakaType(str, Enum):
    """Types of maraka (killer) planets."""

    HOUSE_LORD = "house_lord"  # Lord of 2nd or 7th
    MALEFIC_ASPECTER = "malefic_aspecter"  # Malefic aspecting 2nd/7th
    MALEFIC_IN_HOUSE = "malefic_in_house"  # Malefic in 2nd/7th


# ============================================================================
# LOOKUP TABLES
# ============================================================================

# Table 32: Special 8th house calculation for Rudra
# For odd rasis (Brahma/Vishnu motion): count zodiacally
# For even rasis (Shiva motion): count anti-zodiacally
SPECIAL_8TH_HOUSE_TABLE: dict[int, int] = {
    RASI_ARIES: RASI_SCORPIO,  # Ar → 8th = Sc (zodiacal)
    RASI_TAURUS: RASI_GEMINI,  # Ta → 8th = Ge (anti-zodiacal)
    RASI_GEMINI: RASI_CAPRICORN,  # Ge → 8th = Cp (zodiacal)
    RASI_CANCER: RASI_SAGITTARIUS,  # Cn → 8th = Sg (anti-zodiacal)
    RASI_LEO: RASI_CANCER,  # Le → 8th = Cn (zodiacal)
    RASI_VIRGO: RASI_AQUARIUS,  # Vi → 8th = Aq (anti-zodiacal)
    RASI_LIBRA: RASI_TAURUS,  # Li → 8th = Ta (zodiacal)
    RASI_SCORPIO: RASI_SAGITTARIUS,  # Sc → 8th = Sg (anti-zodiacal)
    RASI_SAGITTARIUS: RASI_CANCER,  # Sg → 8th = Cn (zodiacal)
    RASI_CAPRICORN: RASI_GEMINI,  # Cp → 8th = Ge (anti-zodiacal)
    RASI_AQUARIUS: RASI_CAPRICORN,  # Aq → 8th = Cp (zodiacal)
    RASI_PISCES: RASI_LEO,  # Pi → 8th = Le (anti-zodiacal)
}

# Rasi type classification
RASI_TYPE_MAP: dict[int, RasiType] = {
    RASI_ARIES: RasiType.MOVABLE,
    RASI_TAURUS: RasiType.FIXED,
    RASI_GEMINI: RasiType.DUAL,
    RASI_CANCER: RasiType.MOVABLE,
    RASI_LEO: RasiType.FIXED,
    RASI_VIRGO: RasiType.DUAL,
    RASI_LIBRA: RasiType.MOVABLE,
    RASI_SCORPIO: RasiType.FIXED,
    RASI_SAGITTARIUS: RasiType.DUAL,
    RASI_CAPRICORN: RasiType.MOVABLE,
    RASI_AQUARIUS: RasiType.FIXED,
    RASI_PISCES: RasiType.DUAL,
}

# Table 33: Longevity Category for Each Pair
# Key: (type1, type2) → LongevityCategory
LONGEVITY_PAIR_RULES: dict[tuple[RasiType, RasiType], LongevityCategory] = {
    # Long life combinations
    (RasiType.FIXED, RasiType.DUAL): LongevityCategory.LONG_LIFE,
    (RasiType.DUAL, RasiType.FIXED): LongevityCategory.LONG_LIFE,
    (RasiType.MOVABLE, RasiType.MOVABLE): LongevityCategory.LONG_LIFE,
    # Middle life combinations
    (RasiType.MOVABLE, RasiType.FIXED): LongevityCategory.MIDDLE_LIFE,
    (RasiType.FIXED, RasiType.MOVABLE): LongevityCategory.MIDDLE_LIFE,
    (RasiType.DUAL, RasiType.DUAL): LongevityCategory.MIDDLE_LIFE,
    # Short life combinations
    (RasiType.MOVABLE, RasiType.DUAL): LongevityCategory.SHORT_LIFE,
    (RasiType.DUAL, RasiType.MOVABLE): LongevityCategory.SHORT_LIFE,
    (RasiType.FIXED, RasiType.FIXED): LongevityCategory.SHORT_LIFE,
}

# Table 34: Paramaayush (Maximum longevity) Reckoner
# When 2 pairs give one result and 3rd gives another
# Key: (two_pairs_result, third_pair_result) → years
PARAMAAYUSH_TABLE: dict[tuple[LongevityCategory, LongevityCategory], int] = {
    (LongevityCategory.SHORT_LIFE, LongevityCategory.SHORT_LIFE): 32,
    (LongevityCategory.SHORT_LIFE, LongevityCategory.MIDDLE_LIFE): 36,
    (LongevityCategory.SHORT_LIFE, LongevityCategory.LONG_LIFE): 40,
    (LongevityCategory.MIDDLE_LIFE, LongevityCategory.SHORT_LIFE): 64,
    (LongevityCategory.MIDDLE_LIFE, LongevityCategory.MIDDLE_LIFE): 72,
    (LongevityCategory.MIDDLE_LIFE, LongevityCategory.LONG_LIFE): 80,
    (LongevityCategory.LONG_LIFE, LongevityCategory.SHORT_LIFE): 96,
    (LongevityCategory.LONG_LIFE, LongevityCategory.MIDDLE_LIFE): 108,
    (LongevityCategory.LONG_LIFE, LongevityCategory.LONG_LIFE): 120,
}

# Default longevity ranges
LONGEVITY_RANGE_MAP: dict[LongevityCategory, tuple[int, int]] = {
    LongevityCategory.SHORT_LIFE: (0, 36),
    LongevityCategory.MIDDLE_LIFE: (36, 72),
    LongevityCategory.LONG_LIFE: (72, 108),
}

# Magic number constants
UNANIMOUS_PAIR_COUNT = 3
MAJORITY_PAIR_COUNT = 2
MULTIPLE_MARAKA_THRESHOLD = 3

# Malefic planets
MALEFIC_PLANETS = {"mars", "saturn", "rahu", "kethu", "ketu"}

# Natural benefics
BENEFIC_PLANETS = {"jupiter", "venus", "mercury"}  # Moon depends on paksha

# Rasi lordships (simplified - single lords only)
RASI_LORDS: dict[int, str] = {
    RASI_ARIES: "mars",
    RASI_TAURUS: "venus",
    RASI_GEMINI: "mercury",
    RASI_CANCER: "moon",
    RASI_LEO: "sun",
    RASI_VIRGO: "mercury",
    RASI_LIBRA: "venus",
    RASI_SCORPIO: "mars",  # Primary lord
    RASI_SAGITTARIUS: "jupiter",
    RASI_CAPRICORN: "saturn",
    RASI_AQUARIUS: "saturn",
    RASI_PISCES: "jupiter",
}


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class PlanetPosition:
    """Simplified planet position for longevity calculations."""

    name: str
    rasi: int  # 1-12
    house: int  # 1-12 from lagna
    degrees_in_rasi: float  # 0-30
    is_exalted: bool = False
    is_debilitated: bool = False
    is_retrograde: bool = False


@dataclass
class ChartContext:
    """Chart context for longevity calculations."""

    lagna_rasi: int  # 1-12
    planets: dict[str, PlanetPosition]  # planet_name → position
    house_7_rasi: int  # Rasi of 7th house
    horalagna_rasi: int  # Hora lagna rasi (wealth ascendant)
    atma_karaka: str  # Chara atma karaka planet name


@dataclass
class MarakaIdentification:
    """Identified maraka (killer) planets and houses."""

    maraka_houses: list[int]  # 2nd and 7th houses
    maraka_house_lords: list[str]  # Lords of 2nd/7th
    maraka_malefics: list[str]  # Malefics aspecting/in maraka houses
    all_marakas: list[str]  # Combined list of all maraka planets
    maraka_types: dict[str, MarakaType]  # Planet → MarakaType


@dataclass
class RudraTrishoolaIdentification:
    """Rudra and Trishoola identification."""

    lagna_8th_special: int  # Special 8th from lagna (Table 32)
    house_7_8th_special: int  # Special 8th from 7th house
    lagna_8th_lord: str  # Lord of special 8th from lagna
    house_7_8th_lord: str  # Lord of special 8th from 7th
    rudra_planet: str  # The stronger planet = Rudra
    rudra_rasi: int  # Rasi where Rudra is placed
    trishoola_rasis: list[int]  # Three trines from Rudra (1-5-9)
    reason: str  # Why this planet became Rudra


@dataclass
class MaheswaraIdentification:
    """Maheswara (lord of soul's liberation) identification."""

    ak_planet: str  # Atma Karaka
    ak_rasi: int  # AK's rasi
    eighth_from_ak: int  # 8th rasi from AK
    maheswara: str  # The planet representing soul's liberation
    calculation_notes: str  # Special rules applied


@dataclass
class LongevityPairResult:
    """Result of one pair in three-pairs method."""

    pair_name: str
    element1_name: str
    element1_rasi: int
    element1_type: RasiType
    element2_name: str
    element2_rasi: int
    element2_type: RasiType
    result: LongevityCategory


@dataclass
class ThreePairsResult:
    """Complete three-pairs method result."""

    pair1: LongevityPairResult  # Lagna lord + 8th lord
    pair2: LongevityPairResult  # Moon + Saturn
    pair3: LongevityPairResult  # Lagna + Horalagna
    final_category: LongevityCategory
    paramaayush: int  # Maximum years if 2:1 split
    agreement: str  # "unanimous", "2_vs_1", "split_3_ways"
    preferred_pair: str | None  # Which pair to prefer in split


@dataclass
class EighthLordMethodResult:
    """Result of Eighth Lord method."""

    reference_house: str  # "lagna" or "7th_house"
    reference_rasi: int
    eighth_lord: str
    eighth_lord_house_from_ref: int  # 1-12 from reference
    house_category: HouseCategory
    longevity_category: LongevityCategory


@dataclass
class LongevityAnalysis:
    """Complete longevity analysis results."""

    marakas: MarakaIdentification
    rudra_trishoola: RudraTrishoolaIdentification
    maheswara: MaheswaraIdentification
    three_pairs_result: ThreePairsResult
    eighth_lord_result: EighthLordMethodResult
    final_assessment: str
    longevity_category: LongevityCategory
    estimated_range: tuple[int, int]
    warnings: list[str]
    ethical_note: str = (
        "This analysis is for astrological study only. NEVER use this to scare clients. Gently caution and suggest remedies if needed."
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_rasi_type(rasi: int) -> RasiType:
    """Get rasi type (movable/fixed/dual).

    Args:
        rasi: Rasi number 1-12

    Returns:
        RasiType enum

    """
    return RASI_TYPE_MAP[rasi]


def get_special_8th_house(from_rasi: int) -> int:
    """Get special 8th house using Table 32.

    Uses zodiacal counting for odd rasis, anti-zodiacal for even.

    Args:
        from_rasi: Starting rasi 1-12

    Returns:
        Special 8th house rasi number

    """
    return SPECIAL_8TH_HOUSE_TABLE[from_rasi]


def get_rasi_lord(rasi: int) -> str:
    """Get primary lord of a rasi.

    Args:
        rasi: Rasi number 1-12

    Returns:
        Planet name (lowercase)

    """
    return RASI_LORDS[rasi]


def get_house_from_rasi(lagna_rasi: int, target_rasi: int) -> int:
    """Calculate house number from lagna rasi to target rasi.

    Args:
        lagna_rasi: Lagna rasi 1-12
        target_rasi: Target rasi 1-12

    Returns:
        House number 1-12

    """
    house = target_rasi - lagna_rasi + 1
    if house <= 0:
        house += TOTAL_RASIS
    return house


def get_rasi_at_house(lagna_rasi: int, house: int) -> int:
    """Get rasi at a specific house from lagna.

    Args:
        lagna_rasi: Lagna rasi 1-12
        house: House number 1-12

    Returns:
        Rasi number 1-12

    """
    rasi = lagna_rasi + house - 1
    if rasi > TOTAL_RASIS:
        rasi -= TOTAL_RASIS
    return rasi


def get_trine_rasis(from_rasi: int) -> list[int]:
    """Get three trine rasis (1-5-9 pattern).

    Args:
        from_rasi: Starting rasi 1-12

    Returns:
        List of 3 rasi numbers in trines

    """
    rasi1 = from_rasi
    rasi2 = from_rasi + 4
    if rasi2 > TOTAL_RASIS:
        rasi2 -= TOTAL_RASIS

    rasi3 = from_rasi + 8
    if rasi3 > TOTAL_RASIS:
        rasi3 -= TOTAL_RASIS

    return [rasi1, rasi2, rasi3]


def categorize_house_position(house_from_ref: int) -> HouseCategory:
    """Categorize house as quadrant/panaphara/apoklima.

    Args:
        house_from_ref: House number 1-12 from reference

    Returns:
        HouseCategory enum

    """
    quadrants = {1, 4, 7, 10}
    panapharas = {2, 5, 8, 11}

    if house_from_ref in quadrants:
        return HouseCategory.QUADRANT
    if house_from_ref in panapharas:
        return HouseCategory.PANAPHARA
    return HouseCategory.APOKLIMA


def compare_planet_strength(
    planet1: PlanetPosition,
    planet2: PlanetPosition,
    *,
    context: ChartContext,
) -> str:
    """Compare two planets and return stronger one's name.

    Strength criteria (in order):
    1. Number of conjunctions (more = stronger)
    2. Exaltation/own sign
    3. Conjunct with exalted planets
    4. Aspected by many planets
    5. More advanced in rasi (higher degrees)

    Args:
        planet1: First planet
        planet2: Second planet
        context: Chart context for counting conjunctions

    Returns:
        Name of stronger planet

    """
    # Count conjunctions (planets in same house)
    p1_conjunctions = sum(1 for p in context.planets.values() if p.house == planet1.house and p.name != planet1.name)
    p2_conjunctions = sum(1 for p in context.planets.values() if p.house == planet2.house and p.name != planet2.name)

    if p1_conjunctions > p2_conjunctions:
        return planet1.name
    if p2_conjunctions > p1_conjunctions:
        return planet2.name

    # Check exaltation/own sign
    if planet1.is_exalted and not planet2.is_exalted:
        return planet1.name
    if planet2.is_exalted and not planet1.is_exalted:
        return planet2.name

    # More advanced in rasi (higher degrees)
    if planet1.degrees_in_rasi > planet2.degrees_in_rasi:
        return planet1.name

    return planet2.name


def is_planet_afflicted(planet: PlanetPosition, *, context: ChartContext) -> bool:
    """Check if planet is afflicted (debilitated/enemy sign + malefic aspects).

    Simplified: checks if debilitated or in enemy territory with malefics nearby.

    Args:
        planet: Planet to check
        context: Chart context

    Returns:
        True if afflicted

    """
    if planet.is_debilitated:
        return True

    # Check if malefics in same house
    return any(p.name in MALEFIC_PLANETS and p.house == planet.house for p in context.planets.values())


# ============================================================================
# MARAKA IDENTIFICATION
# ============================================================================


def identify_marakas(context: ChartContext) -> MarakaIdentification:
    """Identify all maraka (killer) planets and houses.

    Marakas:
    - Lords of 2nd and 7th houses
    - Malefics in 2nd or 7th houses
    - Malefics aspecting 2nd/7th houses or their lords

    Args:
        context: Chart context

    Returns:
        MarakaIdentification with all maraka details

    """
    maraka_houses = [HOUSE_2_WEALTH, HOUSE_7_PARTNERSHIP]
    maraka_house_lords = []
    maraka_malefics = []
    maraka_types: dict[str, MarakaType] = {}

    # Get rasis of 2nd and 7th houses
    house_2_rasi = get_rasi_at_house(context.lagna_rasi, HOUSE_2_WEALTH)
    house_7_rasi = context.house_7_rasi

    # Lords of 2nd and 7th
    lord_2 = get_rasi_lord(house_2_rasi)
    lord_7 = get_rasi_lord(house_7_rasi)

    maraka_house_lords = [lord_2, lord_7]
    maraka_types[lord_2] = MarakaType.HOUSE_LORD
    maraka_types[lord_7] = MarakaType.HOUSE_LORD

    # Malefics in 2nd or 7th house
    for planet in context.planets.values():
        if planet.name in MALEFIC_PLANETS and planet.house in maraka_houses:
            maraka_malefics.append(planet.name)
            maraka_types[planet.name] = MarakaType.MALEFIC_IN_HOUSE

    # Combine all
    all_marakas = list(set(maraka_house_lords + maraka_malefics))

    return MarakaIdentification(
        maraka_houses=maraka_houses,
        maraka_house_lords=maraka_house_lords,
        maraka_malefics=maraka_malefics,
        all_marakas=all_marakas,
        maraka_types=maraka_types,
    )


# ============================================================================
# RUDRA & TRISHOOLA
# ============================================================================


def identify_rudra_trishoola(context: ChartContext) -> RudraTrishoolaIdentification:
    """Identify Rudra planet and Trishoola rasis.

    Rudra is the stronger of:
    - Lord of special 8th house from lagna
    - Lord of special 8th house from 7th house

    Exception: If weaker planet is afflicted, it becomes Rudra.

    Args:
        context: Chart context

    Returns:
        RudraTrishoolaIdentification with Rudra and Trishoola details

    """
    # Special 8th houses using Table 32
    lagna_8th_special = get_special_8th_house(context.lagna_rasi)
    house_7_8th_special = get_special_8th_house(context.house_7_rasi)

    # Get lords
    lagna_8th_lord = get_rasi_lord(lagna_8th_special)
    house_7_8th_lord = get_rasi_lord(house_7_8th_special)

    # Get planet positions
    planet1 = context.planets[lagna_8th_lord]
    planet2 = context.planets[house_7_8th_lord]

    # Compare strength
    stronger = compare_planet_strength(planet1, planet2, context=context)
    weaker = house_7_8th_lord if stronger == lagna_8th_lord else lagna_8th_lord
    weaker_planet = context.planets[weaker]

    # Check exception: if weaker is afflicted, it becomes Rudra
    if is_planet_afflicted(weaker_planet, context=context):
        rudra_planet = weaker
        reason = f"{weaker.title()} is weaker but afflicted (debilitated/malefic conjunction)"
    else:
        rudra_planet = stronger
        reason = f"{stronger.title()} is stronger by conjunction/dignity/advancement"

    # Get Rudra's rasi
    rudra_rasi = context.planets[rudra_planet].rasi

    # Trishoola = three trines from Rudra's rasi
    trishoola_rasis = get_trine_rasis(rudra_rasi)

    return RudraTrishoolaIdentification(
        lagna_8th_special=lagna_8th_special,
        house_7_8th_special=house_7_8th_special,
        lagna_8th_lord=lagna_8th_lord,
        house_7_8th_lord=house_7_8th_lord,
        rudra_planet=rudra_planet,
        rudra_rasi=rudra_rasi,
        trishoola_rasis=trishoola_rasis,
        reason=reason,
    )


# ============================================================================
# MAHESWARA
# ============================================================================


def identify_maheswara(context: ChartContext) -> MaheswaraIdentification:
    """Identify Maheswara (lord of soul's liberation).

    Maheswara = 8th lord from Atma Karaka (AK)

    Special rules:
    1. If 8th lord from AK is exalted/own sign → take stronger of 8th/12th lord from him
    2. If Rahu/Ketu with AK or 8th from AK → use 6th lord instead
    3. If Rahu → use Mercury; If Ketu → use Jupiter

    Args:
        context: Chart context with atma_karaka

    Returns:
        MaheswaraIdentification with Maheswara details

    """
    ak_planet = context.atma_karaka
    ak_pos = context.planets[ak_planet]
    ak_rasi = ak_pos.rasi

    # Normal 8th house from AK
    eighth_from_ak = ak_rasi + 7  # 8th = +7
    if eighth_from_ak > TOTAL_RASIS:
        eighth_from_ak -= TOTAL_RASIS

    # Get 8th lord
    eighth_lord = get_rasi_lord(eighth_from_ak)
    maheswara = eighth_lord
    notes = f"8th lord from AK ({ak_planet.title()}) = {eighth_lord.title()}"

    # Check for Rahu/Ketu replacements
    if maheswara == "rahu":
        maheswara = "mercury"
        notes += " → Replaced Rahu with Mercury"
    elif maheswara in {"kethu", "ketu"}:
        maheswara = "jupiter"
        notes += " → Replaced Ketu with Jupiter"

    return MaheswaraIdentification(
        ak_planet=ak_planet,
        ak_rasi=ak_rasi,
        eighth_from_ak=eighth_from_ak,
        maheswara=maheswara,
        calculation_notes=notes,
    )


# ============================================================================
# METHOD OF THREE PAIRS
# ============================================================================


def evaluate_longevity_pair(
    pair_name: str,
    elem1_name: str,
    elem1_rasi: int,
    elem2_name: str,
    elem2_rasi: int,
) -> LongevityPairResult:
    """Evaluate one pair for longevity determination.

    Args:
        pair_name: Name of pair
        elem1_name: Name of first element
        elem1_rasi: Rasi of first element
        elem2_name: Name of second element
        elem2_rasi: Rasi of second element

    Returns:
        LongevityPairResult

    """
    type1 = get_rasi_type(elem1_rasi)
    type2 = get_rasi_type(elem2_rasi)

    result = LONGEVITY_PAIR_RULES[(type1, type2)]

    return LongevityPairResult(
        pair_name=pair_name,
        element1_name=elem1_name,
        element1_rasi=elem1_rasi,
        element1_type=type1,
        element2_name=elem2_name,
        element2_rasi=elem2_rasi,
        element2_type=type2,
        result=result,
    )


def apply_three_pairs_method(context: ChartContext) -> ThreePairsResult:
    """Apply Method of Three Pairs for longevity determination.

    Three pairs:
    1. Lagna lord + Special 8th lord
    2. Moon + Saturn
    3. Lagna + Horalagna

    Args:
        context: Chart context

    Returns:
        ThreePairsResult with final longevity category

    """
    # Pair 1: Lagna lord + 8th lord (special)
    lagna_lord = get_rasi_lord(context.lagna_rasi)
    special_8th = get_special_8th_house(context.lagna_rasi)
    eighth_lord = get_rasi_lord(special_8th)

    pair1 = evaluate_longevity_pair(
        "Lagna Lord + 8th Lord",
        f"{lagna_lord.title()} (Lagna lord)",
        context.planets[lagna_lord].rasi,
        f"{eighth_lord.title()} (8th lord)",
        context.planets[eighth_lord].rasi,
    )

    # Pair 2: Moon + Saturn
    moon_rasi = context.planets["moon"].rasi
    saturn_rasi = context.planets["saturn"].rasi

    pair2 = evaluate_longevity_pair(
        "Moon + Saturn",
        "Moon",
        moon_rasi,
        "Saturn",
        saturn_rasi,
    )

    # Pair 3: Lagna + Horalagna
    pair3 = evaluate_longevity_pair(
        "Lagna + Horalagna",
        "Lagna",
        context.lagna_rasi,
        "Horalagna",
        context.horalagna_rasi,
    )

    # Determine final result
    results = [pair1.result, pair2.result, pair3.result]
    result_counts = {
        LongevityCategory.SHORT_LIFE: results.count(LongevityCategory.SHORT_LIFE),
        LongevityCategory.MIDDLE_LIFE: results.count(LongevityCategory.MIDDLE_LIFE),
        LongevityCategory.LONG_LIFE: results.count(LongevityCategory.LONG_LIFE),
    }

    max_count = max(result_counts.values())

    if max_count == UNANIMOUS_PAIR_COUNT:
        # Unanimous
        final_category = results[0]
        agreement = "unanimous"
        paramaayush = LONGEVITY_RANGE_MAP[final_category][1]
        preferred_pair = None

    elif max_count == MAJORITY_PAIR_COUNT:
        # 2 vs 1
        agreement = "2_vs_1"
        # Find majority
        final_category = max(result_counts.items(), key=lambda x: x[1])[0]

        # Find minority
        minority = next(r for r in results if r != final_category)

        # Get paramaayush from table
        paramaayush = PARAMAAYUSH_TABLE[(final_category, minority)]
        preferred_pair = None

    else:
        # All three different (1-1-1 split)
        agreement = "split_3_ways"
        # Prefer pair 3 (Lagna + Horalagna)
        final_category = pair3.result
        paramaayush = LONGEVITY_RANGE_MAP[final_category][1]
        preferred_pair = "Lagna + Horalagna (default preference)"

        # Exception: If Moon in lagna or 7th, prefer pair 2
        moon_house = context.planets["moon"].house
        if moon_house in {HOUSE_1_SELF, HOUSE_7_PARTNERSHIP}:
            final_category = pair2.result
            paramaayush = LONGEVITY_RANGE_MAP[final_category][1]
            preferred_pair = "Moon + Saturn (Moon in 1st/7th)"

    return ThreePairsResult(
        pair1=pair1,
        pair2=pair2,
        pair3=pair3,
        final_category=final_category,
        paramaayush=paramaayush,
        agreement=agreement,
        preferred_pair=preferred_pair,
    )


# ============================================================================
# EIGHTH LORD METHOD
# ============================================================================


def apply_eighth_lord_method(context: ChartContext) -> EighthLordMethodResult:
    """Apply Eighth Lord Method for longevity determination.

    Uses stronger of lagna/7th as reference.
    Checks 8th lord's position from reference:
    - Quadrant (1,4,7,10) → Long life
    - Panaphara (2,5,8,11) → Middle life
    - Apoklima (3,6,9,12) → Short life

    Args:
        context: Chart context

    Returns:
        EighthLordMethodResult

    """
    # Determine stronger: lagna or 7th house
    # Simplified: use house with more planets or benefics
    lagna_planets = sum(1 for p in context.planets.values() if p.house == HOUSE_1_SELF)
    house_7_planets = sum(1 for p in context.planets.values() if p.house == HOUSE_7_PARTNERSHIP)

    if lagna_planets >= house_7_planets:
        reference = "lagna"
        ref_rasi = context.lagna_rasi
    else:
        reference = "7th_house"
        ref_rasi = context.house_7_rasi

    # Normal 8th house from reference (not special table)
    eighth_rasi = ref_rasi + 7
    if eighth_rasi > TOTAL_RASIS:
        eighth_rasi -= TOTAL_RASIS

    eighth_lord = get_rasi_lord(eighth_rasi)
    eighth_lord_rasi = context.planets[eighth_lord].rasi

    # Find house position of 8th lord from reference
    house_from_ref = get_house_from_rasi(ref_rasi, eighth_lord_rasi)

    # Categorize
    house_category = categorize_house_position(house_from_ref)

    # Determine longevity
    category_map = {
        HouseCategory.QUADRANT: LongevityCategory.LONG_LIFE,
        HouseCategory.PANAPHARA: LongevityCategory.MIDDLE_LIFE,
        HouseCategory.APOKLIMA: LongevityCategory.SHORT_LIFE,
    }

    longevity_category = category_map[house_category]

    return EighthLordMethodResult(
        reference_house=reference,
        reference_rasi=ref_rasi,
        eighth_lord=eighth_lord,
        eighth_lord_house_from_ref=house_from_ref,
        house_category=house_category,
        longevity_category=longevity_category,
    )


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================


def calculate_longevity_analysis(context: ChartContext) -> LongevityAnalysis:
    """Perform complete longevity analysis.

    Combines all methods:
    - Maraka identification
    - Rudra, Trishoola, Maheswara
    - Method of Three Pairs (primary)
    - Eighth Lord Method (secondary)

    Args:
        context: Complete chart context

    Returns:
        LongevityAnalysis with comprehensive results

    """
    # Identify all components
    marakas = identify_marakas(context)
    rudra_trishoola = identify_rudra_trishoola(context)
    maheswara = identify_maheswara(context)
    three_pairs = apply_three_pairs_method(context)
    eighth_lord = apply_eighth_lord_method(context)

    # Primary method = Three Pairs
    final_category = three_pairs.final_category
    estimated_range = LONGEVITY_RANGE_MAP[final_category]

    # Build assessment
    assessment_parts = [
        f"Longevity Category: {final_category.value.replace('_', ' ').title()}",
        f"Estimated Range: {estimated_range[0]}-{estimated_range[1]} years",
        f"Method of Three Pairs: {three_pairs.agreement}",
    ]

    if three_pairs.paramaayush:
        assessment_parts.append(f"Paramaayush (Max years): {three_pairs.paramaayush}")

    # Compare with Eighth Lord Method
    if eighth_lord.longevity_category == final_category:
        assessment_parts.append(f"Eighth Lord Method: AGREES ({eighth_lord.longevity_category.value})")
    else:
        assessment_parts.append(f"Eighth Lord Method: DIFFERS ({eighth_lord.longevity_category.value})")

    final_assessment = "\n".join(assessment_parts)

    # Warnings
    warnings = []
    if len(marakas.all_marakas) > MULTIPLE_MARAKA_THRESHOLD:
        warnings.append(f"Multiple maraka planets identified ({len(marakas.all_marakas)})")

    if final_category == LongevityCategory.SHORT_LIFE:
        warnings.append("Short life indicated - suggest remedial measures")

    if three_pairs.agreement == "split_3_ways":
        warnings.append("Three pairs gave different results - less certainty")

    return LongevityAnalysis(
        marakas=marakas,
        rudra_trishoola=rudra_trishoola,
        maheswara=maheswara,
        three_pairs_result=three_pairs,
        eighth_lord_result=eighth_lord,
        final_assessment=final_assessment,
        longevity_category=final_category,
        estimated_range=estimated_range,
        warnings=warnings,
    )
