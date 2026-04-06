from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# --- Member ---

class MemberCreate(BaseModel):
    name: str
    email: Optional[str] = None

class MemberOut(BaseModel):
    id: int
    name: str
    email: Optional[str] = None

    class Config:
        from_attributes = True

# --- Expense Split ---

class SplitCreate(BaseModel):
    member_id: int
    share_amount: Decimal

class SplitOut(BaseModel):
    member_id: int
    share_amount: Decimal

    class Config:
        from_attributes = True

# --- Expense ---

class ExpenseCreate(BaseModel):
    paid_by_member_id: int
    description: str
    amount: Decimal
    splits: List[SplitCreate]

class ExpenseOut(BaseModel):
    id: int
    paid_by_member_id: int
    description: str
    amount: Decimal
    created_at: datetime
    splits: List[SplitOut]

    class Config:
        from_attributes = True

class ExpenseCreateSubset(BaseModel):
    paid_by_member_id: int
    description: str
    amount: Decimal
    member_ids: List[int]

class ExpenseCreateEqual(BaseModel):
    paid_by_member_id: int
    description: str
    amount: Decimal

# --- Group ---

class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    currency: str = "EUR"
    members: List[MemberCreate]

class GroupOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    currency: str
    created_at: datetime
    members: List[MemberOut]
    expenses: List[ExpenseOut]

    class Config:
        from_attributes = True

# --- Balance ---

class Balance(BaseModel):
    from_member_id: int
    from_member_name: str
    to_member_id: int
    to_member_name: str
    amount: Decimal