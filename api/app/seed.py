"""Početni podatci za razvoj i obranu.

Pokreće se iz mape api/, nakon alembic upgrade head:
    python -m app.seed

Smije se pokrenuti bilo koliko puta: što već postoji, ne stvara se ponovno.
"""

import asyncio
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.core.security import hash_password
from app.models import Boat, Marina, User

# Polja: korisničko ime, lozinka, ime i prezime, uloga
# Dva klijenta, da se vlasništvo može isprobati: Ana ne smije do Ivanovih rezervacija
DEMO_USERS = [
    ("admin@rentaboat.hr", "admin123", "Admin Charter", "admin"),
    ("ana@rentaboat.hr", "ana12345", "Ana Horvat", "customer"),
    ("ivan@rentaboat.hr", "ivan1234", "Ivan Perić", "customer"),
]

# Polja: naziv, grad
DEMO_MARINAS = [
    ("Marina Zadar", "Zadar"),
    ("Marina Kornati", "Biograd na Moru"),
]

# Polja: marina, naziv, vrsta, kapacitet, cijena po danu
DEMO_BOATS = [
    ("Marina Zadar", "Jadranka", "sailboat", 6, Decimal("180.00")),
    ("Marina Zadar", "Bura", "motorboat", 4, Decimal("250.00")),
    ("Marina Kornati", "Maestral", "catamaran", 10, Decimal("520.00")),
]


async def get_or_create_user(
    session: AsyncSession, username: str, password: str, full_name: str, role: str
) -> User:
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
        )
        session.add(user)
        await session.flush()
    return user


async def get_or_create_marina(session: AsyncSession, name: str, city: str) -> Marina:
    result = await session.execute(select(Marina).where(Marina.name == name))
    marina = result.scalar_one_or_none()
    if marina is None:
        marina = Marina(name=name, city=city)
        session.add(marina)
        # flush šalje upis prije commita, da marina dobije id za strani ključ
        await session.flush()
    return marina


async def get_or_create_boat(
    session: AsyncSession,
    marina_id: int,
    name: str,
    boat_type: str,
    capacity: int,
    price_per_day: Decimal,
) -> Boat:
    result = await session.execute(select(Boat).where(Boat.name == name))
    boat = result.scalar_one_or_none()
    if boat is None:
        boat = Boat(
            marina_id=marina_id,
            name=name,
            type=boat_type,
            capacity=capacity,
            price_per_day=price_per_day,
        )
        session.add(boat)
        await session.flush()
    return boat


async def seed() -> None:
    # Jedna transakcija: ili su svi retci upisani, ili nijedan
    async with AsyncSessionLocal() as session, session.begin(): # ako bilo koji korak baci grešku, cijeli unos se poništava
        for user in DEMO_USERS:
            await get_or_create_user(session, *user)

        marinas = {}
        for name, city in DEMO_MARINAS:
            marinas[name] = await get_or_create_marina(session, name, city)

        for marina_name, *boat in DEMO_BOATS:
            await get_or_create_boat(session, marinas[marina_name].id, *boat)

    await engine.dispose()
    print("Seed gotov.")
    for username, password, _, role in DEMO_USERS:
        print(f"  {role}: {username} / {password}")


if __name__ == "__main__":
    asyncio.run(seed())
