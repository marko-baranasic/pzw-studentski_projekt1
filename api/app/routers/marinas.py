from typing import Annotated

from fastapi import APIRouter, Query

from app.core.deps import AdminUser, SessionDep
from app.models import Marina
from app.schemas.marina import MarinaCreate, MarinaResponse
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
