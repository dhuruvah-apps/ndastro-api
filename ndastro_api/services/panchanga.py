"""Panchanga timing utilities.

Computes tithi, karana, vara, and nitya yoga from basic inputs.
"""

from __future__ import annotations

import datetime as datetime_module
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ndastro_engine.utils import normalize_degree

from ndastro_api.core.utils.data_loader import AstroDataLoader
from ndastro_api.services.yogas import calculate_nitya_yoga

if TYPE_CHECKING:
    from datetime import datetime

    from ndastro_api.core.models.astro_system import Karana, Tithi, Vara, Yoga

# Constants
FULL_CIRCLE_DEGREES = 360.0
TITHI_COUNT = 30
KARANA_COUNT = 60
TITHI_DEGREES = FULL_CIRCLE_DEGREES / TITHI_COUNT
KARANA_DEGREES = FULL_CIRCLE_DEGREES / KARANA_COUNT
PAKSHA_DIVIDER = 15
MUHURTA_WEIGHT = 0.6
LIST_WEIGHT = 0.4
DAY_SEGMENTS = 8
NIGHT_SEGMENTS = 8
MUHURTA_COUNT = 15
WEDNESDAY_VARA = 4

TITHI_NAMES = [
    "Pratipada",
    "Dwitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dwadashi",
    "Trayodashi",
    "Chaturdashi",
    "Purnima",
    "Pratipada",
    "Dwitiya",
    "Tritiya",
    "Chaturthi",
    "Panchami",
    "Shashthi",
    "Saptami",
    "Ashtami",
    "Navami",
    "Dashami",
    "Ekadashi",
    "Dwadashi",
    "Trayodashi",
    "Chaturdashi",
    "Amavasya",
]

VARA_NAMES = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
]

MOVABLE_KARANAS = [
    "Bava",
    "Balava",
    "Kaulava",
    "Taitila",
    "Garaja",
    "Vanija",
    "Vishti",
]

FIXED_KARANAS = [
    "Shakuni",
    "Chatushpada",
    "Naga",
]


class MissingWeekdayError(ValueError):
    """Raised when weekday input is missing."""

    def __init__(self) -> None:
        """Initialize the missing weekday error."""
        super().__init__("weekday_index or date_value is required")


class MissingTimezoneError(ValueError):
    """Raised when a timezone-aware datetime is required."""

    def __init__(self) -> None:
        """Initialize the missing timezone error."""
        super().__init__("date_value must include tzinfo")


@dataclass
class TithiResult:
    """Computed tithi details."""

    number: int
    name: str
    paksha: str
    phase_degrees: float
    start_degree: float
    end_degree: float


@dataclass
class KaranaResult:
    """Computed karana details."""

    number: int
    name: str
    start_degree: float
    end_degree: float


@dataclass
class VaraResult:
    """Computed vara (weekday) details."""

    number: int
    name: str


@dataclass
class PanchangaResult:
    """Computed panchanga elements."""

    tithi: TithiResult
    karana: KaranaResult
    vara: VaraResult
    yoga_name: str
    yoga_number: int


@dataclass
class PanchangaDataResult:
    """Panchanga with reference data attached."""

    panchanga: PanchangaResult
    tithi_data: Tithi | None
    karana_data: Karana | None
    vara_data: Vara | None
    yoga_data: Yoga | None
    muhurta_rating: float | None


@dataclass
class PanchangaActivitySupport:
    """Activity support breakdown for panchanga elements."""

    activity: str
    tithi_support: bool
    karana_support: bool
    vara_support: bool
    yoga_support: bool
    inauspicious_flags: list[str]


@dataclass
class PanchangaSummary:
    """Flattened panchanga summary for clients."""

    tithi_name: str
    tithi_number: int
    karana_name: str
    karana_number: int
    vara_name: str
    vara_number: int
    yoga_name: str
    yoga_number: int
    muhurta_rating: float | None
    auspicious_for: list[str]
    inauspicious_for: list[str]
    interpretations: dict[str, str]
    nakshatra_compatibility: dict[str, list[str]]
    activity_support: PanchangaActivitySupport | None


