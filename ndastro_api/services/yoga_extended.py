"""Extended yoga catalog - additional planetary combinations and special yogas.

This module extends the base yoga evaluation with more specialized yogas
organized by category.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ndastro_api.services.yogas import YogaRuleResult

if TYPE_CHECKING:
    from ndastro_api.services.yogas import PlanetaryYogaContext


BENEFIC_PLANETS_LOWER = {"jupiter", "venus", "mercury", "moon"}
MALEFIC_PLANETS_LOWER = {"saturn", "mars", "sun", "rahu", "kethu"}
KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}


@dataclass
class ExtendedYoga:
    """Extended yoga definition."""

    name: str
    category: str
    description: str
    strength: str  # "Strong", "Medium", "Weak"


def _is_in_kendra(house: int) -> bool:
    """Check if house is a kendra."""
    return house in KENDRA_HOUSES


def _is_in_trikona(house: int) -> bool:
    """Check if house is a trikona."""
    return house in TRIKONA_HOUSES


def _is_benefic(planet: str) -> bool:
    """Check if planet is natural benefic."""
    return planet.lower() in BENEFIC_PLANETS_LOWER


def _is_malefic(planet: str) -> bool:
    """Check if planet is natural malefic."""
    return planet.lower() in MALEFIC_PLANETS_LOWER


def _lakshmi_yoga(context: PlanetaryYogaContext) -> YogaRuleResult:
    """Lakshmi Yoga: Venus and Lord of 9th in own/exaltation in kendra/trikona."""
    ninth_lord = context.house_lords.get(9) if context.house_lords else None
    venus_house = context.planet_houses.get("venus")
    ninth_lord_house = context.planet_houses.get(ninth_lord) if ninth_lord else None

    is_present = False
    details = "Venus and 9th lord must be strong in kendra/trikona."

    if venus_house and ninth_lord_house:
        venus_strong = _is_in_kendra(venus_house) or _is_in_trikona(venus_house)
        ninth_strong = _is_in_kendra(ninth_lord_house) or _is_in_trikona(ninth_lord_house)
        if venus_strong and ninth_strong:
            is_present = True
            details = "Venus and 9th lord placed in kendra/trikona - wealth and prosperity."

    return YogaRuleResult(
        name="Lakshmi Yoga",
        category="Wealth",
        is_present=is_present,
        planets_involved=["venus", ninth_lord] if ninth_lord else ["venus"],
        details=details,
    )


def _saraswati_yoga(context: PlanetaryYogaContext) -> YogaRuleResult:
    """Saraswati Yoga: Jupiter, Venus, Mercury in kendra/trikona/2nd from lagna."""
    jupiter_house = context.planet_houses.get("jupiter")
    venus_house = context.planet_houses.get("venus")
    mercury_house = context.planet_houses.get("mercury")

    is_present = False
    details = "Jupiter, Venus, Mercury must be in kendra/trikona/2nd."

    if jupiter_house and venus_house and mercury_house:
        valid_houses = KENDRA_HOUSES | TRIKONA_HOUSES | {2}
        all_valid = all(h in valid_houses for h in [jupiter_house, venus_house, mercury_house])
        if all_valid:
            is_present = True
            details = "Jupiter, Venus, Mercury well-placed - learning, arts, wisdom."

    return YogaRuleResult(
        name="Saraswati Yoga",
        category="Education",
        is_present=is_present,
        planets_involved=["jupiter", "venus", "mercury"],
        details=details,
    )


def _budha_aditya_strong_yoga(context: PlanetaryYogaContext) -> YogaRuleResult:
    """Strong Budha-Aditya Yoga: Mercury-Sun conjunction in benefic houses."""
    sun_house = context.planet_houses.get("sun")
    mercury_house = context.planet_houses.get("mercury")

    is_present = False
    details = "Mercury and Sun must conjoin in a benefic house."

    if sun_house and mercury_house and sun_house == mercury_house and sun_house in {1, 2, 5, 9, 10, 11}:
        is_present = True
        details = f"Mercury-Sun conjunction in house {sun_house} - intelligence, logic."

    return YogaRuleResult(
        name="Budha-Aditya (Strong)",
        category="Intellectual",
        is_present=is_present,
        planets_involved=["mercury", "sun"],
        details=details,
    )


def _parvata_yoga(context: PlanetaryYogaContext) -> YogaRuleResult:
    """Parvata Yoga: Benefics in kendras and no malefics in kendras."""
    benefics_in_kendra = [p for p, h in context.planet_houses.items() if _is_in_kendra(h) and _is_benefic(p)]
    malefics_in_kendra = [p for p, h in context.planet_houses.items() if _is_in_kendra(h) and _is_malefic(p)]

    is_present = len(benefics_in_kendra) >= 2 and len(malefics_in_kendra) == 0  # noqa: PLR2004
    details = (
        f"Benefics in kendras ({benefics_in_kendra}) with no malefics - stability, happiness."
        if is_present
        else "At least 2 benefics in kendras, no malefics required."
    )

    return YogaRuleResult(
        name="Parvata Yoga",
        category="Nabhasa",
        is_present=is_present,
        planets_involved=benefics_in_kendra,
        details=details,
    )


def _kahala_yoga(context: PlanetaryYogaContext) -> YogaRuleResult:
    """Kahala Yoga: 4th and 9th lords in mutual kendras."""
    fourth_lord = context.house_lords.get(4) if context.house_lords else None
    ninth_lord = context.house_lords.get(9) if context.house_lords else None

    is_present = False
    details = "4th and 9th lords must be in mutual kendras."

    if fourth_lord and ninth_lord:
        fourth_house = context.planet_houses.get(fourth_lord)
        ninth_house = context.planet_houses.get(ninth_lord)

        if fourth_house and ninth_house:
            house_diff = abs(fourth_house - ninth_house)
            mutual_kendra = house_diff in {0, 3, 6, 9}
            if mutual_kendra:
                is_present = True
                details = "4th and 9th lords in mutual kendras - prosperity, fame."

    return YogaRuleResult(
        name="Kahala Yoga",
        category="Fame",
        is_present=is_present,
        planets_involved=[fourth_lord, ninth_lord] if fourth_lord and ninth_lord else [],
        details=details,
    )


def _chamara_yoga(context: PlanetaryYogaContext) -> YogaRuleResult:
    """Chamara Yoga: Exalted lagna lord in a kendra aspected by Jupiter."""
    lagna_lord = context.house_lords.get(1) if context.house_lords else None
    lagna_house = context.planet_houses.get(lagna_lord) if lagna_lord else None
    jupiter_house = context.planet_houses.get("jupiter")

    is_present = False
    details = "Exalted lagna lord in kendra aspected by Jupiter required."

    if lagna_lord and lagna_house and jupiter_house:
        lagna_rasi = context.planet_rasis.get(lagna_lord)
        is_exalted = context.exaltation_signs and lagna_rasi and context.exaltation_signs.get(lagna_lord) == lagna_rasi

        if is_exalted and _is_in_kendra(lagna_house):
            is_present = True
            details = "Exalted lagna lord in kendra - royal status, authority."

    return YogaRuleResult(
        name="Chamara Yoga",
        category="Royal",
        is_present=is_present,
        planets_involved=[lagna_lord, "jupiter"] if lagna_lord else ["jupiter"],
        details=details,
    )


def _sankha_yoga(context: PlanetaryYogaContext) -> YogaRuleResult:
    """Sankha Yoga: 5th and 6th lords in mutual kendras."""
    fifth_lord = context.house_lords.get(5) if context.house_lords else None
    sixth_lord = context.house_lords.get(6) if context.house_lords else None

    is_present = False
    details = "5th and 6th lords must be in mutual kendras."

    if fifth_lord and sixth_lord:
        fifth_house = context.planet_houses.get(fifth_lord)
        sixth_house = context.planet_houses.get(sixth_lord)

        if fifth_house and sixth_house:
            house_diff = abs(fifth_house - sixth_house)
            mutual_kendra = house_diff in {0, 3, 6, 9}
            if mutual_kendra:
                is_present = True
                details = "5th and 6th lords in mutual kendras - good conduct, wealth."

    return YogaRuleResult(
        name="Sankha Yoga",
        category="Prosperity",
        is_present=is_present,
        planets_involved=[fifth_lord, sixth_lord] if fifth_lord and sixth_lord else [],
        details=details,
    )


def _matsya_yoga(context: PlanetaryYogaContext) -> YogaRuleResult:
    """Matsya Yoga: All planets in first and last seven houses."""
    houses = list(context.planet_houses.values())

    first_seven = all(h <= 7 for h in houses)  # noqa: PLR2004
    last_seven = all(h >= 6 for h in houses)  # noqa: PLR2004

    is_present = first_seven or last_seven
    details = (
        "All planets in first/last seven houses - flexibility, adaptability."
        if is_present
        else "Planets must be concentrated in 7 consecutive houses."
    )

    return YogaRuleResult(
        name="Matsya Yoga",
        category="Nabhasa",
        is_present=is_present,
        planets_involved=list(context.planet_houses.keys()),
        details=details,
    )


def _vasumathi_yoga(context: PlanetaryYogaContext) -> YogaRuleResult:
    """Vasumathi Yoga: Benefics in upachayas (3, 6, 10, 11) from lagna/moon."""
    upachaya_houses = {3, 6, 10, 11}
    benefics_in_upachaya = [p for p, h in context.planet_houses.items() if _is_benefic(p) and h in upachaya_houses]

    is_present = len(benefics_in_upachaya) >= 1
    details = (
        f"Benefics ({benefics_in_upachaya}) in upachayas - gradual wealth accumulation."
        if is_present
        else "Benefics should be in upachaya houses (3,6,10,11)."
    )

    return YogaRuleResult(
        name="Vasumathi Yoga",
        category="Wealth",
        is_present=is_present,
        planets_involved=benefics_in_upachaya,
        details=details,
    )


def evaluate_extended_yogas(context: PlanetaryYogaContext) -> list[YogaRuleResult]:
    """Evaluate extended catalog of planetary yogas.

    Args:
        context: PlanetaryYogaContext with placements.

    Returns:
        List of YogaRuleResult for extended yogas.

    """
    extended_rules = [
        _lakshmi_yoga,
        _saraswati_yoga,
        _budha_aditya_strong_yoga,
        _parvata_yoga,
        _kahala_yoga,
        _chamara_yoga,
        _sankha_yoga,
        _matsya_yoga,
        _vasumathi_yoga,
    ]

    results = [rule(context) for rule in extended_rules]
    return [result for result in results if result.is_present]
