"""Unit tests for ndastro_api.services.shadbala."""

from ndastro_api.services.shadbala import (
    HALF_LUNAR_CYCLE,
    MAX_CHESTA_BALA,
    MAX_DIG_BALA,
    MAX_DRISHTI_BALA,
    MAX_KALA_BALA,
    MAX_PAKSHA_BALA,
    MAX_SHADBALA,
    MAX_STHANA_BALA,
    ShadbalaPlanetContext,
    calculate_chesta_bala,
    calculate_dig_bala,
    calculate_kala_bala,
    calculate_paksha_bala,
    calculate_shadbala,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_max_sthana_bala():
    assert MAX_STHANA_BALA == 30.0


def test_max_dig_bala():
    assert MAX_DIG_BALA == 15.0


def test_max_kala_bala():
    assert MAX_KALA_BALA == 15.0


def test_max_paksha_bala():
    assert MAX_PAKSHA_BALA == 15.0


def test_max_chesta_bala():
    assert MAX_CHESTA_BALA == 15.0


def test_max_drishti_bala():
    assert MAX_DRISHTI_BALA == 15.0


def test_max_shadbala():
    assert MAX_SHADBALA == 90.0


def test_half_lunar_cycle():
    assert HALF_LUNAR_CYCLE == 90.0


# ---------------------------------------------------------------------------
# ShadbalaPlanetContext dataclass
# ---------------------------------------------------------------------------


def test_shadbala_planet_context_construction():
    ctx = ShadbalaPlanetContext(
        planet_code="SU",
        rasi_number=1,
        house_number=10,
        is_retrograde=False,
        is_night=False,
        moon_phase=45.0,
        avg_speed=1.0,
    )
    assert ctx.planet_code == "SU"
    assert ctx.rasi_number == 1
    assert ctx.house_number == 10
    assert ctx.aspecting_planets is None


def test_shadbala_planet_context_with_aspecting():
    ctx = ShadbalaPlanetContext(
        planet_code="JU",
        rasi_number=5,
        house_number=1,
        is_retrograde=False,
        is_night=True,
        moon_phase=90.0,
        avg_speed=0.08,
        aspecting_planets=[("venus", False)],
    )
    assert ctx.aspecting_planets == [("venus", False)]


# ---------------------------------------------------------------------------
# calculate_dig_bala()
# ---------------------------------------------------------------------------


def test_calculate_dig_bala_returns_float():
    result = calculate_dig_bala("SU", 1)
    assert isinstance(result, float)


def test_calculate_dig_bala_non_negative():
    result = calculate_dig_bala("MO", 4)
    assert result >= 0.0


def test_calculate_dig_bala_within_max():
    result = calculate_dig_bala("JU", 1)
    assert result <= MAX_DIG_BALA


def test_calculate_dig_bala_all_houses():
    for house in range(1, 13):
        result = calculate_dig_bala("SU", house)
        assert 0.0 <= result <= MAX_DIG_BALA


# ---------------------------------------------------------------------------
# calculate_kala_bala()
# ---------------------------------------------------------------------------


def test_calculate_kala_bala_day():
    result = calculate_kala_bala("SU", night=False)
    assert isinstance(result, float)


def test_calculate_kala_bala_night():
    result = calculate_kala_bala("MO", night=True)
    assert isinstance(result, float)


def test_calculate_kala_bala_within_max():
    for planet in ("SU", "MO", "MA", "BU", "GU", "SK", "SA"):
        result = calculate_kala_bala(planet, night=False)
        assert 0.0 <= result <= MAX_KALA_BALA


# ---------------------------------------------------------------------------
# calculate_paksha_bala()
# ---------------------------------------------------------------------------


def test_calculate_paksha_bala_returns_float():
    result = calculate_paksha_bala("MO", 90.0)
    assert isinstance(result, float)


def test_calculate_paksha_bala_within_max():
    result = calculate_paksha_bala("JU", 45.0)
    assert 0.0 <= result <= MAX_PAKSHA_BALA


# ---------------------------------------------------------------------------
# calculate_chesta_bala()
# ---------------------------------------------------------------------------


def test_calculate_chesta_bala_direct():
    result = calculate_chesta_bala("SU", retrograde=False, avg_speed=1.0)
    assert isinstance(result, float)


def test_calculate_chesta_bala_retrograde():
    result = calculate_chesta_bala("SA", retrograde=True, avg_speed=0.03)
    assert isinstance(result, float)


# ---------------------------------------------------------------------------
# calculate_shadbala() — integration
# ---------------------------------------------------------------------------


def test_calculate_shadbala_returns_dict():
    ctx = ShadbalaPlanetContext(
        planet_code="SU",
        rasi_number=1,
        house_number=10,
        is_retrograde=False,
        is_night=False,
        moon_phase=45.0,
        avg_speed=1.0,
    )
    result = calculate_shadbala(ctx)
    assert isinstance(result, dict)


def test_calculate_shadbala_has_expected_keys():
    ctx = ShadbalaPlanetContext(
        planet_code="MO",
        rasi_number=2,
        house_number=4,
        is_retrograde=False,
        is_night=True,
        moon_phase=90.0,
        avg_speed=13.0,
    )
    result = calculate_shadbala(ctx)
    expected_keys = {"sthana_bala", "dig_bala", "kala_bala", "paksha_bala", "chesta_bala", "total_shadbala"}
    assert expected_keys.issubset(result.keys())
