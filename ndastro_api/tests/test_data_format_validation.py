import re

from ndastro_api.core.utils.data_loader import astro_data

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PLANET_CODES = {"SU", "MO", "MA", "ME", "JU", "VE", "SA", "RA", "KE", "EA", "AS", ""}
RASI_PATTERN = re.compile(r"^R(0[1-9]|1[0-2])$")
HOUSE_PATTERN = re.compile(r"^H(0[1-9]|1[0-2])$")
NAKSHATRA_PATTERN = re.compile(r"^N(0[1-9]|1[0-9]|2[0-7])$")


def _is_valid_rasi(code: str) -> bool:
    return code == "" or bool(RASI_PATTERN.match(code))


def _is_valid_house(code: str) -> bool:
    return code == "" or bool(HOUSE_PATTERN.match(code))


def _is_valid_nakshatra(code: str) -> bool:
    return code == "" or bool(NAKSHATRA_PATTERN.match(code))


def _is_valid_planet(code: str) -> bool:
    return code in PLANET_CODES


# ---------------------------------------------------------------------------
# Rasis
# ---------------------------------------------------------------------------


def test_rasis_load_12_entries():
    assert len(astro_data.get_rasis()) == 12


def test_rasi_codes_format():
    for r in astro_data.get_rasis():
        assert _is_valid_rasi(r.code), f"Rasi '{r.name}' has invalid code '{r.code}'"


def test_rasi_planet_fields_are_valid_planet_codes():
    for r in astro_data.get_rasis():
        for field_name, value in [
            ("ruler", r.ruler),
            ("exalted_planet", r.exalted_planet),
            ("debilitated_planet", r.debilitated_planet),
            ("moolatrikona_planet", r.moolatrikona_planet),
        ]:
            assert _is_valid_planet(value), f"Rasi '{r.name}'.{field_name} has invalid planet code '{value}'"


def test_rasi_numbers_are_sequential_1_to_12():
    numbers = sorted(r.number for r in astro_data.get_rasis())
    assert numbers == list(range(1, 13))


# ---------------------------------------------------------------------------
# Houses
# ---------------------------------------------------------------------------


def test_houses_load_12_entries():
    assert len(astro_data.get_houses()) == 12


def test_house_codes_format():
    for h in astro_data.get_houses():
        assert _is_valid_house(h.code), f"House '{h.name}' has invalid code '{h.code}'"


def test_house_natural_sign_is_valid_rasi_code():
    for h in astro_data.get_houses():
        assert _is_valid_rasi(h.natural_sign), f"House '{h.name}'.naturalSign has invalid rasi code '{h.natural_sign}'"


def test_house_natural_ruler_is_valid_planet_code():
    for h in astro_data.get_houses():
        assert _is_valid_planet(h.natural_ruler), f"House '{h.name}'.naturalRuler has invalid planet code '{h.natural_ruler}'"


def test_house_karakas_are_valid_planet_codes():
    for h in astro_data.get_houses():
        for k in h.karakas:
            assert _is_valid_planet(k), f"House '{h.name}'.karakas contains invalid planet code '{k}'"


def test_house_aspects_are_valid_house_codes():
    for h in astro_data.get_houses():
        for a in h.aspects:
            assert _is_valid_house(a), f"House '{h.name}'.aspects contains invalid house code '{a}'"


def test_house_numbers_are_sequential_1_to_12():
    numbers = sorted(h.number for h in astro_data.get_houses())
    assert numbers == list(range(1, 13))


# ---------------------------------------------------------------------------
# Nakshatras
# ---------------------------------------------------------------------------


def test_nakshatras_load_27_entries():
    assert len(astro_data.get_nakshatras()) == 27


def test_nakshatra_codes_format():
    for n in astro_data.get_nakshatras():
        assert _is_valid_nakshatra(n.code), f"Nakshatra '{n.name}' has invalid code '{n.code}'"


def test_nakshatra_ruling_planet_is_valid_planet_code():
    for n in astro_data.get_nakshatras():
        assert _is_valid_planet(n.ruling_planet), f"Nakshatra '{n.name}'.rulingPlanet has invalid code '{n.ruling_planet}'"


def test_nakshatra_padas_navamsa_rasi_are_valid_rasi_codes():
    for n in astro_data.get_nakshatras():
        for pada in n.padas:
            assert _is_valid_rasi(pada.navamsa_rasi), (
                f"Nakshatra '{n.name}' pada {pada.pada_number}.navamsaRasi has invalid code '{pada.navamsa_rasi}'"
            )


def test_nakshatra_padas_navamsa_lord_are_valid_planet_codes():
    for n in astro_data.get_nakshatras():
        for pada in n.padas:
            assert _is_valid_planet(pada.navamsa_lord), (
                f"Nakshatra '{n.name}' pada {pada.pada_number}.navamsaLord has invalid code '{pada.navamsa_lord}'"
            )


def test_nakshatra_numbers_are_sequential_1_to_27():
    numbers = sorted(n.number for n in astro_data.get_nakshatras())
    assert numbers == list(range(1, 28))


# ---------------------------------------------------------------------------
# Planets
# ---------------------------------------------------------------------------

VALID_PLANET_CODES = {"SU", "MO", "MA", "ME", "JU", "VE", "SA", "RA", "KE", "EA", "AS"}


def test_planets_load_expected_count():
    # 9 grahas + Earth + Ascendant = 11
    assert len(astro_data.get_planets()) == 11


def test_planet_codes_are_known():
    for p in astro_data.get_planets():
        assert p.code in VALID_PLANET_CODES, f"Unknown planet code '{p.code}'"


