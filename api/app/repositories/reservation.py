from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Reservation


async def list_all(
    session: AsyncSession,
    limit: int,
    offset: int,
    user_id: int | None,
    status: str | None,
) -> list[Reservation]:
    query = select(Reservation)
    if user_id is not None:
        query = query.where(Reservation.user_id == user_id)
    if status is not None:
        query = query.where(Reservation.status == status)
    query = query.order_by(Reservation.id).limit(limit).offset(offset)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_by_id(session: AsyncSession, reservation_id: int) -> Reservation | None:
    return await session.get(Reservation, reservation_id)


async def create(session: AsyncSession, reservation: Reservation) -> Reservation:
    session.add(reservation)
    await session.commit()
    await session.refresh(reservation)
    return reservation


async def save(session: AsyncSession, reservation: Reservation) -> Reservation:
    await session.commit()
    await session.refresh(reservation)
    return reservation
