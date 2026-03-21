"""Unit tests for ndastro_api.services.dasha_predictions."""

from ndastro_api.services.dasha_predictions import (
    HOUSE_SIGNIFICATIONS,
    PLANET_SIGNIFICATIONS,
    DashaContext,
    DashaPrediction,
    EventTiming,
    LifeArea,
    PredictionStrength,
    analyze_bhukti_combination,
    generate_comprehensive_dasha_prediction,
    generate_life_area_predictions,
    generate_recommendations,
    get_planet_natural_effects,
    interpret_house_lordship,
    interpret_house_placement,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_planet_significations_has_standard_planets():
    for planet in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"):
        assert planet in PLANET_SIGNIFICATIONS


def test_house_significations_has_12_houses():
    assert len(HOUSE_SIGNIFICATIONS) == 12


def test_planet_significations_sun_has_keys():
    sun = PLANET_SIGNIFICATIONS["sun"]
    assert "natural_significations" in sun
    assert "positive_traits" in sun
    assert "negative_traits" in sun


# ---------------------------------------------------------------------------
# LifeArea enum
# ---------------------------------------------------------------------------


def test_life_area_career():
    assert LifeArea.CAREER == "career"


def test_life_area_health():
    assert LifeArea.HEALTH == "health"


def test_life_area_has_members():
    assert len(list(LifeArea)) > 0


# ---------------------------------------------------------------------------
# PredictionStrength enum
# ---------------------------------------------------------------------------


def test_prediction_strength_very_strong():
    assert PredictionStrength.VERY_STRONG == "very_strong"


def test_prediction_strength_very_weak():
    assert PredictionStrength.VERY_WEAK == "very_weak"


# ---------------------------------------------------------------------------
# EventTiming enum
# ---------------------------------------------------------------------------


def test_event_timing_early():
    assert EventTiming.EARLY == "early"


def test_event_timing_throughout():
    assert EventTiming.THROUGHOUT == "throughout"


# ---------------------------------------------------------------------------
# get_planet_natural_effects()
# ---------------------------------------------------------------------------


def test_get_planet_natural_effects_sun():
    result = get_planet_natural_effects("sun")
    assert isinstance(result, dict)


def test_get_planet_natural_effects_has_significations():
    result = get_planet_natural_effects("moon")
    assert "natural_significations" in result or len(result) > 0


def test_get_planet_natural_effects_all_planets():
    for planet in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"):
        result = get_planet_natural_effects(planet)
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# interpret_house_lordship()
# ---------------------------------------------------------------------------


def test_interpret_house_lordship_returns_dict():
    result = interpret_house_lordship("sun", [1, 10])
    assert isinstance(result, dict)


def test_interpret_house_lordship_kendra_lord():
    result = interpret_house_lordship("jupiter", [1, 4])
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# interpret_house_placement()
# ---------------------------------------------------------------------------


def test_interpret_house_placement_returns_dict():
    result = interpret_house_placement("sun", 1)
    assert isinstance(result, dict)


def test_interpret_house_placement_12th_house():
    result = interpret_house_placement("saturn", 12)
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# generate_life_area_predictions()
# ---------------------------------------------------------------------------


def test_generate_life_area_predictions_returns_dict():
    result = generate_life_area_predictions("jupiter", [1, 4], 9)
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# generate_recommendations()
# ---------------------------------------------------------------------------


def test_generate_recommendations_returns_dict():
    result = generate_recommendations("venus", [7, 12])
    assert isinstance(result, dict)


def test_generate_recommendations_has_lists():
    result = generate_recommendations("saturn", [3, 6])
    for value in result.values():
        assert isinstance(value, list)


# ---------------------------------------------------------------------------
# analyze_bhukti_combination()
# ---------------------------------------------------------------------------


def test_analyze_bhukti_combination_returns_dataclass():
    from ndastro_api.services.dasha_predictions import BhuktiPrediction

    result = analyze_bhukti_combination("jupiter", "venus")
    assert isinstance(result, BhuktiPrediction)


def test_analyze_bhukti_combination_fields_set():
    result = analyze_bhukti_combination("sun", "saturn")
    assert result.maha_lord == "sun"
    assert result.bhukti_lord == "saturn"


# ---------------------------------------------------------------------------
# generate_comprehensive_dasha_prediction()
# ---------------------------------------------------------------------------


def test_generate_comprehensive_dasha_prediction_returns_dataclass():
    context = DashaContext(
        planet="jupiter",
        houses_owned=[9, 12],
        house_placed=1,
        dasha_level="maha",
        is_exalted=False,
        is_debilitated=False,
        is_retrograde=False,
    )
    result = generate_comprehensive_dasha_prediction(context)
    assert isinstance(result, DashaPrediction)


def test_generate_comprehensive_dasha_planet_matches():
    context = DashaContext(
        planet="venus",
        houses_owned=[1, 6],
        house_placed=7,
        dasha_level="maha",
        is_exalted=True,
        is_debilitated=False,
        is_retrograde=False,
    )
    result = generate_comprehensive_dasha_prediction(context)
    assert result.dasha_lord == "venus"
