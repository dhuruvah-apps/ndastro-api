"""Unit tests for ndastro_api.services.utils."""

import pytest

from ndastro_api.services.utils import (
    compute_offset,
    dms_to_decimal,
    normalize_degree,
    normalize_rasi_house,
    sign,
)

# ---------------------------------------------------------------------------
# sign()
# ---------------------------------------------------------------------------


def test_sign_positive():
    assert sign(10) == 1


def test_sign_negative():
    assert sign(-5) == -1


def test_sign_zero():
    assert sign(0) == 1  # 0 is non-negative → 1


# ---------------------------------------------------------------------------
# dms_to_decimal()
# ---------------------------------------------------------------------------


def test_dms_to_decimal_whole_degrees():
    assert dms_to_decimal(90, 0, 0) == pytest.approx(90.0)


def test_dms_to_decimal_with_minutes():
    assert dms_to_decimal(10, 30, 0) == pytest.approx(10.5)


def test_dms_to_decimal_with_seconds():
    assert dms_to_decimal(0, 0, 3600) == pytest.approx(1.0)


def test_dms_to_decimal_combined():
    # 1°30'36" = 1 + 30/60 + 36/3600 = 1.51
    assert dms_to_decimal(1, 30, 36) == pytest.approx(1.51)


# ---------------------------------------------------------------------------
# normalize_degree()
# ---------------------------------------------------------------------------


def test_normalize_degree_positive_within_range():
    assert normalize_degree(180.0) == pytest.approx(180.0)


def test_normalize_degree_zero():
    assert normalize_degree(0.0) == pytest.approx(0.0)


def test_normalize_degree_exactly_360():
    # 360 should not wrap; it stays at 360 (boundary)
    assert normalize_degree(360.0) == pytest.approx(360.0)


def test_normalize_degree_over_360():
    assert normalize_degree(370.0) == pytest.approx(10.0)


def test_normalize_degree_over_720():
    assert normalize_degree(720.0) == pytest.approx(360.0)


def test_normalize_degree_negative():
    assert normalize_degree(-10.0) == pytest.approx(350.0)


# ---------------------------------------------------------------------------
# normalize_rasi_house()
# ---------------------------------------------------------------------------


def test_normalize_rasi_house_within_range():
    assert normalize_rasi_house(6) == 6


def test_normalize_rasi_house_exactly_12():
    assert normalize_rasi_house(12) == 12


def test_normalize_rasi_house_over_12():
    assert normalize_rasi_house(13) == 1


def test_normalize_rasi_house_24():
    assert normalize_rasi_house(24) == 12


def test_normalize_rasi_house_negative():
    assert normalize_rasi_house(-1) == 11


# ---------------------------------------------------------------------------
# compute_offset()
# ---------------------------------------------------------------------------


def test_compute_offset_page_1():
    assert compute_offset(1, 10) == 0


def test_compute_offset_page_2():
    assert compute_offset(2, 10) == 10


def test_compute_offset_page_3():
    assert compute_offset(3, 25) == 50
