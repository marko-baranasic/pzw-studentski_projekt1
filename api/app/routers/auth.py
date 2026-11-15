from fastapi import APIRouter

from app.core.deps import CurrentUser, SessionDep
from app.models import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201, response_model=UserResponse)
async def register(data: UserCreate, session: SessionDep) -> User:
    return await auth_service.register(session, data)


@router.post("/login")
async def login(data: LoginRequest, session: SessionDep) -> TokenResponse:
    return await auth_service.login(session, data.username, data.password)


@router.post("/refresh")
async def refresh(data: RefreshRequest, session: SessionDep) -> TokenResponse:
    return await auth_service.refresh(session, data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> User:
    return user
