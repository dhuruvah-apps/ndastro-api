"""Extended panchanga tests covering private helpers and error branches."""

import datetime as dt

import pytest

from ndastro_api.services.panchanga import (
    MissingTimezoneError,
    MissingWeekdayError,
    _average_muhurta_rating,
    _get_muhurta_rating,
    _get_vara_number,
    get_vara_result,
    get_vara_result_from_datetime,
)

# ---------------------------------------------------------------------------
# _average_muhurta_rating — line 297 (return None when all None)
# ---------------------------------------------------------------------------


def test_average_muhurta_rating_empty_returns_none():
    result = _average_muhurta_rating([])
    assert result is None  # line 297 hit (empty list branch)


def test_average_muhurta_rating_all_none_returns_none():
    result = _average_muhurta_rating([None, None, None])
    assert result is None


def test_average_muhurta_rating_with_values():
    result = _average_muhurta_rating([5, 3, None, 7])
    assert result == pytest.approx(5.0, rel=1e-3)


# ---------------------------------------------------------------------------
# _get_muhurta_rating — line 303 (return None when obj is None)
# ---------------------------------------------------------------------------


def test_get_muhurta_rating_obj_none():
    result = _get_muhurta_rating(None)
    assert result is None  # first None branch hit


def test_get_muhurta_rating_no_attribute():
    # obj without muhurta_rating attribute → getattr returns None → return None
    class Obj:
        pass

    result = _get_muhurta_rating(Obj())
    assert result is None  # line 303 (else branch) hit


def test_get_muhurta_rating_with_rating():
    class ObjWithRating:
        muhurta_rating = 5

    result = _get_muhurta_rating(ObjWithRating())
    assert result == 5


def test_get_muhurta_rating_non_int_attribute():
    class ObjWithStr:
        muhurta_rating = "high"

    result = _get_muhurta_rating(ObjWithStr())
    # "high" is not an int → return None
    assert result is None


# ---------------------------------------------------------------------------
# _get_vara_number — line 426 (raise MissingWeekdayError when both None)
# ---------------------------------------------------------------------------


def test_get_vara_number_both_none_raises():
    with pytest.raises(MissingWeekdayError):
        _get_vara_number(weekday_index=None, date_value=None)


def test_get_vara_number_from_weekday():
    result = _get_vara_number(weekday_index=0, date_value=None)
    assert 1 <= result <= 7


# ---------------------------------------------------------------------------
# get_vara_result_from_datetime — raise MissingTimezoneError (line 290)
# ---------------------------------------------------------------------------


def test_get_vara_result_from_datetime_requires_timezone():
    naive_dt = dt.datetime(2024, 1, 15, 12, 0, 0)
    with pytest.raises(MissingTimezoneError):
        get_vara_result_from_datetime(naive_dt, require_timezone=True)


def test_get_vara_result_from_datetime_without_timezone_ok():
    naive_dt = dt.datetime(2024, 1, 15, 12, 0, 0)
    result = get_vara_result_from_datetime(naive_dt, require_timezone=False)
    assert result.number in range(1, 8)


# ---------------------------------------------------------------------------
# get_vara_result — raise MissingWeekdayError (line 275)
# ---------------------------------------------------------------------------


def test_get_vara_result_no_weekday_no_date_raises():
    with pytest.raises(MissingWeekdayError):
        get_vara_result()
