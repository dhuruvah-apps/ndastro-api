"""Unit tests for ndastro_api.services.chart_utils."""

from ndastro_api.services.chart_utils import (
    BORDER_WIDTH,
    CELL_COUNT,
    CENTER_2X2_SKIP,
    CHART_BORDER_COLOR,
    CHART_SIZE,
    MAX_PLANETS_PER_SLOT,
    SOUTH_INDIAN_LAYOUT,
    BirthDetails,
    KattamDisplayData,
    houses,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_chart_border_color():
    assert CHART_BORDER_COLOR == "#FF0000"


def test_chart_size():
    assert CHART_SIZE == 100


def test_cell_count():
    assert CELL_COUNT == 4


def test_border_width():
    assert BORDER_WIDTH == 0.5


def test_max_planets_per_slot():
    assert MAX_PLANETS_PER_SLOT == 4


def test_center_2x2_skip_has_4_entries():
    """The four center cells (2×2) must be detected and skipped."""
    assert len(CENTER_2X2_SKIP) == 4


def test_south_indian_layout_has_12_entries():
    assert len(SOUTH_INDIAN_LAYOUT) == 12


def test_south_indian_layout_house_1():
    # House 1 maps to (row=1, col=0) per source
    assert SOUTH_INDIAN_LAYOUT[1] == (1, 0)


def test_south_indian_layout_all_valid():
    for house in range(1, 13):
        pos = SOUTH_INDIAN_LAYOUT[house]
        row, col = pos
        assert 0 <= row <= 3 and 0 <= col <= 3


def test_houses_roman_numerals():
    assert houses[0] == "I"
    assert houses[11] == "XII"
    assert len(houses) == 12


# ---------------------------------------------------------------------------
# BirthDetails Pydantic model
# ---------------------------------------------------------------------------


def test_birth_details_empty():
    bd = BirthDetails()
    assert bd.name_abbr is None
    assert bd.date is None
    assert bd.time is None
    assert bd.place is None


def test_birth_details_with_values():
    bd = BirthDetails(name_abbr="AB", date="2024-01-15", time="06:30", place="Chennai")
    assert bd.name_abbr == "AB"
    assert bd.date == "2024-01-15"


# ---------------------------------------------------------------------------
# KattamDisplayData dataclass
# ---------------------------------------------------------------------------


def test_kattam_display_data_construction():
    kdd = KattamDisplayData(
        name="Sun",
        short_name="Su",
        display_name="Sun",
        retro=False,
        adv=False,
        px_frac=0.5,
    )
    assert kdd.name == "Sun"
    assert kdd.retro is False
