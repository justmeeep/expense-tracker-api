from fastapi import FastAPI

from routers import auth, expenses

app = FastAPI(title="Expense Tracker API")

app.include_router(auth.router)
app.include_router(expenses.router)


@app.get("/")
def read_root():
    return {"message": "Hello, Expense Tracker!"}
