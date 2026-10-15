from fastapi import HTTPException, status

from typing import List
from datetime import datetime, timedelta

from app.repositories.price_history import PriceHistoryRepository
from app.schemas.price_history import PriceHistoryBase

class PriceHistoryRepositroy:
    def __init__(self, repository: PriceHistoryRepository) -> None:
        self.repository = repository

    async def get_all(self, ticker: str) -> List[PriceHistoryBase]:
        await self._ticker_existing_check(ticker)

        result = await self.repository.get_all(ticker)

        if len(result) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data for ticker {ticker} was not found")

        return result

    async def get_last(self, ticker: str) -> PriceHistoryBase:
        await self._ticker_existing_check(ticker)

        result = await self.repository.get_last(ticker)
        return result

    async def get_by_date_filtered(self, ticker: str, datetime_from: datetime, datetime_to: datetime) -> List[PriceHistoryBase]:
        await self._ticker_existing_check(ticker)

        datetime_diff = datetime_to - datetime_from
        if datetime_diff - timedelta(0):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid datetime interval')

        result = await self.repository.get_by_date_filtered(ticker, datetime_from, datetime_to)

        if len(result) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data for ticker {ticker} \
                                between {datetime_from} and {datetime_to} was not found")
    
        return result

    # можно переписать как декоратор
    async def _ticker_existing_check(self, ticker: str) -> None:
        is_ticker_exists = await self.repository.is_exists(ticker)
        if not is_ticker_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Ticker {ticker} was not found')
        