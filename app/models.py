from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Numeric, TIMESTAMP

from decimal import Decimal
from datetime import datetime

class Base(DeclarativeBase):
    pass

class PriceHistory(Base):
    __tablename__ = 'price_history'

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(
        index=True, 
        index_kwargs={"postgresql_using": "hash"}
    )
    price: Mapped[Decimal] = mapped_column(Numeric(scale=2, precision=10))
    fetched_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
