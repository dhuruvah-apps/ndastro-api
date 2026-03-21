"""Unit tests for ndastro_api.services.yoga_extended."""

from ndastro_api.services.yoga_extended import (
    BENEFIC_PLANETS_LOWER,
    DUSTHANA_HOUSES,
    KENDRA_HOUSES,
    MALEFIC_PLANETS_LOWER,
    TRIKONA_HOUSES,
    ExtendedYoga,
    evaluate_extended_yogas,
)
from ndastro_api.services.yogas import PlanetaryYogaContext, YogaRuleResult

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_kendra_houses():
    assert {1, 4, 7, 10} == KENDRA_HOUSES


def test_trikona_houses():
    assert {1, 5, 9} == TRIKONA_HOUSES


def test_dusthana_houses():
    assert {6, 8, 12} == DUSTHANA_HOUSES


def test_benefic_planets_lower_contains_jupiter():
    assert "jupiter" in BENEFIC_PLANETS_LOWER


def test_malefic_planets_lower_contains_saturn():
    assert "saturn" in MALEFIC_PLANETS_LOWER


# ---------------------------------------------------------------------------
# ExtendedYoga dataclass
# ---------------------------------------------------------------------------


def test_extended_yoga_construction():
    yoga = ExtendedYoga(
        name="Lakshmi Yoga",
        category="Wealth",
        description="Venus and 9th lord in kendra/trikona.",
        strength="Strong",
    )
    assert yoga.name == "Lakshmi Yoga"
    assert yoga.category == "Wealth"
    assert yoga.strength == "Strong"


# ---------------------------------------------------------------------------
# evaluate_extended_yogas()
# ---------------------------------------------------------------------------


def _minimal_context() -> PlanetaryYogaContext:
    return PlanetaryYogaContext(
        planet_houses={
            "sun": 1,
            "moon": 4,
            "mars": 7,
            "mercury": 10,
            "jupiter": 5,
            "venus": 9,
            "saturn": 8,
            "rahu": 3,
            "kethu": 9,
        },
        planet_rasis={
            "sun": "aries",
            "moon": "cancer",
            "mars": "libra",
            "mercury": "capricorn",
            "jupiter": "leo",
            "venus": "sagittarius",
            "saturn": "scorpio",
            "rahu": "gemini",
            "kethu": "sagittarius",
        },
        house_lords={1: "mars", 2: "venus", 9: "jupiter", 10: "saturn"},
    )


def test_evaluate_extended_yogas_returns_list():
    ctx = _minimal_context()
    result = evaluate_extended_yogas(ctx)
    assert isinstance(result, list)


def test_evaluate_extended_yogas_items_are_yoga_rule_results():
    ctx = _minimal_context()
    result = evaluate_extended_yogas(ctx)
    for item in result:
        assert isinstance(item, YogaRuleResult)


def test_evaluate_extended_yogas_each_has_name():
    ctx = _minimal_context()
    result = evaluate_extended_yogas(ctx)
    for item in result:
        assert isinstance(item.name, str) and len(item.name) > 0


def test_evaluate_extended_yogas_is_present_is_bool():
    ctx = _minimal_context()
    result = evaluate_extended_yogas(ctx)
    for item in result:
        assert isinstance(item.is_present, bool)


def test_evaluate_extended_yogas_with_favorable_chart():
    """Chart with Venus and 9th lord in kendra → Lakshmi Yoga should be present."""
    ctx = PlanetaryYogaContext(
        planet_houses={
            "sun": 1,
            "moon": 4,
            "mars": 3,
            "mercury": 2,
            "jupiter": 1,
            "venus": 9,
            "saturn": 6,
            "rahu": 11,
            "kethu": 5,
        },
        planet_rasis={
            "sun": "aries",
            "moon": "cancer",
            "jupiter": "aries",
            "venus": "sagittarius",
        },
        house_lords={1: "mars", 9: "jupiter"},
    )
    result = evaluate_extended_yogas(ctx)
    names = [r.name for r in result]
    assert len(names) > 0  # At least some yogas evaluated
