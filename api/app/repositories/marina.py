from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Marina


async def list_all(session: AsyncSession, limit: int, offset: int) -> list[Marina]:
    query = select(Marina).order_by(Marina.id).limit(limit).offset(offset)
    result = await session.execute(query)
    return list(result.scalars().all())


async def create(session: AsyncSession, marina: Marina) -> Marina:
    session.add(marina)
    await session.commit()
    await session.refresh(marina)
    return marina
