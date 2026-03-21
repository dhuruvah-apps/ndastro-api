"""Dataclass models for astrological reference data.

These models provide type-safe representations of the JSON data files
in ndastro_api/resources/data/
"""

from dataclasses import field
from typing import Literal, TypeAlias

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

PlanetCode: TypeAlias = Literal["SU", "MO", "MA", "ME", "JU", "VE", "SA", "RA", "KE", "EA", "AS", ""]
AstronomicalCode: TypeAlias = Literal[
    "sun", "moon", "mars barycenter", "mercury", "jupiter barycenter", "venus", "saturn barycenter", "rahu", "kethu", "earth", "ascendant", ""
]
RasiCode: TypeAlias = Literal["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11", "R12", ""]
HouseCode: TypeAlias = Literal["H01", "H02", "H03", "H04", "H05", "H06", "H07", "H08", "H09", "H10", "H11", "H12", ""]
NakshatraCode: TypeAlias = Literal[
    "N01",
    "N02",
    "N03",
    "N04",
    "N05",
    "N06",
    "N07",
    "N08",
    "N09",
    "N10",
    "N11",
    "N12",
    "N13",
    "N14",
    "N15",
    "N16",
    "N17",
    "N18",
    "N19",
    "N20",
    "N21",
    "N22",
    "N23",
    "N24",
    "N25",
    "N26",
    "N27",
    "",
]

# ============================================================================
# Planet Models
# ============================================================================


@dataclass
class DegreeInfo:
    """Degree information for exaltation/debilitation."""

    sign: RasiCode | None = None
    deep_exaltation_degree: float | None = None
    deep_debilitation_degree: float | None = None


@dataclass
class DegreeRange:
    """Degree range with start and end values."""

    start: float = 0.0
    end: float = 0.0


@dataclass
class MoolatrikonaInfo:
    """Moolatrikona sign and degree range.

    The degree_range can be either a DegreeRange object (preferred) or a string (for backward compatibility).
    """

    sign: RasiCode = ""
    degree_range: DegreeRange | str = ""


@dataclass
class CompoundRelationship:
    """Compound friendship relationships."""

    best_friend: list["PlanetCode"] = field(default_factory=list)
    friend: list["PlanetCode"] = field(default_factory=list)
    neutral: list["PlanetCode"] = field(default_factory=list)
    enemy: list["PlanetCode"] = field(default_factory=list)
    bitter_enemy: list["PlanetCode"] = field(default_factory=list)


