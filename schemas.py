import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ExpenseCreate(BaseModel):
    description: str
    amount: Decimal
    category: str | None = None
    notes: str | None = None


class Expense(ExpenseCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime.date


class ExpenseUpdate(BaseModel):
    description: str | None = None
    amount: Decimal | None = None
    category: str | None = None
    notes: str | None = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str
