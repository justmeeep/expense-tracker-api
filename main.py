from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Expense Tracker API")


class ExpenseCreate(BaseModel):
    description: str
    amount: float
    category: str | None = None


class Expense(ExpenseCreate):
    id: int


expenses: list[Expense] = []
next_id = 1


@app.get("/")
def read_root():
    return {"message": "Hello, Expense Tracker!"}


@app.post("/expenses", response_model=Expense, status_code=201)
def create_expense(data: ExpenseCreate):
    global next_id
    expense = Expense(id=next_id, **data.model_dump())
    next_id += 1
    expenses.append(expense)
    return expense


@app.get("/expenses", response_model=list[Expense])
def list_expenses():
    return expenses


@app.get("/expenses/{expense_id}", response_model=Expense)
def get_expense(expense_id: int):
    for expense in expenses:
        if expense.id == expense_id:
            return expense
    raise HTTPException(status_code=404, detail="Expense not found")


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int):
    for i, expense in enumerate(expenses):
        if expense.id == expense_id:
            expenses.pop(i)
            return
    raise HTTPException(status_code=404, detail="Expense not found")