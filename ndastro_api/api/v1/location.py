"""Location lookup API endpoints."""

from __future__ import annotations

from typing import Annotated, NoReturn

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.core.config import settings
from ndastro_api.services.location import LocationLookupError, LocationSearchResult, search_locations

router = APIRouter(prefix="/location", tags=["Location"], dependencies=get_conditional_dependencies())


class LocationResultResponse(BaseModel):
    """Normalized location search result."""

    name: str
    display_name: str
    lat: float
    lon: float
    timezone: str | None
    country: str | None
    state: str | None
    country_code: str | None
    result_type: str | None
    provider: str


class LocationSearchResponse(BaseModel):
    """Location search response payload."""

    query: str
    count: int
    results: list[LocationResultResponse] = Field(default_factory=list)


def _to_response(result: LocationSearchResult) -> LocationResultResponse:
    return LocationResultResponse(
        name=result.name,
        display_name=result.display_name,
        lat=round(result.lat, 6),
        lon=round(result.lon, 6),
        timezone=result.timezone,
        country=result.country,
        state=result.state,
        country_code=result.country_code,
        result_type=result.result_type,
        provider=result.provider,
    )


def _raise_bad_request(exc: ValueError) -> NoReturn:
    raise HTTPException(status_code=400, detail={"message": str(exc), "max_limit": settings.LOCATION_SERVICE_MAX_LIMIT}) from exc


def _raise_provider_error(exc: LocationLookupError) -> NoReturn:
    raise HTTPException(status_code=502, detail={"message": str(exc)}) from exc


@router.get("/search", response_model=LocationSearchResponse, summary="Search for locations by text")
def search_location(
    q: Annotated[str, Query(description="Free-form location text", min_length=2, example="Salem")],
    limit: Annotated[int | None, Query(description="Maximum results to return", ge=1)] = None,
) -> LocationSearchResponse:
    """Search locations and return normalized coordinates and metadata."""
    try:
        results = search_locations(q, limit)
    except ValueError as exc:
        _raise_bad_request(exc)
    except LocationLookupError as exc:
        _raise_provider_error(exc)

    payload = [_to_response(result) for result in results]
    return LocationSearchResponse(query=q.strip(), count=len(payload), results=payload)