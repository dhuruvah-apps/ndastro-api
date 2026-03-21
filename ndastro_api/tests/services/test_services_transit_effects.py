"""Unit tests for ndastro_api.services.transit_effects."""

from ndastro_api.services.transit_effects import (
    HOUSE_TRANSIT_THEMES,
    TransitDuration,
    TransitEffect,
    TransitImpact,
    TransitInterpretation,
    analyze_transit_effects,
    interpret_transit,
)

# ---------------------------------------------------------------------------
# TransitImpact enum
# ---------------------------------------------------------------------------


def test_transit_impact_very_favorable():
    assert TransitImpact.VERY_FAVORABLE == "very_favorable"


def test_transit_impact_challenging():
    assert TransitImpact.CHALLENGING == "challenging"


def test_transit_impact_neutral():
    assert TransitImpact.NEUTRAL == "neutral"


def test_transit_impact_has_five_members():
    assert len(list(TransitImpact)) == 5


# ---------------------------------------------------------------------------
# TransitDuration enum
# ---------------------------------------------------------------------------


def test_transit_duration_brief():
    assert TransitDuration.BRIEF == "brief"


def test_transit_duration_extended():
    assert TransitDuration.EXTENDED == "extended"


def test_transit_duration_has_five_members():
    assert len(list(TransitDuration)) == 5


# ---------------------------------------------------------------------------
# HOUSE_TRANSIT_THEMES
# ---------------------------------------------------------------------------


def test_house_transit_themes_has_12_houses():
    assert len(HOUSE_TRANSIT_THEMES) == 12


def test_house_transit_themes_house_1():
    assert 1 in HOUSE_TRANSIT_THEMES


# ---------------------------------------------------------------------------
# interpret_transit()
# ---------------------------------------------------------------------------


def test_interpret_transit_returns_dataclass():
    result = interpret_transit("jupiter", 1)
    assert isinstance(result, TransitInterpretation)


def test_interpret_transit_planet_matches():
    result = interpret_transit("sun", 5)
    assert result.transiting_planet == "sun"


def test_interpret_transit_house_matches():
    result = interpret_transit("moon", 7)
    assert result.natal_house == 7


def test_interpret_transit_impact_is_enum():
    result = interpret_transit("saturn", 8)
    assert isinstance(result.impact, TransitImpact)


def test_interpret_transit_duration_is_enum():
    result = interpret_transit("jupiter", 4)
    assert isinstance(result.duration, TransitDuration)


def test_interpret_transit_description_nonempty():
    result = interpret_transit("mars", 3)
    assert isinstance(result.description, str) and len(result.description) > 0


def test_interpret_transit_no_natal_planet():
    result = interpret_transit("venus", 2)
    assert result.natal_planet is None


def test_interpret_transit_retrograde_flag():
    result = interpret_transit("saturn", 12, is_retrograde=True)
    assert isinstance(result, TransitInterpretation)


# ---------------------------------------------------------------------------
# analyze_transit_effects()
# ---------------------------------------------------------------------------


def test_analyze_transit_effects_returns_list():
    result = analyze_transit_effects({"jupiter": 1, "saturn": 8})
    assert isinstance(result, list)


def test_analyze_transit_effects_count_matches():
    result = analyze_transit_effects({"sun": 1, "moon": 4, "mars": 6})
    assert len(result) == 3


def test_analyze_transit_effects_each_is_transit_effect():
    result = analyze_transit_effects({"venus": 7})
    assert isinstance(result[0], TransitEffect)


def test_analyze_transit_effects_overall_impact_is_enum():
    result = analyze_transit_effects({"jupiter": 9})
    assert isinstance(result[0].overall_impact, TransitImpact)


def test_analyze_transit_effects_retrograde_planets():
    result = analyze_transit_effects(
        {"saturn": 12, "mercury": 3},
        retrograde_planets=["saturn"],
    )
    sat = next(r for r in result if r.planet == "saturn")
    assert sat.is_retrograde is True
