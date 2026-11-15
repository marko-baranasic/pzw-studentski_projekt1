from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.security import hash_password, verify_password
from app.models import User
from app.repositories import user as user_repo
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate


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




async def register(session: AsyncSession, data: UserCreate) -> User:
    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role="customer",
    )
    try:
        return await user_repo.create(session, user)
    except IntegrityError:
        # UNIQUE na username: baza je odbila drugi isti upis
        await session.rollback() # Vraća sesiju baze u čisto stanje
        raise AppError("duplicate", "Korisničko ime je zauzeto", 409) from None


async def refresh(session: AsyncSession, refresh_token: str) -> TokenResponse:
    '''Kada korisniku nakon 15 minuta istekne access token, frontend u pozadini
    šalje refresh token (koji vrijedi 7 dana)ovoj funkciji kako bi korisnik ostao
    prijavljen bez ponovnog upisivanja lozinke.'''
    user_id = decode_token(refresh_token, "refresh")
    user = await user_repo.get_by_id(session, user_id)
    if user is None or not user.is_active:
        raise AppError("invalid_credentials", "Neispravan token", 401)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
