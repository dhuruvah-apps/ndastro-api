"""Unit tests for ndastro_api.services.kattams."""

import inspect

from ndastro_api.services import kattams
from ndastro_api.services.kattams import get_kattams

# ---------------------------------------------------------------------------
# Module-level sanity checks
# ---------------------------------------------------------------------------


def test_get_kattams_is_callable():
    assert callable(get_kattams)


def test_get_kattams_signature():
    sig = inspect.signature(get_kattams)
    params = list(sig.parameters.keys())
    assert "lat" in params
    assert "lon" in params
    assert "given_time" in params
    assert "ayanamsa" in params


def test_get_kattams_takes_4_params():
    sig = inspect.signature(get_kattams)
    assert len(sig.parameters) == 4


def test_kattams_module_importable():
    assert hasattr(kattams, "get_kattams")


def test_get_kattams_annotation_returns_list():
    sig = inspect.signature(get_kattams)
    return_annotation = sig.return_annotation
    # Return annotation should be a list type or str containing "list"
    annotation_str = str(return_annotation)
    assert "list" in annotation_str.lower() or "List" in annotation_str
