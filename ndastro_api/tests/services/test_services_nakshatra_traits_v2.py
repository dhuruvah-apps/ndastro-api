"""Extended tests for ndastro_api.services.nakshatra_traits - compatibility functions."""

import pytest

from ndastro_api.services.nakshatra_traits import (
    NAKSHATRA_COUNT,
    NakshatraCompatibility,
    NakshatraGana,
    NakshatraPosition,
    NakshatraTraits,
    NakshatraType,
    calculate_nakshatra_compatibility,
    calculate_nakshatra_position,
    get_nakshatra_from_longitude,
    get_nakshatra_traits,
    get_pada_from_longitude,
)

# ---------------------------------------------------------------------------
# get_nakshatra_compatibility — main coverage target
# ---------------------------------------------------------------------------


def test_get_nakshatra_compatibility_basic():
    result = calculate_nakshatra_compatibility(1, 2)
    assert isinstance(result, NakshatraCompatibility)
    assert result.nakshatra1 == 1
    assert result.nakshatra2 == 2


def test_get_nakshatra_compatibility_invalid_raises():
    with pytest.raises(ValueError):
        calculate_nakshatra_compatibility(0, 5)

    with pytest.raises(ValueError):
        calculate_nakshatra_compatibility(1, 28)


def test_get_nakshatra_compatibility_kuta_score_range():
    for n1 in range(1, 28):
        for n2 in [1, 14, 27]:
            result = calculate_nakshatra_compatibility(n1, n2)
            assert 0.0 <= result.kuta_score <= 9.0


def test_get_nakshatra_compatibility_levels():
    levels_seen = set()
    for n1 in range(1, 28):
        for n2 in range(1, 28):
            result = calculate_nakshatra_compatibility(n1, n2)
            levels_seen.add(result.compatibility_level)
    assert levels_seen.issubset({"Excellent", "Good", "Average", "Poor"})


def test_get_nakshatra_compatibility_same_nakshatra():
    # Distance = 0 → dina_score = 0 (since 0 is in {0, 9, 18})
    result = calculate_nakshatra_compatibility(1, 1)
    assert result.kuta_score >= 0.0


def test_get_nakshatra_compatibility_distance_9():
    # Distance = 9 → dina_score = 0
    result = calculate_nakshatra_compatibility(1, 10)
    assert result.kuta_score >= 0.0


def test_get_nakshatra_compatibility_deva_deva():
    # Find two Deva nakshatras: 1(Ashwini=Deva) and 5(Mrigashira=Deva)
    result = calculate_nakshatra_compatibility(1, 5)
    assert result.kuta_score >= 6.0  # Deva+Deva = gana_score 6


def test_get_nakshatra_compatibility_description_nonempty():
    result = calculate_nakshatra_compatibility(1, 14)
    assert isinstance(result.description, str) and len(result.description) > 0


def test_get_nakshatra_compatibility_names_set():
    result = calculate_nakshatra_compatibility(1, 27)
    assert result.name1 == "Ashwini"
    assert result.name2 == "Revati"


# ---------------------------------------------------------------------------
# Additional coverage: NakshatraTraits, NakshatraPosition
# ---------------------------------------------------------------------------


def test_get_nakshatra_traits_returns_traits():
    for idx in range(1, 28):
        traits = get_nakshatra_traits(idx)
        assert isinstance(traits, NakshatraTraits)
        assert traits.index == idx


def test_get_nakshatra_traits_gana_is_enum():
    for idx in range(1, 28):
        traits = get_nakshatra_traits(idx)
        assert traits.gana in list(NakshatraGana)


def test_get_nakshatra_traits_type_is_enum():
    for idx in range(1, 28):
        traits = get_nakshatra_traits(idx)
        assert traits.type in list(NakshatraType)


def test_get_nakshatra_position_returns_position():
    pos = calculate_nakshatra_position(45.0)
    assert isinstance(pos, NakshatraPosition)
    assert 1 <= pos.nakshatra_index <= 27
    assert 1 <= pos.pada <= 4


def test_get_nakshatra_traits_invalid_index_raises():
    with pytest.raises(ValueError, match="Invalid nakshatra index"):
        get_nakshatra_traits(0)


def test_get_nakshatra_traits_invalid_high_raises():
    with pytest.raises(ValueError, match="Invalid nakshatra index"):
        get_nakshatra_traits(28)


def test_get_nakshatra_from_longitude_in_range():
    for deg in range(0, 361, 15):
        idx = get_nakshatra_from_longitude(float(deg))
        assert 1 <= idx <= NAKSHATRA_COUNT


def test_get_pada_from_longitude():
    for deg in range(0, 361, 5):
        pada = get_pada_from_longitude(float(deg))
        assert 1 <= pada <= 4
