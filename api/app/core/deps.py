from collections.abc import AsyncIterator # samo oznaka tipa na editoru
from typing import Annotated

from fastapi import Depends 
# prije nego što pokreneš omju rutu izvrši ovu drugu funkciju
# i njezin rezultat ubaci meni kao parametar
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal


async def get_db() -> AsyncIterator[AsyncSession]:
    # async omogućuje čekanje servera dok čeka spor odgovor iz bp, istovremeno
    # posluzuje druge korisnike umjesto da cijela app stoji i čeka
    async with AsyncSessionLocal() as session: # pomoćnik otvara novu vezu prema bp
        yield session 
    # preda tu otvorenu vezu ruti i pauzira dok ruta obavlja svoj posao (traži korisnika)

    # cim ruta zavrsi i vrati odgovor korisniku(šak i ako se dogodi gresku) nastvalja
    # dalje, izlazi iz async with bloka i sam zatvara vezu s bazom.

    # Kad bi pisalo return session, funkcija bi odmah završila i nitko nikad ne bi zatvorio
    # vezu s bazom, pa bi se baza vrlo brzo zagušila otvorenim konekcijama.

SessionDep = Annotated[AsyncSession, Depends(get_db)]
# umjesto ovog:
#   @router.get("/boats")
#   async def get_boats(session: AsyncSession = Depends(get_db)):
#    ...

# ovo:
#   @router.get("/boats")
#   async def get_boats(session: SessionDep):
#    ...