@dataclass(config=ConfigDict(extra="allow", arbitrary_types_allowed=True))
class Planet:
    """Planet data model.

    Attributes:
        name (str): The common name of the planet.
        code (PlanetCode): The unique code identifier for the planet.
        astronomical_code (AstronomicalCode): The astronomical code for the planet (e.g., 'sun' for Sun).
        sanskrit_name (str): The Sanskrit name of the planet.
        description (str): A brief description of the planet.
        element_panchamahabhuta (str): The Panchamahabhuta element associated with the planet.
        gender (str): The gender associated with the planet.
        nature (str): The nature of the planet (e.g., benefic, malefic).
        caste (str): The caste classification of the planet.
        guna (str): The guna classification of the planet.
        presiding_deity (str): The presiding deity of the planet.
        color (str): The color associated with the planet.
        gemstone (str): The gemstone associated with the planet.
        metal (str): The metal associated with the planet.
        day (str): The day of the week associated with the planet.
        direction (str): The direction associated with the planet.
        latitude (float): The latitude of the planet's position.
        longitude (float): The longitude of the planet's position.
        primary_signification (str): The primary significations of the planet.
        body_parts (list[str]): The body parts associated with the planet.
        own_signs (list[str]): The zodiac signs owned by the planet.
        exaltation (DegreeInfo | None): The exaltation information for the planet.
        debilitation (DegreeInfo | None): The debilitation information for the planet.
        moolatrikona (MoolatrikonaInfo | None): The moolatrikona information for the planet.
        vargottama_status (str | None): The vargottama status of the planet.
        posited_at (HouseCode): The house position code (H1-H12).
        natural_friends (list[PlanetCode]): The natural friends of the planet.
        natural_enemies (list[PlanetCode]): The natural enemies of the planet.
        natural_neutrals (list[PlanetCode]): The natural neutrals of the planet.
        temporary_friends (list[PlanetCode] | None): The temporary friends of the planet.
        temporary_enemies (list[PlanetCode] | None): The temporary enemies of the planet.
        compound_relationship (CompoundRelationship | None): The compound relationship of the planet.
        functional_benefic (list[PlanetCode] | None): The functional benefics for the planet.
        functional_malefic (list[PlanetCode] | None): The functional malefics for the planet.
        maraka_status (str | None): The maraka status of the planet.
        karaka_for (list[str]): The significations for which the planet is a karaka.
        shadbala_total (float | None): The total shadbala strength of the planet.
        is_combust (bool | None): Whether the planet is combust.
        dig_bala_score (float | None): The dig bala score of the planet.
        is_retrograde (bool | None): Whether the planet is retrograde.
        is_ascendant (bool | None): Whether the planet is the ascendant.
        nirayana_longitude (float | None): The nirayana (sidereal) longitude of the planet.
        rasi_occupied (RasiCode | None): The zodiac sign (rasi) occupied by the planet.
        advanced_by (float | None): The advancement value of the planet.
        nakshatra (NakshatraCode | None): The nakshatra occupied by the planet.
        pada (int | None): The pada (quarter) of the nakshatra occupied by the planet.
        represents (list[str]): The significations represented by the planet.
        keywords (list[str]): Keywords associated with the planet.
        orbit (str): The orbital characteristics of the planet.
        aspects (list[HouseCode] | None): The house aspects formed by the planet (e.g., ['H7'], ['H4', 'H7', 'H8']).

    """

    name: str = ""
    code: PlanetCode = ""
    astronomical_code: AstronomicalCode = ""
    sanskrit_name: str = ""
    description: str = ""
    element_panchamahabhuta: str | None = None
    gender: str = ""
    nature: str = ""
    caste: str = ""
    guna: str = ""
    presiding_deity: str = ""
    color: str = ""
    gemstone: str = ""
    metal: str = ""
    day: str = ""
    direction: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    posited_at: HouseCode = ""
    nirayana_longitude: float | None = None
    rasi_occupied: RasiCode | None = None
    advanced_by: float | None = None
    nakshatra: NakshatraCode | None = None
    pada: int | None = None
    primary_signification: str = ""
    body_parts: list[str] = field(default_factory=list)
    own_signs: list[str] = field(default_factory=list)
    exaltation: DegreeInfo | None = None
    debilitation: DegreeInfo | None = None
    moolatrikona: MoolatrikonaInfo | None = None
    vargottama_status: str | None = None
    natural_friends: list["PlanetCode"] = field(default_factory=list)
    natural_enemies: list["PlanetCode"] = field(default_factory=list)
    natural_neutrals: list["PlanetCode"] = field(default_factory=list)
    temporary_friends: list["PlanetCode"] | None = None
    temporary_enemies: list["PlanetCode"] | None = None
    compound_relationship: CompoundRelationship | None = None
    functional_benefic: list["PlanetCode"] | None = None
    functional_malefic: list["PlanetCode"] | None = None
    maraka_status: str | None = None
    karaka_for: list[str] = field(default_factory=list)
    shadbala_total: float | None = None
    is_combust: bool | None = False
    dig_bala_score: float | None = None
    is_retrograde: bool | None = False
    is_ascendant: bool | None = False
    represents: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    orbit: str = ""
    aspects: list[HouseCode] | None = None


# ============================================================================
# Rasi (Zodiac Sign) Models
# ============================================================================


@dataclass
class Rasi:
    """Rasi (Zodiac Sign) data model.

    Attributes:
        name (str): The common name of the zodiac sign.
        code (RasiCode): The unique code identifier for the rasi.
        description (str): A brief description of the rasi.
        symbol (str): The symbol representing the rasi.
        number (int): The numerical position of the rasi in the zodiac (1-12).
        element_panchamahabhuta (str): The Panchamahabhuta element associated with the rasi.
        quality (str): The quality classification of the rasi (cardinal, fixed, mutable).
        gender (str): The gender associated with the rasi.
        ruler (PlanetCode): The ruling planet of the rasi.
        exalted_planet (PlanetCode): The planet that is exalted in this rasi.
        debilitated_planet (PlanetCode): The planet that is debilitated in this rasi.
        moolatrikona_planet (PlanetCode): The planet in moolatrikona in this rasi.
        body_parts (list[str]): The body parts associated with the rasi.
        nature (str): The nature of the rasi (e.g., benefic, malefic).
        caste (str): The caste classification of the rasi.
        guna (str): The guna classification of the rasi.
        direction (str): The direction associated with the rasi.
        color (str): The color associated with the rasi.
        lifespan (str): The lifespan characteristics associated with the rasi.
        varna (str): The varna (color/class) classification of the rasi.
        animal (str): The animal symbol associated with the rasi.
        duration (str): The duration of the rasi in the zodiac.
        fertile (bool): Whether the rasi is considered fertile.
        human_animal (str): The human or animal nature of the rasi.
        keywords (list[str]): Keywords associated with the rasi.
        represents (list[str]): The significations represented by the rasi.

    """

    name: str = ""
    code: RasiCode = ""
    description: str = ""
    symbol: str = ""
    number: int = 0
    element_panchamahabhuta: str = ""
    quality: str = ""
    gender: str = ""
    ruler: PlanetCode = ""
    exalted_planet: PlanetCode = ""
    debilitated_planet: PlanetCode = ""
    moolatrikona_planet: PlanetCode = ""
    body_parts: list[str] = field(default_factory=list)
    nature: str = ""
    caste: str = ""
    guna: str = ""
    direction: str = ""
    color: str = ""
    lifespan: str = ""
    varna: str = ""
    animal: str = ""
    duration: str = ""
    fertile: bool = False
    human_animal: str = ""
    keywords: list[str] = field(default_factory=list)
    represents: list[str] = field(default_factory=list)


