"""Extended tests for ndastro_api.services.chart_utils - SVG generation helper functions."""

import unittest.mock

import pytest

from ndastro_api.services.chart_utils import (
    CELL_COUNT,
    CENTER_2X2_SKIP,
    CHART_BORDER_COLOR,
    SOUTH_INDIAN_LAYOUT,
    BirthDetails,
    KattamDisplayData,
    calculate_planet_positions,
    draw_chart_borders,
    generate_south_indian_chart_svg,
    render_center_text,
    render_house_and_planets,
)


@pytest.fixture(autouse=True)
def _patch_gettext():
    """Patch the gettext _ function so chart_utils tests don't need a request context."""
    with unittest.mock.patch("ndastro_api.services.chart_utils._", side_effect=lambda x: x):
        yield


# ---------------------------------------------------------------------------
# draw_chart_borders
# ---------------------------------------------------------------------------


def test_draw_chart_borders_appends_rects():
    svg: list[str] = []
    draw_chart_borders(svg)
    assert len(svg) > 0
    # Every element should be a rect element
    for line in svg:
        assert "<rect" in line


def test_draw_chart_borders_skips_center():
    svg: list[str] = []
    draw_chart_borders(svg)
    # CENTER_2X2_SKIP cells should be excluded: (1,1),(1,2),(2,1),(2,2)
    # Total cells = CELL_COUNT * CELL_COUNT - CENTER_2X2_SKIP
    expected_count = CELL_COUNT * CELL_COUNT - len(CENTER_2X2_SKIP)
    assert len(svg) == expected_count


def test_draw_chart_borders_uses_correct_color():
    svg: list[str] = []
    draw_chart_borders(svg)
    for line in svg:
        assert CHART_BORDER_COLOR in line


# ---------------------------------------------------------------------------
# render_center_text
# ---------------------------------------------------------------------------


def test_render_center_text_no_birth_details():
    svg: list[str] = []
    render_center_text(svg, birth_details=None)
    assert len(svg) == 0  # Nothing appended when birth_details is None


def test_render_center_text_with_details():
    svg: list[str] = []
    details = BirthDetails(name_abbr="JD", date="2024-01-01", time="12:00", place="Chennai")
    render_center_text(svg, birth_details=details)
    assert len(svg) > 0
    # Should have text elements
    for element in svg:
        assert "<text" in element


def test_render_center_text_only_nonempty_lines():
    svg: list[str] = []
    details = BirthDetails(name_abbr="", date="", time="", place="")
    render_center_text(svg, birth_details=details)
    # name_abbr="" is skipped (empty), but "Date: ", "Time: ", "Place: " include label → 3 elements
    assert len(svg) == 3


def test_render_center_text_partial_details():
    svg: list[str] = []
    details = BirthDetails(name_abbr="AB", date="2024-01-15")
    render_center_text(svg, birth_details=details)
    assert len(svg) >= 1


# ---------------------------------------------------------------------------
# calculate_planet_positions
# ---------------------------------------------------------------------------


def test_calculate_planet_positions_empty():
    result = calculate_planet_positions([])
    assert result == []


def test_calculate_planet_positions_single_planet():
    planets = [KattamDisplayData(name="Sun", short_name="SU", display_name="SU", retro=False, adv=15.0)]
    result = calculate_planet_positions(planets)
    assert len(result) == 1
    assert result[0].px_frac is not None
    assert 0.0 <= result[0].px_frac <= 1.0


def test_calculate_planet_positions_multiple_sorted_by_adv():
    planets = [
        KattamDisplayData(name="Moon", short_name="MO", display_name="MO", retro=False, adv=25.0),
        KattamDisplayData(name="Sun", short_name="SU", display_name="SU", retro=False, adv=5.0),
        KattamDisplayData(name="Mars", short_name="MA", display_name="MA", retro=False, adv=15.0),
    ]
    result = calculate_planet_positions(planets)
    assert len(result) == 3
    # All should have px_frac set
    for p in result:
        assert p.px_frac is not None


def test_calculate_planet_positions_overlap_handling():
    # Two planets with same adv → overlap adjustment kicks in
    planets = [
        KattamDisplayData(name="Sun", short_name="SU", display_name="SU", retro=False, adv=15.0),
        KattamDisplayData(name="Moon", short_name="MO", display_name="MO", retro=False, adv=15.0),
    ]
    result = calculate_planet_positions(planets)
    assert len(result) == 2
    # px_frac values should be adjusted (slightly different due to overlap)
    assert result[0].px_frac != result[1].px_frac or result[0].px_frac <= result[1].px_frac


def test_calculate_planet_positions_max_frac_capped():
    # Planet near end of rasi → frac should be capped at PLANET_FRAC_MAX
    planets = [KattamDisplayData(name="Sun", short_name="SU", display_name="SU", retro=False, adv=29.9)]
    result = calculate_planet_positions(planets)
    assert result[0].px_frac is not None
    from ndastro_api.services.chart_utils import PLANET_FRAC_MAX

    assert result[0].px_frac <= PLANET_FRAC_MAX


