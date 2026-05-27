"""Ashtakavarga API endpoints — 8-point strength analysis."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

import pytz
from fastapi import APIRouter, Query
from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from pydantic import BaseModel

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.core.utils.chart_helpers import (
    PLANET_FULL,
    RASI_NAMES,
    classify_planets,
    house_num,
    rasi_num,
)
from ndastro_api.services.ashtakavarga import (
    AshtakavargaContext,
    calculate_sarva_ashtakavarga,
    get_ashtakavarga_interpretation,
    get_house_strength_classification,
)
from ndastro_api.services.position import get_sidereal_planet_positions

router = APIRouter(prefix="/ashtakavarga", tags=["Planetary Strength"], dependencies=get_conditional_dependencies())

_DEFAULT_DT = datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_dt(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=pytz.utc)


class AshtakavargaHouseResponse(BaseModel):
    """SAV score for a single house."""

    house: int
    points: int
    strength: str
    interpretation: str


class BhinnaAshtakavargaResponse(BaseModel):
    """Individual planet's contribution map."""

    planet: str
    points_per_house: dict[str, int]
    total_points: int
    average_per_house: float


class AshtakavargaResponse(BaseModel):
    """Full Sarva + Bhinna Ashtakavarga result."""

    sarva: list[AshtakavargaHouseResponse]
    bhinna: list[BhinnaAshtakavargaResponse]
    strong_houses: list[int]
    weak_houses: list[int]
    moderate_houses: list[int]


@router.get("", response_model=AshtakavargaResponse)
def get_ashtakavarga(
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = _DEFAULT_DT,
) -> AshtakavargaResponse:
    """Calculate Sarva Ashtakavarga (SAV) and Bhinna Ashtakavarga (BAV) for the given chart."""
    dt = _parse_dt(dateandtime)
    ayanamsa_val = get_ayanamsa(dt, ayanamsa)

    planets = get_sidereal_planet_positions(lat, lon, dt, ayanamsa_val)
    exalted, own_rasi, debilitated = classify_planets(planets)

    planets_in_houses = {PLANET_FULL[p.code]: house_num(p) for p in planets if p.code in PLANET_FULL}
    planets_in_rasis = {PLANET_FULL[p.code]: RASI_NAMES.get(rasi_num(p), "aries") for p in planets if p.code in PLANET_FULL}

    context = AshtakavargaContext(
        planets_in_houses=planets_in_houses,
        planets_in_rasis=planets_in_rasis,
        aspecting_planets={},
        conjunct_planets={},
        exalted_planets=exalted,
        own_rasi_planets=own_rasi,
        debilitated_planets=debilitated,
    )

    sav = calculate_sarva_ashtakavarga(context)

    sarva_list = []
    for house in range(1, 13):
        points = sav.points_per_house.get(house, 0)
        strength = get_house_strength_classification(points)
        sarva_list.append(
            AshtakavargaHouseResponse(
                house=house,
                points=points,
                strength=strength.value,
                interpretation=get_ashtakavarga_interpretation(house, points, strength),
            )
        )

    bhinna_list = []
    for planet_name, bav in sav.bhinna_maps.items():
        bhinna_list.append(
            BhinnaAshtakavargaResponse(
                planet=planet_name,
                points_per_house={str(k): v for k, v in bav.points_per_house.items()},
                total_points=bav.total_points,
                average_per_house=round(bav.average_per_house, 2),
            )
        )

    return AshtakavargaResponse(
        sarva=sarva_list,
        bhinna=bhinna_list,
        strong_houses=sav.strong_houses,
        weak_houses=sav.weak_houses,
        moderate_houses=sav.moderate_houses,
    )
