from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import Base
from backend.app.models import Expense, ExpenseSplit, Group, Member, Settlement
from backend.app.routers.expenses import delete_expense
from backend.app.routers.members import delete_member


def test_cannot_delete_member_referenced_by_cancelled_settlement():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    try:
        giulia = Member(name="Giulia")
        marco = Member(name="Marco")
        group = Group(name="Weekend", currency="EUR", members=[giulia, marco])
        session.add(group)
        session.flush()
        session.add(
            Settlement(
                group_id=group.id,
                from_member_id=marco.id,
                to_member_id=giulia.id,
                amount=Decimal("20.00"),
                status="cancelled",
            )
        )
        session.commit()

        with pytest.raises(HTTPException) as exc_info:
            delete_member(group.id, marco.id, session)

        assert exc_info.value.status_code == 400
        assert "storico dei pagamenti" in exc_info.value.detail
        assert session.get(Member, marco.id) is not None
    finally:
        session.close()
        engine.dispose()


def test_can_delete_member_after_their_only_expense_is_deleted():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    try:
        giulia = Member(name="Giulia")
        marco = Member(name="Marco")
        group = Group(name="Weekend", currency="EUR", members=[giulia, marco])
        expense = Expense(
            description="Cena",
            amount=Decimal("20.00"),
            currency="EUR",
            paid_by=marco,
            splits=[
                ExpenseSplit(member=giulia, share_amount=Decimal("10.00")),
                ExpenseSplit(member=marco, share_amount=Decimal("10.00")),
            ],
        )
        group.expenses.append(expense)
        session.add(group)
        session.commit()
        group_id = group.id
        expense_id = expense.id
        member_id = marco.id

        delete_expense(group_id, expense_id, session)
        delete_member(group_id, member_id, session)

        assert session.get(Member, member_id) is None
        assert (
            session.query(ExpenseSplit)
            .filter(ExpenseSplit.expense_id == expense_id)
            .count()
            == 0
        )
    finally:
        session.close()
        engine.dispose()
