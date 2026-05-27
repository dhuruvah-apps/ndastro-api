"""Avasthas API endpoints — planetary state analysis."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

import pytz
from fastapi import APIRouter, Query
from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from pydantic import BaseModel

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.core.utils.chart_helpers import PLANET_FULL, house_num
from ndastro_api.services.avasthas import (
    AvasthaPlanetContext,
    get_all_avasthas,
)
from ndastro_api.services.position import get_sidereal_planet_positions

router = APIRouter(prefix="/avasthas", tags=["Chart Analysis"], dependencies=get_conditional_dependencies())

_DEFAULT_DT = datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_dt(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=pytz.utc)


class AvasthaSummaryResponse(BaseModel):
    """Avastha states for a single planet."""

    planet_code: str
    planet_name: str
    age_avastha: str
    age_interpretation: str
    alertness_avastha: str
    alertness_interpretation: str
    mood_avastha: str
    mood_interpretation: str
    activity_avastha: str | None
    activity_strength: str | None
    activity_interpretation: str | None


@router.get("", response_model=list[AvasthaSummaryResponse])
def get_avasthas(
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = _DEFAULT_DT,
) -> list[AvasthaSummaryResponse]:
    """Calculate age, alertness, mood, and activity avasthas for all planets in the chart."""
    dt = _parse_dt(dateandtime)
    planets = get_sidereal_planet_positions(lat, lon, dt, get_ayanamsa(dt, ayanamsa))

    # Build a map of house → list of planet codes (for conjunction detection)
    from collections import defaultdict  # noqa: PLC0415

    house_planets: dict[int, list[str]] = defaultdict(list)
    for p in planets:
        if p.code in PLANET_FULL:
            house_planets[house_num(p)].append(p.code)

    results = []
    for p in planets:
        if p.code not in PLANET_FULL:
            continue

        h = house_num(p)
        conjuncts = [c for c in house_planets[h] if c != p.code]

        context = AvasthaPlanetContext(
            planet_code=p.code,
            house_number=h,
            degree_in_rasi=p.advanced_by or 0.0,
            rasi_name=p.rasi_occupied or "",
            rasi_number=int((p.rasi_occupied or "R01")[1:]),
            conjunction_planets=conjuncts if conjuncts else None,
            aspecting_planets=None,
        )

        summary = get_all_avasthas(context)
        results.append(
            AvasthaSummaryResponse(
                planet_code=p.code,
                planet_name=PLANET_FULL[p.code],
                age_avastha=summary.age_avastha or "",
                age_interpretation=summary.age_interpretation or "",
                alertness_avastha=summary.alertness_avastha or "",
                alertness_interpretation=summary.alertness_interpretation or "",
                mood_avastha=summary.mood_avastha or "",
                mood_interpretation=summary.mood_interpretation or "",
                activity_avastha=summary.activity_avastha or None,
                activity_strength=summary.activity_strength or None,
                activity_interpretation=summary.activity_interpretation,
            )
        )

    return results
