"""Transit analysis utilities.

Provides house placement, aspect calculation, and simple interpretations
for planetary transits against a natal reference.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ndastro_engine.utils import normalize_degree

# Constants
FULL_CIRCLE_DEGREES = 360.0
RASI_COUNT = 12
DEGREES_PER_RASI = FULL_CIRCLE_DEGREES / RASI_COUNT
KENDRA_HOUSES = {1, 4, 7, 10}
TRIKONA_HOUSES = {1, 5, 9}
DUSTHANA_HOUSES = {6, 8, 12}
UPACHAYA_HOUSES = {3, 6, 10, 11}
MARAKA_HOUSES = {2, 7}

DEFAULT_ASPECTS = {
    "sun": {6},
    "moon": {6},
    "mars": {3, 6, 7},
    "mercury": {6},
    "jupiter": {4, 6, 8},
    "venus": {6},
    "saturn": {2, 6, 9},
    "rahu": {4, 6, 8},
    "kethu": {4, 6, 8},
}


class TransitHouseClass(str, Enum):
    """House classifications for transit interpretation."""

    KENDRA = "kendra"
    TRIKONA = "trikona"
    DUSTHANA = "dusthana"
    UPACHAYA = "upachaya"
    MARAKA = "maraka"
    NORMAL = "normal"


@dataclass
class TransitPlanetPosition:
    """A transit planet position derived from longitude and lagna."""

    planet: str
    longitude: float
    rasi: int
    house: int


@dataclass
class TransitAspect:
    """Represents a transit aspect to a house."""

    planet: str
    to_house: int
    offset: int


@dataclass
class TransitAspectToPlanet:
    """Represents a transit aspect to a natal planet."""

    planet: str
    to_planet: str
    to_house: int
    offset: int


@dataclass
class TransitSummary:
    """Aggregated transit results."""

    positions: dict[str, TransitPlanetPosition] = field(default_factory=dict)
    house_transits: dict[int, list[str]] = field(default_factory=dict)
    aspects_to_houses: list[TransitAspect] = field(default_factory=list)
    aspects_to_planets: list[TransitAspectToPlanet] = field(default_factory=list)


def get_rasi_index(longitude: float) -> int:
    """Return rasi index (1-12) from longitude."""
    normalized = normalize_degree(longitude)
    return int(normalized / DEGREES_PER_RASI) + 1


def get_house_index(longitude: float, lagna_longitude: float) -> int:
    """Return house index (1-12) from longitude and lagna longitude."""
    relative = normalize_degree(longitude - lagna_longitude)
    return int(relative / DEGREES_PER_RASI) + 1


def build_transit_positions(
    transit_longitudes: dict[str, float],
    lagna_longitude: float,
) -> dict[str, TransitPlanetPosition]:
    """Build transit positions from longitudes."""
    positions: dict[str, TransitPlanetPosition] = {}

    for planet, longitude in transit_longitudes.items():
        positions[planet] = TransitPlanetPosition(
            planet=planet,
            longitude=normalize_degree(longitude),
            rasi=get_rasi_index(longitude),
            house=get_house_index(longitude, lagna_longitude),
        )

    return positions


def build_house_transits(
    positions: dict[str, TransitPlanetPosition],
) -> dict[int, list[str]]:
    """Create a mapping of houses to transiting planets."""
    house_map = {house: [] for house in range(1, RASI_COUNT + 1)}

    for planet, position in positions.items():
        house_map[position.house].append(planet)

    for planets in house_map.values():
        planets.sort()

    return house_map


def _get_aspect_offsets(planet: str, aspect_table: dict[str, set[int]] | None) -> set[int]:
    table = aspect_table or DEFAULT_ASPECTS
    return table.get(planet, {6})


def calculate_transit_aspects(
    positions: dict[str, TransitPlanetPosition],
    *,
    aspect_table: dict[str, set[int]] | None = None,
) -> list[TransitAspect]:
    """Calculate aspects from transiting planets to houses."""
    aspects: list[TransitAspect] = []

    for planet, position in positions.items():
        offsets = _get_aspect_offsets(planet, aspect_table)
        for offset in offsets:
            to_house = ((position.house - 1 + offset) % RASI_COUNT) + 1
            aspects.append(TransitAspect(planet=planet, to_house=to_house, offset=offset + 1))

    return aspects


def calculate_aspects_to_natal_planets(
    positions: dict[str, TransitPlanetPosition],
    natal_longitudes: dict[str, float],
    lagna_longitude: float,
    *,
    aspect_table: dict[str, set[int]] | None = None,
) -> list[TransitAspectToPlanet]:
    """Calculate aspects from transits to natal planets."""
    natal_houses = {planet: get_house_index(longitude, lagna_longitude) for planet, longitude in natal_longitudes.items()}

    aspects: list[TransitAspectToPlanet] = []

    for planet, position in positions.items():
        offsets = _get_aspect_offsets(planet, aspect_table)
        for offset in offsets:
            to_house = ((position.house - 1 + offset) % RASI_COUNT) + 1
            for natal_planet, natal_house in natal_houses.items():
                if natal_house == to_house:
                    aspects.append(
                        TransitAspectToPlanet(
                            planet=planet,
                            to_planet=natal_planet,
                            to_house=to_house,
                            offset=offset + 1,
                        )
                    )

    return aspects


def classify_transit_house(house: int) -> TransitHouseClass:
    """Classify a house for transit interpretation."""
    if house in KENDRA_HOUSES:
        return TransitHouseClass.KENDRA
    if house in TRIKONA_HOUSES:
        return TransitHouseClass.TRIKONA
    if house in DUSTHANA_HOUSES:
        return TransitHouseClass.DUSTHANA
    if house in UPACHAYA_HOUSES:
        return TransitHouseClass.UPACHAYA
    if house in MARAKA_HOUSES:
        return TransitHouseClass.MARAKA
    return TransitHouseClass.NORMAL


def get_house_transit_interpretation(house: int, planets: list[str]) -> str:
    """Return a short interpretation for a transit house hit."""
    house_class = classify_transit_house(house)
    planet_list = ", ".join(planets) if planets else "No planets"

    interpretations = {
        TransitHouseClass.KENDRA: "Kendra focus: visibility, action, major events.",
        TransitHouseClass.TRIKONA: "Trikona support: growth, luck, wisdom.",
        TransitHouseClass.DUSTHANA: "Dusthana pressure: challenges, transformation.",
        TransitHouseClass.UPACHAYA: "Upachaya results: gains through effort.",
        TransitHouseClass.MARAKA: "Maraka sensitivity: relationships or vitality tests.",
        TransitHouseClass.NORMAL: "Neutral transit: steady progression.",
    }

    return f"House {house} ({planet_list}): {interpretations[house_class]}"


def evaluate_transits(
    transit_longitudes: dict[str, float],
    natal_longitudes: dict[str, float],
    lagna_longitude: float,
    *,
    aspect_table: dict[str, set[int]] | None = None,
) -> TransitSummary:
    """Evaluate transit positions and aspects against a natal chart."""
    positions = build_transit_positions(transit_longitudes, lagna_longitude)
    house_transits = build_house_transits(positions)
    aspects_to_houses = calculate_transit_aspects(positions, aspect_table=aspect_table)
    aspects_to_planets = calculate_aspects_to_natal_planets(
        positions,
        natal_longitudes,
        lagna_longitude,
        aspect_table=aspect_table,
    )

    return TransitSummary(
        positions=positions,
        house_transits=house_transits,
        aspects_to_houses=aspects_to_houses,
        aspects_to_planets=aspects_to_planets,
    )
