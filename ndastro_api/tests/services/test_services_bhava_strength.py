"""Unit tests for ndastro_api.services.bhava_strength."""

from ndastro_api.services.bhava_strength import (
    HOUSE_COUNT,
    HOUSE_MEANINGS,
    STRONG_THRESHOLD,
    VERY_STRONG_THRESHOLD,
    VERY_WEAK_THRESHOLD,
    WEAK_THRESHOLD,
    BhavaStrengthClass,
    BhavaStrengthContext,
    BhavaStrengthResult,
    BhavaStrengthSummary,
    BhavaStrengthWeights,
    calculate_bhava_strength,
    get_bhava_strength_interpretation,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_house_count():
    assert HOUSE_COUNT == 12


def test_very_strong_threshold():
    assert VERY_STRONG_THRESHOLD == 10.0


def test_strong_threshold():
    assert STRONG_THRESHOLD == 6.0


def test_weak_threshold():
    assert WEAK_THRESHOLD == -2.0


def test_very_weak_threshold():
    assert VERY_WEAK_THRESHOLD == -6.0


def test_house_meanings_has_12_houses():
    assert len(HOUSE_MEANINGS) == 12


def test_house_meanings_house_1():
    assert 1 in HOUSE_MEANINGS
    assert isinstance(HOUSE_MEANINGS[1], str)


# ---------------------------------------------------------------------------
# BhavaStrengthClass
# ---------------------------------------------------------------------------


def test_bhava_strength_class_very_strong():
    assert BhavaStrengthClass.VERY_STRONG == "very_strong"


def test_bhava_strength_class_very_weak():
    assert BhavaStrengthClass.VERY_WEAK == "very_weak"


def test_bhava_strength_class_moderate():
    assert BhavaStrengthClass.MODERATE == "moderate"


# ---------------------------------------------------------------------------
# BhavaStrengthWeights dataclass
# ---------------------------------------------------------------------------


def test_bhava_strength_weights_defaults():
    weights = BhavaStrengthWeights()
    assert weights.occupant_benefic == 2.0
    assert weights.occupant_malefic == -2.0
    assert weights.lord_exalted == 3.0
    assert weights.lord_debilitated == -3.0


# ---------------------------------------------------------------------------
# BhavaStrengthContext dataclass
# ---------------------------------------------------------------------------


def _minimal_context() -> BhavaStrengthContext:
    return BhavaStrengthContext(
        planet_houses={"jupiter": 1, "saturn": 8},
        house_lords={
            1: "mars",
            2: "venus",
            3: "mercury",
            4: "moon",
            5: "sun",
            6: "mercury",
            7: "venus",
            8: "mars",
            9: "jupiter",
            10: "saturn",
            11: "saturn",
            12: "jupiter",
        },
    )


def test_bhava_context_construction():
    ctx = _minimal_context()
    assert ctx.planet_houses["jupiter"] == 1
    assert ctx.house_lords[1] == "mars"


def test_bhava_context_default_benefics():
    ctx = _minimal_context()
    assert "jupiter" in ctx.benefic_planets


def test_bhava_context_default_malefics():
    ctx = _minimal_context()
    assert "saturn" in ctx.malefic_planets


# ---------------------------------------------------------------------------
# calculate_bhava_strength()
# ---------------------------------------------------------------------------


def test_calculate_bhava_strength_returns_summary():
    ctx = _minimal_context()
    result = calculate_bhava_strength(ctx)
    assert isinstance(result, BhavaStrengthSummary)


def test_calculate_bhava_strength_has_12_houses():
    ctx = _minimal_context()
    result = calculate_bhava_strength(ctx)
    assert len(result.results) == 12


def test_calculate_bhava_strength_results_are_results():
    ctx = _minimal_context()
    summary = calculate_bhava_strength(ctx)
    for house, result in summary.results.items():
        assert isinstance(result, BhavaStrengthResult)
        assert result.house == house


def test_calculate_bhava_strength_average_score_is_float():
    ctx = _minimal_context()
    result = calculate_bhava_strength(ctx)
    assert isinstance(result.average_score, float)


def test_calculate_bhava_strength_strong_and_weak_lists():
    ctx = _minimal_context()
    result = calculate_bhava_strength(ctx)
    assert isinstance(result.strong_houses, list)
    assert isinstance(result.weak_houses, list)


def test_calculate_bhava_strength_custom_weights():
    ctx = _minimal_context()
    weights = BhavaStrengthWeights(occupant_benefic=5.0, lord_exalted=10.0)
    result = calculate_bhava_strength(ctx, weights=weights)
    assert isinstance(result, BhavaStrengthSummary)


# ---------------------------------------------------------------------------
# get_bhava_strength_interpretation()
# ---------------------------------------------------------------------------


def test_get_bhava_strength_interpretation_returns_str():
    ctx = _minimal_context()
    summary = calculate_bhava_strength(ctx)
    result_1 = summary.results[1]
    interpretation = get_bhava_strength_interpretation(result_1)
    assert isinstance(interpretation, str) and len(interpretation) > 0
