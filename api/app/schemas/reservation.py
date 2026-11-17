from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ReservationStatus = Literal["pending", "confirmed", "cancelled"]


class ReservationCreate(BaseModel):
    boat_id: int
    start_date: date
    end_date: date
    guests: int = Field(gt=0)

    @model_validator(mode="after")
    def check_dates(self) -> "ReservationCreate":
        if self.end_date <= self.start_date:
            raise ValueError("Kraj mora biti nakon početka")
        return self


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    boat_id: int
    start_date: date
    end_date: date
    guests: int
    total_price: Decimal
    status: str
    created_at: datetime
