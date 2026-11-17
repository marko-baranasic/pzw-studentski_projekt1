from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models import Reservation, User
from app.repositories import reservation as reservation_repo
from app.schemas.reservation import ReservationCreate
from app.services import boat as boat_service


async def create_reservation(
    session: AsyncSession, user: User, data: ReservationCreate
) -> Reservation:
    boat = await boat_service.get_boat(session, data.boat_id)
    if not boat.is_active:
        raise AppError("boat_inactive", "Brod trenutno nije dostupan za najam", 400)
    if data.guests > boat.capacity:
        raise AppError(
            "capacity_exceeded", f"Brod prima najviše {boat.capacity} osoba", 400
        )

    days = (data.end_date - data.start_date).days
    reservation = Reservation(
        user_id=user.id,
        boat_id=boat.id,
        start_date=data.start_date,
        end_date=data.end_date,
        guests=data.guests,
        # Cijena se zapisuje sada; kasnija promjena cijene broda je ne mijenja
        total_price=boat.price_per_day * days,
        status="pending",
    )
    try:
        return await reservation_repo.create(session, reservation)
    except IntegrityError:
        # Baza je odbila preklapanje (ex_reservations_no_overlap)
        await session.rollback()
        raise AppError(
            "boat_unavailable", "Brod je u tom terminu već rezerviran", 409
        ) from None


async def list_reservations(
    session: AsyncSession, user: User, limit: int, offset: int, status: str | None
) -> list[Reservation]:
    # Admin vidi sve, klijent samo svoje
    user_id = None if user.role == "admin" else user.id
    return await reservation_repo.list_all(session, limit, offset, user_id, status)


async def get_reservation(
    session: AsyncSession, user: User, reservation_id: int
) -> Reservation:
    reservation = await reservation_repo.get_by_id(session, reservation_id)
    if reservation is None:
        raise AppError("not_found", "Rezervacija ne postoji", 404)
    if user.role != "admin" and reservation.user_id != user.id:
        raise AppError("forbidden", "Ovo nije vaša rezervacija", 403)
    return reservation
