from datetime import date, timedelta
from decimal import Decimal

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import models, schemas
from backend.app.currency import equal_shares, latest_expense_date
from backend.app.database import Base
from backend.app import exchange_rates
from backend.app.exchange_rates import ExchangeRate
from backend.app.routers import expenses, groups
from backend.app.routers.balances import calculate_balances


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def group(db):
    group = models.Group(
        name="Viaggio",
        currency="EUR",
        members=[
            models.Member(name="Anna"),
            models.Member(name="Bruno"),
            models.Member(name="Carlo"),
        ],
    )
    db.add(group)
    db.commit()
    return group


def make_payload(group, **overrides):
    fields = dict(
        paid_by_member_id=group.members[0].id,
        description="Cena",
        amount="30",
        currency="USD",
        expense_date="2026-01-10",
    )
    fields.update(overrides)
    return schemas.ExpenseCreateEqual(**fields)


def update_payload(expense, **overrides):
    fields = dict(
        paid_by_member_id=expense.paid_by_member_id,
        description="Cena aggiornata",
        amount=expense.amount,
        splits=[
            dict(member_id=split.member_id, share_amount=split.share_amount)
            for split in expense.splits
        ],
    )
    fields.update(overrides)
    return schemas.ExpenseCreate(**fields)


def test_lookup_exchange_rate_identifies_as_http_client(monkeypatch):
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, limit):
            return b'{"date":"2026-09-05","base":"USD","quote":"EUR","rate":0.86006}'

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(exchange_rates, "urlopen", fake_urlopen)

    rate = exchange_rates.lookup_exchange_rate("USD", "EUR", date(2026, 9, 5))

    assert rate.rate == Decimal("0.860060000000")
    assert captured["request"].get_header("User-agent") == "Equa/1.0"
    assert captured["timeout"] == 3


def test_original_currency_and_historical_rate_are_saved(db, group, monkeypatch):
    calls = []

    def lookup(currency, target, day):
        calls.append((currency, target, day))
        return ExchangeRate(
            currency, target, Decimal("0.92"), date(2026, 1, 9), "frankfurter"
        )

    monkeypatch.setattr(expenses, "lookup_exchange_rate", lookup)
    expense = expenses.add_expense_equal(group.id, make_payload(group), db)
    output = schemas.ExpenseOut.model_validate(expense)
    assert calls == [("USD", "EUR", date(2026, 1, 10))]
    assert output.amount == Decimal("30")
    assert output.currency == "USD"
    assert output.exchange_rate == Decimal("0.92")
    assert output.exchange_rate_date == date(2026, 1, 9)
    assert output.exchange_rate_source == "frankfurter"
    assert output.converted_amount == Decimal("27.60")
    assert {b.currency for b in calculate_balances(group)} == {"USD"}
    assert {b.currency for b in calculate_balances(group, "unified")} == {"EUR"}
    assert sum(b.amount for b in calculate_balances(group, "unified")) == Decimal(
        "18.40"
    )


def test_provider_failure_saves_original_but_blocks_unified(db, group, monkeypatch):
    monkeypatch.setattr(expenses, "lookup_exchange_rate", lambda *args: None)
    expense = expenses.add_expense_equal(group.id, make_payload(group), db)
    assert expense.exchange_rate is None
    assert len(calculate_balances(group)) == 2
    with pytest.raises(HTTPException, match="409"):
        calculate_balances(group, "unified")
    with pytest.raises(HTTPException, match="409"):
        groups.update_group_status(
            group.id,
            schemas.GroupStatusUpdate(status="closing", balance_mode="unified"),
            db,
        )
    assert group.status == "active"
    assert group.closing_count == 0
    assert group.settlements == []
    groups.update_group_status(
        group.id, schemas.GroupStatusUpdate(status="closing"), db
    )
    assert group.closing_balance_mode == "separate"
    assert {s.currency for s in group.settlements} == {"USD"}


