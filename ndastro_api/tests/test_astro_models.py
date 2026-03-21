from ndastro_api.core.models.astro_system import Planet, Tithi


def test_planet_and_tithi_basic_construction():
    # create a Planet with engine-aligned codes
    p = Planet(name="Ascendant", code="AS", posited_at="H01", rasi_occupied="R05", nakshatra="N10")
    assert p.name == "Ascendant"
    assert p.code == "AS"
    assert p.posited_at == "H01"
    assert p.rasi_occupied == "R05"
    assert p.nakshatra == "N10"

    # create a Tithi with nakshatra compatibility list
    t = Tithi(name="Pratipat", number=1, nakshatra_compatibility=["N01", "N02", "N03"])
    assert t.number == 1
    assert isinstance(t.nakshatra_compatibility, list)
    assert all(isinstance(x, str) and x.startswith("N") for x in t.nakshatra_compatibility)
