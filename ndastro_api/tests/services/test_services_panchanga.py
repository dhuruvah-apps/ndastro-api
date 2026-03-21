"""Unit tests for ndastro_api.services.panchanga."""

from ndastro_api.services.panchanga import (
    FULL_CIRCLE_DEGREES,
    KARANA_COUNT,
    KARANA_DEGREES,
    MOVABLE_KARANAS,
    PAKSHA_DIVIDER,
    TITHI_COUNT,
    TITHI_DEGREES,
    TITHI_NAMES,
    VARA_NAMES,
    KaranaResult,
    TithiResult,
    VaraResult,
    get_karana_result,
    get_tithi_number,
    get_tithi_result,
    get_vara_number_from_weekday,
    get_vara_result,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_full_circle_degrees():
    assert FULL_CIRCLE_DEGREES == 360.0


def test_tithi_count():
    assert TITHI_COUNT == 30


def test_karana_count():
    assert KARANA_COUNT == 60


def test_tithi_degrees():
    assert TITHI_DEGREES == 360.0 / 30


def test_karana_degrees():
    assert KARANA_DEGREES == 360.0 / 60


def test_paksha_divider():
    assert PAKSHA_DIVIDER == 15


def test_tithi_names_has_30_entries():
    assert len(TITHI_NAMES) == 30


def test_vara_names_has_7_entries():
    assert len(VARA_NAMES) == 7


def test_vara_names_start_sunday():
    assert VARA_NAMES[0] == "Sunday"


def test_movable_karanas_nonempty():
    assert len(MOVABLE_KARANAS) > 0


# ---------------------------------------------------------------------------
# get_tithi_number()
# ---------------------------------------------------------------------------


def test_get_tithi_number_first_tithi():
    # moon ahead of sun by 1 degree → tithi 1 (Pratipada, Shukla)
    assert get_tithi_number(0.0, 1.0) == 1


def test_get_tithi_number_second_tithi():
    # moon ahead of sun by 13 degrees = tithi 2
    assert get_tithi_number(0.0, 13.0) == 2


def test_get_tithi_number_full_moon():
    # 180° apart = tithi 16 (int(180/12)+1 = 16, Krishna Pratipada)
    assert get_tithi_number(0.0, 180.0) == 16


def test_get_tithi_number_new_moon():
    # Amavasya (tithi 30) is at phase just under 360° — use 350°
    result = get_tithi_number(10.0, 10.0 + 350.0)
    assert result == 30


def test_get_tithi_number_returns_int():
    assert isinstance(get_tithi_number(0.0, 90.0), int)


def test_get_tithi_number_in_range():
    for sun in range(0, 360, 30):
        for moon in range(0, 360, 30):
            t = get_tithi_number(float(sun), float(moon))
            assert 1 <= t <= 30, f"Tithi {t} out of range for sun={sun}, moon={moon}"


# ---------------------------------------------------------------------------
# get_tithi_result()
# ---------------------------------------------------------------------------


def test_get_tithi_result_returns_dataclass():
    result = get_tithi_result(0.0, 1.0)
    assert isinstance(result, TithiResult)


def test_get_tithi_result_shukla_paksha():
    result = get_tithi_result(0.0, 1.0)
    assert result.paksha == "shukla"


def test_get_tithi_result_krishna_paksha():
    result = get_tithi_result(0.0, 181.0)
    assert result.paksha == "krishna"


def test_get_tithi_result_name_set():
    result = get_tithi_result(0.0, 1.0)
    assert result.name == "Pratipada"


# ---------------------------------------------------------------------------
# get_karana_result()
# ---------------------------------------------------------------------------


def test_get_karana_result_returns_dataclass():
    result = get_karana_result(0.0, 1.0)
    assert isinstance(result, KaranaResult)


def test_get_karana_result_has_name():
    result = get_karana_result(0.0, 1.0)
    assert isinstance(result.name, str) and len(result.name) > 0


# ---------------------------------------------------------------------------
# get_vara_number_from_weekday()
# ---------------------------------------------------------------------------


def test_vara_number_sunday():
    # weekday 0 in Python = Monday (vedic day sequence starts Monday)
    # Verified: get_vara_number_from_weekday(0) → 2
    assert get_vara_number_from_weekday(0) == 2


def test_vara_number_saturday():
    # weekday 6 in Python = Sunday → vara 1 in vedic sequence
    assert get_vara_number_from_weekday(6) == 1


def test_vara_number_range():
    for day in range(7):
        vara = get_vara_number_from_weekday(day)
        assert 1 <= vara <= 7


# ---------------------------------------------------------------------------
# get_vara_result()
# ---------------------------------------------------------------------------


def test_get_vara_result_returns_dataclass():
    result = get_vara_result(weekday_index=0)
    assert isinstance(result, VaraResult)


def test_get_vara_result_monday():
    # weekday 0 (Python Monday) → vedic vara 2, Monday
    result = get_vara_result(weekday_index=0)
    assert result.number == 2
    assert result.name == "Monday"
