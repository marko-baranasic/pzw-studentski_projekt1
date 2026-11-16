from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models import Boat
from app.repositories import boat as boat_repo
from app.schemas.boat import BoatCreate
from app.services import marina as marina_service


async def list_boats(
    session: AsyncSession,
    limit: int,
    offset: int,
    boat_type: str | None,
    marina_id: int | None,
) -> list[Boat]:
    return await boat_repo.list_all(session, limit, offset, boat_type, marina_id)


async def get_boat(session: AsyncSession, boat_id: int) -> Boat:
    boat = await boat_repo.get_by_id(session, boat_id)
    if boat is None:
        raise AppError("not_found", "Brod ne postoji", 404)
    return boat


async def create_boat(session: AsyncSession, data: BoatCreate) -> Boat:
    # Baci 404 ako marina ne postoji, prije nego što baza odbije strani ključ
    await marina_service.get_marina(session, data.marina_id)
    boat = Boat(**data.model_dump())
    try:
        return await boat_repo.create(session, boat)
    except IntegrityError:
        await session.rollback()
        raise AppError("duplicate", "Brod s tim nazivom već postoji", 409) from None
