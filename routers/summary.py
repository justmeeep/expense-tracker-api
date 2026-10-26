import calendar
import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models import ExpenseDB, UserDB
from schemas import CategoryTotal, MonthlySummary

router = APIRouter(prefix="/summary", tags=["summary"])


def build_insight(by_category: list[CategoryTotal]) -> str:
    if not by_category:
        return "No expenses recorded this month."
    top = by_category[0]
    return (
        f"{top.category.capitalize()} was your biggest expense, "
        f"at {top.percent}% of your spending."
    )


@router.get("", response_model=MonthlySummary)
def monthly_summary(
    year: int | None = Query(default=None, ge=2000, le=2100),
    month: int | None = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    today = datetime.date.today()
    year = year or today.year
    month = month or today.month

    start = datetime.date(year, month, 1)
    end = datetime.date(year, month, calendar.monthrange(year, month)[1])

    rows = db.execute(
        select(ExpenseDB.category, func.sum(ExpenseDB.amount))
        .where(
            ExpenseDB.user_id == current_user.id,
            ExpenseDB.date >= start,
            ExpenseDB.date <= end,
        )
        .group_by(ExpenseDB.category)
    ).all()

    totals = [
        (category or "uncategorized", Decimal(str(total))) for category, total in rows
    ]
    totals.sort(key=lambda item: item[1], reverse=True)
    grand_total = sum((total for _, total in totals), Decimal("0"))

    by_category = [
        CategoryTotal(
            category=category,
            total=total,
            percent=round(float(total / grand_total * 100), 1),
        )
        for category, total in totals
    ]

    return MonthlySummary(
        year=year,
        month=month,
        total=grand_total,
        by_category=by_category,
        insight=build_insight(by_category),
    )
