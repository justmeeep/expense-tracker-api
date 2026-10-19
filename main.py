from fastapi import FastAPI

app = FastAPI(title="Expense Tracker API")

@app.get("/")
def read_root():
    return {"message": "Hello, Expense Tracker!"}