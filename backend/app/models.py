import uuid
from datetime import date, datetime
from sqlalchemy import Column, String, Integer, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Group(Base):
    __tablename__ = "groups"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    currency = Column(String(3), nullable=False, default="EUR")
    status = Column(String(20), nullable=False, default="active")
    closing_count = Column(Integer, nullable=False, default=0)
    closing_balance_mode = Column(String(10), nullable=False, default="separate")
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship(
        "Member", back_populates="group", cascade="all, delete-orphan"
    )
    expenses = relationship(
        "Expense", back_populates="group", cascade="all, delete-orphan"
    )
    settlements = relationship(
        "Settlement", back_populates="group", cascade="all, delete-orphan"
    )


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)

    group = relationship("Group", back_populates="members")
    expenses_paid = relationship("Expense", back_populates="paid_by")
    splits = relationship(
        "ExpenseSplit", back_populates="member", cascade="all, delete-orphan"
    )


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=False)
    paid_by_member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    expense_date = Column(Date, nullable=False, default=date.today)
    exchange_rate = Column(Numeric(24, 12), nullable=True)
    exchange_rate_date = Column(Date, nullable=True)
    exchange_rate_source = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="expenses")
    paid_by = relationship("Member", back_populates="expenses_paid")
    splits = relationship(
        "ExpenseSplit", back_populates="expense", cascade="all, delete-orphan"
    )

    @property
    def converted_amount(self):
        from .currency import round_money

        if self.exchange_rate is None:
            return None
        return round_money(self.amount * self.exchange_rate, self.group.currency)


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    share_amount = Column(Numeric(10, 2), nullable=False)

    expense = relationship("Expense", back_populates="splits")
    member = relationship("Member", back_populates="splits")


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(String(36), ForeignKey("groups.id"), nullable=False)
    from_member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    to_member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="EUR")
    status = Column(String(20), nullable=False, default="pending")
    reported_by_member_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    reported_at = Column(DateTime, nullable=True)
    confirmed_by_member_id = Column(Integer, ForeignKey("members.id"), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    group = relationship("Group", back_populates="settlements")
