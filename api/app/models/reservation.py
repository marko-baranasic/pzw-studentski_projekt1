from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (
        CheckConstraint("end_date > start_date", name="ck_reservations_dates"),
        CheckConstraint("guests > 0", name="ck_reservations_guests"),
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'cancelled')",
            name="ck_reservations_status",
        ),
        # Isti brod ne smije imati dva termina koji se preklapaju
        ExcludeConstraint(
            ("boat_id", "="),
            (text("daterange(start_date, end_date)"), "&&"),
            where=text("status <> 'cancelled'"),
            using="gist",
            name="ex_reservations_no_overlap",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    boat_id: Mapped[int] = mapped_column(ForeignKey("boats.id"))
    start_date: Mapped[date]
    end_date: Mapped[date]
    guests: Mapped[int]
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
