"""Nakshatra API endpoints — position lookup and compatibility."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.services.nakshatra_traits import (
    NakshatraCompatibility,
    NakshatraPosition,
    calculate_nakshatra_compatibility,
    calculate_nakshatra_position,
)

router = APIRouter(prefix="/nakshatra", tags=["Chart Analysis"], dependencies=get_conditional_dependencies())


class NakshatraTraitsResponse(BaseModel):
    """Trait details for a nakshatra."""

    index: int
    name: str
    lord: str
    deity: str
    gana: str
    type: str
    symbol: str
    meaning: str
    qualities: list[str]
    activities: list[str]


class NakshatraPositionResponse(BaseModel):
    """Full nakshatra position breakdown for a longitude."""

    longitude: float
    nakshatra_index: int
    nakshatra_name: str
    pada: int
    degrees_in_nakshatra: float
    degrees_in_pada: float
    lord: str


class NakshatraCompatibilityResponse(BaseModel):
    """Compatibility result between two nakshatras."""

    nakshatra1: int
    nakshatra2: int
    name1: str
    name2: str
    kuta_score: float
    compatibility_level: str
    description: str


def _position_to_response(pos: NakshatraPosition) -> NakshatraPositionResponse:
    return NakshatraPositionResponse(
        longitude=pos.longitude,
        nakshatra_index=pos.nakshatra_index,
        nakshatra_name=pos.nakshatra_name,
        pada=pos.pada,
        degrees_in_nakshatra=pos.degrees_in_nakshatra,
        degrees_in_pada=pos.degrees_in_pada,
        lord=pos.lord,
    )


def _compat_to_response(c: NakshatraCompatibility) -> NakshatraCompatibilityResponse:
    return NakshatraCompatibilityResponse(
        nakshatra1=c.nakshatra1,
        nakshatra2=c.nakshatra2,
        name1=c.name1,
        name2=c.name2,
        kuta_score=c.kuta_score,
        compatibility_level=c.compatibility_level,
        description=c.description,
    )


@router.get("/position", response_model=NakshatraPositionResponse)
def get_nakshatra_position(
    longitude: Annotated[float, Query(description="Sidereal ecliptic longitude (0-360 deg)")] = 0.0,
) -> NakshatraPositionResponse:
    """Return nakshatra index, name, pada, and degree breakdown for a given ecliptic longitude."""
    return _position_to_response(calculate_nakshatra_position(longitude))


@router.get("/compatibility", response_model=NakshatraCompatibilityResponse)
def get_nakshatra_compatibility(
    nakshatra1: Annotated[int, Query(description="First nakshatra index (1-27)")] = 1,
    nakshatra2: Annotated[int, Query(description="Second nakshatra index (1-27)")] = 2,
) -> NakshatraCompatibilityResponse:
    """Calculate Guna Milan compatibility score between two nakshatras."""
    return _compat_to_response(calculate_nakshatra_compatibility(nakshatra1, nakshatra2))
