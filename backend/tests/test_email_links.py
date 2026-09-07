import asyncio
import json
import re
from datetime import datetime, timedelta
from uuid import UUID

import pytest
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.email_delivery import EmailDeliveryError, EmailSettings
from backend.app.models import EmailLinkChallenge, EmailLinkRateLimit, Group, Member
from backend.app.routers import email_links as links
from backend.app.schemas import (
    EmailLinkConfirmation,
    EmailLinkRequest,
    EmailLinkToken,
    GroupOut,
)


@pytest.fixture
def context(monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    group = Group(
        name="Gruppo riservato",
        currency="EUR",
        members=[Member(name="Anna"), Member(name="Luca")],
    )
    session.add(group)
    session.commit()
    settings = EmailSettings(
        secret="x" * 40,
        service_url="https://email.example",
        service_token="t" * 40,
        privacy_url="https://equa.example/privacy",
    )
    messages = []
    monkeypatch.setattr(links, "get_email_settings", lambda: settings)
    monkeypatch.setattr(
        links,
        "send_verification_email",
        lambda settings, email, code: messages.append(("verification", email, code)),
    )
    monkeypatch.setattr(
        links,
        "send_group_link_email",
        lambda settings, email, group_id: messages.append(
            ("group_link", email, group_id)
        ),
    )
    monkeypatch.setattr(links, "utcnow", lambda: datetime(2026, 9, 3, 12, 0, 10))
    try:
        yield session, group, settings, messages
    finally:
        session.close()
        engine.dispose()


def request_link(context, email="anna@example.org", group_id=None):
    session, group, _, _ = context
    request = Request({"type": "http", "client": ("192.0.2.1", 1234)})
    response = Response()
    result = links.request_email_link(
        UUID(group_id or group.id),
        EmailLinkRequest(email=email),
        request,
        response,
        session,
    )
    assert response.headers["Cache-Control"] == "no-store"
    return result["challenge_token"]


def delivered_code(context):
    return context[3][0][2]


def confirm(context, token, code=None, group_id=None):
    session, group, _, _ = context
    links.confirm_email_link(
        UUID(group_id or group.id),
        EmailLinkConfirmation(
            challenge_token=token, code=code or delivered_code(context)
        ),
        session,
    )


def test_link_requires_verification_and_recipient_never_enters_group_data(context):
    session, group, _, messages = context
    token = request_link(context)
    assert len(messages) == 1
    assert messages[0][0] == "verification"
    assert messages[0][1] == "anna@example.org"
    assert re.fullmatch(r"[0-9]{6}", messages[0][2])
    assert "anna@example.org" not in token
    rows = str(session.execute(select(EmailLinkChallenge.__table__)).all())
    assert "anna@example.org" not in rows
    assert token not in rows
    assert "anna@example.org" not in GroupOut.model_validate(group).model_dump_json()
    confirm(context, token)
    assert len(messages) == 2
    assert messages[1] == ("group_link", "anna@example.org", group.id)
    assert session.query(EmailLinkChallenge).count() == 0
    with pytest.raises(HTTPException) as error:
        confirm(context, token, "123456")
    assert error.value.status_code == 410
    assert len(messages) == 2


def test_only_five_code_attempts_are_allowed(context):
    token = request_link(context)
    right_code = delivered_code(context)
    wrong_code = "000001" if right_code == "000000" else "000000"
    for attempt in range(5):
        with pytest.raises(HTTPException) as error:
            confirm(context, token, wrong_code)
        assert error.value.status_code == (410 if attempt == 4 else 400)
    with pytest.raises(HTTPException):
        confirm(context, token, right_code)
    assert len(context[3]) == 1
    assert context[0].query(EmailLinkChallenge).count() == 0


def test_challenge_is_bound_to_group_and_requesting_browser(context):
    token = request_link(context)
    for group_id, candidate in [
        ("00000000-0000-0000-0000-000000000000", token),
        (context[1].id, "X" + token[1:]),
    ]:
        with pytest.raises(HTTPException) as error:
            confirm(context, candidate, group_id=group_id)
        assert error.value.status_code == 410
    confirm(context, token)
    assert len(context[3]) == 2


def test_expiry_and_cleanup(context, monkeypatch):
    token = request_link(context)
    monkeypatch.setattr(links, "utcnow", lambda: datetime(2026, 9, 3, 12, 15, 10))
    with pytest.raises(HTTPException) as error:
        confirm(context, token)
    assert error.value.status_code == 410
    assert context[0].query(EmailLinkChallenge).count() == 0
    links.cleanup_expired(context[0], datetime(2026, 9, 5))
    context[0].commit()
    assert context[0].query(EmailLinkRateLimit).count() == 0


def test_cancel_and_group_deletion_invalidate_requests(context):
    token = request_link(context)
    links.cancel_email_link(
        UUID(context[1].id), EmailLinkToken(challenge_token=token), context[0]
    )
    with pytest.raises(HTTPException):
        confirm(context, token)
    request_link(context, "other@example.org")
    context[0].delete(context[1])
    context[0].commit()
    assert context[0].query(EmailLinkChallenge).count() == 0


def test_recipient_rate_limit_is_case_insensitive_and_survives_cancel(context):
    token = request_link(context)
    links.cancel_email_link(
        UUID(context[1].id), EmailLinkToken(challenge_token=token), context[0]
    )
    with pytest.raises(HTTPException) as error:
        request_link(context, "ANNA@EXAMPLE.ORG")
    assert error.value.status_code == 429
    assert int(error.value.headers["Retry-After"]) > 0
    assert len(context[3]) == 1
    limits = str(context[0].execute(select(EmailLinkRateLimit.__table__)).all())
    assert "anna" not in limits
    assert "192.0.2.1" not in limits


@pytest.mark.parametrize("seconds,maximum", [(60, 1), (3600, 3), (86400, 5)])
def test_limits_are_persistent_and_expire(context, seconds, maximum):
    session, _, settings, _ = context
    now = links.utcnow()
    for _ in range(maximum):
        links.reserve_limit(
            session, settings, "test", "recipient", seconds, maximum, now
        )
        session.commit()
    with pytest.raises(HTTPException) as error:
        links.reserve_limit(
            session, settings, "test", "recipient", seconds, maximum, now
        )
    assert error.value.status_code == 429
    links.reserve_limit(
        session,
        settings,
        "test",
        "recipient",
        seconds,
        maximum,
        now + timedelta(seconds=seconds),
    )
    session.commit()


def test_service_failure_removes_challenge_and_keeps_abuse_limit(context, monkeypatch):
    def fail(*args):
        raise EmailDeliveryError("private service error")

    monkeypatch.setattr(links, "send_verification_email", fail)
    with pytest.raises(HTTPException) as error:
        request_link(context)
    assert error.value.status_code == 503
    assert "private" not in error.value.detail
    assert context[0].query(EmailLinkChallenge).count() == 0
    with pytest.raises(HTTPException) as error:
        request_link(context)
    assert error.value.status_code == 429


def test_failed_final_delivery_cannot_be_replayed(context, monkeypatch):
    token = request_link(context)
    code = delivered_code(context)

    def fail(*args):
        raise EmailDeliveryError()

    monkeypatch.setattr(links, "send_group_link_email", fail)
    with pytest.raises(HTTPException) as error:
        confirm(context, token, code)
    assert error.value.status_code == 503
    with pytest.raises(HTTPException) as error:
        confirm(context, token, code)
    assert error.value.status_code == 410


def test_disabled_feature_never_sends(context, monkeypatch):
    monkeypatch.setattr(links, "get_email_settings", lambda: None)
    assert links.email_link_options(Response()) == {
        "enabled": False,
        "privacy_url": None,
    }
    with pytest.raises(HTTPException) as error:
        request_link(context)
    assert error.value.status_code == 503
    assert not context[3]


@pytest.mark.parametrize(
    "email",
    [
        "bad",
        "a@b",
        "a..b@example.org",
        "a\r\nBcc:x@example.org",
        "a@-example.org",
        "a" * 65 + "@example.org",
    ],
)
def test_email_validation(email):
    with pytest.raises(ValidationError):
        EmailLinkRequest(email=email)


def test_email_normalization():
    assert EmailLinkRequest(email=" Anna@EXAMPLE.ORG ").email == "Anna@example.org"


def test_http_contract_validates_uuid_and_body(context):
    app = FastAPI()
    app.include_router(links.router)
    app.dependency_overrides[get_db] = lambda: context[0]

    async def post(path, body):
        events = []

        async def receive():
            return {
                "type": "http.request",
                "body": json.dumps(body).encode(),
                "more_body": False,
            }

        async def send(event):
            events.append(event)

        await app(
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "scheme": "https",
                "method": "POST",
                "path": path,
                "raw_path": path.encode(),
                "query_string": b"",
                "headers": [(b"content-type", b"application/json")],
                "client": ("192.0.2.1", 1234),
                "server": ("test", 443),
            },
            receive,
            send,
        )
        return events[0]["status"]

    assert (
        asyncio.run(
            post("/groups/not-a-uuid/email-link", {"email": "anna@example.org"})
        )
        == 422
    )
    assert (
        asyncio.run(post(f"/groups/{context[1].id}/email-link", {"email": "bad"}))
        == 422
    )
    assert (
        asyncio.run(
            post(f"/groups/{context[1].id}/email-link", {"email": "anna@example.org"})
        )
        == 201
    )
