from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def get_by_username(session: AsyncSession, username: str) -> User | None:
    result = await session.execute(select(User).where(User.username == username))
    #select(User).where(User.username == username)
    #   Pronađi u tablici users redak u kojem je username == onome
    #   što je korisnik upisao
    #await session.execute(...)
    #   šalje taj upit bazi i čeka odgovor
    return result.scalar_one_or_none()
# baza uvijek vraća sirovi zapakirani rezultat
# iz njega vadi jedan čisti User Objekt ako ga je našle | None ako nema takvog korisnika


async def get_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)
# kada pretražujemo po primarno ključu imamo ugrađeni prečac SQLAlchemya
# umjesto pisanja prijašnjeg koda


async def create(session: AsyncSession, user: User) -> User:
    '''trajno sprema novog korisnika u bazu podataka i vraća ga
    natrag sa svim podacima koje mu je baza dodijelila'''
    session.add(user) # stavljda usera "na čekanje" unutar sesije(item u basket)
    # potvrđuje promjene i trajno upisuje korisnika u tablicu users
    await session.commit()
    # u bazi (kao plaćanje na blagajni), ovdje mora await jer applikacija
    # čeka dok baza ne odradi zapisivanje u disk
    await session.refresh(user) # ponovno učitavanje tog korisnika
    # bez ovog bi user.id ostao None, pa ga UserResponse ne bi mogao vratiti klijentu
    # vraća potpuno popunjen objekt User natrag funkciji koja je pozvala create
    return user
