"""Unit tests for ndastro_api.services.nakshatra_traits."""

from ndastro_api.services.nakshatra_traits import (
    NAKSHATRA_ARC_DEGREES,
    NAKSHATRA_COUNT,
    NAKSHATRA_LORDS,
    NAKSHATRA_NAMES,
    PADA_ARC_DEGREES,
    PADA_PER_NAKSHATRA,
    NakshatraGana,
    NakshatraPosition,
    NakshatraTraits,
    NakshatraType,
    calculate_nakshatra_position,
    get_nakshatra_from_longitude,
    get_nakshatra_traits,
    get_pada_from_longitude,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_nakshatra_count():
    assert NAKSHATRA_COUNT == 27


def test_nakshatra_arc_degrees():
    assert abs(NAKSHATRA_ARC_DEGREES - 360.0 / 27) < 1e-9


def test_pada_per_nakshatra():
    assert PADA_PER_NAKSHATRA == 4


def test_pada_arc_degrees():
    assert abs(PADA_ARC_DEGREES - NAKSHATRA_ARC_DEGREES / 4) < 1e-9


def test_nakshatra_names_count():
    assert len(NAKSHATRA_NAMES) == 27


def test_nakshatra_lords_count():
    assert len(NAKSHATRA_LORDS) == 27


def test_first_nakshatra_name():
    assert NAKSHATRA_NAMES[0] == "Ashwini"


def test_first_nakshatra_lord():
    assert NAKSHATRA_LORDS[0] == "Ketu"


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


def test_nakshatra_gana_values():
    assert NakshatraGana.DEVA.value == "Deva"
    assert NakshatraGana.MANUSHYA.value == "Manushya"
    assert NakshatraGana.RAKSHASA.value == "Rakshasa"


def test_nakshatra_type_values():
    assert NakshatraType.FIXED.value == "Fixed"
    assert NakshatraType.MOVABLE.value == "Movable"
    assert NakshatraType.DUAL.value == "Dual"


# ---------------------------------------------------------------------------
# get_nakshatra_from_longitude()
# ---------------------------------------------------------------------------


def test_nakshatra_at_zero():
    # Longitude 0 → nakshatra index 1 (Ashwini, 1-indexed)
    assert get_nakshatra_from_longitude(0.0) == 1


def test_nakshatra_at_second_nak():
    # Past 13.333° → nakshatra index 2 (Bharani)
    assert get_nakshatra_from_longitude(NAKSHATRA_ARC_DEGREES + 0.1) == 2


def test_nakshatra_at_last():
    # Just before 360° → last nakshatra index 27 (Revati, 1-indexed)
    assert get_nakshatra_from_longitude(359.9) == 27


def test_nakshatra_returns_int():
    assert isinstance(get_nakshatra_from_longitude(45.0), int)


def test_nakshatra_index_in_range():
    for lon in range(0, 360, 13):
        idx = get_nakshatra_from_longitude(float(lon))
        assert 1 <= idx <= 27


# ---------------------------------------------------------------------------
# get_pada_from_longitude()
# ---------------------------------------------------------------------------


def test_pada_first():
    assert get_pada_from_longitude(0.0) == 1


def test_pada_second():
    assert get_pada_from_longitude(PADA_ARC_DEGREES + 0.01) == 2


def test_pada_in_range():
    for lon in range(0, 360, 3):
        pada = get_pada_from_longitude(float(lon))
        assert 1 <= pada <= 4


# ---------------------------------------------------------------------------
# get_nakshatra_traits()
# ---------------------------------------------------------------------------


def test_get_traits_returns_dataclass():
    traits = get_nakshatra_traits(1)
    assert isinstance(traits, NakshatraTraits)


def test_get_traits_ashwini_name():
    traits = get_nakshatra_traits(1)
    assert traits.name == "Ashwini"


def test_get_traits_ashwini_lord():
    traits = get_nakshatra_traits(1)
    assert traits.lord == "Ketu"


def test_get_traits_all_valid():
    for i in range(1, 28):
        traits = get_nakshatra_traits(i)
        assert traits.name == NAKSHATRA_NAMES[i - 1]


# ---------------------------------------------------------------------------
# calculate_nakshatra_position()
# ---------------------------------------------------------------------------


def test_calculate_nakshatra_position_returns_dataclass():
    pos = calculate_nakshatra_position(0.0)
    assert isinstance(pos, NakshatraPosition)


def test_calculate_nakshatra_position_ashwini():
    pos = calculate_nakshatra_position(0.0)
    assert pos.nakshatra_index == 1  # 1-indexed
    assert pos.nakshatra_name == "Ashwini"
    assert pos.pada == 1


def test_calculate_nakshatra_position_mid_nak():
    # Longitude at middle of Bharani (1 * 13.333 + 6.666)
    mid = NAKSHATRA_ARC_DEGREES * 1.5
    pos = calculate_nakshatra_position(mid)
    assert pos.nakshatra_index == 2  # 1-indexed
    assert pos.nakshatra_name == "Bharani"
