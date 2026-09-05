from decimal import Decimal
from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..currency import allocate_amounts, round_money
from ..database import get_db

router = APIRouter(prefix="/groups/{group_id}/balances", tags=["balances"])


def calculate_balances(
    group: models.Group, mode: str = "separate"
) -> List[schemas.Balance]:
    member_names = {member.id: member.name for member in group.members}
    target_currency = group.currency or "EUR"
    nets = {}

    for expense in group.expenses:
        currency = expense.currency or target_currency
        amount = expense.amount
        shares = [(split.member_id, split.share_amount) for split in expense.splits]
        if mode == "unified" and currency != target_currency:
            if expense.exchange_rate is None:
                raise HTTPException(
                    status_code=409,
                    detail="Completa i cambi mancanti nelle spese prima di unificare i conti",
                )
            currency = target_currency
            amount = round_money(expense.amount * expense.exchange_rate, currency)
            shares = allocate_amounts(
                [(mid, share * expense.exchange_rate) for mid, share in shares],
                amount,
                currency,
            )
        net = nets.setdefault(currency, {mid: Decimal("0") for mid in member_names})
        net[expense.paid_by_member_id] += amount
        for mid, share in shares:
            net[mid] -= share

    transactions = []
    for currency, net in sorted(nets.items()):
        creditors = sorted(
            [(mid, amount) for mid, amount in net.items() if amount > 0],
            key=lambda item: (-item[1], item[0]),
        )
        debtors = sorted(
            [(mid, -amount) for mid, amount in net.items() if amount < 0],
            key=lambda item: (-item[1], item[0]),
        )
        i, j = 0, 0
        while i < len(creditors) and j < len(debtors):
            cred_id, cred_amt = creditors[i]
            debt_id, debt_amt = debtors[j]
            amount = min(cred_amt, debt_amt)
            if amount > 0:
                transactions.append(
                    schemas.Balance(
                        from_member_id=debt_id,
                        from_member_name=member_names[debt_id],
                        to_member_id=cred_id,
                        to_member_name=member_names[cred_id],
                        amount=amount,
                        currency=currency,
                    )
                )
            creditors[i] = (cred_id, cred_amt - amount)
            debtors[j] = (debt_id, debt_amt - amount)
            if creditors[i][1] == 0:
                i += 1
            if debtors[j][1] == 0:
                j += 1
    return transactions


@router.get("/", response_model=List[schemas.Balance])
def get_balances(
    group_id: str,
    db: Session = Depends(get_db),
    mode: Literal["separate", "unified"] = "separate",
):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Gruppo non trovato")
    return calculate_balances(group, mode)
