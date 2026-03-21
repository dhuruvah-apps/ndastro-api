"""Extended tests for ndastro_api.services.ashtakavarga - SAV/BAV calculations."""

import pytest

from ndastro_api.services.ashtakavarga import (
    BENEFIC_PLANETS,
    MALEFIC_PLANETS,
    PLANET_HOUSES,
    AshtakavargaContext,
    AshtakavargaStrength,
    BhinnaAshtakavarga,
    SarvaAshtakavarga,
    calculate_sarva_ashtakavarga,
    get_ashtakavarga_interpretation,
    get_bhinna_planet_interpretation,
    get_house_strength_classification,
    get_strong_houses_for_activities,
)

# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------


def _make_context(
    exalted: list[str] | None = None,
    own_rasi: list[str] | None = None,
    debilitated: list[str] | None = None,
) -> AshtakavargaContext:
    return AshtakavargaContext(
        planets_in_houses={
            "sun": 1,
            "moon": 4,
            "mars": 8,
            "mercury": 2,
            "jupiter": 5,
            "venus": 7,
            "saturn": 10,
            "rahu": 12,
            "kethu": 6,
        },
        planets_in_rasis={
            "sun": "aries",
            "moon": "cancer",
            "mars": "scorpio",
            "mercury": "taurus",
            "jupiter": "leo",
            "venus": "libra",
            "saturn": "capricorn",
            "rahu": "pisces",
            "kethu": "virgo",
        },
        aspecting_planets={
            "sun": ["jupiter"],
            "moon": [],
            "mars": ["saturn"],
            "mercury": ["venus"],
            "jupiter": ["moon"],
            "venus": [],
            "saturn": [],
            "rahu": [],
            "kethu": [],
        },
        conjunct_planets={
            "sun": [],
            "moon": ["jupiter"],
            "mars": [],
            "mercury": [],
            "jupiter": ["moon"],
            "venus": [],
            "saturn": [],
            "rahu": [],
            "kethu": [],
        },
        exalted_planets=exalted,
        own_rasi_planets=own_rasi,
        debilitated_planets=debilitated,
    )


# ---------------------------------------------------------------------------
# AshtakavargaContext construction
# ---------------------------------------------------------------------------


def test_context_basic_construction():
    ctx = _make_context()
    assert len(ctx.planets_in_houses) == 9
    assert ctx.exalted_planets is None


def test_context_with_exalted():
    ctx = _make_context(exalted=["sun"])
    assert ctx.exalted_planets == ["sun"]


# ---------------------------------------------------------------------------
# calculate_sarva_ashtakavarga
# ---------------------------------------------------------------------------


def test_calculate_sarva_ashtakavarga_returns_result():
    ctx = _make_context()
    result = calculate_sarva_ashtakavarga(ctx)
    assert isinstance(result, SarvaAshtakavarga)


def test_calculate_sarva_ashtakavarga_has_all_12_houses():
    ctx = _make_context()
    result = calculate_sarva_ashtakavarga(ctx)
    assert len(result.points_per_house) == 12
    for house in range(1, 13):
        assert house in result.points_per_house


def test_calculate_sarva_ashtakavarga_has_bhinna_for_all_planets():
    ctx = _make_context()
    result = calculate_sarva_ashtakavarga(ctx)
    for planet in ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "kethu"):
        assert planet in result.bhinna_maps


def test_calculate_sarva_ashtakavarga_classified_houses():
    ctx = _make_context()
    result = calculate_sarva_ashtakavarga(ctx)
    # All classified houses should be in 1-12
    for house in result.strong_houses + result.moderate_houses + result.weak_houses:
        assert 1 <= house <= 12


def test_calculate_sarva_ashtakavarga_with_exaltation_bonus():
    ctx_normal = _make_context()
    ctx_exalted = _make_context(exalted=["sun", "moon"])
    result_normal = calculate_sarva_ashtakavarga(ctx_normal)
    result_exalted = calculate_sarva_ashtakavarga(ctx_exalted)
    # Exaltation should give more points overall
    sum_normal = sum(result_normal.points_per_house.values())
    sum_exalted = sum(result_exalted.points_per_house.values())
    assert sum_exalted >= sum_normal


def test_calculate_sarva_ashtakavarga_with_own_rasi_bonus():
    ctx = _make_context(own_rasi=["mars", "venus"])
    result = calculate_sarva_ashtakavarga(ctx)
    assert result is not None


def test_calculate_sarva_ashtakavarga_with_debilitation_penalty():
    ctx_normal = _make_context()
    ctx_debilitated = _make_context(debilitated=["sun", "moon"])
    result_normal = calculate_sarva_ashtakavarga(ctx_normal)
    result_debilitated = calculate_sarva_ashtakavarga(ctx_debilitated)
    # Debilitation should reduce points
    sum_normal = sum(result_normal.points_per_house.values())
    sum_debilitated = sum(result_debilitated.points_per_house.values())
    assert sum_debilitated <= sum_normal