# ============================================================================
# Nakshatra Models
# ============================================================================


@dataclass
class NakshatraPada:
    """Nakshatra Pada (quarter) information.

    Attributes:
           pada_number (int): The quarter number of the nakshatra (1-4).
           start_degree (float): The starting degree for this pada within the nakshatra.
           end_degree (float): The ending degree for this pada within the nakshatra.
           navamsa_rasi (RasiCode): The navamsa (9th divisional chart) sign for this pada.
           navamsa_lord (PlanetCode): The ruling planet of the navamsa sign.
           sound (str): The seed sound (beeja mantra) associated with this pada.
           motivation (str): The primary motivation or drive of this pada.
           characteristics (str): Key characteristics and traits of this pada.
           planetary_influence (list[PlanetCode]): The planetary influences governing this pada.
           focus (str): The primary focus or area of emphasis for this pada.

    """

    pada_number: int = 0
    start_degree: float = 0.0
    end_degree: float = 0.0
    navamsa_rasi: RasiCode = ""
    navamsa_lord: PlanetCode = ""
    sound: str = ""
    motivation: str = ""
    characteristics: str = ""
    planetary_influence: list[PlanetCode] = field(default_factory=list)
    focus: str = ""


@dataclass
class Nakshatra:
    """Nakshatra data model.

    Represents a Nakshatra (lunar mansion) in Vedic astrology with comprehensive
    astrological and mythological information.

    Attributes:
        name (str): The name of the Nakshatra.
        code (NakshatraCode): The unique code identifier for the Nakshatra (N01-N27).
        number (int): The sequential number of the Nakshatra (1-27).
        description (str): Detailed description of the Nakshatra's characteristics.
        ruling_planet (PlanetCode): The planetary ruler of the Nakshatra.
        ruling_deity (str): The presiding deity associated with the Nakshatra.
        symbol (str): The symbolic representation of the Nakshatra.
        animal_symbol (str): The animal symbol associated with the Nakshatra.
        yoni (str): The yoni (animal nature) classification of the Nakshatra.
        element_panchamahabhuta (str): The elemental correspondence from the five great elements.
        gana (str): The gana (group) classification: Deva, Manushya, or Rakshasa.
        gender (str): The gender association of the Nakshatra.
        caste (str): The caste classification of the Nakshatra.
        nature (str): The nature or temperament of the Nakshatra.
        quality (str): The quality or gunas associated with the Nakshatra.
        body_parts (list[str]): List of body parts governed by the Nakshatra.
        rasi_lord (str): The sign (Rasi) lord associated with the Nakshatra.
        start_degree (float): The starting degree position in the zodiac.
        end_degree (float): The ending degree position in the zodiac.
        rasi (str): The zodiac sign (Rasi) in which the Nakshatra resides.
        color (str): The color associated with the Nakshatra.
        direction (str): The directional association of the Nakshatra.
        gunas (str): The three gunas (Sattva, Rajas, Tamas) association.
        primary_motivation (str): The primary motivation or desire (Purushartha) of the Nakshatra.
        temperament (str): The temperament characteristics of the Nakshatra.
        muhurta_rating (int): The auspiciousness rating for Muhurta (timing) purposes.
        auspicious_for (list[str]): List of activities or endeavors auspicious under this Nakshatra.
        inauspicious_for (list[str]): List of activities or endeavors inauspicious under this Nakshatra.
        special_characteristics (list[str]): List of unique or special characteristics.
        karmic_lessons (list[str]): List of karmic lessons associated with the Nakshatra.
        birth_nakshatra_traits (list[str]): List of traits for individuals born under this Nakshatra.
        favorable_activities (list[str]): List of activities favorable for this Nakshatra.
        unfavorable_activities (list[str]): List of activities unfavorable for this Nakshatra.
        career (list[str]): List of suitable career paths for natives of this Nakshatra.
        compatibility (list[str]): List of compatible Nakshatras for relationships.
        health_issues (list[str]): List of health issues or vulnerabilities associated with this Nakshatra.
        vedic_references (str): References to Vedic texts mentioning this Nakshatra.
        keywords (list[str]): List of keywords summarizing the Nakshatra.
        represents (list[str]): List of concepts or entities represented by the Nakshatra.
        padas (list[NakshatraPada]): List of Padas (quarters) of the Nakshatra with individual characteristics.

    """

    name: str = ""
    code: NakshatraCode = ""
    number: int = 0
    description: str = ""
    ruling_planet: PlanetCode = ""
    ruling_deity: str = ""
    symbol: str = ""
    animal_symbol: str = ""
    yoni: str = ""
    element_panchamahabhuta: str = ""
    gana: str = ""
    gender: str = ""
    caste: str = ""
    nature: str = ""
    quality: str = ""
    body_parts: list[str] = field(default_factory=list)
    rasi_lord: str = ""
    start_degree: float = 0.0
    end_degree: float = 0.0
    rasi: str = ""
    color: str = ""
    direction: str = ""
    gunas: str = ""
    primary_motivation: str = ""
    temperament: str = ""
    muhurta_rating: int = 0
    auspicious_for: list[str] = field(default_factory=list)
    inauspicious_for: list[str] = field(default_factory=list)
    special_characteristics: list[str] = field(default_factory=list)
    karmic_lessons: list[str] = field(default_factory=list)
    birth_nakshatra_traits: list[str] = field(default_factory=list)
    favorable_activities: list[str] = field(default_factory=list)
    unfavorable_activities: list[str] = field(default_factory=list)
    career: list[str] = field(default_factory=list)
    compatibility: list[str] = field(default_factory=list)
    health_issues: list[str] = field(default_factory=list)
    vedic_references: str = ""
    keywords: list[str] = field(default_factory=list)
    represents: list[str] = field(default_factory=list)
    padas: list[NakshatraPada] = field(default_factory=list)


