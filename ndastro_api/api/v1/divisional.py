"""Divisional Charts (Varga) API endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

import pytz
from fastapi import APIRouter, Query
from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from pydantic import BaseModel

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.core.utils.chart_helpers import PLANET_FULL
from ndastro_api.services.divisional_charts import (
    VargaType,
    compute_varga_chart,
)
from ndastro_api.services.position import get_sidereal_planet_positions

router = APIRouter(prefix="/divisional", tags=["Chart Analysis"], dependencies=get_conditional_dependencies())


class VargaPositionResponse(BaseModel):
    """A planet's position in a divisional chart."""

    planet: str
    longitude: float
    rasi: int
    varga_rasi: int
    division: int
    part_index: int


class VargaChartResponse(BaseModel):
    """Computed divisional chart."""

    varga: str
    division: int
    positions: list[VargaPositionResponse]


@router.get("/{varga}", response_model=VargaChartResponse)
def get_divisional_chart(
    varga: VargaType,
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(timezone.utc).isoformat(timespec="seconds"),
) -> VargaChartResponse:
    """Compute a divisional (varga) chart for the given chart and division type.

    Supported vargas: D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60.
    """
    dt = datetime.fromisoformat(dateandtime)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.utc)

    planets = get_sidereal_planet_positions(lat, lon, dt, get_ayanamsa(dt, ayanamsa))

    # Build longitude dict keyed by planet code (SU, MO, ...)
    longitudes = {p.code: p.longitude for p in planets if p.code in PLANET_FULL}

    chart = compute_varga_chart(longitudes, varga)

    return VargaChartResponse(
        varga=chart.varga.value,
        division=chart.division,
        positions=[
            VargaPositionResponse(
                planet=pos.planet,
                longitude=pos.longitude,
                rasi=pos.rasi,
                varga_rasi=pos.varga_rasi,
                division=pos.division,
                part_index=pos.part_index,
            )
            for pos in chart.positions.values()
        ],
    )
