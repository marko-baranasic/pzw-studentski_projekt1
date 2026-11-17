from collections.abc import AsyncIterator  # samo oznaka tipa na editoru
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# prije nego što pokreneš omju rutu izvrši ovu drugu funkciju
# i njezin rezultat ubaci meni kao parametar
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.errors import AppError
from app.core.jwt import decode_token
from app.models import User
from app.repositories import user as user_repo


async def get_db() -> AsyncIterator[AsyncSession]:
    # async omogućuje čekanje servera dok čeka spor odgovor iz bp, istovremeno
    # posluzuje druge korisnike umjesto da cijela app stoji i čeka
    async with AsyncSessionLocal() as session: # pomoćnik otvara novu vezu prema bp
        yield session
    # preda tu otvorenu vezu ruti i pauzira dok ruta obavlja svoj posao
    # (traži korisnika)

    # cim ruta zavrsi i vrati odgovor korisniku(šak i ako se dogodi gresku) nastvalja
    # dalje, izlazi iz async with bloka i sam zatvara vezu s bazom.

    # Kad bi pisalo return session, funkcija bi odmah završila i nitko nikad
    # ne bi zatvorio vezu s bazom, pa bi se baza vrlo brzo zagušila otvorenim
    # konekcijama.

SessionDep = Annotated[AsyncSession, Depends(get_db)]
# umjesto ovog:
#   @router.get("/boats")
#   async def get_boats(session: AsyncSession = Depends(get_db)):
#    ...

# ovo:
#   @router.get("/boats")
#   async def get_boats(session: SessionDep):
#    ...



bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    if credentials is None:
        raise AppError("invalid_credentials", "Nedostaje token", 401)
    user_id = decode_token(credentials.credentials, "access")
    user = await user_repo.get_by_id(session, user_id)
    if user is None or not user.is_active:
        raise AppError("invalid_credentials", "Neispravan token", 401)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)] #kratki nadimak




def require_role(*roles: str):
    async def checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise AppError("forbidden", "Nemate ovlasti za ovu radnju", 403)
        return user

    return checker


AdminUser = Annotated[User, Depends(require_role("admin"))]


CustomerUser = Annotated[User, Depends(require_role("customer"))]
