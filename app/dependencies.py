from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.price_history import PriceHistoryRepository
from app.services.price_history import PriceHistoryService
from app.database import get_db

def get_price_history_repository(session: AsyncSession = Depends(get_db)):
    return PriceHistoryRepository(session)

def get_price_history_service(repository: PriceHistoryRepository = Depends(get_price_history_repository)):
    return PriceHistoryService(repository)
