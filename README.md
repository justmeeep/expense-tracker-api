# Expense Tracker API

![Tests](https://github.com/justmeeep/expense-tracker-api/actions/workflows/tests.yml/badge.svg)

A REST API for tracking personal expenses, with user accounts, private per-user data, filtering, category suggestions, and monthly summaries.

**Live demo:** https://expense-tracker-api-sc3l.onrender.com/docs
*(Hosted on a free tier, so the first request after inactivity can take about a minute.)*

![API docs](docs/screenshot1.png)
![API docs](docs/screenshot2.png)

## Features

- Register and log in with JWT authentication (Argon2 password hashing)
- Full expense CRUD, with filters by category and date range
- Each user can only see and change their own expenses
- Category suggestion from a description (keyword matching)
- Monthly summary with totals per category and a short insight
- Database migrations with Alembic
- Automated tests and CI on every push

## Tech stack

Python, FastAPI, SQLAlchemy, PostgreSQL (Neon), Alembic, Pydantic, pytest, Ruff, Docker, GitHub Actions, Render

## Run it locally

```bash
git clone https://github.com/YOUR-USERNAME/expense-tracker-api.git
cd expense-tracker-api
python -m venv .venv
.venv\Scripts\activate        # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
DATABASE_URL=postgresql+psycopg://user:password@host/dbname?sslmode=require
SECRET_KEY=generate-with-python--c-"import secrets; print(secrets.token_hex(32))"
```

Then:

```bash
alembic upgrade head
fastapi dev main.py
```

Open http://127.0.0.1:8000/docs.

## Run the tests

```bash
python -m pytest
```

Tests use a temporary in-memory SQLite database, so they never touch real data.

## Design decisions

- **PostgreSQL + Alembic:** schema changes are versioned and repeatable.
- **Per-user filtering in every query:** other users' expenses return 404, so their existence isn't revealed.
- **Decimal for money:** floats cause rounding errors.
- **Swappable categorizer:** `categorizer.py` is one function, so an LLM could replace it without changing the endpoint.

## Possible improvements

- LLM-based category suggestions
- Rate limiting on login
- Refresh tokens
- A simple frontend