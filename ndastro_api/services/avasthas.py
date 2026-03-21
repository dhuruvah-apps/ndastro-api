"""Avasthas (States) calculation utility.

Implements the vedic avastha system to determine planetary states and conditions.
Four types of avasthas are covered:
1. Age-Related Avasthas (5 states based on degree position)
2. Alertness Avasthas (3 states based on dignity)
3. Mood/Attitude Avasthas (15 states based on conditions)
4. Activity Avasthas - Sayanaadi (12 states based on complex formula)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from ndastro_api.core.utils.data_loader import astro_data

if TYPE_CHECKING:
    from ndastro_api.core.models.astro_system import Planet

# Constants for age avastha degree boundaries
AGE_DEGREE_BOUNDARY_1 = 6.0
AGE_DEGREE_BOUNDARY_2 = 12.0
AGE_DEGREE_BOUNDARY_3 = 18.0
AGE_DEGREE_BOUNDARY_4 = 24.0

# Constants for mood avastha
FIFTH_HOUSE = 5

# Constants for activity avastha
ACTIVITY_CYCLE = 12
STRENGTH_VALUES_MAP = {1: "drishti", 2: "cheshta", 3: "vicheshta", 0: "vicheshta"}


class AgeAvastha(str, Enum):
    """Age-related states based on planet's degree position in rasi."""

    SAISAVA = "saisava"  # Child (quarter strength)
    KUMAARA = "kumaara"  # Adolescent (half strength)
    YUVA = "yuva"  # Youth (full strength)
    VRIDDHA = "vriddha"  # Old (some strength)
    MRITA = "mrita"  # Dead (none)


class AlertnessAvastha(str, Enum):
    """Alertness states based on planet's dignity."""

    JAAGRITA = "jaagrita"  # Awake (exaltation or own rasi) - full results
    SWAPNA = "swapna"  # Dreaming (friendly/neutral rasi) - medium results
    SUSHUPTA = "sushupta"  # Asleep (debilitation or enemy) - negligible results


class MoodAvastha(str, Enum):
    """Attitude and mood states."""

    DEEPTA = "deepta"  # Bright (exaltation)
    SWASTHA = "swastha"  # Content (own rasi)
    MUDITA = "mudita"  # Delighted (good friend rasi)
    SAANTA = "saanta"  # Peaceful (friend rasi)
    DEENA = "deena"  # Sad/Depressed (neutral rasi)
    DUKHITA = "dukhita"  # Distressed (enemy rasi)
    VIKALA = "vikala"  # Crippled (joined by malefics)
    KHALA = "khala"  # Mischievous (in malefic rasi)
    KOPITA = "kopita"  # Angry (joined by Sun)
    LAJJITA = "lajjita"  # Ashamed (in 5th with malefics)
    GARVITA = "garvita"  # Proud (exaltation or moolatrikona)
    KSHUDHITA = "kshudhita"  # Hungry (enemy rasi/aspected by enemies)
    TRISHITA = "trishita"  # Thirsty (watery rasi aspected by enemies)
    KSHOBHITA = "kshobhita"  # Shaken (conjunct Sun aspected by malefics)


class ActivityAvastha(str, Enum):
    """Activity states - Sayanaadi Avasthas (12 states)."""

    SAYANA = "sayana"  # Lying down, resting
    UPAVESANA = "upavesana"  # Sitting down
    NETRAPAANI = "netrapaani"  # Eyes and hands
    PRAKAASANA = "prakaasana"  # Shining
    GAMANA = "gamana"  # Going (on the move)
    AAGAMANA = "aagamana"  # Coming, returning
    SABHAA = "sabhaa"  # Being at assembly
    AAGAMA = "aagama"  # Coming/Acquiring
    BHOJANA = "bhojana"  # Eating
    NRITYALIPSAA = "nrityalipsaa"  # Longing to dance
    KAUTUKA = "kautuka"  # Being eager
    NIDRAA = "nidraa"  # Sleeping


class ActivityStrength(str, Enum):
    """Strength classification for activity avasthas."""

    DRISHTI = "drishti"  # Medium results
    CHESHTA = "cheshta"  # Full results
    VICHESHTA = "vicheshta"  # Very little results


