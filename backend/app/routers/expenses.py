from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..currency import MAX_AMOUNT, equal_shares, round_money, validate_money
from ..database import get_db
from ..exchange_rates import lookup_exchange_rate

router = APIRouter(prefix="/groups/{group_id}/expenses", tags=["expenses"])


def get_editable_group(group_id: str, db: Session):
    # Serialize edits with closure, which snapshots these expenses into payments.
    group = (
        db.query(models.Group)
        .filter(models.Group.id == group_id)
        .populate_existing()
        .with_for_update()
        .first()
    )
    if not group:
        raise HTTPException(status_code=404, detail="Gruppo non trovato")
    if group.status != "active":
        raise HTTPException(
            status_code=409,
            detail="Le spese sono bloccate durante la chiusura dei conti",
        )
    return group


def validate_participants(group: models.Group, payer_id: int, member_ids: list[int]):
    valid_ids = {member.id for member in group.members}
    if payer_id not in valid_ids:
        raise HTTPException(
            status_code=400, detail="Il pagante non è membro del gruppo"
        )
    if not member_ids:
        raise HTTPException(status_code=400, detail="Seleziona almeno un membro")
    if len(member_ids) != len(set(member_ids)):
        raise HTTPException(
            status_code=400, detail="I partecipanti non possono essere duplicati"
        )
    if not set(member_ids) <= valid_ids:
        raise HTTPException(
            status_code=400,
            detail="Una quota appartiene a un membro di un altro gruppo",
        )


def expense_currency(group, payload, existing=None):
    currency = payload.currency or (existing.currency if existing else group.currency)
    try:
        validate_money(payload.amount, currency)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return currency


def resolve_exchange_fields(group, payload, currency, existing=None):
    expense_date = payload.expense_date or (
        existing.expense_date if existing else date.today()
    )
    fields = {"currency": currency, "expense_date": expense_date}
    if currency == group.currency:
        if payload.exchange_rate is not None and payload.exchange_rate != 1:
            raise HTTPException(
                status_code=400,
                detail="Il cambio nella valuta del gruppo deve essere 1",
            )
        fields.update(
            exchange_rate=Decimal("1"),
            exchange_rate_date=expense_date,
            exchange_rate_source="identity",
        )
    elif payload.exchange_rate is not None:
        rate_date = payload.exchange_rate_date or expense_date
        if rate_date > expense_date:
            raise HTTPException(
                status_code=400,
                detail="La data del cambio non può essere successiva alla spesa",
            )
        fields.update(
            exchange_rate=payload.exchange_rate,
            exchange_rate_date=rate_date,
            exchange_rate_source="manual",
        )
    elif (
        existing is not None
        and existing.currency == currency
        and existing.expense_date == expense_date
        and not payload.refresh_exchange_rate
    ):
        # Editing amount/description/splits never silently changes the saved rate.
        fields.update(
            exchange_rate=existing.exchange_rate,
            exchange_rate_date=existing.exchange_rate_date,
            exchange_rate_source=existing.exchange_rate_source,
        )
    else:
        rate = lookup_exchange_rate(currency, group.currency, expense_date)
        if (
            rate is None
            and existing is not None
            and existing.currency == currency
            and existing.expense_date == expense_date
        ):
            # A failed explicit refresh must not erase a still-relevant snapshot.
            fields.update(
                exchange_rate=existing.exchange_rate,
                exchange_rate_date=existing.exchange_rate_date,
                exchange_rate_source=existing.exchange_rate_source,
            )
        else:
            fields.update(
                exchange_rate=rate.rate if rate else None,
                exchange_rate_date=rate.date if rate else None,
                exchange_rate_source=rate.source if rate else None,
            )
    if (
        fields["exchange_rate"] is not None
        and round_money(payload.amount * fields["exchange_rate"], group.currency)
        > MAX_AMOUNT
    ):
        raise HTTPException(
            status_code=400, detail="L'importo convertito supera il limite consentito"
        )
    return fields


def custom_shares(group, payload, currency):
    validate_participants(
        group, payload.paid_by_member_id, [split.member_id for split in payload.splits]
    )
    try:
        for split in payload.splits:
            validate_money(split.share_amount, currency, allow_zero=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if (
        sum((split.share_amount for split in payload.splits), Decimal("0"))
        != payload.amount
    ):
        raise HTTPException(
            status_code=400, detail="La somma delle quote non corrisponde al totale"
        )
    return [(split.member_id, split.share_amount) for split in payload.splits]


def save_expense(group, payload, currency, shares, db, existing=None):
    fields = resolve_exchange_fields(group, payload, currency, existing)
    expense = existing or models.Expense(group_id=group.id)
    expense.paid_by_member_id = payload.paid_by_member_id
    expense.description = payload.description
    expense.amount = payload.amount
    for name, value in fields.items():
        setattr(expense, name, value)
    expense.splits = [
        models.ExpenseSplit(member_id=mid, share_amount=amount)
        for mid, amount in shares
    ]
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.post("/", response_model=schemas.ExpenseOut)
def add_expense(
    group_id: str, expense: schemas.ExpenseCreate, db: Session = Depends(get_db)
):
    group = get_editable_group(group_id, db)
    currency = expense_currency(group, expense)
    return save_expense(
        group, expense, currency, custom_shares(group, expense, currency), db
    )


@router.post("/equal", response_model=schemas.ExpenseOut)
def add_expense_equal(
    group_id: str, expense: schemas.ExpenseCreateEqual, db: Session = Depends(get_db)
):
    group = get_editable_group(group_id, db)
    currency = expense_currency(group, expense)
    ids = [member.id for member in group.members]
    validate_participants(group, expense.paid_by_member_id, ids)
    return save_expense(
        group, expense, currency, equal_shares(expense.amount, ids, currency), db
    )


@router.post("/subset", response_model=schemas.ExpenseOut)
def add_expense_subset(
    group_id: str, expense: schemas.ExpenseCreateSubset, db: Session = Depends(get_db)
):
    group = get_editable_group(group_id, db)
    currency = expense_currency(group, expense)
    validate_participants(group, expense.paid_by_member_id, expense.member_ids)
    return save_expense(
        group,
        expense,
        currency,
        equal_shares(expense.amount, expense.member_ids, currency),
        db,
    )


@router.put("/{expense_id}", response_model=schemas.ExpenseOut)
def update_expense(
    group_id: str,
    expense_id: int,
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
):
    group = get_editable_group(group_id, db)
    existing = (
        db.query(models.Expense)
        .filter(models.Expense.id == expense_id, models.Expense.group_id == group_id)
        .first()
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Spesa non trovata")
    currency = expense_currency(group, expense, existing)
    return save_expense(
        group, expense, currency, custom_shares(group, expense, currency), db, existing
    )


@router.delete("/{expense_id}", status_code=204)
def delete_expense(group_id: str, expense_id: int, db: Session = Depends(get_db)):
    get_editable_group(group_id, db)
    expense = (
        db.query(models.Expense)
        .filter(models.Expense.id == expense_id, models.Expense.group_id == group_id)
        .first()
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Spesa non trovata")
    db.delete(expense)
    db.commit()