# ============================================================================
# House Models
# ============================================================================


@dataclass
class House:
    """House data model.

    Represents an astrological house with comprehensive information about
    its significations, natural ruler, and characteristics.

    Attributes:
        name (str): The common name of the house.
        code (str): The unique code identifier for the house.
        number (int): The house number (1-12).
        description (str): A brief description of the house.
        symbol (str): The symbol representing the house.
        element_panchamahabhuta (str): The Panchamahabhuta element associated with the house.
        trikona (str): The trikona (triangular) classification of the house.
        kendra (bool): Whether the house is a kendra (angular) house.
        upachaya (bool): Whether the house is an upachaya (growth) house.
        dusthana (bool): Whether the house is a dusthana (difficult) house.
        maraka_house (bool): Whether the house is a maraka (death-inflicting) house.
        trikona_house (bool): Whether the house is a trikona house.
        artha (bool): Whether the house relates to artha (wealth).
        kama (bool): Whether the house relates to kama (desires).
        moksha (bool): Whether the house relates to moksha (liberation).
        dharma (bool): Whether the house relates to dharma (duty).
        natural_ruler (PlanetCode): The naturally ruling planet of the house.
        natural_sign (RasiCode): The naturally ruling sign of the house.
        body_parts (list[str]): The body parts associated with the house.
        nature (str): The nature of the house.
        signification (str): The primary significations of the house.
        keywords (list[str]): Keywords associated with the house.
        represents (list[str]): The concepts or entities represented by the house.
        karakas (list[PlanetCode]): The karakas (significators) for the house.
        aspects (list[HouseCode]): The aspects associated with the house.

    """

    name: str = ""
    code: str = ""
    number: int = 0
    description: str = ""
    symbol: str = ""
    element_panchamahabhuta: str = ""
    trikona: str = ""
    kendra: bool = False
    upachaya: bool = False
    dusthana: bool = False
    maraka_house: bool = False
    trikona_house: bool = False
    artha: bool = False
    kama: bool = False
    moksha: bool = False
    dharma: bool = False
    natural_ruler: PlanetCode = ""
    natural_sign: RasiCode = ""
    body_parts: list[str] = field(default_factory=list)
    nature: str = ""
    signification: str = ""
    keywords: list[str] = field(default_factory=list)
    represents: list[str] = field(default_factory=list)
    karakas: list[PlanetCode] = field(default_factory=list)
    aspects: list[HouseCode] = field(default_factory=list)


