from celery import Celery
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import asyncio
import aiohttp

from datetime import timedelta, datetime
from typing import Dict, Any

from app.config import settings
from app.repositories.price_history import PriceHistoryRepository
from app.services.price_history import PriceHistoryService

DERIBIT_API_URL = 'https://www.deribit.com/api/v2/public/get_index_price'

celery_app = Celery(
    'tasks',
    broker=settings.redis_dsn
)

celery_app.conf.update(
    timezone='UTC'
)

async def get_index(session: aiohttp.ClientSession, url: str, currency: str) -> Dict[str, Any]:
    """Получение инофрмации о криптовалюте из внешнего API"""
    params = {'index_name': currency}
    async with session.get(url=url, params=params) as response:
        response_json = await response.json()

        return {
            'ticker': currency,
            'price': response_json['result']['index_price'],
            'fetched_at': datetime.fromtimestamp(response_json['usIn']/1_000_000, tz=None)
        }

async def save_index(data: Dict[str, Any], async_session_factory) -> None:
    """Сохранение информации о криптовалюте"""
    async with async_session_factory() as async_session:
        repository = PriceHistoryRepository(async_session)
        service = PriceHistoryService(repository)   

        await service.create(**data)

async def fetch_deribit_api() -> None:
    celery_async_engine = create_async_engine(settings.postgre_dsn)
    celery_async_session_factory = async_sessionmaker(bind=celery_async_engine)

    try:
        async with aiohttp.ClientSession() as session:
            results = await asyncio.gather(
                get_index(session, DERIBIT_API_URL, 'btc_usd'),
                get_index(session, DERIBIT_API_URL, 'eth_usd')
            )

            await asyncio.gather(
                *[save_index(result, celery_async_session_factory) for result in results]
            )
    finally:
        await celery_async_engine.dispose()

@celery_app.task
def fetch_index_price_task():
    asyncio.run(fetch_deribit_api())

celery_app.conf.beat_schedule = {
    'fetch-deribit-api': {
        'task': 'app.celery.fetch_index_price_task',
        'schedule': timedelta(minutes=1)
    }
}