from decimal import Decimal
from typing import Literal  # ograničeni izbor vrijednosti

from pydantic import BaseModel, ConfigDict, Field

BoatType = Literal["motorboat", "sailboat", "catamaran"]


class BoatCreate(BaseModel):
    marina_id: int
    name: str = Field(min_length=1, max_length=100)
    type: BoatType
    capacity: int = Field(gt=0) # strogo veće od 0
    price_per_day: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class BoatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    marina_id: int
    name: str
    type: str
    capacity: int
    price_per_day: Decimal
    is_active: bool
