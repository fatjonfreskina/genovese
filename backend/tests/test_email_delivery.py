import json
from unittest.mock import MagicMock
from urllib.error import HTTPError

import pytest

from backend.app import email_delivery as delivery


@pytest.fixture
def configured(monkeypatch):
    values = {
        "EMAIL_LINK_ENABLED": "true",
        "EMAIL_LINK_SECRET": "x" * 40,
        "EMAIL_SERVICE_URL": "https://email.example/internal",
        "EMAIL_SERVICE_TOKEN": "t" * 40,
        "EMAIL_SERVICE_TIMEOUT": "8",
        "EMAIL_PRIVACY_URL": "https://equa.example/privacy",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("EMAIL_SERVICE_ALLOW_HTTP", raising=False)
    return values


@pytest.mark.parametrize(
    "key,value",
    [
        ("EMAIL_LINK_ENABLED", "false"),
        ("EMAIL_LINK_SECRET", "short"),
        ("EMAIL_SERVICE_TOKEN", "short"),
        ("EMAIL_SERVICE_TOKEN", "x" * 39 + " "),
        ("EMAIL_SERVICE_URL", "https://email.example:invalid"),
        ("EMAIL_SERVICE_URL", "http://production.example"),
        ("EMAIL_SERVICE_URL", "https://user:pass@example.org"),
        ("EMAIL_SERVICE_URL", "https://example.org/?private=1"),
        ("EMAIL_SERVICE_TIMEOUT", "0"),
        ("EMAIL_SERVICE_TIMEOUT", "not-a-number"),
        ("EMAIL_PRIVACY_URL", "javascript:alert(1)"),
    ],
)
def test_bad_configuration_disables_only_email(configured, monkeypatch, key, value):
    monkeypatch.setenv(key, value)
    assert delivery.get_email_settings() is None


def test_local_service_url_is_allowed(configured, monkeypatch):
    monkeypatch.setenv("EMAIL_SERVICE_URL", "http://localhost:8000")
    assert delivery.get_email_settings() is not None


def test_internal_http_requires_explicit_opt_in(configured, monkeypatch):
    monkeypatch.setenv("EMAIL_SERVICE_URL", "http://email-service:8000")
    assert delivery.get_email_settings() is None
    monkeypatch.setenv("EMAIL_SERVICE_ALLOW_HTTP", "true")
    assert delivery.get_email_settings() is not None


def fake_transport(monkeypatch, body=b'{"message":"Email sent"}'):
    opener = MagicMock()
    response = MagicMock()
    response.status = 200
    response.read.return_value = body
    opener.open.return_value.__enter__.return_value = response
    builder = MagicMock(return_value=opener)
    monkeypatch.setattr(delivery, "build_opener", builder)
    return opener, builder


def test_verification_contract_uses_private_bearer_hop(configured, monkeypatch):
    opener, builder = fake_transport(monkeypatch)
    settings = delivery.get_email_settings()

    delivery.send_verification_email(settings, "anna@example.org", "123456")

    request = opener.open.call_args.args[0]
    assert request.full_url == "https://email.example/internal/forward-email-equa"
    assert request.method == "POST"
    assert request.get_header("Authorization") == f"Bearer {'t' * 40}"
    assert request.get_header("Content-type") == "application/json"
    assert json.loads(request.data) == {
        "kind": "verification",
        "email": "anna@example.org",
        "code": "123456",
    }
    assert opener.open.call_args.kwargs == {"timeout": 8}
    assert any(
        isinstance(handler, delivery.ProxyHandler) for handler in builder.call_args.args
    )
    assert any(
        isinstance(handler, delivery._NoRedirect) for handler in builder.call_args.args
    )


def test_group_link_contract_sends_only_identifier(configured, monkeypatch):
    opener, _ = fake_transport(monkeypatch)
    settings = delivery.get_email_settings()
    group_id = "738da6a7-b4c5-4adb-a41a-70e12fa2aa3c"

    delivery.send_group_link_email(settings, "anna@example.org", group_id)

    payload = json.loads(opener.open.call_args.args[0].data)
    assert payload == {
        "kind": "group_link",
        "email": "anna@example.org",
        "group_id": group_id,
    }
    assert "link" not in payload
    assert "subject" not in payload
    assert "body" not in payload


@pytest.mark.parametrize(
    "body",
    [b"not-json", b'{"message":"unexpected"}', b"x" * 4097],
)
def test_invalid_service_responses_are_hidden(configured, monkeypatch, body):
    fake_transport(monkeypatch, body)
    with pytest.raises(delivery.EmailDeliveryError) as error:
        delivery.send_verification_email(
            delivery.get_email_settings(), "anna@example.org", "123456"
        )
    assert "anna" not in str(error.value)


def test_transport_failures_hide_private_details(configured, monkeypatch):
    opener, _ = fake_transport(monkeypatch)
    opener.open.side_effect = HTTPError(
        "https://email.example", 302, "secret redirect", {}, None
    )
    with pytest.raises(delivery.EmailDeliveryError) as error:
        delivery.send_verification_email(
            delivery.get_email_settings(), "anna@example.org", "123456"
        )
    assert "secret" not in str(error.value)
