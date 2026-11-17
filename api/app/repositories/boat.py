from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Boat


async def list_all(
    session: AsyncSession,
    limit: int,
    offset: int,
    boat_type: str | None,
    marina_id: int | None,
) -> list[Boat]:
    query = select(Boat)
    if boat_type is not None:
        query = query.where(Boat.type == boat_type)
    if marina_id is not None:
        query = query.where(Boat.marina_id == marina_id)
    query = query.order_by(Boat.id).limit(limit).offset(offset)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_by_id(session: AsyncSession, boat_id: int) -> Boat | None:
    return await session.get(Boat, boat_id)


async def create(session: AsyncSession, boat: Boat) -> Boat:
    session.add(boat)
    await session.commit()
    await session.refresh(boat)
    return boat


async def save(session: AsyncSession, boat: Boat) -> Boat:
    await session.commit()
    await session.refresh(boat)
    return boat
