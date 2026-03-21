from ndastro_api.services.position import get_nakshatra_and_pada


def test_get_nakshatra_and_pada_at_zero_longitude():
    # longitude 0 should map to first nakshatra (N01) and pada 1
    nak, pada = get_nakshatra_and_pada(0.0)
    assert nak == "N01"
    assert pada == 1
