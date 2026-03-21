"""Unit tests for ndastro_api.core.schemas."""

import datetime
import uuid as uuid_pkg

import pytest

from ndastro_api.core.schemas import (
    AuthToken,
    HealthCheck,
    PersistentDeletion,
    TimestampSchema,
    Token,
    TokenBlacklistCreate,
    TokenData,
    UUIDSchema,
)

# ---------------------------------------------------------------------------
# HealthCheck
# ---------------------------------------------------------------------------


def test_health_check_creation():
    hc = HealthCheck(name="ndastro-api", version="1.0.0", description="All good")
    assert hc.name == "ndastro-api"
    assert hc.version == "1.0.0"


def test_health_check_required_fields():
    with pytest.raises(Exception):
        HealthCheck()  # type: ignore # missing required fields


# ---------------------------------------------------------------------------
# UUIDSchema
# ---------------------------------------------------------------------------


def test_uuid_schema_auto_generates_uuid():
    s = UUIDSchema()
    assert isinstance(s.uuid, uuid_pkg.UUID)


def test_uuid_schema_accepts_provided_uuid():
    fixed = uuid_pkg.UUID("12345678-1234-5678-1234-567812345678")
    s = UUIDSchema(uuid=fixed)
    assert s.uuid == fixed


# ---------------------------------------------------------------------------
# TimestampSchema
# ---------------------------------------------------------------------------


def test_timestamp_schema_has_created_at():
    ts = TimestampSchema()
    assert ts.created_at is not None


def test_timestamp_schema_updated_at_defaults_none():
    ts = TimestampSchema()
    assert ts.updated_at is None


def test_timestamp_schema_serialize_created_at():
    ts = TimestampSchema()
    serialized = ts.serialize_dt(ts.created_at)
    assert isinstance(serialized, str)
    assert "T" in serialized  # ISO 8601 format


def test_timestamp_schema_serialize_updated_at_none():
    ts = TimestampSchema()
    assert ts.serialize_updated_at(None) is None


# ---------------------------------------------------------------------------
# PersistentDeletion
# ---------------------------------------------------------------------------


def test_persistent_deletion_defaults():
    pd = PersistentDeletion()
    assert pd.is_deleted is False
    assert pd.deleted_at is None


# ---------------------------------------------------------------------------
# Token
# ---------------------------------------------------------------------------


def test_token_fields():
    t = Token(token="abc", expires_in=3600, token_type="bearer")  # noqa: S106
    assert t.token == "abc"  # noqa: S105
    assert t.token_type == "bearer"  # noqa: S105
    assert t.expires_in == 3600  # noqa: PLR2004


# ---------------------------------------------------------------------------
# TokenData
# ---------------------------------------------------------------------------


def test_token_data_creation():
    td = TokenData(username_or_email="user@example.com")
    assert td.username_or_email == "user@example.com"


# ---------------------------------------------------------------------------
# AuthToken
# ---------------------------------------------------------------------------


def test_auth_token_fields():
    at = AuthToken(username="testuser")
    assert at.username == "testuser"
    assert at.access_token is None
    assert at.refresh_token is None


# ---------------------------------------------------------------------------
# TokenBlacklistCreate
# ---------------------------------------------------------------------------


def test_token_blacklist_create():
    tbc = TokenBlacklistCreate(token="tok", expires_at=datetime.datetime(2099, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc))  # noqa: S106
    assert tbc.token == "tok"  # noqa: S105
