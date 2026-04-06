from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/groups/{group_id}/expenses", tags=["expenses"])


@router.post("/", response_model=schemas.ExpenseOut)
def add_expense(group_id: str, expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    # Verifica che il gruppo esista
    db_group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Gruppo non trovato")

    # Verifica che chi paga sia membro del gruppo
    payer = db.query(models.Member).filter(
        models.Member.id == expense.paid_by_member_id,
        models.Member.group_id == group_id
    ).first()
    if not payer:
        raise HTTPException(status_code=400, detail="Il pagante non è membro del gruppo")

    # Verifica che la somma degli split corrisponda al totale
    total_splits = sum(s.share_amount for s in expense.splits)
    if abs(total_splits - expense.amount) > Decimal("0.01"):
        raise HTTPException(status_code=400, detail="La somma degli split non corrisponde al totale")

    # Crea la spesa
    db_expense = models.Expense(
        group_id=group_id,
        paid_by_member_id=expense.paid_by_member_id,
        description=expense.description,
        amount=expense.amount,
    )
    db.add(db_expense)
    db.flush()

    # Crea gli split
    for split in expense.splits:
        db_split = models.ExpenseSplit(
            expense_id=db_expense.id,
            member_id=split.member_id,
            share_amount=split.share_amount,
        )
        db.add(db_split)

    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.post("/equal", response_model=schemas.ExpenseOut)
def add_expense_equal(group_id: str, expense: schemas.ExpenseCreateEqual, db: Session = Depends(get_db)):
    # Verifica che il gruppo esista
    db_group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Gruppo non trovato")

    # Verifica che chi paga sia membro del gruppo
    payer = db.query(models.Member).filter(
        models.Member.id == expense.paid_by_member_id,
        models.Member.group_id == group_id
    ).first()
    if not payer:
        raise HTTPException(status_code=400, detail="Il pagante non è membro del gruppo")

    # Calcola gli split equamente
    members = db_group.members
    n = len(members)
    base_share = round(expense.amount / n, 2)
    remainder = expense.amount - (base_share * n)

    # Crea la spesa
    db_expense = models.Expense(
        group_id=group_id,
        paid_by_member_id=expense.paid_by_member_id,
        description=expense.description,
        amount=expense.amount,
    )
    db.add(db_expense)
    db.flush()

    # Distribuisce il resto al primo membro per evitare errori di arrotondamento
    for i, member in enumerate(members):
        share = base_share + (remainder if i == 0 else Decimal("0"))
        db_split = models.ExpenseSplit(
            expense_id=db_expense.id,
            member_id=member.id,
            share_amount=share,
        )
        db.add(db_split)

    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.post("/subset", response_model=schemas.ExpenseOut)
def add_expense_subset(group_id: str, expense: schemas.ExpenseCreateSubset, db: Session = Depends(get_db)):
    db_group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Gruppo non trovato")

    payer = db.query(models.Member).filter(
        models.Member.id == expense.paid_by_member_id,
        models.Member.group_id == group_id
    ).first()
    if not payer:
        raise HTTPException(status_code=400, detail="Il pagante non è membro del gruppo")

    if len(expense.member_ids) < 1:
        raise HTTPException(status_code=400, detail="Seleziona almeno un membro")

    # Verifica che tutti i membri selezionati appartengano al gruppo
    valid_ids = {m.id for m in db_group.members}
    for mid in expense.member_ids:
        if mid not in valid_ids:
            raise HTTPException(status_code=400, detail=f"Membro {mid} non appartiene al gruppo")

    n = len(expense.member_ids)
    base_share = round(expense.amount / n, 2)
    remainder = expense.amount - (base_share * n)

    db_expense = models.Expense(
        group_id=group_id,
        paid_by_member_id=expense.paid_by_member_id,
        description=expense.description,
        amount=expense.amount,
    )
    db.add(db_expense)
    db.flush()

    for i, member_id in enumerate(expense.member_ids):
        share = base_share + (remainder if i == 0 else Decimal("0"))
        db_split = models.ExpenseSplit(
            expense_id=db_expense.id,
            member_id=member_id,
            share_amount=share,
        )
        db.add(db_split)

    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.delete("/{expense_id}", status_code=204)
def delete_expense(group_id: str, expense_id: int, db: Session = Depends(get_db)):
    db_expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.group_id == group_id
    ).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Spesa non trovata")
    db.delete(db_expense)
    db.commit()