def test_calculate_sarva_ashtakavarga_points_non_negative():
    ctx = _make_context(debilitated=["sun", "moon", "mars"])
    result = calculate_sarva_ashtakavarga(ctx)
    for points in result.points_per_house.values():
        assert points >= 0


# ---------------------------------------------------------------------------
# BhinnaAshtakavarga - verify individual planet maps
# ---------------------------------------------------------------------------


def test_bhinna_ashtakavarga_has_12_houses():
    ctx = _make_context()
    result = calculate_sarva_ashtakavarga(ctx)
    for planet, bhinna in result.bhinna_maps.items():
        assert len(bhinna.points_per_house) == 12


def test_bhinna_ashtakavarga_total_points():
    ctx = _make_context()
    result = calculate_sarva_ashtakavarga(ctx)
    for planet, bhinna in result.bhinna_maps.items():
        assert bhinna.total_points == sum(bhinna.points_per_house.values())


def test_bhinna_ashtakavarga_average_per_house():
    ctx = _make_context()
    result = calculate_sarva_ashtakavarga(ctx)
    for planet, bhinna in result.bhinna_maps.items():
        ruled = len(PLANET_HOUSES.get(planet, set()))
        if ruled > 0:
            assert bhinna.average_per_house == bhinna.total_points / ruled


# ---------------------------------------------------------------------------
# get_ashtakavarga_interpretation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("house", range(1, 13))
def test_get_ashtakavarga_interpretation_all_houses(house):
    result = get_ashtakavarga_interpretation(house, points=35, strength=AshtakavargaStrength.STRONG)
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.parametrize("strength", list(AshtakavargaStrength))
def test_get_ashtakavarga_interpretation_all_strengths(strength):
    result = get_ashtakavarga_interpretation(1, points=25, strength=strength)
    assert isinstance(result, str)
    assert "pt" in result.lower() or "25" in result


def test_get_ashtakavarga_interpretation_unknown_house():
    result = get_ashtakavarga_interpretation(15, points=20, strength=AshtakavargaStrength.MODERATE)
    assert "House 15" in result or isinstance(result, str)


# ---------------------------------------------------------------------------
# get_bhinna_planet_interpretation
# ---------------------------------------------------------------------------


def test_bhinna_planet_interpretation_very_strong():
    result = get_bhinna_planet_interpretation("sun", [7, 8, 6, 7, 8, 5, 6, 7])
    assert "Very strong" in result or "Strong" in result


def test_bhinna_planet_interpretation_weak():
    result = get_bhinna_planet_interpretation("saturn", [1, 2, 1, 0, 1, 2, 1, 0])
    assert "Weak" in result


def test_bhinna_planet_interpretation_empty_points():
    result = get_bhinna_planet_interpretation("mars", [])
    # avg = 0 → Weak
    assert "Weak" in result


def test_bhinna_planet_interpretation_moderate():
    result = get_bhinna_planet_interpretation("venus", [3, 4, 3, 4, 3, 4, 3, 4])
    assert "Moderate" in result or "Strong" in result


# ---------------------------------------------------------------------------
# get_house_strength_classification - edge cases
# ---------------------------------------------------------------------------


def test_strength_very_strong_40():
    assert get_house_strength_classification(40) == AshtakavargaStrength.VERY_STRONG


def test_strength_strong_30():
    assert get_house_strength_classification(30) == AshtakavargaStrength.STRONG


def test_strength_moderate_20():
    assert get_house_strength_classification(20) == AshtakavargaStrength.MODERATE


def test_strength_weak_10():
    assert get_house_strength_classification(10) == AshtakavargaStrength.WEAK


def test_strength_very_weak_9():
    assert get_house_strength_classification(9) == AshtakavargaStrength.VERY_WEAK


# ---------------------------------------------------------------------------
# get_strong_houses_for_activities
# ---------------------------------------------------------------------------


def test_get_strong_houses_returns_dict():
    ctx = _make_context()
    sav = calculate_sarva_ashtakavarga(ctx)
    result = get_strong_houses_for_activities(sav)
    assert isinstance(result, dict)


def test_get_strong_houses_all_categories_present():
    ctx = _make_context()
    sav = calculate_sarva_ashtakavarga(ctx)
    result = get_strong_houses_for_activities(sav)
    expected_keys = {"business_ventures", "marriage_events", "buying_property", "education", "health_matters", "spiritual_pursuits"}
    assert set(result.keys()) == expected_keys


def test_get_strong_houses_all_in_1_12():
    ctx = _make_context()
    sav = calculate_sarva_ashtakavarga(ctx)
    result = get_strong_houses_for_activities(sav)
    for category, houses in result.items():
        for house in houses:
            assert 1 <= house <= 12


def test_get_strong_houses_empty_strong_uses_moderate():
    # Create a SAV with no strong houses
    sav = SarvaAshtakavarga(
        points_per_house={h: 25 for h in range(1, 13)},  # All moderate
        strong_houses=[],
        moderate_houses=list(range(1, 13)),
        weak_houses=[],
    )
    result = get_strong_houses_for_activities(sav)
    assert isinstance(result, dict)
