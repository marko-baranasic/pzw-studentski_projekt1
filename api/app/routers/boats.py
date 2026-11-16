from typing import Annotated

from fastapi import APIRouter, Query

from app.core.deps import AdminUser, SessionDep
from app.models import Boat
from app.schemas.boat import BoatCreate, BoatResponse, BoatType
from app.services import boat as boat_service

router = APIRouter(prefix="/boats", tags=["boats"])


@router.get("", response_model=list[BoatResponse])
async def list_boats(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    type: BoatType | None = None,
    marina_id: int | None = None,
) -> list[Boat]:
    return await boat_service.list_boats(session, limit, offset, type, marina_id)


@router.post("", status_code=201, response_model=BoatResponse)
async def create_boat(data: BoatCreate, session: SessionDep, admin: AdminUser) -> Boat:
    return await boat_service.create_boat(session, data)


@router.get("/{boat_id}", response_model=BoatResponse)
async def get_boat(boat_id: int, session: SessionDep) -> Boat:
    return await boat_service.get_boat(session, boat_id)
