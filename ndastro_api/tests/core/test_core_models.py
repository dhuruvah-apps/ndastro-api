"""Unit tests for ndastro_api.core.models (dasha, kattam, astro_system TypeAliases)."""

import dataclasses

from ndastro_api.core.models.dasha_detail import (
    DashaDetail,
    Dashas,
    DashaTypes,
)
from ndastro_api.core.models.kattam import Kattam

# ---------------------------------------------------------------------------
# Dashas enum
# ---------------------------------------------------------------------------


def test_dashas_enum_has_vimshottari():
    assert Dashas.VIMSHOTTARI.name == "VIMSHOTTARI"


def test_dashas_enum_str():
    assert str(Dashas.VIMSHOTTARI) == "Vimshottari"


# ---------------------------------------------------------------------------
# DashaTypes enum
# ---------------------------------------------------------------------------


def test_dasha_types_has_maha():
    assert DashaTypes.MAHA.name == "MAHA"


def test_dasha_types_has_antara():
    assert DashaTypes.ANTAR.name == "ANTAR"


# ---------------------------------------------------------------------------
# DashaDetail dataclass
# ---------------------------------------------------------------------------


def test_dasha_detail_construction():
    d = DashaDetail(name="Vimshottari", cycle_years=120)
    assert d.name == "Vimshottari"
    assert d.cycle_years == 120


def test_dasha_detail_default_system():
    d = DashaDetail(name="Test")
    assert d.dasha_system == Dashas.VIMSHOTTARI


def test_dasha_detail_description_defaults_none():
    d = DashaDetail(name="x")
    assert d.description is None


# ---------------------------------------------------------------------------
# Kattam dataclass — verify fields exist (construction requires ndastro_engine enums)
# ---------------------------------------------------------------------------


def test_kattam_has_required_fields():
    fields = {f.name for f in dataclasses.fields(Kattam)}
    expected = {"order", "is_ascendant", "asc_longitude", "owner", "rasi", "house", "planets"}
    assert expected.issubset(fields)


def test_kattam_is_dataclass():
    assert dataclasses.is_dataclass(Kattam)