def test_identity_uses_group_default_without_network(db, group, monkeypatch):
    group.currency = "JPY"
    db.commit()
    monkeypatch.setattr(
        expenses,
        "lookup_exchange_rate",
        lambda *args: pytest.fail("No FX request for identity"),
    )
    payload = schemas.ExpenseCreateEqual(
        paid_by_member_id=group.members[0].id, description="Metro", amount="1"
    )
    expense = expenses.add_expense_equal(group.id, payload, db)
    assert expense.currency == "JPY"
    assert expense.expense_date == date.today()
    assert expense.exchange_rate == 1
    assert expense.exchange_rate_source == "identity"
    assert sorted(split.share_amount for split in expense.splits) == [0, 0, 1]


def test_manual_rate_and_omitted_update_preserve_rate_currency_date(
    db, group, monkeypatch
):
    monkeypatch.setattr(
        expenses,
        "lookup_exchange_rate",
        lambda *args: pytest.fail("Manual/preserved rate must not fetch"),
    )
    expense = expenses.add_expense_equal(
        group.id, make_payload(group, exchange_rate="0.9"), db
    )
    updated = expenses.update_expense(group.id, expense.id, update_payload(expense), db)
    assert updated.currency == "USD"
    assert updated.expense_date == date(2026, 1, 10)
    assert updated.exchange_rate == Decimal("0.9")
    assert updated.exchange_rate_source == "manual"


@pytest.mark.parametrize(
    "change", [{"expense_date": "2026-01-11"}, {"currency": "GBP"}]
)
def test_change_date_currency_or_explicit_refresh_refetches(
    db, group, monkeypatch, change
):
    expense = expenses.add_expense_equal(
        group.id, make_payload(group, exchange_rate="0.9"), db
    )
    calls = []

    def unavailable(*args):
        calls.append(args)
        return None

    monkeypatch.setattr(expenses, "lookup_exchange_rate", unavailable)
    updated = expenses.update_expense(
        group.id, expense.id, update_payload(expense, **change), db
    )
    assert len(calls) == 1
    assert updated.exchange_rate is None
    assert updated.exchange_rate_date is None
    assert updated.exchange_rate_source is None


def test_failed_explicit_refresh_keeps_existing_valid_snapshot(db, group, monkeypatch):
    expense = expenses.add_expense_equal(
        group.id, make_payload(group, exchange_rate="0.9"), db
    )
    monkeypatch.setattr(expenses, "lookup_exchange_rate", lambda *args: None)
    updated = expenses.update_expense(
        group.id, expense.id, update_payload(expense, refresh_exchange_rate=True), db
    )
    assert updated.exchange_rate == Decimal("0.9")
    assert updated.exchange_rate_source == "manual"
    assert updated.exchange_rate_date == date(2026, 1, 10)


def test_converted_amount_is_bounded(db, group):
    with pytest.raises(HTTPException, match="400"):
        expenses.add_expense_equal(
            group.id, make_payload(group, amount="99999999", exchange_rate="2"), db
        )
    assert group.expenses == []


def test_client_calendar_date_in_ahead_timezone_is_allowed(group):
    assert (
        make_payload(group, expense_date=latest_expense_date()).expense_date
        == latest_expense_date()
    )


def test_unified_closure_freezes_payments_and_blocks_edits(db, group, monkeypatch):
    expense = expenses.add_expense_equal(
        group.id, make_payload(group, exchange_rate="0.9"), db
    )
    monkeypatch.setattr(
        expenses,
        "lookup_exchange_rate",
        lambda *args: pytest.fail("Balances do not fetch"),
    )
    groups.update_group_status(
        group.id,
        schemas.GroupStatusUpdate(status="closing", balance_mode="unified"),
        db,
    )
    assert group.closing_balance_mode == "unified"
    assert {s.currency for s in group.settlements} == {"EUR"}
    assert sum(s.amount for s in group.settlements) == Decimal("18")
    assert schemas.GroupOut.model_validate(group).closing_balance_mode == "unified"
    for settlement in group.settlements:
        assert schemas.SettlementOut.model_validate(settlement).currency == "EUR"
    with pytest.raises(HTTPException, match="409"):
        expenses.update_expense(
            group.id, expense.id, update_payload(expense, exchange_rate="0.8"), db
        )
    with pytest.raises(HTTPException, match="409"):
        expenses.delete_expense(group.id, expense.id, db)
    with pytest.raises(HTTPException, match="409"):
        expenses.add_expense_equal(group.id, make_payload(group), db)


