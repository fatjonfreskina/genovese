from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/groups/{group_id}/settlements", tags=["settlements"])


def get_closing_group(group_id: str, db: Session):
    group = (
        db.query(models.Group)
        .filter(models.Group.id == group_id)
        .populate_existing()
        .with_for_update()
        .first()
    )
    if not group:
        raise HTTPException(status_code=404, detail="Gruppo non trovato")
    if group.status != "closing":
        raise HTTPException(
            status_code=409,
            detail="I pagamenti sono disponibili solo durante la chiusura dei conti",
        )
    return group


@router.get("/", response_model=List[schemas.SettlementOut])
def get_settlements(group_id: str, db: Session = Depends(get_db)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Gruppo non trovato")
    return (
        db.query(models.Settlement)
        .filter(
            models.Settlement.group_id == group_id,
            models.Settlement.status != "cancelled",
        )
        .all()
    )


@router.patch("/{settlement_id}/report", response_model=schemas.SettlementOut)
def report_payment(
    group_id: str,
    settlement_id: int,
    payload: schemas.SettlementAction,
    db: Session = Depends(get_db),
):
    get_closing_group(group_id, db)
    settlement = (
        db.query(models.Settlement)
        .filter(
            models.Settlement.id == settlement_id,
            models.Settlement.group_id == group_id,
        )
        .first()
    )
    if not settlement:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    if settlement.status != "pending" or settlement.reported_at:
        raise HTTPException(
            status_code=409, detail="Questo pagamento è già stato segnalato o chiuso"
        )
    if payload.member_id != settlement.from_member_id:
        raise HTTPException(
            status_code=403,
            detail="Solo chi deve pagare può segnalare questo pagamento",
        )
    settlement.reported_by_member_id = payload.member_id
    settlement.reported_at = datetime.utcnow()
    db.commit()
    db.refresh(settlement)
    return settlement


@router.patch("/{settlement_id}/confirm", response_model=schemas.SettlementOut)
def confirm_payment(
    group_id: str,
    settlement_id: int,
    payload: schemas.SettlementAction,
    db: Session = Depends(get_db),
):
    get_closing_group(group_id, db)
    settlement = (
        db.query(models.Settlement)
        .filter(
            models.Settlement.id == settlement_id,
            models.Settlement.group_id == group_id,
        )
        .first()
    )
    if not settlement:
        raise HTTPException(status_code=404, detail="Pagamento non trovato")
    if settlement.status != "pending" or not settlement.reported_at:
        raise HTTPException(
            status_code=409,
            detail="Il pagamento deve prima essere segnalato da chi paga",
        )
    if payload.member_id != settlement.to_member_id:
        raise HTTPException(
            status_code=403, detail="Solo chi riceve può confermare questo pagamento"
        )
    settlement.status = "confirmed"
    settlement.confirmed_by_member_id = payload.member_id
    settlement.confirmed_at = datetime.utcnow()
    db.commit()
    db.refresh(settlement)
    return settlement
