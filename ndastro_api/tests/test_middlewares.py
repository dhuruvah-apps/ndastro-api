"""Unit tests for ndastro_api.middlewares."""

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from ndastro_api.core.babel_i18n import DEFAULT_LOCALE
from ndastro_api.middlewares.client_cache import ClientCacheMiddleware
from ndastro_api.middlewares.i18n import I18nMiddleware, get_request_language
from ndastro_api.middlewares.monitoring import MonitoringMiddleware

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_app(*middleware_classes_and_kwargs):
    """Build a minimal Starlette app with the given middlewares applied in order."""

    async def homepage(request: Request):
        lang = getattr(request.state, "language", None)
        return PlainTextResponse(f"lang={lang}")

    app = Starlette(routes=[Route("/", homepage)])
    for cls, kwargs in middleware_classes_and_kwargs:
        app.add_middleware(cls, **kwargs)
    return app


# ---------------------------------------------------------------------------
# ClientCacheMiddleware
# ---------------------------------------------------------------------------


def test_client_cache_default_max_age():
    app = _make_app((ClientCacheMiddleware, {}))
    client = TestClient(app)
    response = client.get("/")
    assert "Cache-Control" in response.headers
    assert "max-age=60" in response.headers["Cache-Control"]


def test_client_cache_custom_max_age():
    app = _make_app((ClientCacheMiddleware, {"max_age": 300}))
    client = TestClient(app)
    response = client.get("/")
    assert "max-age=300" in response.headers["Cache-Control"]


def test_client_cache_header_is_public():
    app = _make_app((ClientCacheMiddleware, {}))
    client = TestClient(app)
    response = client.get("/")
    assert "public" in response.headers["Cache-Control"]


# ---------------------------------------------------------------------------
# MonitoringMiddleware
# ---------------------------------------------------------------------------


def test_monitoring_adds_x_process_time_header():
    app = _make_app((MonitoringMiddleware, {}))
    client = TestClient(app)
    response = client.get("/")
    assert "X-Process-Time" in response.headers


def test_monitoring_x_process_time_is_numeric():
    app = _make_app((MonitoringMiddleware, {}))
    client = TestClient(app)
    response = client.get("/")
    value = response.headers["X-Process-Time"]
    assert float(value) >= 0.0


# ---------------------------------------------------------------------------
# I18nMiddleware
# ---------------------------------------------------------------------------


def test_i18n_default_language():
    app = _make_app((I18nMiddleware, {}))
    client = TestClient(app)
    response = client.get("/")
    assert response.headers.get("Content-Language") == DEFAULT_LOCALE


def test_i18n_accept_language_header_tamil():
    app = _make_app((I18nMiddleware, {}))
    client = TestClient(app)
    response = client.get("/", headers={"Accept-Language": "ta"})
    assert response.headers.get("Content-Language") == "ta"


def test_i18n_lang_query_param_overrides():
    app = _make_app((I18nMiddleware, {}))
    client = TestClient(app)
    response = client.get("/?lang=ta")
    assert response.headers.get("Content-Language") == "ta"


def test_i18n_unknown_lang_falls_back_to_default():
    app = _make_app((I18nMiddleware, {}))
    client = TestClient(app)
    response = client.get("/?lang=zz")
    assert response.headers.get("Content-Language") == DEFAULT_LOCALE


# ---------------------------------------------------------------------------
# get_request_language()
# ---------------------------------------------------------------------------


def test_get_request_language_returns_default_when_no_state():
    from unittest.mock import MagicMock

    request = MagicMock()
    del request.state.language  # simulate missing attribute
    request.state = MagicMock(spec=[])  # no language attribute
    result = get_request_language(request)
    assert result == DEFAULT_LOCALE