# ============================================================================
# Yoga Models
# ============================================================================


@dataclass
class Yoga:
    """Yoga (auspicious combination) data model.

    Represents an auspicious planetary combination with comprehensive information
    about its nature, effects, and significance in Vedic astrology.

    Attributes:
        name (str): The name of the yoga.
        code (str): The unique code identifier for the yoga.
        number (int): The sequential number of the yoga.
        description (str): A detailed description of the yoga.
        nature (str): The nature of the yoga.
        quality (str): The quality classification of the yoga.
        element_panchamahabhuta (str): The Panchamahabhuta element associated with the yoga.
        deity (PlanetCode | None): The presiding deity of the yoga.
        guna (str): The guna classification of the yoga.
        effect (str): The primary effect of the yoga.
        muhurta_rating (int): The auspiciousness rating for timing purposes.
        auspicious_for (list[str]): List of activities auspicious under this yoga.
        inauspicious_for (list[str]): List of activities inauspicious under this yoga.
        special_characteristics (list[str]): List of unique or special characteristics.
        karmic_effects (list[str]): List of karmic effects of the yoga.
        birth_yoga_traits (list[str]): List of traits for individuals born under this yoga.
        health_effects (str): Health effects associated with the yoga.
        astrology_significance (str): The astrological significance of the yoga.
        vedic_references (str): References to Vedic texts mentioning this yoga.
        keywords (list[str]): Keywords associated with the yoga.
        represents (list[str]): List of concepts or entities represented by the yoga.

    """

    name: str = ""
    code: str = ""
    number: int = 0
    description: str = ""
    nature: str = ""
    quality: str = ""
    element_panchamahabhuta: str = ""
    deity: str | None = None
    guna: str = ""
    effect: str = ""
    muhurta_rating: int = 0
    auspicious_for: list[str] = field(default_factory=list)
    inauspicious_for: list[str] = field(default_factory=list)
    special_characteristics: list[str] = field(default_factory=list)
    karmic_effects: list[str] = field(default_factory=list)
    birth_yoga_traits: list[str] = field(default_factory=list)
    health_effects: str = ""
    astrology_significance: str = ""
    vedic_references: str = ""
    keywords: list[str] = field(default_factory=list)
    represents: list[str] = field(default_factory=list)


@dataclass
class PlanetaryYoga:
    """Planetary Yoga data model.

    Represents a specific planetary yoga combination with detailed information
    about its formation, effects, and astrological significance.

    Attributes:
        name (str): The name of the planetary yoga.
        sanskrit_name (str | None): The Sanskrit name of the yoga.
        category (str): The category classification of the yoga.
        type (str): The type or classification of the yoga.
        description (str): A detailed description of the yoga.
        formation_rules (list[str]): List of rules governing the formation of the yoga.
        planets (list[PlanetCode]): List of planets involved in the yoga.
        houses (list[House] | None): List of houses associated with the yoga.
        signs (list[Rasi] | None): List of zodiac signs associated with the yoga.
        benefic_malefic_type (str): Classification as benefic or malefic.
        strength (str): The strength level of the yoga.
        rarity (str): The rarity classification of the yoga.
        effects (list[str]): List of effects produced by the yoga.
        positive_results (list[str]): List of positive results of the yoga.
        negative_results (list[str] | None): List of negative results of the yoga.
        cancellation_conditions (list[str]): List of conditions that cancel the yoga.
        time_of_result_manifest (str): When the results of the yoga manifest.
        life_areas (list[str]): List of life areas affected by the yoga.
        vedic_references (str): References to Vedic texts mentioning this yoga.
        keywords (list[str]): Keywords associated with the yoga.
        represents (list[str]): List of concepts or entities represented by the yoga.

    """

    name: str = ""
    sanskrit_name: str | None = None
    category: str = ""
    type: str = ""
    description: str = ""
    formation_rules: list[str] = field(default_factory=list)
    planets: list[PlanetCode] = field(default_factory=list)
    houses: list[House] | None = None
    signs: list[Rasi] | None = None
    benefic_malefic_type: str = ""
    strength: str = ""
    rarity: str = ""
    effects: list[str] = field(default_factory=list)
    positive_results: list[str] = field(default_factory=list)
    negative_results: list[str] | None = None
    cancellation_conditions: list[str] = field(default_factory=list)
    time_of_result_manifest: str = ""
    life_areas: list[str] = field(default_factory=list)
    vedic_references: str = ""
    keywords: list[str] = field(default_factory=list)
    represents: list[str] = field(default_factory=list)


