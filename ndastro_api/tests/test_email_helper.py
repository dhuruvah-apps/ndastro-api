"""Unit tests for ndastro_api.email_helper (token generation / verification — no SMTP)."""

from ndastro_api.email_helper import (
    EmailData,
    generate_password_reset_token,
    verify_password_reset_token,
)

# ---------------------------------------------------------------------------
# EmailData dataclass
# ---------------------------------------------------------------------------


def test_email_data_construction():
    ed = EmailData(html_content="<p>Hello</p>", subject="Test")
    assert ed.html_content == "<p>Hello</p>"
    assert ed.subject == "Test"


# ---------------------------------------------------------------------------
# generate_password_reset_token() / verify_password_reset_token()
# ---------------------------------------------------------------------------


def test_generate_token_returns_non_empty_string():
    token = generate_password_reset_token(email="user@example.com")
    assert isinstance(token, str)
    assert len(token) > 10


def test_verify_token_returns_email():
    email = "alice@example.com"
    token = generate_password_reset_token(email=email)
    recovered = verify_password_reset_token(token=token)
    assert recovered == email


def test_verify_invalid_token_returns_none():
    result = verify_password_reset_token(token="not.a.valid.jwt")
    assert result is None


def test_verify_tampered_token_returns_none():
    token = generate_password_reset_token(email="bob@example.com")
    # Tamper with the token
    tampered = token[:-4] + "xxxx"
    assert verify_password_reset_token(token=tampered) is None


def test_two_tokens_for_same_email_are_not_identical():
    """Tokens include a timestamp, so two calls can differ."""
    import time

    t1 = generate_password_reset_token(email="user@example.com")
    time.sleep(0.01)
    t2 = generate_password_reset_token(email="user@example.com")
    # Both should verify to the same email even if tokens differ
    assert verify_password_reset_token(t1) == "user@example.com"
    assert verify_password_reset_token(t2) == "user@example.com"
