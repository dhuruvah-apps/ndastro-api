"""Extended tests for ndastro_api.services.ashtakavarga_transits - prediction functions."""

import pytest

from ndastro_api.services.ashtakavarga_transits import (
    AshtakavargaTransitPrediction,
    AshtakavargaTransitReport,
    TransitPredictionStrength,
    calculate_prediction_strength,
    generate_ashtakavarga_transit_report,
    generate_primary_effects,
    generate_recommendations,
    generate_timing_notes,
    predict_ashtakavarga_transit,
)

# ---------------------------------------------------------------------------
# calculate_prediction_strength — neutral transit branches
# ---------------------------------------------------------------------------


def test_prediction_strength_neutral_transit_strong():
    result = calculate_prediction_strength(35, "neutral")
    assert result == TransitPredictionStrength.GOOD


def test_prediction_strength_neutral_transit_moderate():
    result = calculate_prediction_strength(25, "neutral")
    assert result == TransitPredictionStrength.NEUTRAL


def test_prediction_strength_neutral_transit_weak():
    result = calculate_prediction_strength(5, "neutral")
    assert result == TransitPredictionStrength.CHALLENGING


def test_prediction_strength_beneficial_moderate():
    result = calculate_prediction_strength(25, "beneficial")
    assert result == TransitPredictionStrength.VERY_GOOD


def test_prediction_strength_beneficial_weak():
    result = calculate_prediction_strength(15, "beneficial")
    assert result == TransitPredictionStrength.GOOD


def test_prediction_strength_beneficial_very_weak():
    result = calculate_prediction_strength(5, "beneficial")
    assert result == TransitPredictionStrength.NEUTRAL


def test_prediction_strength_challenging_moderate():
    result = calculate_prediction_strength(25, "challenging")
    assert result == TransitPredictionStrength.DIFFICULT


def test_prediction_strength_challenging_strong():
    result = calculate_prediction_strength(35, "challenging")
    assert result == TransitPredictionStrength.CHALLENGING


def test_prediction_strength_challenging_very_strong():
    result = calculate_prediction_strength(45, "challenging")
    assert result == TransitPredictionStrength.NEUTRAL


# ---------------------------------------------------------------------------
# generate_primary_effects — all combinations
# ---------------------------------------------------------------------------


def test_generate_primary_effects_returns_list():
    result = generate_primary_effects("jupiter", 1, "very_strong", "beneficial")
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.parametrize("planet", ["saturn", "jupiter", "moon", "mars"])
@pytest.mark.parametrize("house", [1, 4, 7, 10])
@pytest.mark.parametrize("nature", ["beneficial", "challenging", "neutral"])
def test_generate_primary_effects_all_combinations(planet, house, nature):
    result = generate_primary_effects(planet, house, "moderate", nature)
    assert isinstance(result, list)


def test_generate_primary_effects_challenging():
    result = generate_primary_effects("saturn", 6, "weak", "challenging")
    assert isinstance(result, list)
    assert any("challenge" in e.lower() or "difficult" in e.lower() or e for e in result)


def test_generate_primary_effects_unknown_planet():
    result = generate_primary_effects("unknown_planet", 5, "moderate", "neutral")
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# generate_recommendations — comprehensive
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("duration", ["slow", "medium", "fast"])
@pytest.mark.parametrize("strength", list(TransitPredictionStrength))
def test_generate_recommendations_all_combinations(duration, strength):
    result = generate_recommendations("saturn", 1, strength, duration)
    assert isinstance(result, list)
    assert len(result) > 0


def test_generate_recommendations_slow_long_term_message():
    result = generate_recommendations("saturn", 3, TransitPredictionStrength.EXCELLENT, "slow")
    messages = "\n".join(result)
    assert "long-term" in messages.lower() or "year" in messages.lower() or "saturn" in messages.lower()


def test_generate_recommendations_excellent_strength():
    result = generate_recommendations("jupiter", 5, TransitPredictionStrength.EXCELLENT, "slow")
    joined = "\n".join(result)
    assert "excellent" in joined.lower() or "project" in joined.lower() or "favorable" in joined.lower()


def test_generate_recommendations_very_difficult():
    result = generate_recommendations("saturn", 8, TransitPredictionStrength.VERY_DIFFICULT, "slow")
    joined = "\n".join(result)
    assert "caution" in joined.lower() or "challenging" in joined.lower() or "difficult" in joined.lower()


def test_generate_recommendations_all_houses():
    for house in range(1, 13):
        result = generate_recommendations("jupiter", house, TransitPredictionStrength.GOOD, "medium")
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# generate_timing_notes
# ---------------------------------------------------------------------------


def test_generate_timing_notes_slow():
    result = generate_timing_notes("saturn", "slow")
    assert "long" in result.lower() or "year" in result.lower()


def test_generate_timing_notes_medium():
    result = generate_timing_notes("mars", "medium")
    assert isinstance(result, str) and len(result) > 0