@dataclass
class TimeWindow:
    """Represents a time window for a muhurta."""

    name: str
    start: datetime
    end: datetime


def _get_phase_degrees(sun_longitude: float, moon_longitude: float) -> float:
    return normalize_degree(moon_longitude - sun_longitude)


def get_tithi_number(sun_longitude: float, moon_longitude: float) -> int:
    """Return tithi number (1-30) from Sun/Moon longitudes."""
    phase = _get_phase_degrees(sun_longitude, moon_longitude)
    return int(phase / TITHI_DEGREES) + 1


def get_tithi_result(sun_longitude: float, moon_longitude: float) -> TithiResult:
    """Return detailed tithi information."""
    phase = _get_phase_degrees(sun_longitude, moon_longitude)
    number = int(phase / TITHI_DEGREES) + 1
    name = TITHI_NAMES[number - 1] if 1 <= number <= TITHI_COUNT else "Unknown"
    paksha = "shukla" if number <= PAKSHA_DIVIDER else "krishna"
    start_degree = (number - 1) * TITHI_DEGREES
    end_degree = number * TITHI_DEGREES

    return TithiResult(
        number=number,
        name=name,
        paksha=paksha,
        phase_degrees=phase,
        start_degree=start_degree,
        end_degree=end_degree,
    )


def _karana_sequence() -> list[str]:
    sequence = ["Kimstughna"]
    sequence.extend(MOVABLE_KARANAS * 8)
    sequence.extend(FIXED_KARANAS)
    return sequence[:KARANA_COUNT]


def get_karana_result(sun_longitude: float, moon_longitude: float) -> KaranaResult:
    """Return karana details from Sun/Moon longitudes."""
    phase = _get_phase_degrees(sun_longitude, moon_longitude)
    karana_index = int(phase / KARANA_DEGREES) + 1
    sequence = _karana_sequence()
    name = sequence[karana_index - 1] if 1 <= karana_index <= KARANA_COUNT else "Unknown"
    start_degree = (karana_index - 1) * KARANA_DEGREES
    end_degree = karana_index * KARANA_DEGREES

    return KaranaResult(
        number=karana_index,
        name=name,
        start_degree=start_degree,
        end_degree=end_degree,
    )


def get_vara_number_from_weekday(weekday_index: int) -> int:
    """Convert Python weekday (Mon=0..Sun=6) to vara number (Sun=1..Sat=7)."""
    return ((weekday_index + 1) % 7) + 1


def get_vara_result(*, weekday_index: int | None = None, date_value: datetime | None = None) -> VaraResult:
    """Return vara (weekday) details.

    Provide either weekday_index (Mon=0..Sun=6) or date_value.
    """
    if date_value is not None:
        weekday_index = date_value.weekday()
    if weekday_index is None:
        raise MissingWeekdayError

    number = get_vara_number_from_weekday(weekday_index)
    name = VARA_NAMES[number - 1]

    return VaraResult(number=number, name=name)


def get_vara_result_from_datetime(
    date_value: datetime,
    *,
    require_timezone: bool = False,
) -> VaraResult:
    """Return vara from a datetime, with optional timezone requirement."""
    if require_timezone and date_value.tzinfo is None:
        raise MissingTimezoneError
    return get_vara_result(date_value=date_value)


def _average_muhurta_rating(values: list[int | None]) -> float | None:
    ratings = [value for value in values if value is not None]
    if not ratings:
        return None
    return sum(ratings) / len(ratings)


def _get_muhurta_rating(obj: object | None) -> int | None:
    if obj is None:
        return None
    value = getattr(obj, "muhurta_rating", None)
    return value if isinstance(value, int) else None


def _get_list_field(obj: object | None, field_name: str) -> list[str]:
    if obj is None:
        return []
    value = getattr(obj, field_name, None)
    return value if isinstance(value, list) else []


