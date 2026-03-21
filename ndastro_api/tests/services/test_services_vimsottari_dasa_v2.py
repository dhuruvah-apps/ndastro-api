"""Extended tests for ndastro_api.services.vimsottari_dasa - dasa period calculations."""

import datetime

import pytest

from ndastro_api.services.vimsottari_dasa import (
    DASA_SEQUENCE,
    DASA_YEARS,
    DasaLevel,
    DasaPeriod,
    calculate_current_dasa_period,
    calculate_dasa_change_dates,
    get_dasa_interpretation,
    get_dasa_sequence_from_planet,
)

# ---------------------------------------------------------------------------
# DasaPeriod dataclass
# ---------------------------------------------------------------------------


def test_dasa_period_creation():
    period = DasaPeriod(
        level=DasaLevel.MAHA,
        planet="sun",
        duration_years=6.0,
        start_date=datetime.date(2020, 1, 1),
        end_date=datetime.date(2026, 1, 1),
        percentage_complete=50.0,
    )
    assert period.planet == "sun"
    assert period.level == DasaLevel.MAHA


def test_dasa_period_default_percentage():
    period = DasaPeriod(
        level=DasaLevel.BHUKTI,
        planet="moon",
        duration_years=10.0,
        start_date=datetime.date(2020, 1, 1),
        end_date=datetime.date(2030, 1, 1),
    )
    # Default is 0.0
    assert period.percentage_complete == 0.0


# ---------------------------------------------------------------------------
# calculate_current_dasa_period
# ---------------------------------------------------------------------------


def test_current_dasa_period_returns_result():
    birth_date = datetime.datetime(1985, 6, 15)
    current_date = datetime.datetime(2024, 1, 15)
    result = calculate_current_dasa_period(birth_date, current_date, birth_nakshatra=1)
    assert isinstance(result, DasaPeriod)
    assert result.planet in DASA_SEQUENCE
    assert result.level == DasaLevel.MAHA


def test_current_dasa_period_various_nakshatras():
    birth_date = datetime.datetime(1990, 1, 1)
    current_date = datetime.datetime(2024, 6, 1)
    for nak in range(1, 28):
        result = calculate_current_dasa_period(birth_date, current_date, birth_nakshatra=nak)
        assert result.planet in DASA_SEQUENCE


def test_current_dasa_period_start_end_dates():
    birth_date = datetime.datetime(2000, 1, 1)
    current_date = datetime.datetime(2024, 1, 1)
    result = calculate_current_dasa_period(birth_date, current_date, birth_nakshatra=4)
    assert result.start_date < result.end_date


def test_current_dasa_period_percentage_0_to_100():
    birth_date = datetime.datetime(1995, 3, 20)
    current_date = datetime.datetime(2024, 3, 20)
    result = calculate_current_dasa_period(birth_date, current_date, birth_nakshatra=10)
    if result.percentage_complete is not None:
        assert 0.0 <= result.percentage_complete <= 100.0


def test_current_dasa_period_recent_birth():
    # Very recent birth - should return early dasa
    birth_date = datetime.datetime(2023, 1, 1)
    current_date = datetime.datetime(2024, 1, 1)
    result = calculate_current_dasa_period(birth_date, current_date, birth_nakshatra=1)
    assert isinstance(result, DasaPeriod)


# ---------------------------------------------------------------------------
# get_dasa_sequence_from_planet
# ---------------------------------------------------------------------------


def test_dasa_sequence_from_sun():
    result = get_dasa_sequence_from_planet("sun", levels=1)
    assert len(result) == 1
    assert result[0][0] == "sun"
    assert result[0][1] == DASA_YEARS["sun"]


def test_dasa_sequence_from_invalid_planet():
    result = get_dasa_sequence_from_planet("INVALID_PLANET", levels=3)
    assert result == []


def test_dasa_sequence_from_moon_9_planets():
    result = get_dasa_sequence_from_planet("moon", levels=9)
    assert len(result) == 9
    assert result[0][0] == "moon"


def test_dasa_sequence_wraps_around():
    # If levels > planets remaining, should wrap
    result = get_dasa_sequence_from_planet("kethu", levels=9)
    assert len(result) == 9
    # All planets should be in DASA_SEQUENCE
    for planet, years in result:
        assert planet in DASA_SEQUENCE
        assert years == DASA_YEARS[planet]


def test_dasa_sequence_all_9_from_each():
    for planet in DASA_SEQUENCE:
        result = get_dasa_sequence_from_planet(planet, levels=9)
        assert len(result) == 9


def test_dasa_sequence_exceeds_max_capped_at_9():
    result = get_dasa_sequence_from_planet("sun", levels=20)
    assert len(result) == 9  # min(20, PLANET_COUNT=9)


# ---------------------------------------------------------------------------
# calculate_dasa_change_dates
# ---------------------------------------------------------------------------


def test_dasa_change_dates_returns_list():
    birth_date = datetime.datetime(1990, 6, 15)
    result = calculate_dasa_change_dates(birth_date, birth_nakshatra=7, future_years=20)
    assert isinstance(result, list)
    assert len(result) >= 1


def test_dasa_change_dates_first_entry_is_birth():
    birth_date = datetime.datetime(1990, 6, 15)
    result = calculate_dasa_change_dates(birth_date, birth_nakshatra=7, future_years=20)
    assert result[0]["start_date"] == birth_date.date()


def test_dasa_change_dates_all_have_required_keys():
    birth_date = datetime.datetime(2000, 1, 1)
    result = calculate_dasa_change_dates(birth_date, birth_nakshatra=1, future_years=50)
    for entry in result:
        assert "planet" in entry
        assert "start_date" in entry
        assert "end_date" in entry
        assert "duration_years" in entry


def test_dasa_change_dates_planets_in_dasa_sequence():
    birth_date = datetime.datetime(1980, 3, 10)
    result = calculate_dasa_change_dates(birth_date, birth_nakshatra=3, future_years=30)
    for entry in result:
        assert entry["planet"] in DASA_SEQUENCE


def test_dasa_change_dates_future_years_0():
    birth_date = datetime.datetime(1990, 1, 1)
    result = calculate_dasa_change_dates(birth_date, birth_nakshatra=5, future_years=0)
    # Only starting dasa should be returned
    assert len(result) >= 1


# ---------------------------------------------------------------------------
# get_dasa_interpretation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("planet", ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "kethu"])
def test_dasa_interpretation_all_planets_maha(planet):
    result = get_dasa_interpretation(planet, DasaLevel.MAHA)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "(MAHA)" in result


@pytest.mark.parametrize("level", list(DasaLevel))
def test_dasa_interpretation_all_levels_for_sun(level):
    result = get_dasa_interpretation("sun", level)
    assert level.value.upper() in result


def test_dasa_interpretation_unknown_planet():
    result = get_dasa_interpretation("unknown_xyz", DasaLevel.BHUKTI)
    assert "Dasa period" in result
    assert "BHUKTI" in result