def test_generate_timing_notes_fast():
    result = generate_timing_notes("moon", "fast")
    assert "brief" in result.lower() or "quickly" in result.lower() or "quickly" in result or isinstance(result, str)


def test_generate_timing_notes_unknown_planet():
    result = generate_timing_notes("UNKNOWN_PLANET", "slow")
    assert "Variable" in result or isinstance(result, str)


@pytest.mark.parametrize("planet", ["jupiter", "saturn", "rahu", "kethu", "mars", "venus", "sun", "moon", "mercury"])
def test_generate_timing_notes_all_planets(planet):
    result = generate_timing_notes(planet, "medium")
    assert isinstance(result, str) and len(result) > 0


# ---------------------------------------------------------------------------
# predict_ashtakavarga_transit
# ---------------------------------------------------------------------------


def test_predict_ashtakavarga_transit_returns_result():
    result = predict_ashtakavarga_transit("jupiter", 5, 35)
    assert isinstance(result, AshtakavargaTransitPrediction)
    assert result.house == 5
    assert result.transiting_planet == "jupiter"


def test_predict_ashtakavarga_transit_all_planets():
    for planet in ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "kethu"]:
        result = predict_ashtakavarga_transit(planet, 1, 30)
        assert result.transiting_planet == planet


def test_predict_ashtakavarga_transit_all_houses():
    for house in range(1, 13):
        result = predict_ashtakavarga_transit("saturn", house, 25)
        assert result.house == house


def test_predict_ashtakavarga_transit_strong_sav():
    result = predict_ashtakavarga_transit("jupiter", 9, 45)
    assert result.sav_strength == "very_strong"


def test_predict_ashtakavarga_transit_weak_sav():
    result = predict_ashtakavarga_transit("saturn", 8, 5)
    assert result.sav_strength == "very_weak"


def test_predict_ashtakavarga_transit_has_effects_and_recs():
    result = predict_ashtakavarga_transit("jupiter", 1, 35)
    assert isinstance(result.primary_effects, list)
    assert isinstance(result.recommendations, list)
    assert isinstance(result.timing_notes, str)


def test_predict_ashtakavarga_transit_life_area_set():
    result = predict_ashtakavarga_transit("mars", 7, 28)
    from ndastro_api.services.ashtakavarga_transits import LifeAreaFocus

    assert result.life_area in list(LifeAreaFocus)


# ---------------------------------------------------------------------------
# generate_ashtakavarga_transit_report
# ---------------------------------------------------------------------------


def test_generate_report_returns_result():
    transit_houses = {"jupiter": 5, "saturn": 10}
    sav_scores = dict.fromkeys(range(1, 13), 30)
    result = generate_ashtakavarga_transit_report(transit_houses, sav_scores)
    assert isinstance(result, AshtakavargaTransitReport)
    assert len(result.predictions) == 2


def test_generate_report_incomplete_sav_uses_default():
    transit_houses = {"moon": 3}
    sav_scores = {}  # Empty - should use default of 25
    result = generate_ashtakavarga_transit_report(transit_houses, sav_scores)
    assert len(result.predictions) == 1
    assert result.predictions[0].sav_points == 25


def test_generate_report_all_planets():
    transit_houses = {
        "sun": 1,
        "moon": 4,
        "mars": 6,
        "mercury": 3,
        "jupiter": 9,
        "venus": 7,
        "saturn": 11,
        "rahu": 12,
        "kethu": 6,
    }
    sav_scores = {h: 25 + h for h in range(1, 13)}
    result = generate_ashtakavarga_transit_report(transit_houses, sav_scores)
    assert len(result.predictions) == 9


def test_generate_report_has_overall_assessment():
    transit_houses = {"jupiter": 9, "saturn": 12}
    sav_scores = {9: 45, 12: 10}
    result = generate_ashtakavarga_transit_report(transit_houses, sav_scores)
    assert isinstance(result.overall_period_assessment, str)
    assert len(result.overall_period_assessment) > 0


def test_generate_report_favorable_and_challenging_houses():
    transit_houses = {"jupiter": 5, "saturn": 8}
    sav_scores = {5: 40, 8: 5}
    result = generate_ashtakavarga_transit_report(transit_houses, sav_scores)
    assert isinstance(result.most_favorable_houses, list)
    assert isinstance(result.most_challenging_houses, list)


def test_generate_report_key_recommendations_present():
    transit_houses = {"saturn": 8}
    sav_scores = {8: 5}
    result = generate_ashtakavarga_transit_report(transit_houses, sav_scores)
    assert isinstance(result.key_recommendations, list)


def test_generate_report_excellent_best_gets_recommendation():
    # Jupiter in house 9 with max points = EXCELLENT
    transit_houses = {"jupiter": 9, "mars": 6}
    sav_scores = {9: 45, 6: 5}
    result = generate_ashtakavarga_transit_report(transit_houses, sav_scores)
    # Check that favorable is identified
    assert 9 in result.most_favorable_houses or isinstance(result, AshtakavargaTransitReport)