@dataclass
class AvasthaPlanetContext:
    """Context for mood and alertness avastha calculations."""

    planet_code: str
    house_number: int
    degree_in_rasi: float  # 0-30 degrees
    rasi_name: str
    rasi_number: int  # 1-12
    conjunction_planets: list[str] | None = None  # Planet codes
    aspecting_planets: list[str] | None = None  # Planet codes


@dataclass
class ActivityAvasthaPlanetContext:
    """Context for activity avastha (Sayanaadi) calculations."""

    constellation_number: int  # Nakshatra number 1-27
    planet_index: int  # Planet index 1-9
    navamsa_index: int  # Navamsa position 1-9
    moon_constellation: int  # Moon's nakshatra number
    ghati_at_birth: float  # Ghati number at birth
    lagna_rasi: int  # Lagna rasi number 1-12


def calculate_age_avastha(degree_in_rasi: float, rasi_number: int) -> tuple[AgeAvastha, float]:
    """Calculate age-related avastha based on degree position.

    Args:
        degree_in_rasi: Planet's degree position (0-30)
        rasi_number: Rasi number (1-12)

    Returns:
        Tuple of (AgeAvastha state, strength_multiplier)

    """
    # For odd rasis (1,3,5,7,9,11), count zodiacally
    # For even rasis (2,4,6,8,10,12), count anti-zodiacally
    is_odd_rasi = rasi_number % 2 == 1

    # Define boundaries and results for zodiacal (odd) rasis
    zodiacal_states = [
        (AGE_DEGREE_BOUNDARY_1, AgeAvastha.SAISAVA, 0.25),
        (AGE_DEGREE_BOUNDARY_2, AgeAvastha.KUMAARA, 0.50),
        (AGE_DEGREE_BOUNDARY_3, AgeAvastha.YUVA, 1.0),
        (AGE_DEGREE_BOUNDARY_4, AgeAvastha.VRIDDHA, 0.5),
        (float("inf"), AgeAvastha.MRITA, 0.0),
    ]

    # Anti-zodiacal states (reversed order for even rasis)
    anti_zodiacal_states = [
        (AGE_DEGREE_BOUNDARY_1, AgeAvastha.MRITA, 0.0),
        (AGE_DEGREE_BOUNDARY_2, AgeAvastha.VRIDDHA, 0.5),
        (AGE_DEGREE_BOUNDARY_3, AgeAvastha.YUVA, 1.0),
        (AGE_DEGREE_BOUNDARY_4, AgeAvastha.KUMAARA, 0.50),
        (float("inf"), AgeAvastha.SAISAVA, 0.25),
    ]

    states = zodiacal_states if is_odd_rasi else anti_zodiacal_states

    for boundary, avastha, strength in states:
        if degree_in_rasi < boundary:
            return avastha, strength

    return AgeAvastha.MRITA, 0.0


def _get_alertness_from_planet_dignity(planet: Planet, rasi_name: str, rasi_ruler: str) -> AlertnessAvastha | None:
    """Determine alertness state from planet's dignity position."""
    # Check exaltation
    if planet.exaltation and rasi_name == planet.exaltation.sign:
        return AlertnessAvastha.JAAGRITA

    # Check own rasi
    if rasi_name in planet.own_signs:
        return AlertnessAvastha.JAAGRITA

    # Check friendly/neutral
    if rasi_ruler in planet.natural_friends or rasi_ruler in planet.natural_neutrals:
        return AlertnessAvastha.SWAPNA

    # Check debilitation
    if planet.debilitation and rasi_name == planet.debilitation.sign:
        return AlertnessAvastha.SUSHUPTA

    # Check enemy
    if rasi_ruler in planet.natural_enemies:
        return AlertnessAvastha.SUSHUPTA

    return None


