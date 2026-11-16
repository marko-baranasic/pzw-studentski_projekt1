import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import Base
from app.core.deps import get_db
from app.main import create_app

DEV_URL = make_url(settings.database_url)
TEST_DB_NAME = f"{DEV_URL.database}_test"
TEST_URL = DEV_URL.set(database=TEST_DB_NAME)

# NullPool: svaka sesija otvara svoju vezu, pa testovi ne dijele veze
engine = create_async_engine(TEST_URL, poolclass=NullPool)
TestSession = async_sessionmaker(engine, expire_on_commit=False)




async def prepare_database() -> None:
    # CREATE DATABASE ne smije unutar transakcije, zato AUTOCOMMIT
    admin = create_async_engine(
        DEV_URL, isolation_level="AUTOCOMMIT", poolclass=NullPool
    )
    async with admin.connect() as conn:
        exists = await conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": TEST_DB_NAME},
        )
        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    await admin.dispose()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        # Briše sve tablice koje su ostale od prošlog pokretanja testova
        await conn.run_sync(Base.metadata.create_all)
        # Ponovno stvara sve tablice (users, marinas, boats...)


@pytest.fixture(scope="session", autouse=True)
# Označava funkciju kao pripremnu radnju za testove, s dvije važne postavke:
# scope="session" — Pokreće se samo jednom na samom početku svih testova
# autouse=True — pytest je pokreće automatski sam od sebe, bez potrebe da
# je ručno pozivaš u testovima.
def database() -> None:
    '''Pokreće asinkronu funkciju prepare_database()
    i čeka da se tablice naprave prije nego što započne prvi test.'''
    asyncio.run(prepare_database())



@pytest.fixture(autouse=True)
async def clean_tables() -> None:
    tables = ", ".join(table.name for table in Base.metadata.sorted_tables)
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


@pytest.fixture
async def session():
    async with TestSession() as session:
        yield session


@pytest.fixture
async def client():
    app = create_app()

    async def override_get_db():
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
