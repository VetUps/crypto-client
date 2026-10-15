from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Numeric, TIMESTAMP

from decimal import Decimal
from datetime import datetime

class Base(DeclarativeBase):
    pass

class PriceHistory(Base):
    __tablename__ = 'price_history'

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str]
    price: Mapped[Decimal] = mapped_column(Numeric(scale=10, precision=2))
    fetched_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