# ============================================================================
# Dasha System Models
# ============================================================================


@dataclass
class DashaPeriod:
    """Dasha period data model.

    Attributes:
        planet (PlanetCode): The planet governing this dasha period.
        years (int): The duration of the dasha period in years.
        nature (str): The nature of the dasha period.
        effects (str): The effects experienced during this dasha period.
        significations (list[str]): The significations of this dasha period.
        positive_results (str): Positive results of this dasha period.
        negative_results (str): Negative results of this dasha period.
        remedies (list[str]): Remedies recommended during this dasha period.

    """

    planet: PlanetCode = ""
    years: int = 0
    nature: str = ""
    effects: str = ""
    significations: list[str] = field(default_factory=list)
    positive_results: str = ""
    negative_results: str = ""
    remedies: list[str] = field(default_factory=list)


@dataclass
class DashaSystem:
    """Dasha system data model.

    Attributes:
        name (str): The name of the dasha system.
        total_years (int): The total duration of the dasha system in years.
        type (str): The type or classification of the dasha system.
        importance (str): The importance level of the dasha system.
        popularity (str): The popularity of the dasha system.
        description (str): A detailed description of the dasha system.
        calculation_basis (str): The basis for calculating the dasha periods.
        starting_point (str): The starting point of the dasha system.
        applicability (str): The applicability of the dasha system.
        sequence (list[str]): The sequence of dasha periods.
        periods (list[DashaPeriod]): The list of dasha periods in the system.

    """

    name: str = ""
    total_years: int | str = 0
    type: str = ""
    importance: str = ""
    popularity: str = ""
    description: str = ""
    calculation_basis: str = ""
    starting_point: str = ""
    applicability: str = ""
    sequence: str | list[str] = field(default_factory=list)
    periods: str | list[DashaPeriod] = field(default_factory=list)


# ============================================================================
# Panchanga Elements Models
# ============================================================================


@dataclass
class Tithi:
    """Tithi (Lunar Day) data model.

    Represents a Tithi (lunar day) in the Vedic lunar calendar with comprehensive
    astrological and ritualistic information.

    Attributes:
        name (str): The name of the Tithi.
        code (str): The unique code identifier for the Tithi.
        number (int): The sequential number of the Tithi (1-30).
        paksha (str): The lunar fortnight (Shukla/Bright or Krishna/Dark).
        description (str): A detailed description of the Tithi's characteristics.
        deity (str): The presiding deity associated with the Tithi.
        tithi_lord (PlanetCode): The ruling planet of the Tithi.
        element_panchamahabhuta (str): The Panchamahabhuta element associated with the Tithi.
        nature (str): The nature or temperament of the Tithi.
        quality (str): The quality classification of the Tithi.
        guna (str): The guna (Sattva, Rajas, Tamas) association.
        duration_characteristic (str): Characteristic duration information for the Tithi.
        muhurta_rating (int): The auspiciousness rating for Muhurta (timing) purposes.
        auspicious_for (list[str]): List of activities auspicious under this Tithi.
        inauspicious_for (list[str]): List of activities inauspicious under this Tithi.
        special_observances (list[str]): List of special observances or fasts associated with the Tithi.
        karmic_effects (list[str]): List of karmic effects of the Tithi.
        birth_tithi_traits (list[str]): List of traits for individuals born on this Tithi.
        nakshatra_compatibility (list[NakshatraCode]): List of compatible Nakshatras.
        agricultural_significance (str): Agricultural significance of the Tithi.
        specific_rituals (list[str]): List of specific rituals performed on this Tithi.
        vedic_references (str): References to Vedic texts mentioning this Tithi.
        keywords (list[str]): Keywords associated with the Tithi.
        represents (list[str]): List of concepts or entities represented by the Tithi.

    """

    name: str = ""
    code: str = ""
    number: int = 0
    paksha: str = ""
    description: str = ""
    deity: str = ""
    tithi_lord: PlanetCode = ""
    element_panchamahabhuta: str = ""
    nature: str = ""
    quality: str = ""
    guna: str = ""
    duration_characteristic: str = ""
    muhurta_rating: int = 0
    auspicious_for: list[str] = field(default_factory=list)
    inauspicious_for: list[str] = field(default_factory=list)
    special_observances: list[str] = field(default_factory=list)
    karmic_effects: list[str] = field(default_factory=list)
    birth_tithi_traits: list[str] = field(default_factory=list)
    nakshatra_compatibility: list[NakshatraCode] = field(default_factory=list)
    agricultural_significance: str = ""
    specific_rituals: list[str] = field(default_factory=list)
    vedic_references: str = ""
    keywords: list[str] = field(default_factory=list)
    represents: list[str] = field(default_factory=list)


