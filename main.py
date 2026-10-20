import datetime
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import ExpenseDB

app = FastAPI(title="Expense Tracker API")


class ExpenseCreate(BaseModel):
    description: str
    amount: Decimal
    category: str | None = None


class Expense(ExpenseCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime.date

class ExpenseUpdate(BaseModel):
    description: str | None = None
    amount: Decimal | None = None
    category: str | None = None

@app.get("/")
def read_root():
    return {"message": "Hello, Expense Tracker!"}


@app.post("/expenses", response_model=Expense, status_code=201)
def create_expense(data: ExpenseCreate, db: Session = Depends(get_db)):
    expense = ExpenseDB(**data.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@app.get("/expenses", response_model=list[Expense])
def list_expenses(
    category: str | None = None,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    db: Session = Depends(get_db),
):
    query = select(ExpenseDB).order_by(ExpenseDB.id)
    if category:
        query = query.where(ExpenseDB.category == category)
    if start_date:
        query = query.where(ExpenseDB.date >= start_date)
    if end_date:
        query = query.where(ExpenseDB.date <= end_date)
    return db.scalars(query).all()

@app.get("/expenses/{expense_id}", response_model=Expense)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(ExpenseDB, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(ExpenseDB, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()

@app.patch("/expenses/{expense_id}", response_model=Expense)
def update_expense(
    expense_id: int, data: ExpenseUpdate, db: Session = Depends(get_db)
):
    expense = db.get(ExpenseDB, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense