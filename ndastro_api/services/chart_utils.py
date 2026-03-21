"""Chart generation utilities for astrology charts.

This module provides helper functions for generating SVG charts, particularly
South Indian astrology charts with proper layout and multilingual support.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from ndastro_engine.enums import Houses, Planets, Rasis
from pydantic import BaseModel

from ndastro_api.core.babel_i18n import _

if TYPE_CHECKING:
    from ndastro_api.core.models.kattam import Kattam

# Chart generation constants
CHART_BORDER_COLOR = "#FF0000"
CHART_SIZE = 100
CELL_COUNT = 4
CELL_SIZE = CHART_SIZE / CELL_COUNT
BORDER_WIDTH = 0.5
CENTER_2X2_SKIP = [(1, 1), (1, 2), (2, 1), (2, 2)]
MAX_PLANETS_PER_SLOT = 4
CENTER_TEXT_COLOR = "#000000"

# Layout mapping for South Indian chart (row, col)
SOUTH_INDIAN_LAYOUT = {
    1: (1, 0),
    2: (2, 0),
    3: (3, 0),
    4: (3, 1),
    5: (3, 2),
    6: (3, 3),
    7: (2, 3),
    8: (1, 3),
    9: (0, 3),
    10: (0, 2),
    11: (0, 1),
    12: (0, 0),
}

# Planet placement constants
PLANET_FRAC_MIN = 0.2
PLANET_FRAC_MAX = 0.8
PLANET_TOP_OFFSET = 0.3
PLANET_SLOT_HEIGHT_FACTOR = 0.6
PLANET_OVERLAP_OFFSET = 0.05
PLANET_TEXT_COLOR = "#000000"

# Lagna diagonal line offsets
LAGNA_LINE_OFFSET_1 = 0.2
LAGNA_LINE_OFFSET_2 = 0.25

# Retrograde and text constants
RETRO_SUPERSCRIPT_DY = -1.5
RETRO_SUPERSCRIPT_SCALE = 0.6
CENTER_TEXT_FONT = 3.5
CENTER_TEXT_LINE_SPACING = 2
HOUSE_NUM_MAX_FONT = 4
HOUSE_NUM_MIN_FONT = 1
DEGREES_PER_RASI = 30.0

houses = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


class BirthDetails(BaseModel):
    """Model for birth details to display in chart center."""

    name_abbr: str | None = None
    date: str | None = None
    time: str | None = None
    place: str | None = None


@dataclass
class KattamDisplayData:
    """Data class to hold processed kattam data for chart rendering."""

    name: str
    short_name: str
    display_name: str
    retro: bool | None
    adv: float | None
    px_frac: float | None = None


def process_rasi_data(kattams_data: list[Kattam]) -> tuple[dict[Rasis, list[KattamDisplayData]], Rasis | None, dict[Rasis, Houses]]:
    """Process kattams data to extract rasi and planet information."""
    rasi_data: dict[Rasis, list[KattamDisplayData]] = {}
    asc_rasi: Rasis | None = None
    house_map: dict[Rasis, Houses] = {}

    for item in kattams_data:
        rasi = item.rasi
        house_map[rasi] = item.house
        if item.is_ascendant:
            asc_rasi = rasi

        planets: list[KattamDisplayData] = []
        if item.planets:
            planets = [
                KattamDisplayData(name=p.name, short_name=p.code, display_name=p.code, retro=p.is_retrograde, adv=p.advanced_by) for p in item.planets
            ]
        rasi_data[rasi] = planets

    return rasi_data, asc_rasi, house_map


def calculate_planet_positions(planets: list[KattamDisplayData]) -> list[KattamDisplayData]:
    """Calculate positions for planets within a rasi cell."""
    if not planets:
        return planets

    planets = sorted(planets, key=lambda p: cast("float", p.adv))
    positions: list[float] = []

    for p in planets:
        frac = PLANET_FRAC_MIN + PLANET_SLOT_HEIGHT_FACTOR * (cast("float", p.adv) / DEGREES_PER_RASI)
        overlaps = [pos for pos in positions if abs(pos - frac) < PLANET_OVERLAP_OFFSET]
        if overlaps:
            frac += len(overlaps) * PLANET_OVERLAP_OFFSET
        frac = min(frac, PLANET_FRAC_MAX)
        positions.append(frac)
        p.px_frac = frac

    return planets


def draw_chart_borders(svg: list[str]) -> None:
    """Draw the outer borders of the chart, skipping center 2x2."""
    for i in range(CELL_COUNT):
        for j in range(CELL_COUNT):
            if (i, j) in CENTER_2X2_SKIP:
                continue
            x, y = j * CELL_SIZE, i * CELL_SIZE
            svg.append(
                f'<rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" stroke="{CHART_BORDER_COLOR}" fill="none" stroke-width="{BORDER_WIDTH}"/>'
            )


def render_center_text(svg: list[str], birth_details: BirthDetails | None) -> None:
    """Render birth details in the center of the chart."""
    if not birth_details:
        return

    cx, cy = CHART_SIZE / 2, CHART_SIZE / 2
    lines = [
        birth_details.name_abbr or "",
        f"{_('Date')}: {birth_details.date or ''}",
        f"{_('Time')}: {birth_details.time or ''}",
        f"{_('Place')}: {birth_details.place or ''}",
    ]
    for i, text in enumerate(lines):
        if text.strip():  # Only add non-empty lines
            y_pos = cy + (i - 1) * CENTER_TEXT_FONT * CENTER_TEXT_LINE_SPACING
            svg.append(f'<text x="{cx}" y="{y_pos}" text-anchor="middle" font-size="{CENTER_TEXT_FONT}" fill="{CENTER_TEXT_COLOR}">{text}</text>')


def render_house_and_planets(  # noqa: PLR0913
    svg: list[str], rasi: int, layout_pos: tuple[int, int], planets: list[KattamDisplayData], house_map: dict, asc_rasi: int | None
) -> None:
    """Render a single house and its planets."""
    col, row = layout_pos
    x0, y0 = col * CELL_SIZE, row * CELL_SIZE
    slot_count = len(planets)
    rasi_font_size = (
        HOUSE_NUM_MAX_FONT
        if slot_count <= MAX_PLANETS_PER_SLOT
        else max(HOUSE_NUM_MAX_FONT * (MAX_PLANETS_PER_SLOT / slot_count), HOUSE_NUM_MIN_FONT)
    )

    # House number (Roman)
    hx, hy = x0 + CELL_SIZE - rasi_font_size * 0.5, y0 + rasi_font_size * 0.8
    house_num = house_map.get(rasi, rasi)
    color = "red" if rasi == asc_rasi else "black"
    svg.append(f'<text x="{hx}" y="{hy}" text-anchor="end" font-size="{rasi_font_size}" fill="{color}">{houses[house_num - 1]}</text>')

    # Lagna diagonal double lines
    if rasi == asc_rasi:
        offset1, offset2 = LAGNA_LINE_OFFSET_1 * CELL_SIZE, LAGNA_LINE_OFFSET_2 * CELL_SIZE
        svg.append(f'<line x1="{x0}" y1="{y0 + offset1}" x2="{x0 + offset1}" y2="{y0}" stroke="red" stroke-width="{BORDER_WIDTH}"/>')
        svg.append(f'<line x1="{x0}" y1="{y0 + offset2}" x2="{x0 + offset2}" y2="{y0}" stroke="red" stroke-width="{BORDER_WIDTH}"/>')

    if not planets:
        return

    # Render planets
    start_py = y0 + PLANET_TOP_OFFSET * CELL_SIZE
    slot_height = (CELL_SIZE * PLANET_SLOT_HEIGHT_FACTOR) / max(len(planets), 1)

    for i, p in enumerate(planets):
        px = x0 + CELL_SIZE * p.px_frac if p.px_frac is not None else x0 + CELL_SIZE * 0.5
        py = start_py + i * slot_height
        fill = PLANET_TEXT_COLOR
        show_retro = p.retro and p.short_name not in [Planets.RAHU.code, Planets.KETHU.code]

        if show_retro:
            svg.append(
                f'<text x="{px}" y="{py}" text-anchor="middle" font-size="{rasi_font_size}" fill="{fill}">'
                f'{_(p.short_name)}<tspan dy="{RETRO_SUPERSCRIPT_DY}" font-size="{rasi_font_size * RETRO_SUPERSCRIPT_SCALE}">℞</tspan></text>'
            )
        else:
            svg.append(f'<text x="{px}" y="{py}" text-anchor="middle" font-size="{rasi_font_size}" fill="{fill}">{_(p.display_name)}</text>')


def generate_south_indian_chart_svg(kattams_data: list[Kattam], birth_details: BirthDetails | None = None) -> str:
    """Generate SVG for South Indian astrology chart with enhanced layout and multilingual support.

    Args:
        kattams_data: List of kattam responses containing house and planet data.
        birth_details: Optional birth details to display in center.

    Returns:
        str: SVG markup for the South Indian chart.

    """
    layout = SOUTH_INDIAN_LAYOUT

    # Process kattams data using helper function
    rasi_data, asc_rasi, house_map = process_rasi_data(kattams_data)

    # SVG setup
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 {CHART_SIZE} {CHART_SIZE}">',
        "<style>text{font-family:Arial;dominant-baseline:middle;}</style>",
        f'<rect x="0" y="0" width="{CHART_SIZE}" height="{CHART_SIZE}" fill="#fff59d"/>',
    ]

    # Draw chart components using helper functions
    draw_chart_borders(svg)

    # Draw houses and planets
    for rasi, layout_pos in layout.items():
        planets = rasi_data.get(Rasis(rasi), [])
        planets_with_positions = calculate_planet_positions(planets)
        render_house_and_planets(svg, rasi, layout_pos, planets_with_positions, house_map, asc_rasi)

    # Render center birth details
    render_center_text(svg, birth_details)

    svg.append("</svg>")
    return "\n".join(svg)
