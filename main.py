import datetime
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import ExpenseDB, UserDB
from security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

app = FastAPI(title="Expense Tracker API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------- Schemas ----------
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


# ---------- Auth ----------
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UserDB:
    user_id = decode_access_token(token)
    user = db.get(UserDB, user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@app.get("/")
def read_root():
    return {"message": "Hello, Expense Tracker!"}


@app.post("/auth/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    email = data.email.lower()
    existing = db.scalar(select(UserDB).where(UserDB.email == email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = UserDB(email=email, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.scalar(select(UserDB).where(UserDB.email == form.username.lower()))
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.id), token_type="bearer")


@app.get("/auth/me", response_model=UserOut)
def read_me(current_user: UserDB = Depends(get_current_user)):
    return current_user


# ---------- Expenses (all require login) ----------
def get_user_expense(db: Session, expense_id: int, user: UserDB) -> ExpenseDB:
    expense = db.scalar(
        select(ExpenseDB).where(
            ExpenseDB.id == expense_id, ExpenseDB.user_id == user.id
        )
    )
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@app.post("/expenses", response_model=Expense, status_code=201)
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


@app.get("/expenses", response_model=list[Expense])
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


@app.get("/expenses/{expense_id}", response_model=Expense)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    return get_user_expense(db, expense_id, current_user)


@app.patch("/expenses/{expense_id}", response_model=Expense)
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


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    expense = get_user_expense(db, expense_id, current_user)
    db.delete(expense)
    db.commit()