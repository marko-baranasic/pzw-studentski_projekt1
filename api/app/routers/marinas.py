from typing import Annotated

from fastapi import APIRouter, Query

from app.core.deps import AdminUser, SessionDep
from app.models import Marina
from app.schemas.marina import MarinaCreate, MarinaResponse, MarinaUpdate
from app.services import marina as marina_service

router = APIRouter(prefix="/marinas", tags=["marinas"])


@router.get("", response_model=list[MarinaResponse])
async def list_marinas(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[Marina]:
    return await marina_service.list_marinas(session, limit, offset)


@router.post("", status_code=201, response_model=MarinaResponse)
async def create_marina(
    data: MarinaCreate, session: SessionDep, admin: AdminUser
) -> Marina:
    return await marina_service.create_marina(session, data)




@router.get("/{marina_id}", response_model=MarinaResponse)
async def get_marina(marina_id: int, session: SessionDep) -> Marina:
    return await marina_service.get_marina(session, marina_id)


@router.patch("/{marina_id}", response_model=MarinaResponse)
async def update_marina(
    marina_id: int, data: MarinaUpdate, session: SessionDep, admin: AdminUser
) -> Marina:
    return await marina_service.update_marina(session, marina_id, data)
