from fastapi import HTTPException, status

from typing import List, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

from app.repositories.price_history import PriceHistoryRepository
from app.schemas.price_history import PriceHistoryBase

class PriceHistoryService:
    def __init__(self, repository: PriceHistoryRepository) -> None:
        self.repository = repository

    async def get_all(self, ticker: str) -> List[PriceHistoryBase]:
        """Возвращает всю информацию о криптовалюте"""
        await self._ticker_existing_check(ticker)

        result = await self.repository.get_all(ticker)

        if len(result) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data for ticker {ticker} was not found")

        return result

    async def get_last(self, ticker: str) -> PriceHistoryBase:
        """Возвращает последнюю запись о криптовалюте"""
        await self._ticker_existing_check(ticker)

        result = await self.repository.get_last(ticker)
        return result

    async def get_by_date_filtered(self, ticker: str, datetime_from: datetime, datetime_to: datetime) -> List[PriceHistoryBase]:
        """Возвращает список записей о криптовалюте, отфильтрованный по дате"""
        await self._ticker_existing_check(ticker)

        naive_datetime_from, naive_datetime_to = self._transfer_into_naive(datetime_from, datetime_to)
        if not self._datetime_validate(naive_datetime_from, naive_datetime_to):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid date interval")

        result = await self.repository.get_by_date_filtered(ticker, naive_datetime_from, naive_datetime_to)

        if len(result) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data for ticker {ticker} between {datetime_from} and {datetime_to} was not found")
    
        return result

    async def create(self, ticker: str, price: Decimal, fetched_at: datetime) -> None:
        """Создаёт запись о криптовалюте"""
        await self.repository.create(ticker, price, fetched_at)

    # можно переписать как декоратор
    async def _ticker_existing_check(self, ticker: str) -> None:
        """Проверка наличия криптовалюты по тикеру"""
        is_ticker_exists = await self.repository.is_exists(ticker)
        if not is_ticker_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Ticker {ticker} was not found')

    def _datetime_validate(self, datetime_from: datetime, datetime_to: datetime) -> bool:
        """Валидация дати и вермя"""
        datetime_diff = datetime_to - datetime_from
        if not datetime_diff - timedelta(0):
            return False
        return True

    @staticmethod
    def _transfer_into_naive(datetime_from: datetime, datetime_to: datetime) -> Tuple[datetime, datetime]:
        """Приведение даты и вермя к наивному формату (без информации о часовом поясе)"""
        datetime_to = datetime_to.replace(tzinfo=None)
        datetime_from = datetime_from.replace(tzinfo=None)

        return datetime_from, datetime_to
    