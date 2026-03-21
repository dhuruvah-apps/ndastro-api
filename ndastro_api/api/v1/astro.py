"""Astro API endpoints for planetary and astronomy calculations."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, cast

import pytz
from babel.dates import format_datetime
from fastapi import APIRouter, Query, Request
from fastapi.responses import Response
from fastapi_babel import _
from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from ndastro_engine.core import get_lunar_node_positions, get_sunrise_sunset
from ndastro_engine.planet_enum import Planets
from pydantic import BaseModel

from ndastro_api.api.deps import get_conditional_dependencies
from ndastro_api.core.babel_i18n import get_locale
from ndastro_api.core.exceptions.app_exceptions import PlanetNotFoundError
from ndastro_api.core.models.astro_system import Planet
from ndastro_api.core.utils.data_loader import astro_data
from ndastro_api.services.chart_utils import (
    BirthDetails,
    generate_south_indian_chart_svg,
)
from ndastro_api.services.kattams import get_kattams
from ndastro_api.services.position import (
    get_sidereal_ascendant_position,
    get_sidereal_planet_positions,
)
from ndastro_api.services.utils import convert_kattams_to_response_format

router = APIRouter(prefix="/astro", tags=["Astro"], dependencies=get_conditional_dependencies())


def _parse_datetime_with_tz(dateandtime: str) -> datetime:
    """Parse datetime string and ensure it has timezone info (assume UTC if naive)."""
    dt = datetime.fromisoformat(dateandtime)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.utc)
    return dt


class ChartType(str, Enum):
    """Enumeration for different chart types."""

    SOUTH_INDIAN = "south-indian"
    NORTH_INDIAN = "north-indian"  # For future implementation


class ChartConfig(BaseModel):
    """Configuration for chart generation."""

    chart_type: ChartType = ChartType.SOUTH_INDIAN
    lang: str = "en"
    name: str | None = "ND Astro"
    place: str | None = "Salem"


class ChartRequest(BaseModel):
    """Request model for chart generation."""

    lat: float
    lon: float
    datetime: datetime
    ayanamsa: str
    chart_type: ChartType = ChartType.SOUTH_INDIAN
    name: str = "ND Astro"
    place: str = "Salem"
    lang: str = "en"


@router.get("/lunar-nodes")
def get_lunar_nodes(
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(timezone.utc).isoformat(timespec="seconds"),
) -> list[Planet]:
    """Calculate the positions of Rahu and Kethu (lunar nodes) for a given datetime."""
    results = get_lunar_node_positions(_parse_datetime_with_tz(dateandtime))

    rahu = astro_data.get_planet_by_astronomical_code(Planets.RAHU.astronomical_code)
    kethu = astro_data.get_planet_by_astronomical_code(Planets.KETHU.astronomical_code)

    if not rahu or not kethu:
        err = "Rahu or Kethu not found in the data source."
        raise PlanetNotFoundError(err)

    return cast("list[Planet]", [{**vars(rahu), "longitude": results[0]}, {**vars(kethu), "longitude": results[1]}])


class SiderealPositionsRequest(BaseModel):
    """Request model for sidereal planetary positions."""

    lat: float
    lon: float
    datetime: datetime
    ayanamsa: str


@router.get("/planets")
def get_sidereal_positions(
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(timezone.utc).isoformat(timespec="seconds"),
) -> list[Planet]:
    """Calculate sidereal planetary positions for given latitude, longitude, datetime, and ayanamsa."""
    dt = _parse_datetime_with_tz(dateandtime)

    return get_sidereal_planet_positions(lat, lon, dt, get_ayanamsa(dt, ayanamsa))


class AscendantRequest(BaseModel):
    """Request model for ascendant calculation."""

    lat: float
    lon: float
    datetime: datetime
    ayanamsa: str


@router.get("/ascendant", response_model=Planet)
def get_sidereal_ascendant(
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(timezone.utc).isoformat(timespec="seconds"),
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
) -> Planet:
    """Calculate the sidereal ascendant (lagna) for given latitude, longitude, datetime, and ayanamsa."""
    dt = _parse_datetime_with_tz(dateandtime)

    return get_sidereal_ascendant_position(dt, lat, lon, ayanamsa=get_ayanamsa(dt, ayanamsa))


class SunriseSunsetRequest(BaseModel):
    """Request model for sunrise and sunset calculation."""

    lat: float
    lon: float
    datetime: datetime


class SunriseSunsetResponse(BaseModel):
    """Response model for sunrise and sunset calculation."""

    sunrise: str | None
    sunset: str | None


@router.get("/sunrise-sunset", response_model=SunriseSunsetResponse)
def get_sun_rise_set(
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(timezone.utc).isoformat(timespec="seconds"),
) -> SunriseSunsetResponse:
    """Calculate the sunrise and sunset times for a given location and date."""
    result = get_sunrise_sunset(lat, lon, _parse_datetime_with_tz(dateandtime))
    return SunriseSunsetResponse(
        sunrise=result[0].isoformat() if result[0] else None,
        sunset=result[1].isoformat() if result[1] else None,
    )


class KattamRequest(BaseModel):
    """Request model for kattam chart generation."""

    lat: float
    lon: float
    datetime: datetime
    ayanamsa: float


class KattamResponse(BaseModel):
    """Response model for kattam chart."""

    order: int
    is_ascendant: bool
    asc_longitude: float
    owner: int
    rasi: int
    house: int
    planets: list[Planet] | None


@router.get("/kattams", response_model=list[KattamResponse])
def get_astro_kattams(
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(timezone.utc).isoformat(timespec="seconds"),
) -> list[KattamResponse]:
    """Generate kattam chart (list of squares) for given lat, lon, datetime, and ayanamsa."""
    dt = _parse_datetime_with_tz(dateandtime)
    kattams = get_kattams(lat, lon, dt, get_ayanamsa(dt, ayanamsa))

    return convert_kattams_to_response_format(kattams, KattamResponse, Planet)


@router.get("/chart")
def get_astrology_chart_svg(  # noqa: PLR0913
    request: Request,
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(timezone.utc).isoformat(timespec="seconds"),
    chart_type: Annotated[ChartType, Query(description="Type of astrology chart")] = ChartType.SOUTH_INDIAN,
    name: Annotated[str, Query(description="Name for the chart")] = "ND Astro",
    place: Annotated[str, Query(description="Place of birth")] = "Salem",
    lang: Annotated[str | None, Query(description="Language code for localization")] = None,
    tz: Annotated[str, Query(description="Timezone for the birth location, e.g., 'Asia/Kolkata'")] = "UTC",
) -> Response:
    """Generate astrology chart as SVG image based on chart type.

    Args:
        request: FastAPI request object (for language detection)
        lat: Latitude for birth location
        lon: Longitude for birth location
        ayanamsa: Ayanamsa system to use
        dateandtime: Birth date and time in ISO format
        chart_type: Type of astrology chart ('south-indian' or 'north-indian')
        name: Name for the chart
        place: Place of birth
        lang: Language code for localization
        tz: Timezone for the birth location, e.g., 'Asia/Kolkata'

    Returns:
        Response: SVG image of the astrology chart with Content-Language header

    """
    # Determine the target language using babel's get_locale function
    target_lang = lang or get_locale(request)

    # Get the kattams data using the same logic as the kattams endpoint
    dt = _parse_datetime_with_tz(dateandtime)
    kattams = get_kattams(lat, lon, dt, get_ayanamsa(dt, ayanamsa))

    # Convert to KattamResponse format using the utility function
    kattams_data = convert_kattams_to_response_format(kattams, KattamResponse, Planet)

    # Create birth details using input parameters
    datetz = dt.astimezone(pytz.timezone(tz))
    birth_details = BirthDetails(
        name_abbr=name,
        date=format_datetime(datetz, format=_("DateFormat"), locale=target_lang, tzinfo=pytz.timezone(tz)),
        time=format_datetime(datetz, format=_("TimeFormat"), locale=target_lang, tzinfo=pytz.timezone(tz)),
        place=place,
    )

    # Generate SVG based on chart type using the detected language
    if chart_type == ChartType.SOUTH_INDIAN:
        svg_content = generate_south_indian_chart_svg(kattams_data, birth_details)
        filename = f"south_indian_chart_{target_lang}.svg"
    elif chart_type == ChartType.NORTH_INDIAN:
        # Placeholder for future north indian chart implementation with translation
        coming_soon_text = _("Coming Soon")
        chart_title = _("Birth Chart")
        svg_content = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">'
            f'<text x="200" y="180" text-anchor="middle" font-size="16">{chart_title}</text>'
            f'<text x="200" y="220" text-anchor="middle" font-size="14">{coming_soon_text}</text>'
            "</svg>"
        )
        filename = f"north_indian_chart_{target_lang}.svg"
    else:
        # Default to south indian
        svg_content = generate_south_indian_chart_svg(kattams_data, birth_details, target_lang)
        filename = f"chart_{target_lang}.svg"

    # Return response with proper Content-Language header for i18n
    return Response(
        content=svg_content,
        media_type="image/svg+xml",
        headers={"Content-Disposition": f"inline; filename={filename}", "Content-Language": target_lang},
    )