def test_separate_balances_do_not_net_different_currencies(db, group):
    expenses.add_expense_equal(group.id, make_payload(group, exchange_rate="1"), db)
    expenses.add_expense_equal(
        group.id,
        make_payload(group, currency="EUR", paid_by_member_id=group.members[1].id),
        db,
    )
    assert {b.currency for b in calculate_balances(group)} == {"USD", "EUR"}
    assert {b.currency for b in calculate_balances(group, "unified")} == {"EUR"}


def test_rounding_is_deterministic_and_no_zero_transfers(db, group):
    expense = expenses.add_expense_equal(
        group.id, make_payload(group, amount="0.03", exchange_rate="0.5"), db
    )
    first = calculate_balances(group, "unified")
    expense.splits.reverse()
    assert calculate_balances(group, "unified") == first
    assert len(first) == 1
    assert first[0].amount == Decimal("0.01")
    assert expense.converted_amount == Decimal("0.02")
    expenses.update_expense(
        group.id, expense.id, update_payload(expense, exchange_rate="0.01"), db
    )
    assert calculate_balances(group, "unified") == []


@pytest.mark.parametrize(
    "amount,currency,expected",
    [
        ("0.02", "EUR", [Decimal("0.01"), Decimal("0.01"), Decimal("0")]),
        ("2", "JPY", [Decimal("1"), Decimal("1"), Decimal("0")]),
    ],
)
def test_tiny_equal_splits_are_never_negative(amount, currency, expected):
    assert equal_shares(Decimal(amount), [1, 2, 3], currency) == list(
        zip([1, 2, 3], expected)
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"amount": "NaN"},
        {"amount": "Infinity"},
        {"amount": "0"},
        {"amount": "-1"},
        {"amount": "100000000"},
        {"currency": "BTC"},
        {"exchange_rate": "0"},
        {"exchange_rate": "NaN"},
        {"exchange_rate": "Infinity"},
        {"exchange_rate": "1000000001"},
        {"exchange_rate": "0.0000000000001"},
        {"expense_date": latest_expense_date() + timedelta(days=1)},
    ],
)
def test_invalid_expense_fields_rejected(group, overrides):
    with pytest.raises(ValidationError):
        make_payload(group, **overrides)


def test_custom_and_subset_split_validation(db, group):
    ids = [member.id for member in group.members]
    with pytest.raises(HTTPException, match="400"):
        expenses.add_expense_subset(
            group.id,
            schemas.ExpenseCreateSubset(
                paid_by_member_id=ids[0],
                description="Cena",
                amount="1",
                member_ids=[ids[0], ids[0]],
            ),
            db,
        )
    for split_data in [
        [(ids[0], "0.5"), (ids[0], "0.5")],
        [(9999, "1")],
        [(ids[0], "0.99")],
        [(ids[0], "0.995"), (ids[1], "0.005")],
    ]:
        payload = schemas.ExpenseCreate(
            paid_by_member_id=ids[0],
            description="Cena",
            amount="1",
            splits=[
                dict(member_id=mid, share_amount=share) for mid, share in split_data
            ],
        )
        with pytest.raises(HTTPException, match="400"):
            expenses.add_expense(group.id, payload, db)
    with pytest.raises(HTTPException, match="400"):
        expenses.add_expense_equal(
            group.id,
            make_payload(group, currency="JPY", amount="1.50", exchange_rate="1"),
            db,
        )
    assert group.expenses == []


def test_lookup_endpoint_is_read_only_and_rejects_invalid_dates(db, group, monkeypatch):
    monkeypatch.setattr(
        groups,
        "lookup_exchange_rate",
        lambda *args: ExchangeRate(
            "ALL", "EUR", Decimal("0.01"), date(2026, 1, 9), "frankfurter"
        ),
    )
    result = groups.get_exchange_rate(group.id, "ALL", date(2026, 1, 10), db)
    assert result.rate == Decimal("0.01")
    assert group.expenses == []
    with pytest.raises(HTTPException, match="422"):
        groups.get_exchange_rate(
            group.id, "ALL", latest_expense_date() + timedelta(days=1), db
        )
    with pytest.raises(HTTPException, match="422"):
        groups.get_exchange_rate(group.id, "BTC", date(2026, 1, 10), db)
