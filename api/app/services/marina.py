from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models import Marina
from app.repositories import marina as marina_repo
from app.schemas.marina import MarinaCreate, MarinaUpdate


async def list_marinas(session: AsyncSession, limit: int, offset: int) -> list[Marina]:
    return await marina_repo.list_all(session, limit, offset)


async def create_marina(session: AsyncSession, data: MarinaCreate) -> Marina:
    marina = Marina(**data.model_dump())
    try:
        return await marina_repo.create(session, marina)
    except IntegrityError:
        await session.rollback()
        raise AppError("duplicate", "Marina s tim nazivom već postoji", 409) from None




async def get_marina(session: AsyncSession, marina_id: int) -> Marina:
    marina = await marina_repo.get_by_id(session, marina_id)
    if marina is None:
        raise AppError("not_found", "Marina ne postoji", 404)
    return marina


async def update_marina(
    session: AsyncSession, marina_id: int, data: MarinaUpdate
) -> Marina:
    marina = await get_marina(session, marina_id)
    # exclude_unset: samo polja koja je klijent stvarno poslao
    changes = data.model_dump(exclude_unset=True)
    if None in changes.values():
        raise AppError("validation_error", "Polje ne smije biti null", 422)
    for field, value in changes.items():
        setattr(marina, field, value)
    try:
        return await marina_repo.save(session, marina)
    except IntegrityError:
        await session.rollback()
        raise AppError("duplicate", "Marina s tim nazivom već postoji", 409) from None
