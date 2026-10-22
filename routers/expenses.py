import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from categorizer import suggest_category
from database import get_db
from dependencies import get_current_user
from models import ExpenseDB, UserDB
from schemas import (
    CategorySuggestion,
    CategorySuggestRequest,
    Expense,
    ExpenseCreate,
    ExpenseUpdate,
)

router = APIRouter(prefix="/expenses", tags=["expenses"])


def get_user_expense(db: Session, expense_id: int, user: UserDB) -> ExpenseDB:
    expense = db.scalar(
        select(ExpenseDB).where(
            ExpenseDB.id == expense_id, ExpenseDB.user_id == user.id
        )
    )
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.post("", response_model=Expense, status_code=201)
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    expense = ExpenseDB(**data.model_dump(), user_id=current_user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("", response_model=list[Expense])
def list_expenses(
    category: str | None = None,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    query = (
        select(ExpenseDB)
        .where(ExpenseDB.user_id == current_user.id)
        .order_by(ExpenseDB.id)
    )
    if category:
        query = query.where(ExpenseDB.category == category)
    if start_date:
        query = query.where(ExpenseDB.date >= start_date)
    if end_date:
        query = query.where(ExpenseDB.date <= end_date)
    return db.scalars(query).all()


@router.get("/{expense_id}", response_model=Expense)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    return get_user_expense(db, expense_id, current_user)


@router.patch("/{expense_id}", response_model=Expense)
def update_expense(
    expense_id: int,
    data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    expense = get_user_expense(db, expense_id, current_user)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=204)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    expense = get_user_expense(db, expense_id, current_user)
    db.delete(expense)
    db.commit()


@router.post("/suggest-category", response_model=CategorySuggestion)
def suggest_expense_category(
    data: CategorySuggestRequest,
    current_user: UserDB = Depends(get_current_user),
):
    return CategorySuggestion(category=suggest_category(data.description))
