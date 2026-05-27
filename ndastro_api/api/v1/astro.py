"""Astro API endpoints for planetary and astronomy calculations."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Annotated, cast

import pytz
from babel.dates import format_datetime
from fastapi import APIRouter, Query, Request
from fastapi.responses import Response
from fastapi_babel import _
from ndastro_engine.ayanamsa import AyanamsaSystem, get_ayanamsa
from ndastro_engine.config import EngineSettingsOverride, override_settings
from ndastro_engine.core import (
    get_lunar_node_positions,
    get_planet_position,
    get_planet_rise_set,
    get_sunrise_sunset,
)
from ndastro_engine.enums import Planets as EnginePlanets
from ndastro_engine.planet_enum import Planets
from ndastro_engine.utils import normalize_degree as _norm_deg
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
from ndastro_api.services.panchanga import (
    _TITHI_KARANA_RATE,
    _YOGA_RATE,
    _find_end_time,
    _find_start_time,
    build_panchanga_summary,
    get_durmuhurta,
    get_gulika,
    get_panchanga_with_data,
    get_rahu_kalam,
    get_varjya,
    get_yamagandam,
)
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
    node_type: Annotated[
        str | None, Query(description="Override node type: 'true' (osculating) or 'mean' (IAU polynomial). Defaults to server setting.")
    ] = None,
) -> list[Planet]:
    """Calculate the positions of Rahu and Kethu (lunar nodes) for a given datetime."""
    if node_type is not None:
        with override_settings(EngineSettingsOverride(node_type=node_type)):  # type: ignore[arg-type]
            results = get_lunar_node_positions(_parse_datetime_with_tz(dateandtime))
    else:
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
    node_type: Annotated[
        str | None, Query(description="Override node type: 'true' (osculating) or 'mean' (IAU polynomial). Defaults to server setting.")
    ] = None,
    position_reference: Annotated[
        str | None, Query(description="Override position reference: 'geocentric' or 'topocentric'. Defaults to server setting.")
    ] = None,
) -> list[Planet]:
    """Calculate sidereal planetary positions for given latitude, longitude, datetime, and ayanamsa."""
    dt = _parse_datetime_with_tz(dateandtime)
    if node_type is not None or position_reference is not None:
        with override_settings(
            EngineSettingsOverride(
                node_type=node_type,  # type: ignore[arg-type]
                position_reference=position_reference,  # type: ignore[arg-type]
            )
        ):
            return get_sidereal_planet_positions(lat, lon, dt, get_ayanamsa(dt, ayanamsa))
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


class ActivitySupportResponse(BaseModel):
    """Response model for activity support across panchanga elements."""

    activity: str
    tithi_support: bool
    karana_support: bool
    vara_support: bool
    yoga_support: bool
    inauspicious_flags: list[str]


class TimeRange(BaseModel):
    """A time window with start and end."""

    start: datetime
    end: datetime


class PanchangaResponse(BaseModel):
    """Response model for panchanga calculation."""

    tithi_name: str
    tithi_number: int
    tithi_start: datetime | None = None
    tithi_end: datetime | None = None
    karana_name: str
    karana_number: int
    karana_start: datetime | None = None
    karana_end: datetime | None = None
    vara_name: str
    vara_number: int
    vara_start: datetime | None = None
    vara_end: datetime | None = None
    yoga_name: str
    yoga_number: int
    yoga_start: datetime | None = None
    yoga_end: datetime | None = None
    muhurta_rating: float | None
    auspicious_for: list[str]
    inauspicious_for: list[str]
    interpretations: dict[str, str]
    nakshatra_compatibility: dict[str, list[str]]
    activity_support: ActivitySupportResponse | None
    sunrise: datetime | None = None
    sunset: datetime | None = None
    moonrise: datetime | None = None
    moonset: datetime | None = None
    rahu_kalam: TimeRange | None = None
    gulika_kala: TimeRange | None = None
    yama_ghantaka: TimeRange | None = None
    durmuhurta: list[TimeRange] = []
    varjya: list[TimeRange] = []


@router.get("/panchanga", response_model=PanchangaResponse)
def get_panchanga(
    lat: Annotated[float, Query(description="Latitude")] = 12.971667,
    lon: Annotated[float, Query(description="Longitude")] = 77.593611,
    ayanamsa: Annotated[AyanamsaSystem, Query(description="Ayanamsa name i.e 'lahiri', 'chitrapaksha', etc.")] = "lahiri",
    dateandtime: Annotated[str, Query(description="Datetime in ISO format")] = datetime.now(timezone.utc).isoformat(timespec="seconds"),
    activity: Annotated[str | None, Query(description="Optional activity name to check support for (e.g. 'marriage', 'travel')")] = None,
) -> PanchangaResponse:
    """Calculate panchanga (tithi, karana, vara, yoga) for given latitude, longitude, datetime, and ayanamsa."""
    dt = _parse_datetime_with_tz(dateandtime)
    ayanamsa_val = get_ayanamsa(dt, ayanamsa)
    planets = get_sidereal_planet_positions(lat, lon, dt, ayanamsa_val)

    sun = next(p for p in planets if p.code == Planets.SUN.code)
    moon = next(p for p in planets if p.code == Planets.MOON.code)

    panchanga_data = get_panchanga_with_data(sun.longitude, moon.longitude, date_value=dt)
    summary = build_panchanga_summary(panchanga_data, activity=activity)

    # --- phase function closures for timing binary search ---
    def _diff_phase(t: datetime) -> float:
        """(moon - sun) sidereal longitude, used for tithi/karana timing."""
        ayan = get_ayanamsa(t, ayanamsa)
        s = _norm_deg(get_planet_position(EnginePlanets.SUN, lat, lon, t).longitude - ayan)
        m = _norm_deg(get_planet_position(EnginePlanets.MOON, lat, lon, t).longitude - ayan)
        return _norm_deg(m - s)

    def _sum_phase(t: datetime) -> float:
        """(moon + sun) sidereal longitude, used for yoga timing."""
        ayan = get_ayanamsa(t, ayanamsa)
        s = _norm_deg(get_planet_position(EnginePlanets.SUN, lat, lon, t).longitude - ayan)
        m = _norm_deg(get_planet_position(EnginePlanets.MOON, lat, lon, t).longitude - ayan)
        return _norm_deg(m + s)

    current_diff = _diff_phase(dt)
    current_sum = _sum_phase(dt)
    t_data = panchanga_data.panchanga

    tithi_start = _find_start_time(dt, current_diff, t_data.tithi.start_degree, _TITHI_KARANA_RATE, _diff_phase)
    tithi_end = _find_end_time(dt, current_diff, t_data.tithi.end_degree, _TITHI_KARANA_RATE, _diff_phase)
    karana_start = _find_start_time(dt, current_diff, t_data.karana.start_degree, _TITHI_KARANA_RATE, _diff_phase)
    karana_end = _find_end_time(dt, current_diff, t_data.karana.end_degree, _TITHI_KARANA_RATE, _diff_phase)

    yoga_result = panchanga_data.panchanga
    yoga_start_deg = (yoga_result.yoga_number - 1) * (360.0 / 27)
    yoga_end_deg = yoga_result.yoga_number * (360.0 / 27)
    yoga_start = _find_start_time(dt, current_sum, yoga_start_deg, _YOGA_RATE, _sum_phase)
    yoga_end = _find_end_time(dt, current_sum, yoga_end_deg, _YOGA_RATE, _sum_phase)

    # Vara runs from today's sunrise to tomorrow's sunrise (Vedic convention)
    sunrise, sunset = get_sunrise_sunset(lat, lon, dt)
    tomorrow = dt + timedelta(days=1)
    vara_end, _ = get_sunrise_sunset(lat, lon, tomorrow)

    moonrise, moonset = get_planet_rise_set(EnginePlanets.MOON, lat, lon, dt)

    # --- moon sidereal longitude closure for nakshatra / varjya ---
    def _moon_sidereal_lon(t: datetime) -> float:
        ayan = get_ayanamsa(t, ayanamsa)
        return _norm_deg(get_planet_position(EnginePlanets.MOON, lat, lon, t).longitude - ayan)

    current_moon_lon = _moon_sidereal_lon(dt)

    # --- inauspicious timings ---
    _rahu_tw = get_rahu_kalam(sunrise=sunrise, sunset=sunset, date_value=dt) if sunrise and sunset else None
    _gulika_tw = get_gulika(sunrise=sunrise, sunset=sunset, date_value=dt) if sunrise and sunset else None
    _yama_tw = get_yamagandam(sunrise=sunrise, sunset=sunset, date_value=dt) if sunrise and sunset else None
    _durmuhurta_tws = get_durmuhurta(sunrise=sunrise, sunset=sunset, next_sunrise=vara_end, date_value=dt) if sunrise and sunset and vara_end else []
    _varjya_tws = get_varjya(ref_dt=dt, current_moon_lon=current_moon_lon, moon_lon_fn=_moon_sidereal_lon)

    return PanchangaResponse(
        tithi_name=summary.tithi_name,
        tithi_number=summary.tithi_number,
        tithi_start=tithi_start,
        tithi_end=tithi_end,
        karana_name=summary.karana_name,
        karana_number=summary.karana_number,
        karana_start=karana_start,
        karana_end=karana_end,
        vara_name=summary.vara_name,
        vara_number=summary.vara_number,
        vara_start=sunrise,
        vara_end=vara_end,
        yoga_name=summary.yoga_name,
        yoga_number=summary.yoga_number,
        yoga_start=yoga_start,
        yoga_end=yoga_end,
        muhurta_rating=summary.muhurta_rating,
        auspicious_for=summary.auspicious_for,
        inauspicious_for=summary.inauspicious_for,
        interpretations=summary.interpretations,
        nakshatra_compatibility=summary.nakshatra_compatibility,
        activity_support=ActivitySupportResponse(
            activity=summary.activity_support.activity,
            tithi_support=summary.activity_support.tithi_support,
            karana_support=summary.activity_support.karana_support,
            vara_support=summary.activity_support.vara_support,
            yoga_support=summary.activity_support.yoga_support,
            inauspicious_flags=summary.activity_support.inauspicious_flags,
        )
        if summary.activity_support
        else None,
        sunrise=sunrise,
        sunset=sunset,
        moonrise=moonrise,
        moonset=moonset,
        rahu_kalam=TimeRange(start=_rahu_tw.start, end=_rahu_tw.end) if _rahu_tw else None,
        gulika_kala=TimeRange(start=_gulika_tw.start, end=_gulika_tw.end) if _gulika_tw else None,
        yama_ghantaka=TimeRange(start=_yama_tw.start, end=_yama_tw.end) if _yama_tw else None,
        durmuhurta=[TimeRange(start=tw.start, end=tw.end) for tw in _durmuhurta_tws],
        varjya=[TimeRange(start=tw.start, end=tw.end) for tw in _varjya_tws],
    )
