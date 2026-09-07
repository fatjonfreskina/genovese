"""A code in the requesting browser proves mailbox access, not group ownership."""

import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta
from uuid import UUID

from cryptography.fernet import InvalidToken
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..email_delivery import (
    EmailDeliveryError,
    EmailSettings,
    get_email_settings,
    send_group_link_email,
    send_verification_email,
)

router = APIRouter(tags=["email-link"])
CHALLENGE_SECONDS = 900
MAX_ATTEMPTS = 5


def utcnow() -> datetime:
    return datetime.utcnow()


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def digest(settings: EmailSettings, value: str) -> str:
    return hmac.new(
        settings.secret.encode(), value.encode(), hashlib.sha256
    ).hexdigest()


def require_settings() -> EmailSettings:
    settings = get_email_settings()
    if settings is None:
        raise HTTPException(
            503, "Invio email non disponibile. Conserva il link in una chat."
        )
    return settings


def cleanup_expired(db: Session, now: datetime) -> None:
    db.query(models.EmailLinkChallenge).filter(
        models.EmailLinkChallenge.expires_at <= now
    ).delete()
    db.query(models.EmailLinkRateLimit).filter(
        models.EmailLinkRateLimit.expires_at <= now
    ).delete()


def reserve_limit(
    db: Session,
    settings: EmailSettings,
    scope: str,
    value: str,
    seconds: int,
    maximum: int,
    now: datetime,
) -> None:
    epoch = datetime(1970, 1, 1)
    bucket = int((now - epoch).total_seconds()) // seconds
    expires = epoch + timedelta(seconds=(bucket + 1) * seconds)
    key = digest(settings, f"limit:{scope}:{value}:{seconds}:{bucket}")
    # Savepoint + conditional increment enforce limits across API workers too.
    try:
        with db.begin_nested():
            db.add(models.EmailLinkRateLimit(key=key, count=0, expires_at=expires))
            db.flush()
    except IntegrityError:
        pass
    updated = (
        db.query(models.EmailLinkRateLimit)
        .filter(
            models.EmailLinkRateLimit.key == key,
            models.EmailLinkRateLimit.count < maximum,
        )
        .update(
            {models.EmailLinkRateLimit.count: models.EmailLinkRateLimit.count + 1},
            synchronize_session=False,
        )
    )
    if not updated:
        db.rollback()
        raise HTTPException(
            429,
            "Troppe richieste. Attendi prima di richiedere un nuovo codice.",
            headers={"Retry-After": str(max(1, int((expires - now).total_seconds())))},
        )


@router.get("/email-link/options", response_model=schemas.EmailLinkOptions)
def email_link_options(response: Response):
    response.headers["Cache-Control"] = "no-store"
    settings = get_email_settings()
    return {
        "enabled": settings is not None,
        "privacy_url": settings.privacy_url if settings else None,
    }


