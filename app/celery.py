from celery import Celery
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

import asyncio
import aiohttp

from datetime import timedelta, datetime, timezone
from typing import Dict, Any

from app.config import settings
from app.database import engine
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

AsyncSessionFactory = async_sessionmaker(bind=engine)

async def get_index(session: aiohttp.ClientSession, url: str, currency: str) -> Dict[str, Any]:
    params = {'index_name': currency}
    async with session.get(url=url, params=params) as response:
        response_json = await response.json()

        return {
            'ticker': currency,
            'price': response_json['result']['index_price'],
            'fetched_at': datetime.fromtimestamp(response_json['usIn']/1_000_000, tz=timezone.utc)
        }

async def save_index(data: Dict[str, Any]):
    async with AsyncSessionFactory() as async_session:
        repository = PriceHistoryRepository(async_session)
        service = PriceHistoryService(repository)   

        await service.create(**data)

async def fetch_deribit_api():
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            get_index(session, DERIBIT_API_URL, 'btc_usd'),
            get_index(session, DERIBIT_API_URL, 'eth_usd')
        )

        await asyncio.gather(
            *[save_index(result) for result in results]
        )

@celery_app.task
def fetch_index_price_task():
    asyncio.run(fetch_deribit_api())

celery_app.conf.beat_schedule = {
    'fetch-deribit-api': {
        'task': 'app.celery.fetch_index_price_task',
        'schedule': timedelta(minutes=1)
    }
}