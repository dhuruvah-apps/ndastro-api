"""Yogas API endpoints — nitya yoga, planetary yogas, extended yogas."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

import pytz
from fastapi import APIRouter, Query
from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from ndastro_engine.planet_enum import Planets
from pydantic import BaseModel

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.core.utils.chart_helpers import (
    PLANET_FULL,
    build_house_lords,
    house_num,
    rasi_num,
)
from ndastro_api.services.position import (
    get_sidereal_ascendant_position,
    get_sidereal_planet_positions,
)
from ndastro_api.services.yoga_extended import evaluate_extended_yogas
from ndastro_api.services.yogas import (
    PlanetaryYogaContext,
    YogaRuleResult,
    calculate_nitya_yoga,
    evaluate_planetary_yogas,
)

router = APIRouter(prefix="/yogas", tags=["Chart Analysis"], dependencies=get_conditional_dependencies())

_DEFAULT_DT = datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_dt(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=pytz.utc)


class NityaYogaResponse(BaseModel):
    """Nitya yoga result derived from Sun + Moon longitudes."""

    name: str
    number: int
    longitude_sum: float
    arc_start: float
    arc_end: float


class YogaRuleResponse(BaseModel):
    """Result for a single planetary yoga rule."""

    name: str
    category: str
    is_present: bool
    planets_involved: list[str]
    details: str


class YogasResponse(BaseModel):
    """Full yoga analysis: nitya + planetary + extended."""

    nitya_yoga: NityaYogaResponse
    planetary_yogas: list[YogaRuleResponse]
    extended_yogas: list[YogaRuleResponse]


def _build_yoga_context(planets: list, lagna_rasi_number: int) -> PlanetaryYogaContext:
    planet_houses: dict[str, int] = {}
    planet_rasis: dict[str, str] = {}
    own_signs: dict[str, set[str]] = {}
    exaltation_signs: dict[str, str] = {}
    debilitation_signs: dict[str, str] = {}

    for p in planets:
        name = PLANET_FULL.get(p.code)
        if not name:
            continue
        planet_houses[name] = house_num(p)
        planet_rasis[name] = p.rasi_occupied or ""
        own_signs[name] = set(p.own_signs) if p.own_signs else set()
        exaltation_signs[name] = (p.exaltation.sign or "") if p.exaltation else ""
        debilitation_signs[name] = (p.debilitation.sign or "") if p.debilitation else ""

    return PlanetaryYogaContext(
        planet_houses=planet_houses,
        planet_rasis=planet_rasis,
        own_signs=own_signs,
        exaltation_signs=exaltation_signs,
        debilitation_signs=debilitation_signs,
        house_lords=build_house_lords(lagna_rasi_number),
        lagna_house=1,
    )


def _yoga_to_response(y: YogaRuleResult) -> YogaRuleResponse:
    return YogaRuleResponse(
        name=y.name,
        category=y.category,
        is_present=y.is_present,
        planets_involved=y.planets_involved,
        details=y.details,
    )


@router.get("", response_model=YogasResponse)
def get_yogas(
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = _DEFAULT_DT,
    include_absent: Annotated[bool, Query(description="Include yogas that are not present in the chart")] = False,  # noqa: FBT002
) -> YogasResponse:
    """Evaluate all yogas — nitya yoga (27), planetary yogas, and extended yogas — for the given chart."""
    dt = _parse_dt(dateandtime)
    ayanamsa_val = get_ayanamsa(dt, ayanamsa)

    planets = get_sidereal_planet_positions(lat, lon, dt, ayanamsa_val)
    lagna = get_sidereal_ascendant_position(dt, lat, lon, ayanamsa=ayanamsa_val)

    sun = next(p for p in planets if p.code == Planets.SUN.code)
    moon = next(p for p in planets if p.code == Planets.MOON.code)
    nitya = calculate_nitya_yoga(sun.longitude, moon.longitude)

    lagna_rasi = rasi_num(lagna)
    context = _build_yoga_context(planets, lagna_rasi)

    planetary = evaluate_planetary_yogas(context, include_missing=include_absent)
    extended = evaluate_extended_yogas(context)

    return YogasResponse(
        nitya_yoga=NityaYogaResponse(
            name=nitya.name,
            number=nitya.number,
            longitude_sum=nitya.longitude_sum,
            arc_start=nitya.arc_start,
            arc_end=nitya.arc_end,
        ),
        planetary_yogas=[_yoga_to_response(y) for y in planetary],
        extended_yogas=[_yoga_to_response(y) for y in extended],
    )