def calculate_alertness_avastha(planet_code: str, rasi_name: str) -> tuple[AlertnessAvastha, str]:
    """Calculate alertness-related avastha based on planetary dignity.

    Args:
        planet_code: Planet code (e.g., 'sun', 'mercury')
        rasi_name: Name of rasi occupied by planet

    Returns:
        Tuple of (AlertnessAvastha state, description)

    """
    planet = astro_data.get_planet_by_code(planet_code)
    if not planet:
        return AlertnessAvastha.SWAPNA, "Unknown planet"

    # Get rasi details
    rasi = astro_data.get_rasi_by_name(rasi_name)
    if not rasi or not rasi.ruler:
        return AlertnessAvastha.SWAPNA, "Default - dreaming"

    ruler_code = rasi.ruler.lower()

    # Get alertness state from dignity
    alertness = _get_alertness_from_planet_dignity(planet, rasi_name, ruler_code)
    if alertness is None:
        alertness = AlertnessAvastha.SWAPNA

    # Map state to description
    description_map = {
        AlertnessAvastha.JAAGRITA: "Fully awake",
        AlertnessAvastha.SWAPNA: "Dreaming",
        AlertnessAvastha.SUSHUPTA: "Asleep",
    }

    return alertness, description_map.get(alertness, "Unknown state")


def _check_mood_exaltation(planet: Planet, rasi_name: str) -> tuple[MoodAvastha, str] | None:
    """Check if planet is exalted."""
    if planet.exaltation and rasi_name == planet.exaltation.sign:
        return MoodAvastha.DEEPTA, "Exalted - bright"
    return None


def _check_mood_own_sign(planet: Planet, rasi_name: str) -> tuple[MoodAvastha, str] | None:
    """Check if planet is in own sign."""
    if rasi_name in planet.own_signs:
        return MoodAvastha.SWASTHA, "Own sign - content"
    return None


def _check_mood_moolatrikona(planet: Planet, rasi_name: str) -> tuple[MoodAvastha, str] | None:
    """Check if planet is in moolatrikona."""
    if planet.moolatrikona and rasi_name == planet.moolatrikona.sign:
        return MoodAvastha.GARVITA, "Moolatrikona - proud"
    return None


def _check_mood_debilitation(planet: Planet, rasi_name: str) -> tuple[MoodAvastha, str] | None:
    """Check if planet is debilitated."""
    if planet.debilitation and rasi_name == planet.debilitation.sign:
        return MoodAvastha.DUKHITA, "Debilitated - distressed"
    return None


def _check_mood_malefic_conjunction(
    context: AvasthaPlanetContext,
) -> tuple[MoodAvastha, str] | None:
    """Check conjunction with malefics."""
    if not context.conjunction_planets:
        return None

    malefics = {"mars barycenter", "saturn barycenter", "rahu", "kethu"}
    for conj_planet in context.conjunction_planets:
        if conj_planet.lower() in malefics:
            # Check if in 5th house
            if context.house_number == FIFTH_HOUSE:
                return MoodAvastha.LAJJITA, "In 5th with malefics - ashamed"
            return MoodAvastha.VIKALA, "Joined by malefics - crippled"
    return None


def _check_mood_sun_conjunction(
    context: AvasthaPlanetContext,
) -> tuple[MoodAvastha, str] | None:
    """Check conjunction with Sun."""
    if context.conjunction_planets and "sun" in context.conjunction_planets:
        return MoodAvastha.KOPITA, "Joined by Sun - angry"
    return None


def _check_mood_friendly_rasi(planet: Planet, context: AvasthaPlanetContext) -> tuple[MoodAvastha, str] | None:
    """Check friendly/good friend rasi."""
    rasi = astro_data.get_rasi_by_name(context.rasi_name)
    if not rasi or not rasi.ruler:
        return None

    ruler_code = rasi.ruler.lower()
    if ruler_code not in planet.natural_friends:
        return None

    # If also aspected by benefics, return Mudita
    if context.aspecting_planets:
        benefics = {"jupiter barycenter", "venus", "mercury", "moon"}
        for asp_planet in context.aspecting_planets:
            if asp_planet.lower() in benefics:
                return MoodAvastha.MUDITA, "Good friend rasi - delighted"

    return MoodAvastha.SAANTA, "Friend rasi - peaceful"