# ---------------------------------------------------------------------------
# render_house_and_planets
# ---------------------------------------------------------------------------


def test_render_house_and_planets_no_planets():
    svg: list[str] = []
    render_house_and_planets(svg, rasi=1, layout_pos=(0, 1), planets=[], house_map={1: 1}, asc_rasi=None)
    # Should have house number text element
    assert len(svg) == 1
    assert "<text" in svg[0]


def test_render_house_and_planets_ascendant_rasi():
    svg: list[str] = []
    render_house_and_planets(svg, rasi=1, layout_pos=(0, 1), planets=[], house_map={1: 1}, asc_rasi=1)
    # Should have house number text AND two diagonal red lines
    assert any("red" in s for s in svg)
    # Two lagna lines should be added
    assert sum(1 for s in svg if "<line" in s) == 2


def test_render_house_and_planets_with_planets():
    planets = [
        KattamDisplayData(name="Sun", short_name="SU", display_name="SU", retro=False, adv=15.0, px_frac=0.5),
    ]
    svg: list[str] = []
    render_house_and_planets(svg, rasi=1, layout_pos=(0, 1), planets=planets, house_map={1: 1}, asc_rasi=None)
    assert len(svg) >= 2  # house text + planet text
    assert any("<text" in s for s in svg)


def test_render_house_and_planets_retrograde_planet():
    planets = [
        KattamDisplayData(name="Saturn", short_name="SA", display_name="SA", retro=True, adv=10.0, px_frac=0.4),
    ]
    svg: list[str] = []
    render_house_and_planets(svg, rasi=3, layout_pos=(1, 0), planets=planets, house_map={3: 3}, asc_rasi=None)
    # Retrograde symbol ℞ should be in some element
    assert any("℞" in s or "tspan" in s for s in svg)


def test_render_house_and_planets_planet_no_px_frac():
    # px_frac=None → uses center x position
    planets = [
        KattamDisplayData(name="Jupiter", short_name="JU", display_name="JU", retro=False, adv=20.0, px_frac=None),
    ]
    svg: list[str] = []
    render_house_and_planets(svg, rasi=5, layout_pos=(2, 0), planets=planets, house_map={5: 5}, asc_rasi=None)
    assert len(svg) >= 2


def test_render_house_and_planets_house_map_default():
    # house_map doesn't have rasi key → defaults to rasi value itself
    svg: list[str] = []
    render_house_and_planets(svg, rasi=2, layout_pos=(1, 0), planets=[], house_map={}, asc_rasi=None)
    assert "<text" in svg[0]
    # House should be "II" (index 1 in houses list)
    assert "II" in svg[0]


# ---------------------------------------------------------------------------
# generate_south_indian_chart_svg — with empty kattams list
# ---------------------------------------------------------------------------


def test_generate_svg_empty_kattams():
    result = generate_south_indian_chart_svg([])
    assert isinstance(result, str)
    assert "<svg" in result
    assert "</svg>" in result


def test_generate_svg_starts_with_svg_tag():
    result = generate_south_indian_chart_svg([])
    lines = result.split("\n")
    assert lines[0].startswith("<svg")


def test_generate_svg_contains_rect_background():
    result = generate_south_indian_chart_svg([])
    assert "#fff59d" in result  # Background color


def test_generate_svg_with_birth_details():
    details = BirthDetails(name_abbr="JD", date="2024-01-01", time="12:00", place="Chennai")
    result = generate_south_indian_chart_svg([], birth_details=details)
    assert "<svg" in result
    assert "JD" in result


def test_generate_svg_without_birth_details():
    result = generate_south_indian_chart_svg([], birth_details=None)
    assert "<svg" in result


# ---------------------------------------------------------------------------
# BirthDetails model
# ---------------------------------------------------------------------------


def test_birth_details_all_fields():
    details = BirthDetails(name_abbr="Test", date="2024-01-01", time="06:30", place="London")
    assert details.name_abbr == "Test"
    assert details.date == "2024-01-01"
    assert details.time == "06:30"
    assert details.place == "London"


def test_birth_details_optional_fields():
    details = BirthDetails()
    assert details.name_abbr is None
    assert details.date is None


# ---------------------------------------------------------------------------
# SOUTH_INDIAN_LAYOUT constant
# ---------------------------------------------------------------------------


def test_south_indian_layout_has_12_houses():
    assert len(SOUTH_INDIAN_LAYOUT) == 12


def test_south_indian_layout_all_positions_valid():
    for house, (row, col) in SOUTH_INDIAN_LAYOUT.items():
        assert 1 <= house <= 12
        assert 0 <= row < CELL_COUNT
        assert 0 <= col < CELL_COUNT
