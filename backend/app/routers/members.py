from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/groups/{group_id}/members", tags=["members"])


def get_editable_group(group_id: str, db: Session):
    db_group = (
        db.query(models.Group)
        .filter(models.Group.id == group_id)
        .populate_existing()
        .with_for_update()
        .first()
    )
    if not db_group:
        raise HTTPException(status_code=404, detail="Gruppo non trovato")
    if db_group.status != "active":
        raise HTTPException(
            status_code=409,
            detail="I partecipanti sono bloccati durante la chiusura dei conti",
        )
    return db_group


@router.post("/", response_model=schemas.MemberOut, status_code=201)
def add_member(
    group_id: str, member: schemas.MemberCreate, db: Session = Depends(get_db)
):
    get_editable_group(group_id, db)

    db_member = models.Member(
        group_id=group_id,
        name=member.name,
        email=member.email,
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


@router.patch("/{member_id}", response_model=schemas.MemberOut)
def update_member(
    group_id: str,
    member_id: int,
    payload: schemas.MemberUpdate,
    db: Session = Depends(get_db),
):
    get_editable_group(group_id, db)

    member = (
        db.query(models.Member)
        .filter(models.Member.id == member_id, models.Member.group_id == group_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Membro non trovato")

    if payload.name is not None:
        member.name = payload.name
    if payload.email is not None:
        member.email = payload.email or None  # stringa vuota → NULL

    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=204)
def delete_member(group_id: str, member_id: int, db: Session = Depends(get_db)):
    get_editable_group(group_id, db)

    member = (
        db.query(models.Member)
        .filter(models.Member.id == member_id, models.Member.group_id == group_id)
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Membro non trovato")

    # Controlla se il membro è pagante in qualche spesa
    as_payer = (
        db.query(models.Expense)
        .filter(
            models.Expense.paid_by_member_id == member_id,
            models.Expense.group_id == group_id,
        )
        .first()
    )
    if as_payer:
        raise HTTPException(
            status_code=400,
            detail="Impossibile eliminare: il membro ha pagato una o più spese",
        )

    # Controlla se il membro è coinvolto in qualche split
    in_split = (
        db.query(models.ExpenseSplit)
        .join(models.Expense)
        .filter(
            models.ExpenseSplit.member_id == member_id,
            models.Expense.group_id == group_id,
        )
        .first()
    )
    if in_split:
        raise HTTPException(
            status_code=400,
            detail="Impossibile eliminare: il membro è coinvolto in una o più spese",
        )

    in_settlement = (
        db.query(models.Settlement)
        .filter(
            models.Settlement.group_id == group_id,
            or_(
                models.Settlement.from_member_id == member_id,
                models.Settlement.to_member_id == member_id,
                models.Settlement.reported_by_member_id == member_id,
                models.Settlement.confirmed_by_member_id == member_id,
            ),
        )
        .first()
    )
    if in_settlement:
        raise HTTPException(
            status_code=400,
            detail="Impossibile eliminare: il membro è coinvolto nello storico dei pagamenti",
        )

    db.delete(member)
    db.commit()