def _ensure_timezone(*, require_timezone: bool, sunrise: datetime, sunset: datetime) -> None:
    if require_timezone and (sunrise.tzinfo is None or sunset.tzinfo is None):
        raise MissingTimezoneError


def _segment_minutes(sunrise: datetime, sunset: datetime) -> float:
    duration = sunset - sunrise
    return duration.total_seconds() / 60.0 / DAY_SEGMENTS


def _segment_minutes_for_window(start: datetime, end: datetime, segments: int) -> float:
    duration = end - start
    return duration.total_seconds() / 60.0 / segments


def _segment_window(
    *,
    name: str,
    sunrise: datetime,
    segment_index: int,
    segment_minutes: float,
) -> TimeWindow:
    start = sunrise + datetime_module.timedelta(minutes=segment_minutes * (segment_index - 1))
    end = start + datetime_module.timedelta(minutes=segment_minutes)
    return TimeWindow(name=name, start=start, end=end)


def get_day_segments(
    *,
    sunrise: datetime,
    sunset: datetime,
    require_timezone: bool = False,
) -> list[TimeWindow]:
    """Return 8 equal day segments from sunrise to sunset."""
    _ensure_timezone(require_timezone=require_timezone, sunrise=sunrise, sunset=sunset)
    minutes = _segment_minutes(sunrise, sunset)
    return [
        _segment_window(
            name=f"day_segment_{index}",
            sunrise=sunrise,
            segment_index=index,
            segment_minutes=minutes,
        )
        for index in range(1, DAY_SEGMENTS + 1)
    ]


def get_night_segments(
    *,
    sunset: datetime,
    next_sunrise: datetime,
    require_timezone: bool = False,
) -> list[TimeWindow]:
    """Return 8 equal night segments from sunset to next sunrise."""
    if require_timezone and (sunset.tzinfo is None or next_sunrise.tzinfo is None):
        raise MissingTimezoneError
    minutes = _segment_minutes_for_window(sunset, next_sunrise, NIGHT_SEGMENTS)
    return [
        TimeWindow(
            name=f"night_segment_{index}",
            start=sunset + datetime_module.timedelta(minutes=minutes * (index - 1)),
            end=sunset + datetime_module.timedelta(minutes=minutes * index),
        )
        for index in range(1, NIGHT_SEGMENTS + 1)
    ]


def _muhurta_minutes(start: datetime, end: datetime) -> float:
    return _segment_minutes_for_window(start, end, MUHURTA_COUNT)


def get_abhijit_muhurta(
    *,
    sunrise: datetime,
    sunset: datetime,
    date_value: datetime | None = None,
    exclude_wednesday: bool = False,
    require_timezone: bool = False,
) -> TimeWindow | None:
    """Return Abhijit muhurta window (midday)."""
    _ensure_timezone(require_timezone=require_timezone, sunrise=sunrise, sunset=sunset)
    if exclude_wednesday:
        vara_number = _get_vara_number(weekday_index=None, date_value=date_value)
        if vara_number == WEDNESDAY_VARA:
            return None

    minutes = _muhurta_minutes(sunrise, sunset)
    start = sunrise + datetime_module.timedelta(minutes=minutes * 7)
    end = sunrise + datetime_module.timedelta(minutes=minutes * 8)
    return TimeWindow(name="abhijit_muhurta", start=start, end=end)


def get_brahma_muhurta(
    *,
    sunset: datetime,
    next_sunrise: datetime,
    require_timezone: bool = False,
) -> TimeWindow:
    """Return Brahma muhurta window (last two muhurtas before sunrise)."""
    if require_timezone and (sunset.tzinfo is None or next_sunrise.tzinfo is None):
        raise MissingTimezoneError
    minutes = _muhurta_minutes(sunset, next_sunrise)
    start = next_sunrise - datetime_module.timedelta(minutes=minutes * 2)
    end = next_sunrise
    return TimeWindow(name="brahma_muhurta", start=start, end=end)


