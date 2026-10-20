import datetime
from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class ExpenseDB(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(200))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    category: Mapped[str | None] = mapped_column(String(50))
    date: Mapped[datetime.date] = mapped_column(default=datetime.date.today)
    notes: Mapped[str | None] = mapped_column(String(500))