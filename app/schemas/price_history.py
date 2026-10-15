from pydantic import BaseModel, ConfigDict

from decimal import Decimal
from datetime import datetime

class PriceHistoryBase(BaseModel):
    id: int
    ticker: str
    price: Decimal
    fetched_at: datetime

    model_config = ConfigDict(from_attributes=True) # чтобы TypeAdapater-ы работали как надо
