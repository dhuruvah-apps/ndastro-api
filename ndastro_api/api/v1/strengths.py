"""Strengths API endpoints — Shadbala, Vimshopaka Bala, Aspect Strength."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

import pytz
from fastapi import APIRouter, Query
from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from ndastro_engine.core import get_sunrise_sunset
from ndastro_engine.planet_enum import Planets
from pydantic import BaseModel

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.core.utils.chart_helpers import (
    AVG_SPEEDS,
    PLANET_FULL,
    house_num,
    rasi_num,
)
from ndastro_api.services.aspect_strength import (
    calculate_aspects_with_strength,
)
from ndastro_api.services.position import get_sidereal_planet_positions
from ndastro_api.services.shadbala import (
    ShadbalaPlanetContext,
    calculate_shadbala,
)
from ndastro_api.services.vimshopaka_bala import (
    compute_vimshopaka_bala,
    get_strength_label,
)

router = APIRouter(prefix="/strengths", tags=["Planetary Strength"], dependencies=get_conditional_dependencies())

_DEFAULT_DT = datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_dt(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=pytz.utc)


# ── Shadbala ─────────────────────────────────────────────────────────────────


class ShadbalaResponse(BaseModel):
    """Shadbala (six strengths) for a single planet."""

    planet_code: str
    planet_name: str
    sthana_bala: float
    dig_bala: float
    kala_bala: float
    paksha_bala: float
    chesta_bala: float
    drishti_bala: float
    total_shadbala: float
    shadbala_percentage: float


@router.get("/shadbala", response_model=list[ShadbalaResponse])
def get_shadbala(
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = _DEFAULT_DT,
) -> list[ShadbalaResponse]:
    """Calculate Shadbala (six-fold strength) for all planets."""
    dt = _parse_dt(dateandtime)
    ayanamsa_val = get_ayanamsa(dt, ayanamsa)

    planets = get_sidereal_planet_positions(lat, lon, dt, ayanamsa_val)

    # Determine day/night from sunrise
    sr, ss = get_sunrise_sunset(lat, lon, dt)
    is_night = bool(sr and ss and not (sr <= dt <= ss))

    # Moon phase for paksha bala
    sun = next(p for p in planets if p.code == Planets.SUN.code)
    moon = next(p for p in planets if p.code == Planets.MOON.code)
    from ndastro_engine.utils import normalize_degree  # noqa: PLC0415

    moon_phase = normalize_degree(moon.longitude - sun.longitude)

    results = []
    for p in planets:
        if p.code not in PLANET_FULL:
            continue

        ctx = ShadbalaPlanetContext(
            planet_code=p.code,
            rasi_number=rasi_num(p),
            house_number=house_num(p),
            is_retrograde=bool(p.is_retrograde),
            is_night=is_night,
            moon_phase=moon_phase,
            avg_speed=AVG_SPEEDS.get(p.code, 1.0),
            aspecting_planets=None,
        )
        scores = calculate_shadbala(ctx)
        results.append(
            ShadbalaResponse(
                planet_code=p.code,
                planet_name=PLANET_FULL[p.code],
                sthana_bala=round(scores.get("sthana_bala", 0), 2),
                dig_bala=round(scores.get("dig_bala", 0), 2),
                kala_bala=round(scores.get("kala_bala", 0), 2),
                paksha_bala=round(scores.get("paksha_bala", 0), 2),
                chesta_bala=round(scores.get("chesta_bala", 0), 2),
                drishti_bala=round(scores.get("drishti_bala", 0), 2),
                total_shadbala=round(scores.get("total_shadbala", 0), 2),
                shadbala_percentage=round(scores.get("shadbala_percentage", 0), 2),
            )
        )

    return results


# ── Vimshopaka Bala ──────────────────────────────────────────────────────────


class VimshopakaPlanetScore(BaseModel):
    """Vimshopaka score for a single planet."""

    planet: str
    total_score: float
    vimshopaka_ratio: float
    strength_label: str


class VimshopakaBalaResponse(BaseModel):
    """Vimshopaka Bala report across a scheme."""

    scheme: str
    max_score: float
    scores: list[VimshopakaPlanetScore]


@router.get("/vimshopaka", response_model=VimshopakaBalaResponse)
def get_vimshopaka(
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = _DEFAULT_DT,
    scheme: Annotated[str, Query(description="Varga scheme: shadvarga, saptavarga, dasavarga, shodasavarga")] = "shodasavarga",
) -> VimshopakaBalaResponse:
    """Calculate Vimshopaka Bala (divisional chart composite dignity) for all planets."""
    dt = _parse_dt(dateandtime)
    ayanamsa_val = get_ayanamsa(dt, ayanamsa)
    planets = get_sidereal_planet_positions(lat, lon, dt, ayanamsa_val)

    longitudes = {p.code: p.longitude for p in planets if p.code in PLANET_FULL}
    report = compute_vimshopaka_bala(longitudes, scheme=scheme)

    return VimshopakaBalaResponse(
        scheme=report.scheme,
        max_score=report.max_score,
        scores=[
            VimshopakaPlanetScore(
                planet=score.planet,
                total_score=round(score.total_score, 3),
                vimshopaka_ratio=round(score.vimshopaka_ratio, 3),
                strength_label=get_strength_label(score),
            )
            for score in report.scores.values()
        ],
    )


# ── Aspect Strength ───────────────────────────────────────────────────────────


class AspectDetailResponse(BaseModel):
    """Details of a single planetary aspect."""

    aspecting_planet: str
    aspected_planet: str
    aspect_type: str
    orb: float
    orb_strength: float
    total_strength: float
    is_applying: bool
    quality: str


class AspectStrengthResponse(BaseModel):
    """Aspect strength report for the chart."""

    aspects: list[AspectDetailResponse]
    benefic_count: int
    malefic_count: int


@router.get("/aspects", response_model=AspectStrengthResponse)
def get_aspects(
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = _DEFAULT_DT,
) -> AspectStrengthResponse:
    """Calculate aspect strengths between all planets in the chart."""
    dt = _parse_dt(dateandtime)
    ayanamsa_val = get_ayanamsa(dt, ayanamsa)
    planets = get_sidereal_planet_positions(lat, lon, dt, ayanamsa_val)

    longitudes = {p.code: p.longitude for p in planets if p.code in PLANET_FULL}
    report = calculate_aspects_with_strength(longitudes)

    return AspectStrengthResponse(
        aspects=[
            AspectDetailResponse(
                aspecting_planet=a.aspecting_planet,
                aspected_planet=a.aspected_planet,
                aspect_type=a.aspect_type.value if hasattr(a.aspect_type, "value") else str(a.aspect_type),
                orb=round(a.orb, 3),
                orb_strength=round(a.orb_strength, 3),
                total_strength=round(a.total_strength, 3),
                is_applying=a.is_applying,
                quality=a.quality.value if hasattr(a.quality, "value") else str(a.quality),
            )
            for a in report.aspects
        ],
        benefic_count=len(report.benefic_aspects),
        malefic_count=len(report.malefic_aspects),
    )
