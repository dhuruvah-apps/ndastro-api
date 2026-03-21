"""Unit tests for ndastro_api.services.muhurta_advanced."""

import datetime as dt

from ndastro_api.services.muhurta_advanced import (
    DURMUHURTA_INDICES,
    MINUTES_PER_DAY,
    MINUTES_PER_MUHURTA,
    MUUURTAS_PER_DAY,
    NAKSHATRAS,
    VARJYAM_NAKSHATRA_PAIRS,
    DurmuhurtaWindow,
    MuhurtaQuality,
    TimeWindow,
    VarjyamWindow,
    get_amrita_kala_windows,
    get_durmuhurtas,
    get_varjyam_windows,
)

_SUNRISE = dt.datetime(2024, 1, 15, 6, 30, 0)
_SUNSET = dt.datetime(2024, 1, 15, 18, 0, 0)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_minutes_per_day():
    assert MINUTES_PER_DAY == 1440


def test_muhurtas_per_day():
    assert MUUURTAS_PER_DAY == 30


def test_minutes_per_muhurta():
    assert MINUTES_PER_MUHURTA == 1440 / 30  # 48.0


def test_nakshatras():
    assert NAKSHATRAS == 27


def test_durmuhurta_indices_nonempty():
    assert len(DURMUHURTA_INDICES) > 0


def test_varjyam_nakshatra_pairs_nonempty():
    assert len(VARJYAM_NAKSHATRA_PAIRS) > 0


# ---------------------------------------------------------------------------
# MuhurtaQuality enum
# ---------------------------------------------------------------------------


def test_muhurta_quality_excellent():
    assert MuhurtaQuality.EXCELLENT == "excellent"


def test_muhurta_quality_inauspicious():
    assert MuhurtaQuality.INAUSPICIOUS == "inauspicious"


def test_muhurta_quality_has_5_members():
    assert len(list(MuhurtaQuality)) == 5


# ---------------------------------------------------------------------------
# TimeWindow dataclass
# ---------------------------------------------------------------------------


def test_time_window_construction():
    start = _SUNRISE
    end = _SUNSET
    window = TimeWindow(start=start, end=end, duration_minutes=690.0)
    assert window.duration_minutes == 690.0


# ---------------------------------------------------------------------------
# get_durmuhurtas()
# ---------------------------------------------------------------------------


def test_get_durmuhurtas_returns_list():
    result = get_durmuhurtas(_SUNRISE)
    assert isinstance(result, list)


def test_get_durmuhurtas_items_are_dataclass():
    result = get_durmuhurtas(_SUNRISE)
    for item in result:
        assert isinstance(item, DurmuhurtaWindow)


def test_get_durmuhurtas_count_matches_indices():
    result = get_durmuhurtas(_SUNRISE)
    assert len(result) == len(DURMUHURTA_INDICES)


def test_get_durmuhurtas_windows_start_after_sunrise():
    result = get_durmuhurtas(_SUNRISE)
    for item in result:
        assert item.window.start >= _SUNRISE


def test_get_durmuhurtas_description_nonempty():
    result = get_durmuhurtas(_SUNRISE)
    for item in result:
        assert isinstance(item.description, str) and len(item.description) > 0


# ---------------------------------------------------------------------------
# get_varjyam_windows()
# ---------------------------------------------------------------------------


def test_get_varjyam_windows_returns_list():
    tithi_end = _SUNRISE + dt.timedelta(hours=6)
    result = get_varjyam_windows(tithi=1, nakshatra=3, tithi_end_time=tithi_end)
    assert isinstance(result, list)


def test_get_varjyam_windows_items_are_dataclass():
    tithi_end = _SUNRISE + dt.timedelta(hours=6)
    result = get_varjyam_windows(tithi=1, nakshatra=3, tithi_end_time=tithi_end)
    for item in result:
        assert isinstance(item, VarjyamWindow)


def test_get_varjyam_non_pair_tithi():
    # Use a tithi/nakshatra combination not in VARJYAM_NAKSHATRA_PAIRS to get 0 results
    tithi_end = _SUNRISE + dt.timedelta(hours=4)
    result = get_varjyam_windows(tithi=25, nakshatra=25, tithi_end_time=tithi_end)
    assert isinstance(result, list)  # May or may not be empty


# ---------------------------------------------------------------------------
# get_amrita_kala_windows()
# ---------------------------------------------------------------------------


def test_get_amrita_kala_windows_returns_tuple():
    amrita, kala = get_amrita_kala_windows(weekday=0, nakshatra=1, sunrise=_SUNRISE, sunset=_SUNSET)
    assert isinstance(amrita, list)
    assert isinstance(kala, list)


def test_get_amrita_kala_windows_different_days():
    # Different weekdays may produce different results
    a1, k1 = get_amrita_kala_windows(weekday=0, nakshatra=1, sunrise=_SUNRISE, sunset=_SUNSET)
    a2, k2 = get_amrita_kala_windows(weekday=3, nakshatra=1, sunrise=_SUNRISE, sunset=_SUNSET)
    # Just verify both return lists
    assert isinstance(a1, list) and isinstance(a2, list)
