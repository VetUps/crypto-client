from fastapi import APIRouter, Depends

from datetime import datetime
from typing import List

from app.dependencies import get_price_history_service
from app.services.price_history import PriceHistoryService
from app.schemas.price_history import PriceHistoryBase

router = APIRouter(
    tags=['Currency'],
    prefix='/currency'
)

@router.get(path='/all', response_model=List[PriceHistoryBase])
async def get_all(ticker: str, service: PriceHistoryService = Depends(get_price_history_service)):
    return await service.get_all(ticker)

@router.get(path='/last', response_model=PriceHistoryBase)
async def get_last(ticker: str, service: PriceHistoryService = Depends(get_price_history_service)):
    return await service.get_last(ticker)

@router.get(path='/date_filtered', response_model=List[PriceHistoryBase])
async def get_by_date_filtered(ticker: str, datetime_from: datetime, datetime_to: datetime, 
                               service: PriceHistoryService = Depends(get_price_history_service)):
    return await service.get_by_date_filtered(ticker, datetime_from, datetime_to)
