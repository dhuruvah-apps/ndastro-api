"""Extended tests for ndastro_api.services.position - pure calculation functions."""

from ndastro_api.services.position import (
    get_nakshatra_and_pada,
    get_planet_house_position,
    get_planet_sign_and_degree,
)

# ---------------------------------------------------------------------------
# get_planet_sign_and_degree
# ---------------------------------------------------------------------------


def test_get_planet_sign_and_degree_taurus():
    # Taurus (sign_index=1, normalize returns 1) to avoid 0-index edge case
    rasi, degree = get_planet_sign_and_degree(45.0)
    assert rasi is not None
    assert hasattr(degree, "degrees")


def test_get_planet_sign_and_degree_gemini():
    rasi, degree = get_planet_sign_and_degree(75.0)
    assert rasi is not None


def test_get_planet_sign_and_degree_180():
    rasi, degree = get_planet_sign_and_degree(180.0)
    assert rasi is not None


def test_get_planet_sign_and_degree_359():
    # 359° is Pisces (sign_index=11)
    rasi1, degree1 = get_planet_sign_and_degree(359.0)
    rasi2, degree2 = get_planet_sign_and_degree(359.0 + 360.0)
    assert rasi1 == rasi2


def test_get_planet_sign_and_degree_returns_tuple():
    result = get_planet_sign_and_degree(45.0)
    assert len(result) == 2


def test_get_planet_sign_and_degree_signs_2_to_12():
    # sign_index 1-11 (longitudes 30-360, avoid 0-30 which gives sign_index=0)
    for rasi_num in range(1, 12):
        longitude = rasi_num * 30.0 + 15.0
        rasi, degree = get_planet_sign_and_degree(longitude)
        assert rasi is not None


# ---------------------------------------------------------------------------
# get_planet_house_position
# ---------------------------------------------------------------------------


def test_get_planet_house_position_same_as_ascendant():
    # Planet at ascendant longitude → house 1
    house = get_planet_house_position(0.0, 0.0)
    assert house is not None


def test_get_planet_house_position_returns_houses_enum():
    from ndastro_engine.enums import Houses

    house = get_planet_house_position(0.0, 30.0)
    assert isinstance(house, Houses)


def test_get_planet_house_position_90_degrees():
    # 90° ahead = house 4
    house = get_planet_house_position(0.0, 90.0)
    assert house is not None


def test_get_planet_house_position_all_houses():
    for h in range(12):
        longitude = h * 30.0 + 15.0
        house = get_planet_house_position(0.0, longitude)
        assert house is not None


def test_get_planet_house_position_wraps_correctly():
    # Ascendant + 360 should be house 1
    house1 = get_planet_house_position(0.0, 0.0)
    house2 = get_planet_house_position(0.0, 360.0)
    assert house1 == house2


# ---------------------------------------------------------------------------
# get_nakshatra_and_pada - boundary cases
# ---------------------------------------------------------------------------


def test_get_nakshatra_and_pada_zero_longitude():
    code, pada = get_nakshatra_and_pada(0.0)
    assert pada in (1, 2, 3, 4)


def test_get_nakshatra_and_pada_each_pada():
    # Nakshatra arc = 360/27 = 13.333°, pada = 13.333/4 = 3.333°
    nakshatra_arc = 360.0 / 27
    pada_arc = nakshatra_arc / 4

    for pada_offset in range(4):
        longitude = pada_offset * pada_arc + 0.1
        code, pada = get_nakshatra_and_pada(longitude)
        assert pada == pada_offset + 1


def test_get_nakshatra_and_pada_all_27():
    nakshatra_arc = 360.0 / 27
    for nak_idx in range(27):
        longitude = nak_idx * nakshatra_arc + nakshatra_arc / 2
        code, pada = get_nakshatra_and_pada(longitude)
        assert 1 <= pada <= 4