@dataclass
class Karana:
    """Represents a Karana, half of a lunar day (Tithi) in Vedic astrology.

    A Karana is a unit of time calculation used in Vedic astrology and Hindu calendar.
    Each Tithi is divided into two Karanas.

    Attributes:
        name: Name of the Karana.
        code: Short code for the Karana.
        number: Numerical order of the Karana.
        type: Type/category of the Karana (movable, fixed, etc.).
        description: Detailed description of the Karana.
        deity: Presiding deity associated with the Karana.
        nature: Nature or characteristic quality.
        quality: Specific quality attributed to the Karana.
        guna: Guna (quality) classification (Sattva, Rajas, Tamas).
        muhurta_rating: Auspiciousness rating for muhurta selection.
        auspicious_for: Activities considered auspicious during this Karana.
        inauspicious_for: Activities to avoid during this Karana.
        characteristics: Key characteristics and traits.
        effects: Astrological effects and influences.
        vedic_references: Classical Vedic texts mentioning this Karana.
        keywords: Keywords for quick reference.
        represents: What this Karana represents or symbolizes.

    """

    name: str = ""
    code: str = ""
    number: int = 0
    type: str = ""
    description: str = ""
    deity: str | None = None
    nature: str = ""
    quality: str = ""
    guna: str = ""
    muhurta_rating: int = 0
    auspicious_for: list[str] = field(default_factory=list)
    inauspicious_for: list[str] = field(default_factory=list)
    characteristics: list[str] = field(default_factory=list)
    effects: list[str] = field(default_factory=list)
    vedic_references: str = ""
    keywords: list[str] = field(default_factory=list)
    represents: list[str] = field(default_factory=list)


@dataclass
class Vara:
    """Represents a Vara (day of the week) in Vedic astrology.

    Each Vara is ruled by a specific planet and has unique astrological significance.

    Attributes:
        name: Name of the Vara (day of the week).
        code: Short code for the Vara.
        number: Day number (1-7).
        description: Detailed description of the Vara.
        ruling_planet: Planet that rules this day.
        deity: Presiding deity for this day.
        element_panchamahabhuta: Associated element from the five great elements.
        nature: Nature or quality of the day.
        color: Color associated with this day.
        gemstone: Gemstone associated with this day.
        metal_association: Metal associated with this day.
        direction: Directional association.
        auspicious_for: Activities recommended for this day.
        inauspicious_for: Activities to avoid on this day.
        fasting_day: Whether this is traditionally a fasting day.
        special_observances: Special religious or spiritual observances.
        character_traits: Personality traits of people born on this day.
        vedic_references: Classical Vedic texts mentioning this Vara.
        keywords: Keywords for quick reference.
        represents: What this Vara represents or symbolizes.

    """

    name: str = ""
    code: str = ""
    number: int = 0
    description: str = ""
    ruling_planet: PlanetCode = ""
    deity: str = ""
    element_panchamahabhuta: str = ""
    nature: str = ""
    color: str = ""
    gemstone: str = ""
    metal_association: str = ""
    direction: str = ""
    auspicious_for: list[str] = field(default_factory=list)
    inauspicious_for: list[str] = field(default_factory=list)
    fasting_day: bool = False
    special_observances: list[str] = field(default_factory=list)
    character_traits: list[str] = field(default_factory=list)
    vedic_references: str = ""
    keywords: list[str] = field(default_factory=list)
    represents: list[str] = field(default_factory=list)


# ============================================================================
# Advanced Techniques Models
# ============================================================================


