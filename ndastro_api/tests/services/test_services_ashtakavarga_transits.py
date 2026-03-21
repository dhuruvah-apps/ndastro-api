"""Unit tests for ndastro_api.services.ashtakavarga_transits."""

from ndastro_api.services.ashtakavarga_transits import (
    FAST_PLANETS,
    HOUSE_TO_LIFE_AREA,
    MEDIUM_PLANETS,
    SAV_MODERATE,
    SAV_STRONG,
    SAV_VERY_STRONG,
    SAV_WEAK,
    SLOW_PLANETS,
    LifeAreaFocus,
    TransitPredictionStrength,
    calculate_prediction_strength,
    classify_sav_strength,
    determine_transit_nature,
    generate_primary_effects,
    generate_timing_notes,
    get_duration_category,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_sav_very_strong():
    assert SAV_VERY_STRONG == 40


def test_sav_strong():
    assert SAV_STRONG == 30


def test_sav_moderate():
    assert SAV_MODERATE == 20


def test_sav_weak():
    assert SAV_WEAK == 10


def test_slow_planets_contains_saturn():
    assert "saturn" in SLOW_PLANETS


def test_fast_planets_contains_moon():
    assert "moon" in FAST_PLANETS


def test_medium_planets_contains_mars():
    assert "mars" in MEDIUM_PLANETS


def test_house_to_life_area_has_12_houses():
    assert len(HOUSE_TO_LIFE_AREA) == 12


# ---------------------------------------------------------------------------
# TransitPredictionStrength enum
# ---------------------------------------------------------------------------


def test_transit_strength_excellent():
    assert TransitPredictionStrength.EXCELLENT == "excellent"


def test_transit_strength_very_difficult():
    assert TransitPredictionStrength.VERY_DIFFICULT == "very_difficult"


def test_transit_strength_has_7_members():
    assert len(list(TransitPredictionStrength)) == 7


# ---------------------------------------------------------------------------
# LifeAreaFocus enum
# ---------------------------------------------------------------------------


def test_life_area_self_health():
    assert LifeAreaFocus.SELF_HEALTH == "self_health"


def test_life_area_career_status():
    assert LifeAreaFocus.CAREER_STATUS == "career_status"


def test_life_area_has_12_members():
    assert len(list(LifeAreaFocus)) == 12


# ---------------------------------------------------------------------------
# classify_sav_strength()
# ---------------------------------------------------------------------------


def test_classify_sav_very_strong():
    assert classify_sav_strength(45) == "very_strong"


def test_classify_sav_strong():
    assert classify_sav_strength(35) == "strong"


def test_classify_sav_moderate():
    assert classify_sav_strength(25) == "moderate"


def test_classify_sav_weak():
    assert classify_sav_strength(15) == "weak"


def test_classify_sav_very_weak():
    assert classify_sav_strength(5) == "very_weak"


def test_classify_sav_boundary_strong():
    assert classify_sav_strength(SAV_STRONG) == "strong"


def test_classify_sav_boundary_very_strong():
    assert classify_sav_strength(SAV_VERY_STRONG) == "very_strong"


# ---------------------------------------------------------------------------
# get_duration_category()
# ---------------------------------------------------------------------------


def test_duration_slow_planet():
    result = get_duration_category("saturn")
    assert isinstance(result, str) and len(result) > 0


def test_duration_fast_planet():
    result = get_duration_category("moon")
    assert isinstance(result, str) and len(result) > 0


def test_duration_differs_slow_vs_fast():
    slow = get_duration_category("saturn")
    fast = get_duration_category("moon")
    assert slow != fast


# ---------------------------------------------------------------------------
# determine_transit_nature()
# ---------------------------------------------------------------------------


def test_determine_transit_nature_returns_str():
    result = determine_transit_nature("jupiter", 1)
    assert result in ("beneficial", "neutral", "challenging")


def test_determine_transit_nature_all_houses():
    for house in range(1, 13):
        result = determine_transit_nature("saturn", house)
        assert result in ("beneficial", "neutral", "challenging")


# ---------------------------------------------------------------------------
# calculate_prediction_strength()
# ---------------------------------------------------------------------------


def test_calculate_prediction_strength_returns_enum():
    result = calculate_prediction_strength(45, "beneficial")
    assert isinstance(result, TransitPredictionStrength)


def test_calculate_prediction_strength_excellent():
    result = calculate_prediction_strength(45, "beneficial")
    assert result == TransitPredictionStrength.EXCELLENT


def test_calculate_prediction_strength_very_difficult():
    result = calculate_prediction_strength(5, "challenging")
    assert result == TransitPredictionStrength.VERY_DIFFICULT


# ---------------------------------------------------------------------------
# generate_primary_effects()
# ---------------------------------------------------------------------------


def test_generate_primary_effects_returns_list():
    result = generate_primary_effects("jupiter", 1, "very_strong", "beneficial")
    assert isinstance(result, list)


def test_generate_primary_effects_nonempty():
    result = generate_primary_effects("saturn", 8, "weak", "challenging")
    assert len(result) > 0


# ---------------------------------------------------------------------------
# generate_timing_notes()
# ---------------------------------------------------------------------------


def test_generate_timing_notes_returns_str():
    result = generate_timing_notes("saturn", "long")
    assert isinstance(result, str) and len(result) > 0