def _check_mood_neutral_rasi(planet: Planet, context: AvasthaPlanetContext) -> tuple[MoodAvastha, str] | None:
    """Check neutral rasi."""
    rasi = astro_data.get_rasi_by_name(context.rasi_name)
    if not rasi or not rasi.ruler:
        return None

    ruler_code = rasi.ruler.lower()
    if ruler_code in planet.natural_neutrals:
        return MoodAvastha.DEENA, "Neutral rasi - sad"
    return None


def _check_mood_enemy_rasi(planet: Planet, context: AvasthaPlanetContext) -> tuple[MoodAvastha, str] | None:
    """Check enemy rasi."""
    rasi = astro_data.get_rasi_by_name(context.rasi_name)
    if not rasi or not rasi.ruler:
        return None

    ruler_code = rasi.ruler.lower()
    if ruler_code in planet.natural_enemies:
        return MoodAvastha.DUKHITA, "Enemy rasi - distressed"
    return None


def calculate_mood_avastha(context: AvasthaPlanetContext) -> tuple[MoodAvastha, str]:
    """Calculate mood/attitude avastha based on various placements.

    Args:
        context: AvasthaPlanetContext with planet and chart details

    Returns:
        Tuple of (MoodAvastha state, description)

    """
    planet = astro_data.get_planet_by_code(context.planet_code)
    if not planet:
        return MoodAvastha.DEENA, "Unknown planet"

    # Check conditions in order of priority
    checks = [
        _check_mood_exaltation(planet, context.rasi_name),
        _check_mood_own_sign(planet, context.rasi_name),
        _check_mood_moolatrikona(planet, context.rasi_name),
        _check_mood_debilitation(planet, context.rasi_name),
        _check_mood_malefic_conjunction(context),
        _check_mood_sun_conjunction(context),
        _check_mood_friendly_rasi(planet, context),
        _check_mood_neutral_rasi(planet, context),
        _check_mood_enemy_rasi(planet, context),
    ]

    for result in checks:
        if result is not None:
            return result

    return MoodAvastha.DEENA, "Default - depressed"


def calculate_activity_avastha(
    context: ActivityAvasthaPlanetContext,
) -> tuple[ActivityAvastha, ActivityStrength, str]:
    """Calculate Sayanaadi activity avastha (most complex).

    Uses the classical Parasara formula:
    (C * P * A) + M + G + L, divide by 12, take remainder

    Args:
        context: ActivityAvasthaPlanetContext with all calculation parameters

    Returns:
        Tuple of (ActivityAvastha, ActivityStrength, description)

    """
    # Core formula: (C * P * A) + M + G + L
    base_value = (
        (context.constellation_number * context.planet_index * context.navamsa_index)
        + context.moon_constellation
        + int(context.ghati_at_birth)
        + context.lagna_rasi
    )

    # Divide by 12 and get remainder for avastha index
    avastha_index_val: int = int(base_value % ACTIVITY_CYCLE)
    if avastha_index_val == 0:
        avastha_index_val = ACTIVITY_CYCLE

    # Map index to avastha
    avastha_map: dict[int, ActivityAvastha] = {
        1: ActivityAvastha.SAYANA,
        2: ActivityAvastha.UPAVESANA,
        3: ActivityAvastha.NETRAPAANI,
        4: ActivityAvastha.PRAKAASANA,
        5: ActivityAvastha.GAMANA,
        6: ActivityAvastha.AAGAMANA,
        7: ActivityAvastha.SABHAA,
        8: ActivityAvastha.AAGAMA,
        9: ActivityAvastha.BHOJANA,
        10: ActivityAvastha.NRITYALIPSAA,
        11: ActivityAvastha.KAUTUKA,
        12: ActivityAvastha.NIDRAA,
    }

    avastha = avastha_map.get(avastha_index_val, ActivityAvastha.SAYANA)

    # Calculate strength based on planet and avastha
    strength = _calculate_activity_strength(avastha_index_val, context.planet_index)

    description = f"{avastha.value} - {strength.value}"

    return avastha, strength, description


