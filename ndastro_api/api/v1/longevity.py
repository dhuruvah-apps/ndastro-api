"""Longevity API endpoints — traditional Jyotish longevity assessment."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

import pytz
from fastapi import APIRouter, Query
from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from ndastro_engine.core import get_sunrise_sunset
from pydantic import BaseModel

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.core.utils.chart_helpers import PLANET_FULL
from ndastro_api.services.longevity import (
    ChartContext,
    LongevityAnalysis,
    PlanetPosition,
    calculate_longevity_analysis,
)
from ndastro_api.services.position import (
    get_sidereal_ascendant_position,
    get_sidereal_planet_positions,
)

router = APIRouter(prefix="/longevity", tags=["Timing & Predictions"], dependencies=get_conditional_dependencies())

_DEFAULT_DT = datetime.now(timezone.utc).isoformat(timespec="seconds")

# Planet codes for Atmakaraka (excludes nodes)
_AK_CODES = ("SU", "MO", "MA", "ME", "JU", "VE", "SA")


def _parse_dt(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=pytz.utc)


class MarakaResponse(BaseModel):
    """Maraka (death-inflicting) planet identification."""

    marakas: list[str]
    primary_marakas: list[str]
    secondary_marakas: list[str]
    description: str


class ThreePairsResponse(BaseModel):
    """Three pairs longevity method result."""

    short_life: list[str]
    medium_life: list[str]
    long_life: list[str]
    result: str
    verdict: str


class EighthLordResponse(BaseModel):
    """Eighth lord method result."""

    eighth_lord: str
    eighth_lord_house: int
    verdict: str
    description: str


class LongevityResponse(BaseModel):
    """Full longevity analysis result."""

    lagna_rasi: int
    atma_karaka: str
    marakas: MarakaResponse | None
    three_pairs_result: ThreePairsResponse | None
    eighth_lord_result: EighthLordResponse | None
    longevity_category: str
    estimated_range: list[int]
    final_assessment: str
    warnings: list[str]
    ethical_note: str


def _build_planet_position(planet: object) -> PlanetPosition:
    """Build a PlanetPosition for the longevity service from a Planet model."""
    rasi_num = int(getattr(planet, "rasi_occupied", "R01")[1:]) if getattr(planet, "rasi_occupied", None) else 1
    house_num = int(getattr(planet, "posited_at", "H01")[1:]) if getattr(planet, "posited_at", None) else 1
    exaltation = getattr(planet, "exaltation", None)
    debilitation = getattr(planet, "debilitation", None)
    rasi_occupied = getattr(planet, "rasi_occupied", "")
    exaltation_sign = exaltation.sign if exaltation and exaltation.sign else ""
    debilitation_sign = debilitation.sign if debilitation and debilitation.sign else ""
    code = getattr(planet, "code", "")
    name = PLANET_FULL.get(code) or code.lower()
    return PlanetPosition(
        name=name,
        rasi=rasi_num,
        house=house_num,
        degrees_in_rasi=getattr(planet, "advanced_by", 0.0) or 0.0,
        is_exalted=(exaltation_sign != "" and exaltation_sign == rasi_occupied),
        is_debilitated=(debilitation_sign != "" and debilitation_sign == rasi_occupied),
        is_retrograde=bool(getattr(planet, "is_retrograde", False)),
    )


@router.get("", response_model=LongevityResponse)
def get_longevity(
    lat: Annotated[float, Query(description="Geographic latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Geographic longitude")] = 77.593611,
    dateandtime: Annotated[str, Query(description="Birth datetime in ISO format")] = _DEFAULT_DT,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
) -> LongevityResponse:
    """Calculate longevity assessment using traditional Jyotish techniques.

    Uses multiple classical methods including the Three Pairs method,
    Eighth Lord analysis, and Maraka identification to assess potential lifespan.

    **Note:** This is a traditional astrological assessment provided for educational
    and cultural purposes only.
    """
    dt = _parse_dt(dateandtime)
    ayan = get_ayanamsa(dt, ayanamsa)

    planets = get_sidereal_planet_positions(lat, lon, dt, ayan)
    lagna = get_sidereal_ascendant_position(dt, lat, lon, ayanamsa=ayan)

    lagna_rasi_num = int(lagna.rasi_occupied[1:]) if lagna.rasi_occupied else 1
    house_7_rasi = ((lagna_rasi_num - 1 + 6) % 12) + 1

    # Hora Lagna: advances 1 rasi per 2 hours from sunrise
    try:
        sr, _ = get_sunrise_sunset(lat, lon, dt)
        if sr:
            hours_since = (dt - sr).total_seconds() / 3600.0
            horalagna_rasi = ((lagna_rasi_num - 1 + int(hours_since / 2)) % 12) + 1
        else:
            horalagna_rasi = lagna_rasi_num
    except OSError:
        horalagna_rasi = lagna_rasi_num

    # Atma Karaka: planet (excluding nodes) with highest degree in its sign
    ak_candidates = [p for p in planets if p.code in _AK_CODES]
    atma_karaka_planet = max(ak_candidates, key=lambda p: p.advanced_by or 0.0) if ak_candidates else None
    atma_karaka = PLANET_FULL.get(atma_karaka_planet.code, "sun") if atma_karaka_planet else "sun"

    planet_positions = {PLANET_FULL[p.code]: _build_planet_position(p) for p in planets if p.code in PLANET_FULL}

    context = ChartContext(
        lagna_rasi=lagna_rasi_num,
        planets=planet_positions,
        house_7_rasi=house_7_rasi,
        horalagna_rasi=horalagna_rasi,
        atma_karaka=atma_karaka,
    )

    analysis: LongevityAnalysis = calculate_longevity_analysis(context)

    # Build response from analysis result
    marakas_resp = None
    if analysis.marakas:
        m = analysis.marakas
        marakas_resp = MarakaResponse(
            marakas=getattr(m, "marakas", []),
            primary_marakas=getattr(m, "primary_marakas", []),
            secondary_marakas=getattr(m, "secondary_marakas", []),
            description=getattr(m, "description", ""),
        )

    three_pairs_resp = None
    if analysis.three_pairs_result:
        r = analysis.three_pairs_result
        three_pairs_resp = ThreePairsResponse(
            short_life=getattr(r, "short_life", []),
            medium_life=getattr(r, "medium_life", []),
            long_life=getattr(r, "long_life", []),
            result=getattr(r, "result", ""),
            verdict=getattr(r, "verdict", ""),
        )

    eighth_resp = None
    if analysis.eighth_lord_result:
        e = analysis.eighth_lord_result
        eighth_resp = EighthLordResponse(
            eighth_lord=getattr(e, "eighth_lord", ""),
            eighth_lord_house=getattr(e, "eighth_lord_house", 0),
            verdict=getattr(e, "verdict", ""),
            description=getattr(e, "description", ""),
        )

    estimated_range = list(analysis.estimated_range) if analysis.estimated_range else []

    return LongevityResponse(
        lagna_rasi=lagna_rasi_num,
        atma_karaka=atma_karaka,
        marakas=marakas_resp,
        three_pairs_result=three_pairs_resp,
        eighth_lord_result=eighth_resp,
        longevity_category=getattr(analysis, "longevity_category", "unknown"),
        estimated_range=estimated_range,
        final_assessment=getattr(analysis, "final_assessment", ""),
        warnings=list(analysis.warnings) if analysis.warnings else [],
        ethical_note=getattr(analysis, "ethical_note", ""),
    )
