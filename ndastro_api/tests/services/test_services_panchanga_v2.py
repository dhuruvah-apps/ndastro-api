"""Extended tests for ndastro_api.services.panchanga - timing windows and complex functions."""

import datetime

import pytest

from ndastro_api.services.panchanga import (
    MissingTimezoneError,
    MissingWeekdayError,
    PanchangaActivitySupport,
    PanchangaDataResult,
    PanchangaResult,
    PanchangaSummary,
    TimeWindow,
    build_panchanga_summary,
    calculate_auspicious_score,
    calculate_panchanga,
    calculate_panchanga_from_datetime,
    get_abhijit_muhurta,
    get_activity_support,
    get_brahma_muhurta,
    get_day_segments,
    get_gulika,
    get_inauspicious_timings,
    get_nakshatra_compatibility,
    get_night_segments,
    get_panchanga_interpretations,
    get_panchanga_with_data,
    get_rahu_kalam,
    get_vara_result_from_datetime,
    get_yamagandam,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_SUN = 60.0  # Taurus
_MOON = 120.0  # Cancer
_WEEKDAY = 0  # Monday (Python weekday)

_SUNRISE = datetime.datetime(2024, 1, 15, 6, 30, 0)
_SUNSET = datetime.datetime(2024, 1, 15, 18, 0, 0)
_NEXT_SUNRISE = datetime.datetime(2024, 1, 16, 6, 31, 0)

_SUNRISE_TZ = datetime.datetime(2024, 1, 15, 6, 30, 0, tzinfo=datetime.timezone.utc)
_SUNSET_TZ = datetime.datetime(2024, 1, 15, 18, 0, 0, tzinfo=datetime.timezone.utc)
_NEXT_SUNRISE_TZ = datetime.datetime(2024, 1, 16, 6, 31, 0, tzinfo=datetime.timezone.utc)


# ---------------------------------------------------------------------------
# calculate_panchanga
# ---------------------------------------------------------------------------


def test_calculate_panchanga_with_weekday_index():
    result = calculate_panchanga(_SUN, _MOON, weekday_index=_WEEKDAY)
    assert isinstance(result, PanchangaResult)
    assert result.tithi is not None
    assert result.karana is not None
    assert result.vara is not None


def test_calculate_panchanga_with_date_value():
    date = datetime.datetime(2024, 1, 15)
    result = calculate_panchanga(_SUN, _MOON, date_value=date)
    assert isinstance(result, PanchangaResult)


def test_calculate_panchanga_no_weekday_raises():
    with pytest.raises(MissingWeekdayError):
        calculate_panchanga(_SUN, _MOON)  # Neither weekday_index nor date_value


def test_calculate_panchanga_yoga_name_and_number():
    result = calculate_panchanga(_SUN, _MOON, weekday_index=0)
    assert isinstance(result.yoga_name, str)
    assert 1 <= result.yoga_number <= 27


# ---------------------------------------------------------------------------
# calculate_panchanga_from_datetime
# ---------------------------------------------------------------------------


def test_calculate_panchanga_from_datetime_basic():
    date = datetime.datetime(2024, 3, 15, 12, 0, 0, tzinfo=datetime.timezone.utc)
    result = calculate_panchanga_from_datetime(_SUN, _MOON, date_value=date)
    assert isinstance(result, PanchangaResult)


def test_calculate_panchanga_from_datetime_no_tz_ok_without_require():
    date = datetime.datetime(2024, 3, 15, 12, 0, 0)
    result = calculate_panchanga_from_datetime(_SUN, _MOON, date_value=date, require_timezone=False)
    assert isinstance(result, PanchangaResult)


def test_calculate_panchanga_from_datetime_require_timezone_raises():
    date = datetime.datetime(2024, 3, 15, 12, 0, 0)  # no tzinfo
    with pytest.raises(MissingTimezoneError):
        calculate_panchanga_from_datetime(_SUN, _MOON, date_value=date, require_timezone=True)


# ---------------------------------------------------------------------------
# get_panchanga_with_data
# ---------------------------------------------------------------------------


def test_get_panchanga_with_data_weekday():
    result = get_panchanga_with_data(336.78, 11.02, weekday_index=0)
    assert isinstance(result, PanchangaDataResult)
    assert result.panchanga is not None


def test_get_panchanga_with_data_has_muhurta_rating():
    result = get_panchanga_with_data(_SUN, _MOON, weekday_index=3)
    # muhurta_rating may be None or a float
    assert result.muhurta_rating is None or isinstance(result.muhurta_rating, float)


def test_get_panchanga_with_data_from_date():
    date = datetime.datetime(2024, 4, 10)
    result = get_panchanga_with_data(_SUN, _MOON, date_value=date)
    assert isinstance(result, PanchangaDataResult)


# ---------------------------------------------------------------------------
# get_panchanga_interpretations
# ---------------------------------------------------------------------------


def test_get_panchanga_interpretations_returns_dict():
    pd_result = get_panchanga_with_data(_SUN, _MOON, weekday_index=0)
    interp = get_panchanga_interpretations(pd_result)
    assert isinstance(interp, dict)
    assert "tithi" in interp
    assert "karana" in interp
    assert "vara" in interp
    assert "yoga" in interp


def test_get_panchanga_interpretations_strings():
    pd_result = get_panchanga_with_data(_SUN, _MOON, weekday_index=1)
    interp = get_panchanga_interpretations(pd_result)
    for key, val in interp.items():
        assert isinstance(val, str)


# ---------------------------------------------------------------------------
# get_nakshatra_compatibility
# ---------------------------------------------------------------------------


def test_get_nakshatra_compatibility_returns_dict():
    pd_result = get_panchanga_with_data(_SUN, _MOON, weekday_index=0)
    compat = get_nakshatra_compatibility(pd_result)
    assert isinstance(compat, dict)
    assert "tithi" in compat
    assert "vara" in compat


# ---------------------------------------------------------------------------
# calculate_auspicious_score
# ---------------------------------------------------------------------------


def test_calculate_auspicious_score_returns_value_or_none():
    pd_result = get_panchanga_with_data(_SUN, _MOON, weekday_index=0)
    score = calculate_auspicious_score(pd_result)
    assert score is None or isinstance(score, float)


def test_calculate_auspicious_score_none_when_no_muhurta():
    # Create a fake PanchangaDataResult with muhurta_rating=None
    panchanga = calculate_panchanga(_SUN, _MOON, weekday_index=0)
    pd_result = PanchangaDataResult(
        panchanga=panchanga,
        tithi_data=None,
        karana_data=None,
        vara_data=None,
        yoga_data=None,
        muhurta_rating=None,
    )
    score = calculate_auspicious_score(pd_result)
    assert score is None


# ---------------------------------------------------------------------------
# get_activity_support
# ---------------------------------------------------------------------------


def test_get_activity_support_returns_support_object():
    pd_result = get_panchanga_with_data(_SUN, _MOON, weekday_index=0)
    support = get_activity_support(pd_result, activity="travel")
    assert isinstance(support, PanchangaActivitySupport)
    assert support.activity == "travel"
    assert isinstance(support.inauspicious_flags, list)


def test_get_activity_support_with_all_none_data():
    panchanga = calculate_panchanga(_SUN, _MOON, weekday_index=0)
    pd_result = PanchangaDataResult(
        panchanga=panchanga,
        tithi_data=None,
        karana_data=None,
        vara_data=None,
        yoga_data=None,
        muhurta_rating=None,
    )
    support = get_activity_support(pd_result, activity="marriage")
    assert support.tithi_support is False
    assert support.karana_support is False


# ---------------------------------------------------------------------------
# build_panchanga_summary
# ---------------------------------------------------------------------------


def test_build_panchanga_summary_returns_summary():
    pd_result = get_panchanga_with_data(_SUN, _MOON, weekday_index=0)
    summary = build_panchanga_summary(pd_result)
    assert isinstance(summary, PanchangaSummary)
    assert isinstance(summary.tithi_name, str)
    assert isinstance(summary.vara_name, str)


def test_build_panchanga_summary_with_activity():
    pd_result = get_panchanga_with_data(_SUN, _MOON, weekday_index=2)
    summary = build_panchanga_summary(pd_result, activity="travel")
    assert summary.activity_support is not None


def test_build_panchanga_summary_without_activity():
    pd_result = get_panchanga_with_data(_SUN, _MOON, weekday_index=2)
    summary = build_panchanga_summary(pd_result, activity=None)
    assert summary.activity_support is None


# ---------------------------------------------------------------------------
# get_vara_result_from_datetime
# ---------------------------------------------------------------------------


def test_get_vara_result_from_datetime_without_timezone():
    date = datetime.datetime(2024, 1, 15)  # Monday
    result = get_vara_result_from_datetime(date)
    assert result.name == "Monday"


def test_get_vara_result_from_datetime_with_timezone():
    date = datetime.datetime(2024, 1, 14, tzinfo=datetime.timezone.utc)  # Sunday
    result = get_vara_result_from_datetime(date, require_timezone=True)
    assert result.name == "Sunday"


def test_get_vara_result_from_datetime_require_tz_raises():
    date = datetime.datetime(2024, 1, 15)  # no tzinfo
    with pytest.raises(MissingTimezoneError):
        get_vara_result_from_datetime(date, require_timezone=True)


# ---------------------------------------------------------------------------
# get_day_segments
# ---------------------------------------------------------------------------


def test_get_day_segments_returns_8():
    segments = get_day_segments(sunrise=_SUNRISE, sunset=_SUNSET)
    assert len(segments) == 8


def test_get_day_segments_all_time_windows():
    segments = get_day_segments(sunrise=_SUNRISE, sunset=_SUNSET)
    for seg in segments:
        assert isinstance(seg, TimeWindow)
        assert seg.start < seg.end


def test_get_day_segments_require_timezone_no_tz_raises():
    with pytest.raises(MissingTimezoneError):
        get_day_segments(sunrise=_SUNRISE, sunset=_SUNSET, require_timezone=True)


def test_get_day_segments_with_timezone():
    segments = get_day_segments(sunrise=_SUNRISE_TZ, sunset=_SUNSET_TZ)
    assert len(segments) == 8


# ---------------------------------------------------------------------------
# get_night_segments
# ---------------------------------------------------------------------------


def test_get_night_segments_returns_8():
    segments = get_night_segments(sunset=_SUNSET, next_sunrise=_NEXT_SUNRISE)
    assert len(segments) == 8


def test_get_night_segments_all_time_windows():
    segments = get_night_segments(sunset=_SUNSET, next_sunrise=_NEXT_SUNRISE)
    for seg in segments:
        assert isinstance(seg, TimeWindow)
        assert seg.start < seg.end


def test_get_night_segments_require_timezone_no_tz_raises():
    with pytest.raises(MissingTimezoneError):
        get_night_segments(sunset=_SUNSET, next_sunrise=_NEXT_SUNRISE, require_timezone=True)


# ---------------------------------------------------------------------------
# get_abhijit_muhurta
# ---------------------------------------------------------------------------


def test_get_abhijit_muhurta_returns_window():
    window = get_abhijit_muhurta(sunrise=_SUNRISE, sunset=_SUNSET)
    assert isinstance(window, TimeWindow)
    assert window.name == "abhijit_muhurta"


def test_get_abhijit_muhurta_not_wednesday():
    # Jan 15, 2024 is a Monday → not excluded
    window = get_abhijit_muhurta(
        sunrise=_SUNRISE,
        sunset=_SUNSET,
        date_value=datetime.datetime(2024, 1, 15),
        exclude_wednesday=True,
    )
    assert isinstance(window, TimeWindow)


def test_get_abhijit_muhurta_wednesday_excluded():
    # Find a Wednesday: Jan 17, 2024 is Wednesday
    window = get_abhijit_muhurta(
        sunrise=_SUNRISE,
        sunset=_SUNSET,
        date_value=datetime.datetime(2024, 1, 17),
        exclude_wednesday=True,
    )
    assert window is None


def test_get_abhijit_muhurta_require_timezone_raises():
    with pytest.raises(MissingTimezoneError):
        get_abhijit_muhurta(sunrise=_SUNRISE, sunset=_SUNSET, require_timezone=True)


# ---------------------------------------------------------------------------
# get_brahma_muhurta
# ---------------------------------------------------------------------------


def test_get_brahma_muhurta_returns_window():
    window = get_brahma_muhurta(sunset=_SUNSET, next_sunrise=_NEXT_SUNRISE)
    assert isinstance(window, TimeWindow)
    assert window.name == "brahma_muhurta"


def test_get_brahma_muhurta_require_timezone_raises():
    with pytest.raises(MissingTimezoneError):
        get_brahma_muhurta(sunset=_SUNSET, next_sunrise=_NEXT_SUNRISE, require_timezone=True)


# ---------------------------------------------------------------------------
# get_rahu_kalam
# ---------------------------------------------------------------------------


def test_get_rahu_kalam_returns_window():
    result = get_rahu_kalam(sunrise=_SUNRISE, sunset=_SUNSET, weekday_index=0)
    assert isinstance(result, TimeWindow)
    assert result.name == "rahu_kalam"


def test_get_rahu_kalam_all_weekdays():
    for weekday in range(7):
        result = get_rahu_kalam(sunrise=_SUNRISE, sunset=_SUNSET, weekday_index=weekday)
        assert isinstance(result, TimeWindow)


def test_get_rahu_kalam_require_timezone_raises():
    with pytest.raises(MissingTimezoneError):
        get_rahu_kalam(sunrise=_SUNRISE, sunset=_SUNSET, weekday_index=0, require_timezone=True)


# ---------------------------------------------------------------------------
# get_yamagandam
# ---------------------------------------------------------------------------


def test_get_yamagandam_returns_window():
    result = get_yamagandam(sunrise=_SUNRISE, sunset=_SUNSET, weekday_index=1)
    assert isinstance(result, TimeWindow)
    assert result.name == "yamagandam"


def test_get_yamagandam_all_weekdays():
    for weekday in range(7):
        result = get_yamagandam(sunrise=_SUNRISE, sunset=_SUNSET, weekday_index=weekday)
        assert isinstance(result, TimeWindow)


# ---------------------------------------------------------------------------
# get_gulika
# ---------------------------------------------------------------------------


def test_get_gulika_returns_window():
    result = get_gulika(sunrise=_SUNRISE, sunset=_SUNSET, weekday_index=2)
    assert isinstance(result, TimeWindow)
    assert result.name == "gulika"


def test_get_gulika_all_weekdays():
    for weekday in range(7):
        result = get_gulika(sunrise=_SUNRISE, sunset=_SUNSET, weekday_index=weekday)
        assert isinstance(result, TimeWindow)


# ---------------------------------------------------------------------------
# get_inauspicious_timings
# ---------------------------------------------------------------------------


def test_get_inauspicious_timings_returns_dict():
    result = get_inauspicious_timings(sunrise=_SUNRISE, sunset=_SUNSET, weekday_index=3)
    assert isinstance(result, dict)
    assert "rahu_kalam" in result
    assert "yamagandam" in result
    assert "gulika" in result


def test_get_inauspicious_timings_from_date():
    date = datetime.datetime(2024, 1, 15)
    result = get_inauspicious_timings(sunrise=_SUNRISE, sunset=_SUNSET, date_value=date)
    assert "rahu_kalam" in result


def test_get_inauspicious_timings_aliases():
    result = get_inauspicious_timings(sunrise=_SUNRISE, sunset=_SUNSET, weekday_index=0)
    # yamakanda is alias for yamagandam
    assert "yamakanda" in result
    assert "kuliga" in result


# ---------------------------------------------------------------------------
# MissingWeekdayError and MissingTimezoneError
# ---------------------------------------------------------------------------


def test_missing_weekday_error_message():
    err = MissingWeekdayError()
    assert "weekday_index" in str(err)


def test_missing_timezone_error_message():
    err = MissingTimezoneError()
    assert "tzinfo" in str(err)
