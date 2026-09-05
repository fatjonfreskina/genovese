"""Currency precision and deterministic, conserving money allocation."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

SUPPORTED_CURRENCIES = frozenset(
    "EUR USD GBP CHF ALL JPY CAD AUD NZD CNY HKD SGD INR THB IDR MYR PHP "
    "KRW VND AED SAR TRY SEK NOK DKK PLN CZK HUF RON BGN BRL MXN ZAR CLP ISK".split()
)
ZERO_DECIMAL_CURRENCIES = frozenset({"JPY", "KRW", "VND", "CLP", "ISK"})
MAX_AMOUNT = Decimal("99999999.99")
RATE_QUANTUM = Decimal("0.000000000001")
MAX_RATE = Decimal("1000000000")


def latest_expense_date():
    # A client in UTC+14 may already be in tomorrow's calendar date.
    return datetime.now(timezone.utc).date() + timedelta(days=1)


def validate_currency(value: str) -> str:
    value = value.strip().upper()
    if value not in SUPPORTED_CURRENCIES:
        raise ValueError("Valuta non supportata")
    return value


def quantum(currency: str) -> Decimal:
    return Decimal("1") if currency in ZERO_DECIMAL_CURRENCIES else Decimal("0.01")


def round_money(amount: Decimal, currency: str) -> Decimal:
    return amount.quantize(quantum(currency), rounding=ROUND_HALF_UP)


def validate_money(amount: Decimal, currency: str, *, allow_zero=False) -> Decimal:
    if not amount.is_finite() or amount > MAX_AMOUNT or amount < 0:
        raise ValueError("Importo non valido o superiore al limite consentito")
    if not allow_zero and amount == 0:
        raise ValueError("L'importo deve essere maggiore di zero")
    if amount != round_money(amount, currency):
        raise ValueError(f"L'importo non rispetta i decimali della valuta {currency}")
    return amount


def validate_rate(rate: Decimal) -> Decimal:
    if not rate.is_finite() or not RATE_QUANTUM <= rate <= MAX_RATE:
        raise ValueError(
            "Il cambio deve essere positivo e compreso tra 0,000000000001 e 1000000000"
        )
    if rate != rate.quantize(RATE_QUANTUM):
        raise ValueError("Il cambio può avere al massimo 12 decimali")
    return rate


def allocate_amounts(
    amounts: list[tuple[int, Decimal]], total: Decimal, currency: str
) -> list[tuple[int, Decimal]]:
    """Round shares down, then give minor units to largest fractional remainders.

    Ties use member IDs, so neither request order nor database row order changes
    the result. Works for zero shares and totals smaller than the member count.
    """
    unit = quantum(currency)
    rounded = [amount.quantize(unit, rounding=ROUND_DOWN) for _, amount in amounts]
    units_left = int((total - sum(rounded, Decimal("0"))) / unit)
    order = sorted(
        range(len(amounts)),
        key=lambda i: (-(amounts[i][1] - rounded[i]), amounts[i][0]),
    )
    if not 0 <= units_left <= len(order):
        raise ValueError("Le quote non corrispondono al totale")
    for i in order[:units_left]:
        rounded[i] += unit
    return [(member_id, rounded[i]) for i, (member_id, _) in enumerate(amounts)]


def equal_shares(amount: Decimal, member_ids: list[int], currency: str):
    share = amount / len(member_ids)
    return allocate_amounts([(mid, share) for mid in member_ids], amount, currency)