def _calculate_activity_strength(avastha_index: int, planet_index: int) -> ActivityStrength:
    """Calculate activity strength (Cheshta, Drishti, or Vicheshta).

    Formula: ([avastha_index]² + first_sound_number) % 12, add planet adjustment, % 3
    Result: 1=Drishti, 2=Cheshta, 0/3=Vicheshta

    """
    # First sound values from classical texts (simplified)
    first_sound_values: dict[ActivityAvastha, int] = {
        ActivityAvastha.SAYANA: 1,
        ActivityAvastha.UPAVESANA: 1,
        ActivityAvastha.NETRAPAANI: 5,
        ActivityAvastha.PRAKAASANA: 1,
        ActivityAvastha.GAMANA: 3,
        ActivityAvastha.AAGAMANA: 1,
        ActivityAvastha.SABHAA: 1,
        ActivityAvastha.AAGAMA: 1,
        ActivityAvastha.BHOJANA: 2,
        ActivityAvastha.NRITYALIPSAA: 2,
        ActivityAvastha.KAUTUKA: 2,
        ActivityAvastha.NIDRAA: 2,
    }

    avastha_map: dict[int, ActivityAvastha] = {
        1: ActivityAvastha.SAYANA,
        2: ActivityAvastha.UPAVESANA,
        3: ActivityAvastha.NETRAPAANI,
        4: ActivityAvastha.PRAKAASANA,
        5: ActivityAvastha.GAMANA,
        6: ActivityAvastha.AAGAMANA,
        7: ActivityAvastha.SABHAA,
        8: ActivityAvastha.AAGAMA,
        9: ActivityAvastha.BHOJANA,
        10: ActivityAvastha.NRITYALIPSAA,
        11: ActivityAvastha.KAUTUKA,
        12: ActivityAvastha.NIDRAA,
    }

    avastha = avastha_map.get(avastha_index, ActivityAvastha.SAYANA)
    sound_value = first_sound_values.get(avastha, 1)

    # Calculate strength
    square_value = (avastha_index * avastha_index) + sound_value
    remainder = square_value % ACTIVITY_CYCLE

    # Planet adjustment (5 for Sun/Jupiter, 2 for Moon/Mars, 3 for Mercury/Venus/Saturn)
    planet_adjustment_map: dict[int, int] = {
        1: 5,
        2: 2,
        3: 3,
        4: 2,
        5: 2,
        6: 3,
        7: 3,
        8: 4,
        9: 4,
    }
    adjustment = planet_adjustment_map.get(planet_index, 3)

    final_value = (remainder + adjustment) % 3
    if final_value == 0:
        final_value = 3

    # Map to strength
    strength_map: dict[int, ActivityStrength] = {
        1: ActivityStrength.DRISHTI,
        2: ActivityStrength.CHESHTA,
        3: ActivityStrength.VICHESHTA,
    }
    return strength_map.get(final_value, ActivityStrength.VICHESHTA)


def get_age_avastha_interpretation(planet_code: str, avastha: AgeAvastha) -> str:
    """Get interpretation text for age avastha by planet."""
    interpretations: dict[str, dict[AgeAvastha, str]] = {
        "sun": {
            AgeAvastha.SAISAVA: "Sun in childhood: weak vitality, less assertiveness",
            AgeAvastha.KUMAARA: "Sun in adolescence: developing confidence",
            AgeAvastha.YUVA: "Sun in youth: maximum vitality and authority",
            AgeAvastha.VRIDDHA: "Sun in old age: waning energy, wisdom",
            AgeAvastha.MRITA: "Sun in death state: minimal impact on ego/will",
        },
        "moon": {
            AgeAvastha.SAISAVA: "Moon in childhood: emotional vulnerability",
            AgeAvastha.KUMAARA: "Moon in adolescence: developing emotional maturity",
            AgeAvastha.YUVA: "Moon in youth: full emotional expression",
            AgeAvastha.VRIDDHA: "Moon in old age: experienced, withdrawn emotions",
            AgeAvastha.MRITA: "Moon in death state: emotional instability",
        },
        "mercury": {
            AgeAvastha.SAISAVA: "Mercury in childhood: learning phase",
            AgeAvastha.KUMAARA: "Mercury in adolescence: developing intellect",
            AgeAvastha.YUVA: "Mercury in youth: sharp intellect and communication",
            AgeAvastha.VRIDDHA: "Mercury in old age: experienced but slower",
            AgeAvastha.MRITA: "Mercury in death state: poor communication",
        },
    }

    planet_lower = planet_code.lower().replace(" barycenter", "")
    if planet_lower in interpretations:
        return interpretations[planet_lower].get(avastha, f"{avastha.value} state")

    return f"Planet in {avastha.value} state"


