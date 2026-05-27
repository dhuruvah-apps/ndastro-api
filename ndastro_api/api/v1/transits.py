"""Transits API endpoints — current transit analysis against natal chart."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

import pytz
from fastapi import APIRouter, Query
from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from pydantic import BaseModel

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.core.utils.chart_helpers import PLANET_FULL
from ndastro_api.services.position import (
    get_sidereal_ascendant_position,
    get_sidereal_planet_positions,
)
from ndastro_api.services.transit_effects import (
    TransitEffect,
    analyze_transit_effects,
)
from ndastro_api.services.transits import TransitSummary, evaluate_transits

router = APIRouter(prefix="/transits", tags=["Timing & Predictions"], dependencies=get_conditional_dependencies())

_DEFAULT_DT = datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_dt(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=pytz.utc)


class TransitPositionResponse(BaseModel):
    """A planet's current transit position."""

    planet: str
    longitude: float
    rasi: int
    house: int


class TransitAspectResponse(BaseModel):
    """An aspect formed by a transiting planet."""

    planet: str
    to_house: int
    offset: int


class TransitAspectToNatalResponse(BaseModel):
    """An aspect from a transiting planet to a natal planet."""

    planet: str
    to_planet: str
    to_house: int
    offset: int


class TransitInterpretationResponse(BaseModel):
    """Interpretation for a single transiting planet in a house."""

    transiting_planet: str
    natal_house: int
    natal_planet: str | None
    impact: str
    duration: str
    description: str
    themes: list[str]
    recommendations: list[str]


class TransitEffectResponse(BaseModel):
    """Transit effect summary for a single planet."""

    planet: str
    current_house: int
    is_retrograde: bool
    overall_impact: str
    interpretations: list[TransitInterpretationResponse]


class TransitSummaryResponse(BaseModel):
    """Full transit analysis results."""

    positions: list[TransitPositionResponse]
    aspects_to_houses: list[TransitAspectResponse]
    aspects_to_natal_planets: list[TransitAspectToNatalResponse]
    effects: list[TransitEffectResponse]


@router.get("", response_model=TransitSummaryResponse)
def get_transits(
    natal_lat: Annotated[float, Query(description="Natal chart latitude")] = 12.971667,
    natal_lon: Annotated[float, Query(description="Natal chart longitude")] = 77.593611,
    natal_dateandtime: Annotated[str, Query(description="Birth datetime in ISO format")] = _DEFAULT_DT,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    transit_dateandtime: Annotated[str | None, Query(description="Transit datetime (defaults to now)")] = None,
) -> TransitSummaryResponse:
    """Evaluate current transits against the natal chart positions.

    Provide natal birth details plus an optional transit datetime (defaults to now).
    Returns transit positions, house/planet aspects, and life-area interpretations.
    """
    natal_dt = _parse_dt(natal_dateandtime)
    transit_dt = _parse_dt(transit_dateandtime) if transit_dateandtime else datetime.now(timezone.utc)

    natal_ayanamsa = get_ayanamsa(natal_dt, ayanamsa)
    transit_ayanamsa = get_ayanamsa(transit_dt, ayanamsa)

    natal_planets = get_sidereal_planet_positions(natal_lat, natal_lon, natal_dt, natal_ayanamsa)
    natal_lagna = get_sidereal_ascendant_position(natal_dt, natal_lat, natal_lon, ayanamsa=natal_ayanamsa)

    transit_planets = get_sidereal_planet_positions(natal_lat, natal_lon, transit_dt, transit_ayanamsa)

    natal_longitudes = {p.code: p.longitude for p in natal_planets if p.code in PLANET_FULL}
    transit_longitudes = {p.code: p.longitude for p in transit_planets if p.code in PLANET_FULL}

    summary: TransitSummary = evaluate_transits(
        transit_longitudes=transit_longitudes,
        natal_longitudes=natal_longitudes,
        lagna_longitude=natal_lagna.longitude,
    )

    # Transit effects interpretation
    transiting_houses = {pos.planet: pos.house for pos in summary.positions.values()}
    retrograde_set = {p.code for p in transit_planets if p.is_retrograde and p.code in PLANET_FULL}
    effects: list[TransitEffect] = analyze_transit_effects(transiting_houses, retrograde_planets=list(retrograde_set))

    return TransitSummaryResponse(
        positions=[
            TransitPositionResponse(
                planet=pos.planet,
                longitude=pos.longitude,
                rasi=pos.rasi,
                house=pos.house,
            )
            for pos in summary.positions.values()
        ],
        aspects_to_houses=[TransitAspectResponse(planet=a.planet, to_house=a.to_house, offset=a.offset) for a in summary.aspects_to_houses],
        aspects_to_natal_planets=[
            TransitAspectToNatalResponse(planet=a.planet, to_planet=a.to_planet, to_house=a.to_house, offset=a.offset)
            for a in summary.aspects_to_planets
        ],
        effects=[
            TransitEffectResponse(
                planet=e.planet,
                current_house=e.current_house,
                is_retrograde=e.is_retrograde,
                overall_impact=e.overall_impact.value if hasattr(e.overall_impact, "value") else str(e.overall_impact),
                interpretations=[
                    TransitInterpretationResponse(
                        transiting_planet=i.transiting_planet,
                        natal_house=i.natal_house,
                        natal_planet=i.natal_planet,
                        impact=i.impact.value if hasattr(i.impact, "value") else str(i.impact),
                        duration=i.duration.value if hasattr(i.duration, "value") else str(i.duration),
                        description=i.description,
                        themes=i.themes,
                        recommendations=i.recommendations,
                    )
                    for i in e.interpretations
                ],
            )
            for e in effects
        ],
    )