@dataclass
class DivisionalChart:
    """Represents a Divisional Chart (Varga/Amshas) in Vedic astrology.

    Divisional charts are subdivisions of the main birth chart used to analyze
    specific areas of life in greater detail.

    Attributes:
        name: Name of the divisional chart (e.g., Navamsa, Dasamsa).
        code: Short code for the chart.
        division: Division number (e.g., D-9 for Navamsa).
        description: Detailed description of the chart's purpose.
        signification: Areas of life signified by this chart.
        importance: Importance level in astrological analysis.
        usage: How and when to use this divisional chart.
        interpretation_focus: Key focus areas for interpretation.
        good_for_analyzing: Specific life aspects best analyzed with this chart.
        calculation_method: Method used to calculate the chart divisions.
        strength_factor: Relative strength or weightage in predictions.
        vedic_references: Classical texts mentioning this chart.
        keywords: Keywords for quick reference.

    """

    name: str = ""
    code: str = ""
    division: int = 0
    description: str = ""
    signification: list[str] = field(default_factory=list)
    importance: str = ""
    usage: str = ""
    interpretation_focus: list[str] = field(default_factory=list)
    good_for_analyzing: list[str] = field(default_factory=list)
    calculation_method: str = ""
    strength_factor: float = 0.0
    vedic_references: str = ""
    keywords: list[str] = field(default_factory=list)


@dataclass
class Avastha:
    """Represents an Avastha (planetary state/condition) in Vedic astrology.

    Avastha describes the condition or state of a planet that affects its ability
    to deliver results.

    Attributes:
        name: Name of the Avastha state.
        type: Type or category of Avastha.
        description: Detailed description of this planetary state.
        conditions: Conditions under which this Avastha occurs.
        effects: Astrological effects when planet is in this state.
        strength: Strength level of the planet in this state.
        interpretation: Interpretative guidelines for this Avastha.

    """

    name: str = ""
    type: str = ""
    description: str = ""
    conditions: list[str] = field(default_factory=list)
    effects: list[str] = field(default_factory=list)
    strength: str = ""
    interpretation: str = ""


@dataclass
class Upagraha:
    """Represents an Upagraha (sensitive point/sub-planet) in Vedic astrology.

    Upagrahas are calculated mathematical points that have astrological significance,
    derived from the positions of the Sun and other planets.

    Attributes:
        name: Name of the Upagraha.
        code: Short code for the Upagraha.
        sanskrit_name: Sanskrit name of the Upagraha.
        description: Detailed description of this sensitive point.
        type: Type or category of Upagraha.
        calculation_method: Method used to calculate the position.
        father: Parent planet from which this Upagraha is derived.
        nature: Nature or characteristic quality.
        signification: Areas of life signified by this Upagraha.
        effects: Astrological effects and influences.
        interpretation: Interpretative guidelines.
        importance: Importance level in astrological analysis.
        vedic_references: Classical Vedic texts mentioning this Upagraha.
        keywords: Keywords for quick reference.
        represents: What this Upagraha represents or symbolizes.

    """

    name: str = ""
    code: str = ""
    sanskrit_name: str = ""
    description: str = ""
    type: str = ""
    calculation_method: str = ""
    father: PlanetCode | None = None
    nature: str = ""
    signification: list[str] = field(default_factory=list)
    effects: list[str] = field(default_factory=list)
    interpretation: str = ""
    importance: str = ""
    vedic_references: str = ""
    keywords: list[str] = field(default_factory=list)
    represents: list[str] = field(default_factory=list)


@dataclass
class SpecialLagna:
    """Represents a Special Lagna (special ascendant) in Vedic astrology.

    Special Lagnas are calculated points used to analyze specific aspects of life,
    derived from various planetary positions and birth time.

    Attributes:
        name: Name of the Special Lagna.
        code: Short code for the Special Lagna.
        sanskrit_name: Sanskrit name of the Special Lagna.
        description: Detailed description and significance.
        calculation_method: Method used to calculate the position.
        signification: Areas of life signified by this Lagna.
        usage: How and when to use this Special Lagna.
        importance: Importance level in astrological analysis.
        interpretation_focus: Key focus areas for interpretation.
        good_for_analyzing: Specific life aspects best analyzed with this Lagna.
        vedic_references: Classical Vedic texts mentioning this Lagna.
        keywords: Keywords for quick reference.
        represents: What this Special Lagna represents or symbolizes.

    """

    name: str = ""
    code: str = ""
    sanskrit_name: str = ""
    description: str = ""
    calculation_method: str = ""
    signification: list[str] = field(default_factory=list)
    usage: str = ""
    importance: str = ""
    interpretation_focus: list[str] = field(default_factory=list)
    good_for_analyzing: list[str] = field(default_factory=list)
    vedic_references: str = ""
    keywords: list[str] = field(default_factory=list)
    represents: list[str] = field(default_factory=list)