def get_alertness_avastha_interpretation(planet_code: str, avastha: AlertnessAvastha) -> str:
    """Get interpretation for alertness avastha by planet."""
    interpretations: dict[str, dict[AlertnessAvastha, str]] = {
        "sun": {
            AlertnessAvastha.JAAGRITA: "Sun fully awake: radiates authority, leadership",
            AlertnessAvastha.SWAPNA: "Sun dreaming: moderate will, diplomatic",
            AlertnessAvastha.SUSHUPTA: "Sun asleep: weak will, indecisive",
        },
        "moon": {
            AlertnessAvastha.JAAGRITA: "Moon fully awake: strong emotions, nurturing",
            AlertnessAvastha.SWAPNA: "Moon dreaming: changeable moods, adaptable",
            AlertnessAvastha.SUSHUPTA: "Moon asleep: emotional weakness, instability",
        },
        "mars": {
            AlertnessAvastha.JAAGRITA: "Mars fully awake: courageous, aggressive",
            AlertnessAvastha.SWAPNA: "Mars dreaming: moderate courage, tactical",
            AlertnessAvastha.SUSHUPTA: "Mars asleep: weak courage, passive",
        },
        "mercury": {
            AlertnessAvastha.JAAGRITA: "Mercury fully awake: sharp intellect, communicative",
            AlertnessAvastha.SWAPNA: "Mercury dreaming: learning oriented, curious",
            AlertnessAvastha.SUSHUPTA: "Mercury asleep: confused, poor communication",
        },
        "jupiter": {
            AlertnessAvastha.JAAGRITA: "Jupiter fully awake: generous, wise teacher",
            AlertnessAvastha.SWAPNA: "Jupiter dreaming: helpful, moderate wisdom",
            AlertnessAvastha.SUSHUPTA: "Jupiter asleep: poor judgment, stingy",
        },
        "venus": {
            AlertnessAvastha.JAAGRITA: "Venus fully awake: attractive, artistic",
            AlertnessAvastha.SWAPNA: "Venus dreaming: romantic, pleasurable",
            AlertnessAvastha.SUSHUPTA: "Venus asleep: undesirable, prone to conflict",
        },
        "saturn": {
            AlertnessAvastha.JAAGRITA: "Saturn fully awake: disciplined, responsible",
            AlertnessAvastha.SWAPNA: "Saturn dreaming: hardworking, moderate control",
            AlertnessAvastha.SUSHUPTA: "Saturn asleep: weak discipline, suffering",
        },
    }

    planet_lower = planet_code.lower().replace(" barycenter", "")
    if planet_lower in interpretations:
        return interpretations[planet_lower].get(avastha, f"{avastha.value} state")

    return f"Planet in {avastha.value} state"


