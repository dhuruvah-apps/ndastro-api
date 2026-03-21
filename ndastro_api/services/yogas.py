"""Yoga calculation utilities.

Includes:
- Nitya Yoga (27 yogas) based on Sun + Moon longitudes.
- Planetary yoga rule evaluation (common combinations).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

# Constants
FULL_CIRCLE_DEGREES = 360.0
YOGA_COUNT = 27
YOGA_ARC_DEGREES = FULL_CIRCLE_DEGREES / YOGA_COUNT
RASI_COUNT = 12
KENDRA_HOUSES = {1, 4, 7, 10}
KENDRA_OFFSETS = {0, 3, 6, 9}
TRIKONA_HOUSES = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}
BENEFIC_PLANETS = {"jupiter", "venus", "mercury", "moon"}
MALEFIC_PLANETS = {"saturn", "mars", "sun", "rahu", "kethu"}

PLANET_CODE_MAP = {
    "su": "sun",
    "mo": "moon",
    "ma": "mars",
    "me": "mercury",
    "ju": "jupiter",
    "ve": "venus",
    "sa": "saturn",
    "ra": "rahu",
    "ke": "kethu",
}

NITYA_YOGA_NAMES = [
    "Vishkambha",
    "Priti",
    "Ayushman",
    "Saubhagya",
    "Sobhana",
    "Atiganda",
    "Sukarma",
    "Dhriti",
    "Shoola",
    "Ganda",
    "Vriddhi",
    "Dhruva",
    "Vyaghata",
    "Harshana",
    "Vajra",
    "Siddhi",
    "Vyatipata",
    "Variyana",
    "Parigha",
    "Siva",
    "Siddha",
    "Sadhya",
    "Subha",
    "Sukla",
    "Brahma",
    "Indra",
    "Vaidhriti",
]


@dataclass
class NityaYogaResult:
    """Result for Nitya Yoga calculation."""

    name: str
    number: int
    longitude_sum: float
    arc_start: float
    arc_end: float


@dataclass
class PlanetaryYogaContext:
    """Context for planetary yoga evaluation."""

    planet_houses: dict[str, int]  # {planet: house_number}
    planet_rasis: dict[str, str]  # {planet: rasi_name}
    own_signs: dict[str, set[str]] | None = None  # {planet: {rasi_names}}
    exaltation_signs: dict[str, str] | None = None  # {planet: rasi_name}
    debilitation_signs: dict[str, str] | None = None  # {planet: rasi_name}
    house_lords: dict[int, str] | None = None  # {house_number: planet}
    lagna_house: int | None = None


@dataclass
class YogaRuleResult:
    """Result for a planetary yoga rule evaluation."""

    name: str
    category: str
    is_present: bool
    planets_involved: list[str]
    details: str


@dataclass
class YogaRule:
    """Represents a planetary yoga rule."""

    name: str
    category: str
    evaluator: Callable[[PlanetaryYogaContext], YogaRuleResult]


def _normalize_degrees(angle: float) -> float:
    """Normalize degrees to [0, 360)."""
    normalized = angle % FULL_CIRCLE_DEGREES
    return normalized if normalized >= 0 else normalized + FULL_CIRCLE_DEGREES


def _normalize_planet_key(planet: str) -> str:
    """Normalize planet names or codes to lowercase keys."""
    cleaned = planet.strip().lower()
    return PLANET_CODE_MAP.get(cleaned, cleaned)


def calculate_nitya_yoga(sun_longitude: float, moon_longitude: float) -> NityaYogaResult:
    """Calculate Nitya Yoga from Sun and Moon longitudes.

    Args:
        sun_longitude: Sun longitude in degrees
        moon_longitude: Moon longitude in degrees

    Returns:
        NityaYogaResult with yoga name and arc boundaries

    """
    longitude_sum = _normalize_degrees(sun_longitude + moon_longitude)
    yoga_index = int(longitude_sum / YOGA_ARC_DEGREES) + 1
    yoga_name = get_nitya_yoga_name(yoga_index)

    arc_start = (yoga_index - 1) * YOGA_ARC_DEGREES
    arc_end = yoga_index * YOGA_ARC_DEGREES

    return NityaYogaResult(
        name=yoga_name,
        number=yoga_index,
        longitude_sum=longitude_sum,
        arc_start=arc_start,
        arc_end=arc_end,
    )


def get_nitya_yoga_name(number: int) -> str:
    """Get Nitya Yoga name by number (1-27)."""
    if 1 <= number <= YOGA_COUNT:
        return NITYA_YOGA_NAMES[number - 1]
    return "Unknown"


def _get_house(context: PlanetaryYogaContext, planet: str) -> int | None:
    normalized = _normalize_planet_key(planet)
    return context.planet_houses.get(normalized)


def _get_rasi(context: PlanetaryYogaContext, planet: str) -> str | None:
    normalized = _normalize_planet_key(planet)
    return context.planet_rasis.get(normalized)


def _is_in_kendra(house: int | None) -> bool:
    return house in KENDRA_HOUSES if house is not None else False


def _is_kendra_from(context: PlanetaryYogaContext, planet_a: str, planet_b: str) -> bool:
    house_a = _get_house(context, planet_a)
    house_b = _get_house(context, planet_b)

    if house_a is None or house_b is None:
        return False

    return ((house_a - house_b) % RASI_COUNT) in KENDRA_OFFSETS


def _is_same_house(context: PlanetaryYogaContext, planet_a: str, planet_b: str) -> bool:
    house_a = _get_house(context, planet_a)
    house_b = _get_house(context, planet_b)
    return house_a is not None and house_a == house_b


def _is_benefic(planet: str) -> bool:
    return _normalize_planet_key(planet) in BENEFIC_PLANETS


def _is_malefic(planet: str) -> bool:
    return _normalize_planet_key(planet) in MALEFIC_PLANETS


def _get_planets_in_house(context: PlanetaryYogaContext, house: int) -> list[str]:
    return [planet for planet, value in context.planet_houses.items() if value == house]


def _house_from(base_house: int, offset: int) -> int:
    return ((base_house - 1 + offset) % RASI_COUNT) + 1


def _get_house_lord(context: PlanetaryYogaContext, house: int) -> str | None:
    if context.house_lords is None:
        return None
    return _normalize_planet_key(context.house_lords.get(house, ""))


def _get_lagna_lord(context: PlanetaryYogaContext) -> str | None:
    if context.lagna_house is None:
        return None
    return _get_house_lord(context, context.lagna_house)


def _get_occupied_houses(context: PlanetaryYogaContext) -> list[int]:
    return sorted({house for house in context.planet_houses.values()})


def _is_own_or_exalted(context: PlanetaryYogaContext, planet: str) -> bool:
    rasi = _get_rasi(context, planet)
    normalized = _normalize_planet_key(planet)

    if rasi is None:
        return False

    own_signs = context.own_signs.get(normalized) if context.own_signs else None
    exalted_sign = context.exaltation_signs.get(normalized) if context.exaltation_signs else None

    in_own_sign = bool(own_signs and rasi in own_signs)
    in_exaltation = bool(exalted_sign and rasi == exalted_sign)
    return in_own_sign or in_exaltation


def _is_debilitated(context: PlanetaryYogaContext, planet: str) -> bool:
    rasi = _get_rasi(context, planet)
    normalized = _normalize_planet_key(planet)
    if rasi is None:
        return False
    debilitation = context.debilitation_signs.get(normalized) if context.debilitation_signs else None
    return bool(debilitation and rasi == debilitation)


def _result(
    name: str,
    category: str,
    *,
    is_present: bool,
    planets: list[str],
    details: str,
) -> YogaRuleResult:
    return YogaRuleResult(
        name=name,
        category=category,
        is_present=is_present,
        planets_involved=planets,
        details=details,
    )


def _mahapurusha_rule(
    context: PlanetaryYogaContext,
    planet: str,
    yoga_name: str,
) -> YogaRuleResult:
    house = _get_house(context, planet)
    rasi = _get_rasi(context, planet)

    if house is None or rasi is None:
        return _result(
            yoga_name,
            "Pancha Mahapurusha",
            is_present=False,
            planets=[planet],
            details="Missing house or rasi for planet",
        )

    in_kendra = _is_in_kendra(house)
    strong_sign = _is_own_or_exalted(context, planet)

    is_present = in_kendra and strong_sign
    details = "Planet in own/exaltation sign and kendra" if is_present else "Conditions not met"

    return _result(
        yoga_name,
        "Pancha Mahapurusha",
        is_present=is_present,
        planets=[planet],
        details=details,
    )


def _gajakesari_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    is_present = _is_kendra_from(context, "jupiter", "moon")
    details = "Jupiter in kendra from Moon" if is_present else "Jupiter not in kendra from Moon"

    return _result(
        "Gajakesari Yoga",
        "Kendra",
        is_present=is_present,
        planets=["jupiter", "moon"],
        details=details,
    )


def _budha_aditya_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    is_present = _is_same_house(context, "sun", "mercury")
    details = "Sun and Mercury conjunct" if is_present else "Sun and Mercury not conjunct"

    return _result(
        "Budha-Aditya Yoga",
        "Conjunction",
        is_present=is_present,
        planets=["sun", "mercury"],
        details=details,
    )


def _chandra_mangala_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    is_present = _is_same_house(context, "moon", "mars")
    details = "Moon and Mars conjunct" if is_present else "Moon and Mars not conjunct"

    return _result(
        "Chandra-Mangala Yoga",
        "Conjunction",
        is_present=is_present,
        planets=["moon", "mars"],
        details=details,
    )


def _guru_chandala_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    is_present = _is_same_house(context, "jupiter", "rahu") or _is_same_house(context, "jupiter", "kethu")
    details = "Jupiter conjunct Rahu/Kethu" if is_present else "No Jupiter-Rahu/Kethu conjunction"

    return _result(
        "Guru-Chandala Yoga",
        "Conjunction",
        is_present=is_present,
        planets=["jupiter", "rahu", "kethu"],
        details=details,
    )


def _shukra_mangala_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    is_present = _is_same_house(context, "venus", "mars")
    details = "Venus and Mars conjunct" if is_present else "Venus and Mars not conjunct"

    return _result(
        "Shukra-Mangala Yoga",
        "Conjunction",
        is_present=is_present,
        planets=["venus", "mars"],
        details=details,
    )


def _raja_yoga_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    if context.house_lords is None:
        return _result(
            "Raja Yoga",
            "Lords",
            is_present=False,
            planets=[],
            details="Missing house_lords mapping",
        )

    kendra_lords = [lord for house in KENDRA_HOUSES if (lord := _get_house_lord(context, house))]
    trikona_lords = [lord for house in TRIKONA_HOUSES if (lord := _get_house_lord(context, house))]

    for kendra_lord in kendra_lords:
        for trikona_lord in trikona_lords:
            if kendra_lord == trikona_lord:
                continue
            if _is_same_house(context, kendra_lord, trikona_lord):
                return _result(
                    "Raja Yoga",
                    "Lords",
                    is_present=True,
                    planets=[kendra_lord, trikona_lord],
                    details="Kendra and trikona lords conjunct",
                )

    return _result(
        "Raja Yoga",
        "Lords",
        is_present=False,
        planets=[],
        details="No kendra-trikona lord conjunction",
    )


def _dhana_yoga_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    if context.house_lords is None:
        return _result(
            "Dhana Yoga",
            "Wealth",
            is_present=False,
            planets=[],
            details="Missing house_lords mapping",
        )

    wealth_lords = [lord for house in (2, 11) if (lord := _get_house_lord(context, house))]
    support_lords = [lord for house in (1, 5, 9) if (lord := _get_house_lord(context, house))]

    for wealth_lord in wealth_lords:
        for support_lord in support_lords:
            if wealth_lord == support_lord:
                continue
            if _is_same_house(context, wealth_lord, support_lord):
                return _result(
                    "Dhana Yoga",
                    "Wealth",
                    is_present=True,
                    planets=[wealth_lord, support_lord],
                    details="Wealth lord conjunct with lagna/trikona lord",
                )

    return _result(
        "Dhana Yoga",
        "Wealth",
        is_present=False,
        planets=[],
        details="No wealth lord conjunction with lagna/trikona lords",
    )


def _vipareeta_raja_yoga_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    if context.house_lords is None:
        return _result(
            "Vipareeta Raja Yoga",
            "Dusthana",
            is_present=False,
            planets=[],
            details="Missing house_lords mapping",
        )

    dusthana_lords = [lord for house in (6, 8, 12) if (lord := _get_house_lord(context, house))]

    for lord in dusthana_lords:
        house = _get_house(context, lord)
        if house in DUSTHANA_HOUSES:
            return _result(
                "Vipareeta Raja Yoga",
                "Dusthana",
                is_present=True,
                planets=[lord],
                details="Dusthana lord placed in dusthana",
            )

    return _result(
        "Vipareeta Raja Yoga",
        "Dusthana",
        is_present=False,
        planets=[],
        details="No dusthana lord placed in dusthana",
    )


def _parivartana_yoga_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    if context.own_signs is None:
        return _result(
            "Parivartana Yoga",
            "Exchange",
            is_present=False,
            planets=[],
            details="Missing own_signs mapping",
        )

    planets = list(context.planet_rasis.keys())
    for planet_a in planets:
        for planet_b in planets:
            if planet_a >= planet_b:
                continue
            rasi_a = _get_rasi(context, planet_a)
            rasi_b = _get_rasi(context, planet_b)
            if not rasi_a or not rasi_b:
                continue
            own_a = context.own_signs.get(_normalize_planet_key(planet_a), set())
            own_b = context.own_signs.get(_normalize_planet_key(planet_b), set())
            if rasi_a in own_b and rasi_b in own_a:
                return _result(
                    "Parivartana Yoga",
                    "Exchange",
                    is_present=True,
                    planets=[planet_a, planet_b],
                    details="Mutual exchange of signs",
                )

    return _result(
        "Parivartana Yoga",
        "Exchange",
        is_present=False,
        planets=[],
        details="No mutual sign exchange",
    )


def _kemadruma_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    moon_house = _get_house(context, "moon")
    if moon_house is None:
        return _result(
            "Kemadruma Yoga",
            "Moon",
            is_present=False,
            planets=[],
            details="Missing Moon house",
        )

    adjacent_houses = {
        _house_from(moon_house, -1),
        _house_from(moon_house, 1),
    }
    other_planets = [planet for planet in context.planet_houses if planet != "moon"]
    moon_companions = [planet for planet in other_planets if _get_house(context, planet) == moon_house]
    adjacent_planets = [planet for planet in other_planets if _get_house(context, planet) in adjacent_houses]

    is_present = not moon_companions and not adjacent_planets
    details = "Moon isolated from adjacent houses" if is_present else "Moon has support nearby"

    return _result(
        "Kemadruma Yoga",
        "Moon",
        is_present=is_present,
        planets=["moon"],
        details=details,
    )


def _adhi_yoga_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    moon_house = _get_house(context, "moon")
    if moon_house is None:
        return _result(
            "Adhi Yoga",
            "Moon",
            is_present=False,
            planets=[],
            details="Missing Moon house",
        )

    target_houses = {
        _house_from(moon_house, 5),
        _house_from(moon_house, 6),
        _house_from(moon_house, 7),
    }
    benefics = [planet for planet in context.planet_houses if _is_benefic(planet)]
    benefics_in_targets = [planet for planet in benefics if _get_house(context, planet) in target_houses]

    is_present = bool(benefics_in_targets)
    details = "Benefics in 6th/7th/8th from Moon" if is_present else "No benefics in 6th/7th/8th from Moon"

    return _result(
        "Adhi Yoga",
        "Moon",
        is_present=is_present,
        planets=benefics_in_targets,
        details=details,
    )


def _amala_yoga_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    if context.lagna_house is None:
        return _result(
            "Amala Yoga",
            "Lagna",
            is_present=False,
            planets=[],
            details="Missing lagna_house",
        )

    lagna_tenth = _house_from(context.lagna_house, 9)
    moon_house = _get_house(context, "moon")
    moon_tenth = _house_from(moon_house, 9) if moon_house else None

    benefics = [planet for planet in context.planet_houses if _is_benefic(planet)]
    benefics_in_lagna_tenth = [planet for planet in benefics if _get_house(context, planet) == lagna_tenth]
    benefics_in_moon_tenth = [planet for planet in benefics if moon_tenth and _get_house(context, planet) == moon_tenth]

    planets = list({*benefics_in_lagna_tenth, *benefics_in_moon_tenth})
    is_present = bool(planets)
    details = "Benefic in 10th from Lagna or Moon" if is_present else "No benefic in 10th from Lagna or Moon"

    return _result(
        "Amala Yoga",
        "Lagna",
        is_present=is_present,
        planets=planets,
        details=details,
    )


def _dharma_karmadhipati_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    if context.house_lords is None:
        return _result(
            "Dharma-Karmadhipati Yoga",
            "Raja",
            is_present=False,
            planets=[],
            details="Missing house_lords mapping",
        )

    dharma_lord = _get_house_lord(context, 9)
    karma_lord = _get_house_lord(context, 10)
    if not dharma_lord or not karma_lord:
        return _result(
            "Dharma-Karmadhipati Yoga",
            "Raja",
            is_present=False,
            planets=[],
            details="Missing dharma or karma lord",
        )

    is_present = _is_same_house(context, dharma_lord, karma_lord)
    details = "9th and 10th lords conjunct" if is_present else "No 9th/10th lord conjunction"

    return _result(
        "Dharma-Karmadhipati Yoga",
        "Raja",
        is_present=is_present,
        planets=[dharma_lord, karma_lord],
        details=details,
    )


def _neecha_bhanga_raja_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    if context.debilitation_signs is None or context.exaltation_signs is None:
        return _result(
            "Neecha-Bhanga Raja Yoga",
            "Raja",
            is_present=False,
            planets=[],
            details="Missing debilitation or exaltation signs mapping",
        )

    for planet in context.planet_houses:
        if not _is_debilitated(context, planet):
            continue

        planet_house = _get_house(context, planet)
        if planet_house is None:
            continue

        dispositor = _get_house_lord(context, planet_house)
        if dispositor and _is_in_kendra(_get_house(context, dispositor)):
            return _result(
                "Neecha-Bhanga Raja Yoga",
                "Raja",
                is_present=True,
                planets=[planet, dispositor],
                details="Debilitated planet with dispositor in kendra",
            )

    return _result(
        "Neecha-Bhanga Raja Yoga",
        "Raja",
        is_present=False,
        planets=[],
        details="No debilitation cancellation found",
    )


def _wealth_lord_in_kendra_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    if context.house_lords is None:
        return _result(
            "Wealth Lord in Kendra",
            "Wealth",
            is_present=False,
            planets=[],
            details="Missing house_lords mapping",
        )

    wealth_lords = [lord for house in (2, 11) if (lord := _get_house_lord(context, house))]
    for lord in wealth_lords:
        if _is_in_kendra(_get_house(context, lord)):
            return _result(
                "Wealth Lord in Kendra",
                "Wealth",
                is_present=True,
                planets=[lord],
                details="2nd/11th lord in kendra",
            )

    return _result(
        "Wealth Lord in Kendra",
        "Wealth",
        is_present=False,
        planets=[],
        details="No 2nd/11th lord in kendra",
    )


def _gola_yoga_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    occupied = _get_occupied_houses(context)
    is_present = len(occupied) == 1
    details = "All planets in one house" if is_present else "Planets spread across houses"

    return _result(
        "Gola Yoga",
        "Nabhasa",
        is_present=is_present,
        planets=list(context.planet_houses.keys()) if is_present else [],
        details=details,
    )


def _yuga_yoga_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    occupied = _get_occupied_houses(context)
    is_present = len(occupied) == 2
    details = "All planets in two houses" if is_present else "Planets spread across more than two houses"

    return _result(
        "Yuga Yoga",
        "Nabhasa",
        is_present=is_present,
        planets=list(context.planet_houses.keys()) if is_present else [],
        details=details,
    )


def _sula_yoga_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    occupied = _get_occupied_houses(context)
    is_present = len(occupied) == 3
    details = "All planets in three houses" if is_present else "Planets spread across more than three houses"

    return _result(
        "Sula Yoga",
        "Nabhasa",
        is_present=is_present,
        planets=list(context.planet_houses.keys()) if is_present else [],
        details=details,
    )


def _maraka_yoga_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    if context.house_lords is None:
        return _result(
            "Maraka Yoga",
            "Arishta",
            is_present=False,
            planets=[],
            details="Missing house_lords mapping",
        )

    maraka_lords = [lord for house in (2, 7) if (lord := _get_house_lord(context, house))]
    for lord in maraka_lords:
        if _get_house(context, lord) in DUSTHANA_HOUSES:
            return _result(
                "Maraka Yoga",
                "Arishta",
                is_present=True,
                planets=[lord],
                details="Maraka lord placed in dusthana",
            )

    return _result(
        "Maraka Yoga",
        "Arishta",
        is_present=False,
        planets=[],
        details="No maraka lord in dusthana",
    )


def _arishta_yoga_rule(context: PlanetaryYogaContext) -> YogaRuleResult:
    lagna_lord = _get_lagna_lord(context)
    if not lagna_lord:
        return _result(
            "Arishta Yoga",
            "Arishta",
            is_present=False,
            planets=[],
            details="Missing lagna lord",
        )

    lagna_lord_house = _get_house(context, lagna_lord)
    moon_house = _get_house(context, "moon")

    is_present = False
    planets: list[str] = []

    if lagna_lord_house in DUSTHANA_HOUSES and _is_malefic(lagna_lord):
        is_present = True
        planets.append(lagna_lord)

    if moon_house in DUSTHANA_HOUSES:
        is_present = True
        planets.append("moon")

    details = "Lagna lord or Moon in dusthana" if is_present else "No arishta triggers"

    return _result(
        "Arishta Yoga",
        "Arishta",
        is_present=is_present,
        planets=planets,
        details=details,
    )


def evaluate_planetary_yogas(
    context: PlanetaryYogaContext,
    *,
    include_missing: bool = False,
) -> list[YogaRuleResult]:
    """Evaluate common planetary yogas.

    Args:
        context: PlanetaryYogaContext with placements
        include_missing: Include non-formed yogas if True

    Returns:
        List of YogaRuleResult

    """
    rules = [
        YogaRule("Bhadra Yoga", "Pancha Mahapurusha", lambda ctx: _mahapurusha_rule(ctx, "mercury", "Bhadra Yoga")),
        YogaRule("Ruchaka Yoga", "Pancha Mahapurusha", lambda ctx: _mahapurusha_rule(ctx, "mars", "Ruchaka Yoga")),
        YogaRule("Hamsa Yoga", "Pancha Mahapurusha", lambda ctx: _mahapurusha_rule(ctx, "jupiter", "Hamsa Yoga")),
        YogaRule("Malavya Yoga", "Pancha Mahapurusha", lambda ctx: _mahapurusha_rule(ctx, "venus", "Malavya Yoga")),
        YogaRule("Sasa Yoga", "Pancha Mahapurusha", lambda ctx: _mahapurusha_rule(ctx, "saturn", "Sasa Yoga")),
        YogaRule("Raja Yoga", "Lords", _raja_yoga_rule),
        YogaRule("Dharma-Karmadhipati Yoga", "Raja", _dharma_karmadhipati_rule),
        YogaRule("Neecha-Bhanga Raja Yoga", "Raja", _neecha_bhanga_raja_rule),
        YogaRule("Dhana Yoga", "Wealth", _dhana_yoga_rule),
        YogaRule("Wealth Lord in Kendra", "Wealth", _wealth_lord_in_kendra_rule),
        YogaRule("Vipareeta Raja Yoga", "Dusthana", _vipareeta_raja_yoga_rule),
        YogaRule("Parivartana Yoga", "Exchange", _parivartana_yoga_rule),
        YogaRule("Kemadruma Yoga", "Moon", _kemadruma_rule),
        YogaRule("Adhi Yoga", "Moon", _adhi_yoga_rule),
        YogaRule("Amala Yoga", "Lagna", _amala_yoga_rule),
        YogaRule("Gola Yoga", "Nabhasa", _gola_yoga_rule),
        YogaRule("Yuga Yoga", "Nabhasa", _yuga_yoga_rule),
        YogaRule("Sula Yoga", "Nabhasa", _sula_yoga_rule),
        YogaRule("Maraka Yoga", "Arishta", _maraka_yoga_rule),
        YogaRule("Arishta Yoga", "Arishta", _arishta_yoga_rule),
        YogaRule("Gajakesari Yoga", "Kendra", _gajakesari_rule),
        YogaRule("Budha-Aditya Yoga", "Conjunction", _budha_aditya_rule),
        YogaRule("Chandra-Mangala Yoga", "Conjunction", _chandra_mangala_rule),
        YogaRule("Guru-Chandala Yoga", "Conjunction", _guru_chandala_rule),
        YogaRule("Shukra-Mangala Yoga", "Conjunction", _shukra_mangala_rule),
    ]

    results = [rule.evaluator(context) for rule in rules]

    if include_missing:
        return results

    return [result for result in results if result.is_present]