def _get_vara_number(*, weekday_index: int | None, date_value: datetime | None) -> int:
    if date_value is not None:
        weekday_index = date_value.weekday()
    if weekday_index is None:
        raise MissingWeekdayError
    return get_vara_number_from_weekday(weekday_index)


RAHU_SEGMENT_BY_VARA = {
    1: 8,
    2: 2,
    3: 7,
    4: 5,
    5: 6,
    6: 4,
    7: 3,
}
YAMA_SEGMENT_BY_VARA = {
    1: 5,
    2: 4,
    3: 3,
    4: 2,
    5: 1,
    6: 7,
    7: 6,
}
GULIKA_SEGMENT_BY_VARA = {
    1: 7,
    2: 6,
    3: 5,
    4: 4,
    5: 3,
    6: 2,
    7: 1,
}


def calculate_panchanga(
    sun_longitude: float,
    moon_longitude: float,
    *,
    weekday_index: int | None = None,
    date_value: datetime | None = None,
) -> PanchangaResult:
    """Compute panchanga elements for given longitudes and weekday."""
    tithi = get_tithi_result(sun_longitude, moon_longitude)
    karana = get_karana_result(sun_longitude, moon_longitude)
    vara = get_vara_result(weekday_index=weekday_index, date_value=date_value)
    yoga = calculate_nitya_yoga(sun_longitude, moon_longitude)

    return PanchangaResult(
        tithi=tithi,
        karana=karana,
        vara=vara,
        yoga_name=yoga.name,
        yoga_number=yoga.number,
    )


def calculate_panchanga_from_datetime(
    sun_longitude: float,
    moon_longitude: float,
    *,
    date_value: datetime,
    require_timezone: bool = False,
) -> PanchangaResult:
    """Compute panchanga elements using a datetime for weekday resolution."""
    if require_timezone and date_value.tzinfo is None:
        raise MissingTimezoneError
    return calculate_panchanga(
        sun_longitude,
        moon_longitude,
        date_value=date_value,
    )


def get_panchanga_with_data(
    sun_longitude: float,
    moon_longitude: float,
    *,
    weekday_index: int | None = None,
    date_value: datetime | None = None,
) -> PanchangaDataResult:
    """Compute panchanga elements and attach reference data from JSON."""
    panchanga = calculate_panchanga(
        sun_longitude,
        moon_longitude,
        weekday_index=weekday_index,
        date_value=date_value,
    )

    loader = AstroDataLoader()
    tithi_data = loader.get_tithi_by_number(panchanga.tithi.number)
    karana_data = loader.get_karana_by_number(panchanga.karana.number)
    vara_data = loader.get_vara_by_number(panchanga.vara.number)
    yoga_data = loader.get_yoga_by_number(panchanga.yoga_number)

    muhurta_rating = _average_muhurta_rating(
        [
            _get_muhurta_rating(tithi_data),
            _get_muhurta_rating(karana_data),
            _get_muhurta_rating(vara_data),
            _get_muhurta_rating(yoga_data),
        ]
    )

    return PanchangaDataResult(
        panchanga=panchanga,
        tithi_data=tithi_data,
        karana_data=karana_data,
        vara_data=vara_data,
        yoga_data=yoga_data,
        muhurta_rating=muhurta_rating,
    )


def get_panchanga_interpretations(panchanga_data: PanchangaDataResult) -> dict[str, str]:
    """Return short interpretation strings for each panchanga element."""
    tithi = panchanga_data.tithi_data
    karana = panchanga_data.karana_data
    vara = panchanga_data.vara_data
    yoga = panchanga_data.yoga_data

    return {
        "tithi": tithi.description if tithi and tithi.description else "",
        "karana": karana.description if karana and karana.description else "",
        "vara": vara.description if vara and vara.description else "",
        "yoga": yoga.description if yoga and yoga.description else "",
    }


def get_nakshatra_compatibility(panchanga_data: PanchangaDataResult) -> dict[str, list[str]]:
    """Return nakshatra compatibility lists for tithi and vara."""
    return {
        "tithi": _get_list_field(panchanga_data.tithi_data, "nakshatra_compatibility"),
        "vara": _get_list_field(panchanga_data.vara_data, "nakshatra_compatibility"),
    }