def get_mood_avastha_interpretation(planet_code: str, avastha: MoodAvastha) -> str:
    """Get interpretation for mood avastha by planet."""
    interpretations: dict[str, dict[MoodAvastha, str]] = {
        "sun": {
            MoodAvastha.DEEPTA: "Sun bright: supreme authority, victory",
            MoodAvastha.SWASTHA: "Sun content: confident, giving",
            MoodAvastha.MUDITA: "Sun delighted: generous, admired",
            MoodAvastha.SAANTA: "Sun peaceful: balanced, diplomatic",
            MoodAvastha.DEENA: "Sun sad: weak authority, humble",
            MoodAvastha.DUKHITA: "Sun distressed: obstacles to power",
            MoodAvastha.VIKALA: "Sun crippled: diminished authority",
            MoodAvastha.KHALA: "Sun mischievous: misuse of power",
            MoodAvastha.KOPITA: "Sun angry: excessive ego, conflicts",
            MoodAvastha.LAJJITA: "Sun ashamed: lack of confidence",
            MoodAvastha.GARVITA: "Sun proud: self-respect, dignity",
            MoodAvastha.KSHUDHITA: "Sun hungry: seeks recognition",
            MoodAvastha.TRISHITA: "Sun thirsty: craves attention",
            MoodAvastha.KSHOBHITA: "Sun shaken: disturbed authority",
        },
        "moon": {
            MoodAvastha.DEEPTA: "Moon bright: clear mind, happiness",
            MoodAvastha.SWASTHA: "Moon content: emotional happiness",
            MoodAvastha.MUDITA: "Moon delighted: joy, pleasure",
            MoodAvastha.SAANTA: "Moon peaceful: calm, serene",
            MoodAvastha.DEENA: "Moon sad: depression, anxiety",
            MoodAvastha.DUKHITA: "Moon distressed: emotional pain",
            MoodAvastha.VIKALA: "Moon crippled: mental weakness",
            MoodAvastha.KHALA: "Moon mischievous: emotional turmoil",
            MoodAvastha.KOPITA: "Moon angry: irritability, outbursts",
            MoodAvastha.LAJJITA: "Moon ashamed: insecurity, shyness",
            MoodAvastha.GARVITA: "Moon proud: confidence, satisfaction",
            MoodAvastha.KSHUDHITA: "Moon hungry: emotional need",
            MoodAvastha.TRISHITA: "Moon thirsty: desires, cravings",
            MoodAvastha.KSHOBHITA: "Moon shaken: emotional disturbance",
        },
        "mars": {
            MoodAvastha.DEEPTA: "Mars bright: courageous, victorious",
            MoodAvastha.SWASTHA: "Mars content: confident warrior",
            MoodAvastha.MUDITA: "Mars delighted: joyful aggression",
            MoodAvastha.SAANTA: "Mars peaceful: controlled courage",
            MoodAvastha.DEENA: "Mars sad: cowardly, weak",
            MoodAvastha.DUKHITA: "Mars distressed: injuries, losses",
            MoodAvastha.VIKALA: "Mars crippled: lack of courage",
            MoodAvastha.KHALA: "Mars mischievous: reckless, violent",
            MoodAvastha.KOPITA: "Mars angry: rage, accidents",
            MoodAvastha.LAJJITA: "Mars ashamed: humiliated",
            MoodAvastha.GARVITA: "Mars proud: heroic, bold",
            MoodAvastha.KSHUDHITA: "Mars hungry: intense desire",
            MoodAvastha.TRISHITA: "Mars thirsty: competitive",
            MoodAvastha.KSHOBHITA: "Mars shaken: aggressive disturbance",
        },
    }

    planet_lower = planet_code.lower().replace(" barycenter", "")
    if planet_lower in interpretations:
        return interpretations[planet_lower].get(avastha, f"{avastha.value} state")

    # Default interpretations for planets not in map
    default_interpretations: dict[MoodAvastha, str] = {
        MoodAvastha.DEEPTA: "Excellent state, full strength",
        MoodAvastha.SWASTHA: "Content state, normal function",
        MoodAvastha.MUDITA: "Delighted state, positive",
        MoodAvastha.SAANTA: "Peaceful state, balanced",
        MoodAvastha.DEENA: "Depressed state, weakened",
        MoodAvastha.DUKHITA: "Distressed state, difficult",
        MoodAvastha.VIKALA: "Crippled state, impaired",
        MoodAvastha.KHALA: "Mischievous state, troubling",
        MoodAvastha.KOPITA: "Angry state, volatile",
        MoodAvastha.LAJJITA: "Ashamed state, inhibited",
        MoodAvastha.GARVITA: "Proud state, exalted",
        MoodAvastha.KSHUDHITA: "Hungry state, needy",
        MoodAvastha.TRISHITA: "Thirsty state, desiring",
        MoodAvastha.KSHOBHITA: "Shaken state, disturbed",
    }

    return default_interpretations.get(avastha, f"{avastha.value} state")


