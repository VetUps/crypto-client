from pydantic import BaseModel

from decimal import Decimal
from datetime import datetime

class PriceHistoryBase(BaseModel):
    id: int
    ticker: str
    price: Decimal
    fetched_at: datetime
    