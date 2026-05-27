"""Dasha API endpoints backed by the unified dasha service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Annotated, NoReturn, cast

import pytz
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ndastro_engine.ayanamsa import AyanamsaSystem

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.services.dasha import (
    DasaBirthDetails,
    DasaPeriodDetails,
    DasaTimelineDetails,
    RunningDasaDetails,
    get_dasa_timeline_details,
    get_running_dasa_details,
    get_supported_dasa_type_names,
)

router = APIRouter(prefix="/dasha", tags=["Timing & Predictions"], dependencies=get_conditional_dependencies())

_DEFAULT_DT = datetime.now(timezone.utc).isoformat(timespec="seconds")


def _parse_dt(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    return dt if dt.tzinfo else dt.replace(tzinfo=pytz.utc)


class DasaPeriodResponse(BaseModel):
    """Detailed period information for a dasa segment."""

    dasa_type: str
    level: int
    level_name: str
    lord_name: str
    lord_code: str
    start_utc: str
    end_utc: str
    duration_years: float
    elapsed_years: float | None
    remaining_years: float | None
    progress_percent: float | None
    interpretation: str
    child_count: int
    children: list[DasaPeriodResponse] = Field(default_factory=list)


class DasaCurrentResponse(BaseModel):
    """Running dasa details across all current levels."""

    dasa_type: str
    as_of_utc: str
    birth_info: DasaBirthInfoResponse
    maha: DasaPeriodResponse | None
    antara: DasaPeriodResponse | None
    pratyantara: DasaPeriodResponse | None
    sookshma: DasaPeriodResponse | None


class DasaBirthInfoResponse(BaseModel):
    """Birth details that drive all dasa computations."""

    sidereal_moon_longitude: float
    janma_nakshatra_code: str
    janma_nakshatra_name: str
    janma_nakshatra_pada: int
    nakshatra_progress_fraction: float
    nakshatra_remaining_fraction: float
    start_lord_name: str
    start_lord_code: str


class DasaCurrentQuery(BaseModel):
    """Query parameters for current dasa endpoint."""

    lat: float = Query(default=12.971667, description="Latitude")
    lon: float = Query(default=77.593611, description="Longitude")
    ayanamsa: Annotated[AyanamsaSystem, Query(default="lahiri", description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")]
    dateandtime: str = Query(default=_DEFAULT_DT, description="Birth datetime in ISO format")
    current_dateandtime: str | None = Query(
        default=None,
        description="Reference datetime for 'current' period (defaults to now)",
    )


class DasaTimelineQuery(BaseModel):
    """Query parameters for timeline endpoint."""

    lat: float = Query(default=12.971667, description="Latitude")
    lon: float = Query(default=77.593611, description="Longitude")
    ayanamsa: Annotated[AyanamsaSystem, Query(default="lahiri", description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")]
    dateandtime: str = Query(default=_DEFAULT_DT, description="Birth datetime in ISO format")
    levels: int = Query(default=1, description="Number of dasa levels to include (1-4)", ge=1, le=4)
    years: float | None = Query(default=None, description="Timeline horizon in years; omit to use engine default", gt=0)


class DasaTimelineQueryResponse(BaseModel):
    """Query parameters actually used to build the timeline."""

    levels: int
    years: float | None


class DasaTimelineResponse(BaseModel):
    """Detailed dasa timeline response."""

    dasa_type: str
    birth_info: DasaBirthInfoResponse
    query: DasaTimelineQueryResponse
    periods: list[DasaPeriodResponse]


class DasaTypesResponse(BaseModel):
    """Supported dasa systems from ndastro_engine."""

    supported_types: list[str]


def _birth_info_response(birth_info: DasaBirthDetails) -> DasaBirthInfoResponse:
    return DasaBirthInfoResponse(
        sidereal_moon_longitude=round(birth_info.sidereal_moon_longitude, 6),
        janma_nakshatra_code=birth_info.janma_nakshatra_code,
        janma_nakshatra_name=birth_info.janma_nakshatra_name,
        janma_nakshatra_pada=birth_info.janma_nakshatra_pada,
        nakshatra_progress_fraction=round(birth_info.nakshatra_progress_fraction, 8),
        nakshatra_remaining_fraction=round(birth_info.nakshatra_remaining_fraction, 8),
        start_lord_name=birth_info.start_lord_name,
        start_lord_code=birth_info.start_lord_code,
    )


def _period_response(period: DasaPeriodDetails | None) -> DasaPeriodResponse | None:
    if period is None:
        return None

    return DasaPeriodResponse(
        dasa_type=period.dasa_type,
        level=period.level,
        level_name=period.level_name,
        lord_name=period.lord_name,
        lord_code=period.lord_code,
        start_utc=period.start_utc.isoformat(),
        end_utc=period.end_utc.isoformat(),
        duration_years=round(period.duration_years, 8),
        elapsed_years=round(period.elapsed_years, 8) if period.elapsed_years is not None else None,
        remaining_years=round(period.remaining_years, 8) if period.remaining_years is not None else None,
        progress_percent=round(period.progress_percent, 4) if period.progress_percent is not None else None,
        interpretation=period.interpretation,
        child_count=period.child_count,
        children=[child for child in [_period_response(p) for p in period.children] if child is not None],
    )


def _current_response(details: RunningDasaDetails) -> DasaCurrentResponse:
    return DasaCurrentResponse(
        dasa_type=details.dasa_type,
        as_of_utc=details.as_of_utc.isoformat(),
        birth_info=_birth_info_response(details.birth_info),
        maha=_period_response(details.maha),
        antara=_period_response(details.antara),
        pratyantara=_period_response(details.pratyantara),
        sookshma=_period_response(details.sookshma),
    )


def _timeline_response(details: DasaTimelineDetails) -> DasaTimelineResponse:
    return DasaTimelineResponse(
        dasa_type=details.dasa_type,
        birth_info=_birth_info_response(details.birth_info),
        query=DasaTimelineQueryResponse(levels=details.levels, years=details.years),
        periods=[period for period in [_period_response(p) for p in details.periods] if period is not None],
    )


def _raise_bad_request(exc: ValueError) -> NoReturn:
    message = str(exc)
    supported_types = list(get_supported_dasa_type_names())
    raise HTTPException(status_code=400, detail={"message": message, "supported_types": supported_types}) from exc


@router.get("/types", response_model=DasaTypesResponse)
def get_dasa_types() -> DasaTypesResponse:
    """List supported dasa systems exposed by the dasha service."""
    return DasaTypesResponse(supported_types=list(get_supported_dasa_type_names()))


@router.get("/{dasa_name}/current", response_model=DasaCurrentResponse)
def get_current_dasa(
    params: Annotated[DasaCurrentQuery, Depends()],
    dasa_name: Annotated[str, Path(title="Dasa system name", example="vimshottari", description="Name of the dasa system to query")],
) -> DasaCurrentResponse:
    """Return running dasa details for the requested dasa system."""
    birth_dt = _parse_dt(params.dateandtime)
    ref_dt = _parse_dt(params.current_dateandtime) if params.current_dateandtime else datetime.now(timezone.utc)
    try:
        details = get_running_dasa_details(
            query_datetime=ref_dt,
            birth_datetime=birth_dt,
            lat=params.lat,
            lon=params.lon,
            ayanamsa_system=cast("AyanamsaSystem", params.ayanamsa),
            dasa_type=dasa_name,
        )
    except ValueError as exc:
        _raise_bad_request(exc)
    return _current_response(details)


@router.get("/{dasa_name}/timeline", response_model=DasaTimelineResponse)
def get_dasa_timeline_by_type(
    params: Annotated[DasaTimelineQuery, Depends()],
    dasa_name: Annotated[str, Path(title="Dasa system name", example="vimshottari", description="Name of the dasa system to query")],
) -> DasaTimelineResponse:
    """Return a dasa timeline for the requested dasa system."""
    birth_dt = _parse_dt(params.dateandtime)
    try:
        details = get_dasa_timeline_details(
            birth_datetime=birth_dt,
            lat=params.lat,
            lon=params.lon,
            ayanamsa_system=cast("AyanamsaSystem", params.ayanamsa),
            dasa_type=dasa_name,
            levels=params.levels,
            years=params.years,
        )
    except ValueError as exc:
        _raise_bad_request(exc)
    return _timeline_response(details)


DasaPeriodResponse.model_rebuild()