def get_activity_avastha_interpretation(_planet_code: str, avastha: ActivityAvastha, strength: ActivityStrength) -> str:
    """Get interpretation for activity avastha by planet and strength."""
    activity_meanings: dict[ActivityAvastha, str] = {
        ActivityAvastha.SAYANA: "Lying down, rest, recovery",
        ActivityAvastha.UPAVESANA: "Sitting, planning, consideration",
        ActivityAvastha.NETRAPAANI: "Eyes and hands, perception, action",
        ActivityAvastha.PRAKAASANA: "Shining, visibility, fame",
        ActivityAvastha.GAMANA: "Going, movement, travel",
        ActivityAvastha.AAGAMANA: "Coming back, return, retrieval",
        ActivityAvastha.SABHAA: "Being at assembly, social activity",
        ActivityAvastha.AAGAMA: "Acquiring, obtaining, gains",
        ActivityAvastha.BHOJANA: "Eating, consumption, satisfaction",
        ActivityAvastha.NRITYALIPSAA: "Desire to dance, expression",
        ActivityAvastha.KAUTUKA: "Eagerness, enthusiasm, interest",
        ActivityAvastha.NIDRAA: "Sleeping, dormancy, passivity",
    }

    strength_map = {
        ActivityStrength.CHESHTA: "Full strength",
        ActivityStrength.DRISHTI: "Medium strength",
        ActivityStrength.VICHESHTA: "Minimal strength",
    }

    meaning = activity_meanings.get(avastha, avastha.value)
    strength_desc = strength_map.get(strength, "")

    return f"{meaning} ({strength_desc})"


@dataclass
class AvasthaSummary:
    """Complete avastha summary for a planet."""

    planet_code: str
    age_avastha: str  # Name of age avastha
    age_interpretation: str
    alertness_avastha: str  # Name of alertness avastha
    alertness_interpretation: str
    mood_avastha: str  # Name of mood avastha
    mood_interpretation: str
    activity_avastha: str | None = None  # Name of activity avastha
    activity_strength: str | None = None  # (Cheshta, Drishti, Vicheshta)
    activity_interpretation: str | None = None


def get_all_avasthas(context: AvasthaPlanetContext) -> AvasthaSummary:
    """Get all four avastha types for a planet in one call.

    Args:
        context: AvasthaPlanetContext with planet and chart details

    Returns:
        AvasthaSummary with all avastha information

    """
    # Calculate age avastha
    age_state, _ = calculate_age_avastha(context.degree_in_rasi, context.rasi_number)
    age_interp = get_age_avastha_interpretation(context.planet_code, age_state)

    # Calculate alertness avastha
    alertness_state, _ = calculate_alertness_avastha(context.planet_code, context.rasi_name)
    alertness_interp = get_alertness_avastha_interpretation(context.planet_code, alertness_state)

    # Calculate mood avastha
    mood_state, _ = calculate_mood_avastha(context)
    mood_interp = get_mood_avastha_interpretation(context.planet_code, mood_state)

    return AvasthaSummary(
        planet_code=context.planet_code,
        age_avastha=age_state.value,
        age_interpretation=age_interp,
        alertness_avastha=alertness_state.value,
        alertness_interpretation=alertness_interp,
        mood_avastha=mood_state.value,
        mood_interpretation=mood_interp,
    )


def get_all_avasthas_with_activity(
    context: AvasthaPlanetContext,
    activity_context: ActivityAvasthaPlanetContext,
) -> AvasthaSummary:
    """Get all four avastha types including activity avasthas.

    Args:
        context: AvasthaPlanetContext with planet and chart details
        activity_context: ActivityAvasthaPlanetContext for activity calculations

    Returns:
        AvasthaSummary with all avastha information including activity

    """
    # Get base summary
    summary = get_all_avasthas(context)

    # Add activity avastha
    activity_state, activity_strength, _ = calculate_activity_avastha(activity_context)
    activity_interp = get_activity_avastha_interpretation(context.planet_code, activity_state, activity_strength)

    # Update summary with activity info
    summary.activity_avastha = activity_state.value
    summary.activity_strength = activity_strength.value
    summary.activity_interpretation = activity_interp

    return summary
