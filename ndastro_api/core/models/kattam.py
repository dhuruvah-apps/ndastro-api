"""Module to hold planet postion related data classes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ndastro_engine.enums import Houses, Planets, Rasis

    from ndastro_api.core.models.astro_system import Planet


@dataclass
class Kattam:
    """Holds data for each square (kattam/கட்டம்) on the chart."""

    order: int
    is_ascendant: bool
    asc_longitude: float | None
    owner: Planets
    rasi: Rasis
    house: Houses
    planets: list[Planet] | None
