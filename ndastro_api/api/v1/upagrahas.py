"""Upagrahas API endpoints — shadow sub-planets derived from the Sun."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

import pytz
from fastapi import APIRouter, Query
from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from ndastro_engine.planet_enum import Planets
from pydantic import BaseModel

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.services.position import get_sidereal_planet_positions
from ndastro_api.services.upagrahas import (
    get_all_sun_based_upagrahas,
    get_upagraha_interpretation,
)

router = APIRouter(prefix="/upagrahas", tags=["Chart Analysis"], dependencies=get_conditional_dependencies())


class UpagrahaResponse(BaseModel):
    """A single upagraha with position and interpretation."""

    name: str
    longitude: float
    rasi_number: int
    rasi_name: str
    degree_in_rasi: float
    ruling_planet: str
    interpretation: str


@router.get("", response_model=list[UpagrahaResponse])
def get_upagrahas(
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(timezone.utc).isoformat(timespec="seconds"),
) -> list[UpagrahaResponse]:
    """Calculate all 11 sun-based upagrahas (shadow sub-planets) for the given chart."""
    dt = datetime.fromisoformat(dateandtime)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.utc)

    planets = get_sidereal_planet_positions(lat, lon, dt, get_ayanamsa(dt, ayanamsa))
    sun = next(p for p in planets if p.code == Planets.SUN.code)

    upagrahas = get_all_sun_based_upagrahas(sun.longitude)
    return [
        UpagrahaResponse(
            name=u.name,
            longitude=u.longitude,
            rasi_number=u.rasi_number,
            rasi_name=u.rasi_name,
            degree_in_rasi=u.degree_in_rasi,
            ruling_planet=u.ruling_planet or "",
            interpretation=get_upagraha_interpretation(u),
        )
        for u in upagrahas
    ]
