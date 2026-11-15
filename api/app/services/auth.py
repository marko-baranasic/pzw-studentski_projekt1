from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.jwt import create_access_token, create_refresh_token
from app.core.security import verify_password
from app.repositories import user as user_repo
from app.schemas.auth import TokenResponse


async def login(session: AsyncSession, username: str, password: str) -> TokenResponse:
    user = await user_repo.get_by_username(session, username)
    if (
        user is None
        or not user.is_active
        or not verify_password(password, user.password_hash)
    ):
        # Ista pogreška za nepoznatog korisnika i krivu lozinku
        raise AppError(
            "invalid_credentials", "Neispravno korisničko ime ili lozinka", 401
        )
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
