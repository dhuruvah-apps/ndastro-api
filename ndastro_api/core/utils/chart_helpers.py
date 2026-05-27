"""Shared chart-building helpers used across Jyotish API routers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ndastro_api.core.models.astro_system import Planet

# Planet short-code → lowercase full name (used in yoga / ashtakavarga contexts)
PLANET_FULL: dict[str, str] = {
    "SU": "sun",
    "MO": "moon",
    "MA": "mars",
    "ME": "mercury",
    "JU": "jupiter",
    "VE": "venus",
    "SA": "saturn",
    "RA": "rahu",
    "KE": "kethu",
}

# Rasi number (1-12) → lowercase rasi name
RASI_NAMES: dict[int, str] = {
    1: "aries",
    2: "taurus",
    3: "gemini",
    4: "cancer",
    5: "leo",
    6: "virgo",
    7: "libra",
    8: "scorpio",
    9: "sagittarius",
    10: "capricorn",
    11: "aquarius",
    12: "pisces",
}

# Rasi number (1-12) → primary lord (lowercase full name)
RASI_LORDS: dict[int, str] = {
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
}

# Average daily speeds in degrees (used for chesta bala approximation)
AVG_SPEEDS: dict[str, float] = {
    "SU": 1.0,
    "MO": 13.2,
    "MA": 0.524,
    "ME": 1.384,
    "JU": 0.083,
    "VE": 1.2,
    "SA": 0.033,
    "RA": -0.053,
    "KE": -0.053,
}


def house_num(planet: Planet) -> int:
    """Extract house number (1-12) from Planet.posited_at ('H01'...)."""
    return int(planet.posited_at[1:]) if planet.posited_at else 1


def rasi_num(planet: Planet) -> int:
    """Extract rasi number (1-12) from Planet.rasi_occupied ('R01'...)."""
    return int(planet.rasi_occupied[1:]) if planet.rasi_occupied else 1


def nakshatra_num(planet: Planet) -> int:
    """Extract nakshatra number (1-27) from Planet.nakshatra ('N01'...)."""
    return int(planet.nakshatra[1:]) if planet.nakshatra else 1


def build_house_lords(lagna_rasi_number: int) -> dict[int, str]:
    """Build house-number → lord-name mapping from lagna rasi."""
    return {h: RASI_LORDS[((lagna_rasi_number - 1 + h - 1) % 12) + 1] for h in range(1, 13)}


def classify_planets(
    planets: list[Planet],  # type: ignore[type-arg]
) -> tuple[list[str], list[str], list[str]]:
    """Return (exalted, own_rasi, debilitated) planet name lists (lowercase full names)."""
    exalted, own_rasi, debilitated = [], [], []
    for p in planets:
        name = PLANET_FULL.get(p.code)
        if not name:
            continue
        rasi = p.rasi_occupied or ""
        if p.exaltation and p.exaltation.sign == rasi:
            exalted.append(name)
        if rasi and rasi in (p.own_signs or []):
            own_rasi.append(name)
        if p.debilitation and p.debilitation.sign == rasi:
            debilitated.append(name)
    return exalted, own_rasi, debilitated
