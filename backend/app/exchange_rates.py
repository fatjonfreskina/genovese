"""Public historical rates; only a currency pair and date leave Equa."""

import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.error import URLError
from urllib.request import Request, urlopen

from .currency import RATE_QUANTUM, validate_currency, validate_rate


@dataclass(frozen=True)
class ExchangeRate:
    currency: str
    target_currency: str
    rate: Decimal
    date: date
    source: str


def lookup_exchange_rate(currency: str, target_currency: str, expense_date: date):
    currency = validate_currency(currency)
    target_currency = validate_currency(target_currency)
    if currency == target_currency:
        return ExchangeRate(
            currency, target_currency, Decimal("1"), expense_date, "identity"
        )
    url = (
        f"https://api.frankfurter.dev/v2/rate/{currency}/{target_currency}"
        f"?date={expense_date.isoformat()}"
    )
    try:
        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "Equa/1.0",
            },
        )
        with urlopen(request, timeout=3) as response:
            body = response.read(65537)
        if len(body) > 65536:
            return None
        payload = json.loads(body, parse_float=Decimal)
        rate_date = date.fromisoformat(payload["date"])
        rate = Decimal(str(payload["rate"]))
        if not rate.is_finite():
            return None
        rate = validate_rate(rate.quantize(RATE_QUANTUM, rounding=ROUND_HALF_UP))
        if payload["base"] != currency or payload["quote"] != target_currency:
            return None
        if rate_date > expense_date:
            return None
        return ExchangeRate(currency, target_currency, rate, rate_date, "frankfurter")
    except (
        URLError,
        TimeoutError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
        InvalidOperation,
    ):
        # Recording an original expense must remain possible when FX is unavailable.
        return None
