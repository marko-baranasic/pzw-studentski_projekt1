from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.marina import Marina


class Boat(Base):
    __tablename__ = "boats"
    __table_args__ = (
        CheckConstraint(
            "type IN ('motorboat', 'sailboat', 'catamaran')", name="ck_boats_type"
        ),
        CheckConstraint("capacity > 0", name="ck_boats_capacity"),
        CheckConstraint("price_per_day > 0", name="ck_boats_price_per_day"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    marina_id: Mapped[int] = mapped_column(ForeignKey("marinas.id"))
    name: Mapped[str] = mapped_column(String(100), unique=True)
    type: Mapped[str] = mapped_column(String(20))
    capacity: Mapped[int]
    price_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    is_active: Mapped[bool] = mapped_column(default=True)

    marina: Mapped[Marina] = relationship()
