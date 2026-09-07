"""Private client for transactional email. Never log recipients or payloads."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from json import JSONDecodeError
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from cryptography.fernet import Fernet


@dataclass(frozen=True)
class EmailSettings:
    secret: str
    service_url: str
    service_token: str
    privacy_url: str
    timeout: int = 10

    def cipher(self) -> Fernet:
        return Fernet(
            base64.urlsafe_b64encode(hashlib.sha256(self.secret.encode()).digest())
        )


def _valid_url(value: str, allow_http: bool = False) -> bool:
    try:
        parsed = urlsplit(value)
        valid_port = parsed.port is None or 1 <= parsed.port <= 65535
    except ValueError:
        return False
    local_http = parsed.scheme == "http" and parsed.hostname in {
        "localhost",
        "127.0.0.1",
        "::1",
    }
    return bool(
        value
        and parsed.hostname
        and (
            parsed.scheme == "https"
            or local_http
            or (allow_http and parsed.scheme == "http")
        )
        and not parsed.username
        and not parsed.password
        and not parsed.query
        and not parsed.fragment
        and valid_port
        and not any(character.isspace() for character in value)
    )


def get_email_settings() -> EmailSettings | None:
    if os.getenv("EMAIL_LINK_ENABLED", "false").lower() not in {"true", "1"}:
        return None
    try:
        secret = os.environ["EMAIL_LINK_SECRET"]
        service_url = os.environ["EMAIL_SERVICE_URL"].rstrip("/")
        service_token = os.environ["EMAIL_SERVICE_TOKEN"]
        privacy_url = os.environ["EMAIL_PRIVACY_URL"]
        timeout = int(os.getenv("EMAIL_SERVICE_TIMEOUT", "10"))
        allow_http = os.getenv("EMAIL_SERVICE_ALLOW_HTTP", "false").lower() in {
            "true",
            "1",
        }
        if (
            len(secret) < 32
            or len(service_token) < 32
            or not service_token.isascii()
            or any(character.isspace() for character in service_token)
            or not _valid_url(service_url, allow_http=allow_http)
            or not _valid_url(privacy_url)
            or not 1 <= timeout <= 30
        ):
            return None
        return EmailSettings(
            secret=secret,
            service_url=service_url,
            service_token=service_token,
            privacy_url=privacy_url,
            timeout=timeout,
        )
    except (KeyError, ValueError):
        return None


class EmailDeliveryError(Exception):
    pass


class _NoRedirect(HTTPRedirectHandler):
    """Do not forward the Bearer token to a redirect destination."""

    def redirect_request(self, request, file_pointer, code, message, headers, url):
        return None


def _send(settings: EmailSettings, payload: dict[str, str]) -> None:
    request = Request(
        f"{settings.service_url}/forward-email-equa",
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.service_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    # Ignore environment proxies: this token belongs only on the private hop.
    opener = build_opener(ProxyHandler({}), _NoRedirect())
    try:
        with opener.open(request, timeout=settings.timeout) as response:
            body = response.read(4097)
            if response.status != 200 or len(body) > 4096:
                raise EmailDeliveryError("Invio email non disponibile")
        result = json.loads(body.decode("utf-8"))
        if result != {"message": "Email sent"}:
            raise EmailDeliveryError("Invio email non disponibile")
    except EmailDeliveryError:
        raise
    except (
        HTTPError,
        URLError,
        OSError,
        TimeoutError,
        JSONDecodeError,
        UnicodeDecodeError,
        ValueError,
    ):
        raise EmailDeliveryError("Invio email non disponibile") from None


def send_verification_email(settings: EmailSettings, recipient: str, code: str) -> None:
    _send(
        settings,
        {"kind": "verification", "email": recipient, "code": code},
    )


def send_group_link_email(
    settings: EmailSettings, recipient: str, group_id: str
) -> None:
    _send(
        settings,
        {"kind": "group_link", "email": recipient, "group_id": group_id},
    )
