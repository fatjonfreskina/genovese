import re

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, List
from datetime import date, datetime
from decimal import Decimal

from .currency import MAX_AMOUNT, latest_expense_date, validate_currency, validate_rate

# --- Member ---


def normalize_contact_email(value: str) -> str:
    value = value.strip()
    if len(value) > 254 or value.count("@") != 1:
        raise ValueError("Inserisci un indirizzo email valido")
    local, domain = value.rsplit("@", 1)
    try:
        domain = domain.encode("idna").decode("ascii").lower()
    except UnicodeError:
        raise ValueError("Inserisci un indirizzo email valido") from None
    if (
        not re.fullmatch(r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]{1,64}", local)
        or local.startswith(".")
        or local.endswith(".")
        or ".." in local
        or len(local + "@" + domain) > 254
        or "." not in domain
        or any(
            not re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", label)
            for label in domain.split(".")
        )
    ):
        raise ValueError("Inserisci un indirizzo email valido")
    return local + "@" + domain


class EmailLinkRequest(BaseModel):
    email: str = Field(max_length=254)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        return normalize_contact_email(value)


class EmailLinkToken(BaseModel):
    challenge_token: str = Field(
        min_length=100, max_length=2048, pattern=r"^[A-Za-z0-9_=-]+$"
    )


class EmailLinkConfirmation(EmailLinkToken):
    code: str = Field(pattern=r"^[0-9]{6}$")


class EmailLinkRequested(BaseModel):
    challenge_token: str
    expires_in: int


class EmailLinkOptions(BaseModel):
    enabled: bool
    privacy_url: Optional[str] = None


class MemberCreate(BaseModel):
    name: str
    email: Optional[str] = None


class MemberOut(BaseModel):
    id: int
    name: str
    email: Optional[str] = None

    class Config:
        from_attributes = True


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


# --- Expense Split ---


class SplitCreate(BaseModel):
    member_id: int
    share_amount: Decimal = Field(ge=0, le=MAX_AMOUNT, allow_inf_nan=False)


class SplitOut(BaseModel):
    member_id: int
    share_amount: Decimal

    class Config:
        from_attributes = True


# --- Expense ---


class ExpenseFields(BaseModel):
    paid_by_member_id: int
    description: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0, le=MAX_AMOUNT, allow_inf_nan=False)
    currency: Optional[str] = None
    expense_date: Optional[date] = None
    exchange_rate: Optional[Decimal] = None
    exchange_rate_date: Optional[date] = None
    refresh_exchange_rate: bool = False

    @field_validator("currency")
    @classmethod
    def valid_currency(cls, value):
        return validate_currency(value) if value is not None else None

    @field_validator("exchange_rate")
    @classmethod
    def valid_rate(cls, value):
        return validate_rate(value) if value is not None else None

    @field_validator("expense_date", "exchange_rate_date")
    @classmethod
    def valid_date(cls, value):
        if value is not None and value > latest_expense_date():
            raise ValueError("La data non può essere futura")
        return value


class ExpenseCreate(ExpenseFields):
    splits: List[SplitCreate]


class ExpenseOut(BaseModel):
    id: int
    paid_by_member_id: int
    description: str
    amount: Decimal
    currency: str
    expense_date: date
    exchange_rate: Optional[Decimal] = None
    exchange_rate_date: Optional[date] = None
    exchange_rate_source: Optional[Literal["identity", "frankfurter", "manual"]] = None
    converted_amount: Optional[Decimal] = None
    created_at: datetime
    splits: List[SplitOut]

    class Config:
        from_attributes = True


class ExpenseCreateSubset(ExpenseFields):
    member_ids: List[int]


class ExpenseCreateEqual(ExpenseFields):
    pass


class ExchangeRateOut(BaseModel):
    currency: str
    target_currency: str
    rate: Decimal
    date: date
    source: Literal["identity", "frankfurter"]


# --- Group ---


class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    currency: str = "EUR"
    members: List[MemberCreate]

    @field_validator("currency")
    @classmethod
    def valid_currency(cls, value):
        return validate_currency(value)


class GroupOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    currency: str
    status: Literal["active", "closing", "closed"]
    closing_count: int
    closing_balance_mode: Literal["separate", "unified"]
    created_at: datetime
    members: List[MemberOut]
    expenses: List[ExpenseOut]

    class Config:
        from_attributes = True


class GroupStatusUpdate(BaseModel):
    status: Literal["active", "closing", "closed"]
    balance_mode: Literal["separate", "unified"] = "separate"


# --- Balance ---


class Balance(BaseModel):
    from_member_id: int
    from_member_name: str
    to_member_id: int
    to_member_name: str
    amount: Decimal
    currency: str


class SettlementAction(BaseModel):
    member_id: int


class SettlementOut(BaseModel):
    id: int
    from_member_id: int
    to_member_id: int
    amount: Decimal
    currency: str
    status: Literal["pending", "confirmed", "cancelled"]
    reported_by_member_id: Optional[int] = None
    reported_at: Optional[datetime] = None
    confirmed_by_member_id: Optional[int] = None
    confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