def calculate_auspicious_score(panchanga_data: PanchangaDataResult) -> float | None:
    """Compute a combined auspicious score from panchanga data."""
    if panchanga_data.muhurta_rating is None:
        return None

    auspicious_count = sum(
        len(_get_list_field(data, "auspicious_for"))
        for data in (
            panchanga_data.tithi_data,
            panchanga_data.karana_data,
            panchanga_data.vara_data,
            panchanga_data.yoga_data,
        )
    )
    inauspicious_count = sum(
        len(_get_list_field(data, "inauspicious_for"))
        for data in (
            panchanga_data.tithi_data,
            panchanga_data.karana_data,
            panchanga_data.vara_data,
            panchanga_data.yoga_data,
        )
    )

    list_score = auspicious_count - inauspicious_count
    return (panchanga_data.muhurta_rating * MUHURTA_WEIGHT) + (list_score * LIST_WEIGHT)


def get_activity_support(
    panchanga_data: PanchangaDataResult,
    *,
    activity: str,
) -> PanchangaActivitySupport:
    """Determine activity support across panchanga elements."""
    activity_lower = activity.strip().lower()

    tithi_a = [item.lower() for item in _get_list_field(panchanga_data.tithi_data, "auspicious_for")]
    karana_a = [item.lower() for item in _get_list_field(panchanga_data.karana_data, "auspicious_for")]
    vara_a = [item.lower() for item in _get_list_field(panchanga_data.vara_data, "auspicious_for")]
    yoga_a = [item.lower() for item in _get_list_field(panchanga_data.yoga_data, "auspicious_for")]

    tithi_i = [item.lower() for item in _get_list_field(panchanga_data.tithi_data, "inauspicious_for")]
    karana_i = [item.lower() for item in _get_list_field(panchanga_data.karana_data, "inauspicious_for")]
    vara_i = [item.lower() for item in _get_list_field(panchanga_data.vara_data, "inauspicious_for")]
    yoga_i = [item.lower() for item in _get_list_field(panchanga_data.yoga_data, "inauspicious_for")]

    inauspicious_flags = []
    if activity_lower in tithi_i:
        inauspicious_flags.append("tithi")
    if activity_lower in karana_i:
        inauspicious_flags.append("karana")
    if activity_lower in vara_i:
        inauspicious_flags.append("vara")
    if activity_lower in yoga_i:
        inauspicious_flags.append("yoga")

    return PanchangaActivitySupport(
        activity=activity,
        tithi_support=activity_lower in tithi_a,
        karana_support=activity_lower in karana_a,
        vara_support=activity_lower in vara_a,
        yoga_support=activity_lower in yoga_a,
        inauspicious_flags=inauspicious_flags,
    )


def build_panchanga_summary(
    panchanga_data: PanchangaDataResult,
    *,
    activity: str | None = None,
) -> PanchangaSummary:
    """Build a flattened panchanga summary for clients."""
    auspicious_for = (
        _get_list_field(panchanga_data.tithi_data, "auspicious_for")
        + _get_list_field(panchanga_data.karana_data, "auspicious_for")
        + _get_list_field(panchanga_data.vara_data, "auspicious_for")
        + _get_list_field(panchanga_data.yoga_data, "auspicious_for")
    )
    inauspicious_for = (
        _get_list_field(panchanga_data.tithi_data, "inauspicious_for")
        + _get_list_field(panchanga_data.karana_data, "inauspicious_for")
        + _get_list_field(panchanga_data.vara_data, "inauspicious_for")
        + _get_list_field(panchanga_data.yoga_data, "inauspicious_for")
    )

    activity_support = get_activity_support(panchanga_data, activity=activity) if activity else None

    return PanchangaSummary(
        tithi_name=panchanga_data.panchanga.tithi.name,
        tithi_number=panchanga_data.panchanga.tithi.number,
        karana_name=panchanga_data.panchanga.karana.name,
        karana_number=panchanga_data.panchanga.karana.number,
        vara_name=panchanga_data.panchanga.vara.name,
        vara_number=panchanga_data.panchanga.vara.number,
        yoga_name=panchanga_data.panchanga.yoga_name,
        yoga_number=panchanga_data.panchanga.yoga_number,
        muhurta_rating=panchanga_data.muhurta_rating,
        auspicious_for=auspicious_for,
        inauspicious_for=inauspicious_for,
        interpretations=get_panchanga_interpretations(panchanga_data),
        nakshatra_compatibility=get_nakshatra_compatibility(panchanga_data),
        activity_support=activity_support,
    )


