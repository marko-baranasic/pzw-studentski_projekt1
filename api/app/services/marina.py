from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models import Marina
from app.repositories import marina as marina_repo
from app.schemas.marina import MarinaCreate


async def list_marinas(session: AsyncSession, limit: int, offset: int) -> list[Marina]:
    return await marina_repo.list_all(session, limit, offset)


async def create_marina(session: AsyncSession, data: MarinaCreate) -> Marina:
    marina = Marina(**data.model_dump())
    try:
        return await marina_repo.create(session, marina)
    except IntegrityError:
        await session.rollback()
        raise AppError("duplicate", "Marina s tim nazivom već postoji", 409) from None