def test_planet_exaltation_sign_is_valid_rasi_code():
    for p in astro_data.get_planets():
        if p.exaltation and p.exaltation.sign:
            assert _is_valid_rasi(p.exaltation.sign), f"Planet '{p.code}'.exaltation.sign has invalid rasi code '{p.exaltation.sign}'"


def test_planet_debilitation_sign_is_valid_rasi_code():
    for p in astro_data.get_planets():
        if p.debilitation and p.debilitation.sign:
            assert _is_valid_rasi(p.debilitation.sign), f"Planet '{p.code}'.debilitation.sign has invalid rasi code '{p.debilitation.sign}'"


def test_planet_moolatrikona_sign_is_valid_rasi_code():
    for p in astro_data.get_planets():
        if p.moolatrikona and p.moolatrikona.sign:
            assert _is_valid_rasi(p.moolatrikona.sign), f"Planet '{p.code}'.moolatrikona.sign has invalid rasi code '{p.moolatrikona.sign}'"


def test_planet_aspects_are_valid_house_codes():
    for p in astro_data.get_planets():
        for a in p.aspects or []:
            assert _is_valid_house(a), f"Planet '{p.code}'.aspects contains invalid house code '{a}'"


def test_planet_natural_friends_are_valid_planet_codes():
    for p in astro_data.get_planets():
        for code in p.natural_friends:
            assert _is_valid_planet(code), f"Planet '{p.code}'.naturalFriends has invalid code '{code}'"


def test_planet_natural_enemies_are_valid_planet_codes():
    for p in astro_data.get_planets():
        for code in p.natural_enemies:
            assert _is_valid_planet(code), f"Planet '{p.code}'.naturalEnemies has invalid code '{code}'"


def test_planet_natural_neutrals_are_valid_planet_codes():
    for p in astro_data.get_planets():
        for code in p.natural_neutrals:
            assert _is_valid_planet(code), f"Planet '{p.code}'.naturalNeutrals has invalid code '{code}'"


# ---------------------------------------------------------------------------
# Tithis
# ---------------------------------------------------------------------------


def test_tithis_load_30_entries():
    assert len(astro_data.get_tithis()) == 30


def test_tithi_lord_is_valid_planet_code():
    for t in astro_data.get_tithis():
        assert _is_valid_planet(t.tithi_lord), f"Tithi '{t.name}'.tithiLord has invalid code '{t.tithi_lord}'"


def test_tithi_nakshatra_compatibility_are_valid_nakshatra_codes():
    for t in astro_data.get_tithis():
        for code in t.nakshatra_compatibility:
            assert _is_valid_nakshatra(code), f"Tithi '{t.name}'.nakshatraCompatibility has invalid code '{code}'"


def test_tithi_numbers_are_1_to_15_per_paksha():
    # Tithis are numbered 1-15 within each paksha (Shukla and Krishna).
    # There are 15 Shukla + 15 Krishna = 30 total, with numbers repeating per paksha.
    tithis = astro_data.get_tithis()
    by_paksha: dict[str, list[int]] = {}
    for t in tithis:
        by_paksha.setdefault(t.paksha, []).append(t.number)
    for paksha, numbers in by_paksha.items():
        assert sorted(numbers) == list(range(1, 16)), f"Paksha '{paksha}' tithi numbers {sorted(numbers)} are not 1-15"


# ---------------------------------------------------------------------------
# Varas (weekdays)
# ---------------------------------------------------------------------------


def test_varas_load_7_entries():
    assert len(astro_data.get_varas()) == 7


def test_vara_ruling_planet_is_valid_planet_code():
    for v in astro_data.get_varas():
        assert _is_valid_planet(v.ruling_planet), f"Vara '{v.name}'.rulingPlanet has invalid code '{v.ruling_planet}'"


def test_vara_numbers_are_sequential_1_to_7():
    numbers = sorted(v.number for v in astro_data.get_varas())
    assert numbers == list(range(1, 8))


# ---------------------------------------------------------------------------
# Karanas
# ---------------------------------------------------------------------------


def test_karanas_load_11_entries():
    # 7 movable + 4 fixed = 11
    assert len(astro_data.get_karanas()) == 11


def test_karana_numbers_are_sequential_1_to_11():
    numbers = sorted(k.number for k in astro_data.get_karanas())
    assert numbers == list(range(1, 12))


# ---------------------------------------------------------------------------
# Yogas
# ---------------------------------------------------------------------------


def test_yogas_load_27_entries():
    assert len(astro_data.get_yogas()) == 27


def test_yoga_numbers_are_sequential_1_to_27():
    numbers = sorted(y.number for y in astro_data.get_yogas())
    assert numbers == list(range(1, 28))


# ---------------------------------------------------------------------------
# Cross-file consistency
# ---------------------------------------------------------------------------


def test_house_natural_sign_maps_to_existing_rasi_code():
    rasi_codes = {r.code for r in astro_data.get_rasis()}
    for h in astro_data.get_houses():
        if h.natural_sign:
            assert h.natural_sign in rasi_codes, f"House '{h.name}'.naturalSign '{h.natural_sign}' not found in rasis.json"


def test_planet_exaltation_sign_maps_to_existing_rasi():
    rasi_codes = {r.code for r in astro_data.get_rasis()}
    for p in astro_data.get_planets():
        if p.exaltation and p.exaltation.sign:
            assert p.exaltation.sign in rasi_codes, f"Planet '{p.code}'.exaltation.sign '{p.exaltation.sign}' not in rasis.json"