def get_rahu_kalam(
    *,
    sunrise: datetime,
    sunset: datetime,
    weekday_index: int | None = None,
    date_value: datetime | None = None,
    require_timezone: bool = False,
) -> TimeWindow:
    """Calculate Rahu Kalam window for the given date."""
    _ensure_timezone(require_timezone=require_timezone, sunrise=sunrise, sunset=sunset)
    vara_number = _get_vara_number(weekday_index=weekday_index, date_value=date_value)
    segment = RAHU_SEGMENT_BY_VARA[vara_number]
    minutes = _segment_minutes(sunrise, sunset)
    return _segment_window(name="rahu_kalam", sunrise=sunrise, segment_index=segment, segment_minutes=minutes)


def get_yamagandam(
    *,
    sunrise: datetime,
    sunset: datetime,
    weekday_index: int | None = None,
    date_value: datetime | None = None,
    require_timezone: bool = False,
) -> TimeWindow:
    """Calculate Yamagandam window for the given date."""
    _ensure_timezone(require_timezone=require_timezone, sunrise=sunrise, sunset=sunset)
    vara_number = _get_vara_number(weekday_index=weekday_index, date_value=date_value)
    segment = YAMA_SEGMENT_BY_VARA[vara_number]
    minutes = _segment_minutes(sunrise, sunset)
    return _segment_window(name="yamagandam", sunrise=sunrise, segment_index=segment, segment_minutes=minutes)


def get_gulika(
    *,
    sunrise: datetime,
    sunset: datetime,
    weekday_index: int | None = None,
    date_value: datetime | None = None,
    require_timezone: bool = False,
) -> TimeWindow:
    """Calculate Gulika (Kuliga/Maandi) window for the given date."""
    _ensure_timezone(require_timezone=require_timezone, sunrise=sunrise, sunset=sunset)
    vara_number = _get_vara_number(weekday_index=weekday_index, date_value=date_value)
    segment = GULIKA_SEGMENT_BY_VARA[vara_number]
    minutes = _segment_minutes(sunrise, sunset)
    return _segment_window(name="gulika", sunrise=sunrise, segment_index=segment, segment_minutes=minutes)


def get_inauspicious_timings(
    *,
    sunrise: datetime,
    sunset: datetime,
    weekday_index: int | None = None,
    date_value: datetime | None = None,
    require_timezone: bool = False,
) -> dict[str, TimeWindow]:
    """Return inauspicious day-time windows for the given date."""
    rahu = get_rahu_kalam(
        sunrise=sunrise,
        sunset=sunset,
        weekday_index=weekday_index,
        date_value=date_value,
        require_timezone=require_timezone,
    )
    yama = get_yamagandam(
        sunrise=sunrise,
        sunset=sunset,
        weekday_index=weekday_index,
        date_value=date_value,
        require_timezone=require_timezone,
    )
    gulika = get_gulika(
        sunrise=sunrise,
        sunset=sunset,
        weekday_index=weekday_index,
        date_value=date_value,
        require_timezone=require_timezone,
    )

    return {
        "rahu_kalam": rahu,
        "yamagandam": yama,
        "yamakanda": yama,
        "gulika": gulika,
        "kuliga": gulika,
        "maandi": gulika,
    }