@router.post(
    "/groups/{group_id}/email-link",
    response_model=schemas.EmailLinkRequested,
    status_code=201,
)
def request_email_link(
    group_id: UUID,
    payload: schemas.EmailLinkRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    settings = require_settings()
    group_id = str(group_id)
    if db.get(models.Group, group_id) is None:
        raise HTTPException(404, "Gruppo non trovato")
    now = utcnow()
    cleanup_expired(db, now)
    address = request.client.host if request.client else "unknown"
    # Keyed, short-lived hashes: no recipient or IP is stored in the database.
    for scope, value, seconds, maximum in [
        ("ip", address, 60, 10),
        ("ip", address, 3600, 30),
        ("recipient", payload.email.casefold(), 60, 1),
        ("recipient", payload.email.casefold(), 3600, 3),
        ("recipient", payload.email.casefold(), 86400, 5),
        ("group", group_id, 3600, 10),
        ("global", "all", 3600, 200),
    ]:
        reserve_limit(db, settings, scope, value, seconds, maximum, now)
    code = f"{secrets.randbelow(1_000_000):06d}"
    token = (
        settings.cipher()
        .encrypt(
            json.dumps(
                {
                    "email": payload.email,
                    "group_id": group_id,
                    "nonce": secrets.token_urlsafe(16),
                }
            ).encode()
        )
        .decode()
    )
    challenge_hash = token_hash(token)
    db.add(
        models.EmailLinkChallenge(
            token_hash=challenge_hash,
            group_id=group_id,
            code_hash=digest(settings, token + ":" + code),
            attempts=0,
            expires_at=now + timedelta(seconds=CHALLENGE_SECONDS),
        )
    )
    db.commit()
    try:
        send_verification_email(settings, payload.email, code)
    except EmailDeliveryError:
        db.query(models.EmailLinkChallenge).filter_by(
            token_hash=challenge_hash
        ).delete()
        db.commit()
        raise HTTPException(
            503, "Non siamo riusciti a inviare il codice. Riprova più tardi."
        ) from None
    response.headers["Cache-Control"] = "no-store"
    return {"challenge_token": token, "expires_in": CHALLENGE_SECONDS}


@router.post("/groups/{group_id}/email-link/confirm", status_code=204)
def confirm_email_link(
    group_id: UUID,
    payload: schemas.EmailLinkConfirmation,
    db: Session = Depends(get_db),
):
    settings = require_settings()
    group_id = str(group_id)
    now = utcnow()
    challenge_hash = token_hash(payload.challenge_token)
    query = db.query(models.EmailLinkChallenge).filter(
        models.EmailLinkChallenge.token_hash == challenge_hash,
        models.EmailLinkChallenge.group_id == group_id,
        models.EmailLinkChallenge.expires_at > now,
        models.EmailLinkChallenge.attempts < MAX_ATTEMPTS,
    )
    if not query.update(
        {models.EmailLinkChallenge.attempts: models.EmailLinkChallenge.attempts + 1},
        synchronize_session=False,
    ):
        cleanup_expired(db, now)
        db.commit()
        raise HTTPException(
            410,
            "Codice scaduto o già utilizzato. Controlla la posta prima di richiederne uno nuovo.",
        )
    db.commit()
    challenge = db.get(models.EmailLinkChallenge, challenge_hash)
    if challenge is None:
        raise HTTPException(410, "Richiesta già utilizzata o annullata.")
    expected = digest(settings, payload.challenge_token + ":" + payload.code)
    if not hmac.compare_digest(expected, challenge.code_hash):
        exhausted = challenge.attempts >= MAX_ATTEMPTS
        if exhausted:
            db.delete(challenge)
            db.commit()
        raise HTTPException(
            410 if exhausted else 400,
            (
                "Troppi tentativi. Richiedi un nuovo codice."
                if exhausted
                else "Codice non corretto. Riprova."
            ),
        )
    try:
        delivery = json.loads(
            settings.cipher().decrypt(payload.challenge_token.encode())
        )
        if delivery["group_id"] != group_id:
            raise InvalidToken
    except (InvalidToken, ValueError, KeyError):
        raise HTTPException(
            410, "Richiesta non valida. Richiedi un nuovo codice."
        ) from None
    # Consume atomically BEFORE sending: a replay cannot cause another email.
    removed = (
        db.query(models.EmailLinkChallenge)
        .filter_by(token_hash=challenge_hash)
        .delete()
    )
    db.commit()
    if not removed:
        raise HTTPException(410, "Richiesta già utilizzata o annullata.")
    if db.get(models.Group, group_id) is None:
        raise HTTPException(404, "Gruppo non trovato")
    try:
        send_group_link_email(settings, delivery["email"], group_id)
    except EmailDeliveryError:
        raise HTTPException(
            503, "Invio del link non riuscito. Richiedi un nuovo codice più tardi."
        ) from None


@router.post("/groups/{group_id}/email-link/cancel", status_code=204)
def cancel_email_link(
    group_id: UUID, payload: schemas.EmailLinkToken, db: Session = Depends(get_db)
):
    db.query(models.EmailLinkChallenge).filter_by(
        group_id=str(group_id), token_hash=token_hash(payload.challenge_token)
    ).delete()
    db.commit()
