from fastapi import APIRouter

from app.core.deps import SessionDep
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(data: LoginRequest, session: SessionDep) ->TokenResponse:
    return await auth_service.login(session, data.username, data.password)
