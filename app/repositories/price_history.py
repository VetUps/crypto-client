from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from pydantic import TypeAdapter
from typing import List
from datetime import datetime

from app import models
from app.schemas import price_history

price_history_adapter = TypeAdapter(price_history.PriceHistoryBase)
price_history_list_adapter = TypeAdapter(List[price_history.PriceHistoryBase])

class PriceHistoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, ticker: str) -> List[price_history.PriceHistoryBase]:
        query = (
            select(models.PriceHistory)
            .where(models.PriceHistory.ticker == ticker)
        )

        result = (await self.session.execute(query)).scalars()
        return price_history_list_adapter.validate_python(result)

    async def get_last(self, ticker: str) -> price_history.PriceHistoryBase | None:
        query = (
            select(models.PriceHistory)
            .where(models.PriceHistory.ticker == ticker)
            .order_by(models.PriceHistory.fetched_at.desc())
            .limit(1)
        )

        result = (await self.session.execute(query)).scalar_one_or_none()
        return price_history_adapter.validate_python(result) if result is not None else None

    async def get_by_date_filtered(self, ticker: str, datetime_from: datetime, datetime_to: datetime) \
        -> List[price_history.PriceHistoryBase]:
        query = (
            select(models.PriceHistory)
            .where(models.PriceHistory.ticker == ticker, 
                   models.PriceHistory.fetched_at.between(datetime_from, datetime_to))
        )

        result = (await self.session.execute(query)).scalar_one_or_none()
        return price_history_list_adapter.validate_python(result)

    async def is_exists(self, ticker: str) -> bool:
        query = select(
            exists(
                select(models.PriceHistory)
                .where(models.PriceHistory.ticker == ticker)
            )
        )

        result = (await self.session.execute(query)).scalar_one()
        return result
    