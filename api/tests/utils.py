import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.jwt import create_access_token
from app.models import User

PASSWORD = "lozinka123"


def fast_hash(password: str) -> str:
    # rounds=4 je najbrži bcrypt; u testovima ne trebamo spor hash
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=4)).decode()


async def make_user(
    session: AsyncSession,
    username: str,
    role: str = "customer",
    is_active: bool = True,
) -> User:
    user = User(
        username=username,
        password_hash=fast_hash(PASSWORD),
        full_name="Test Korisnik",
        role=role,
        is_active=is_active,
    )
    session.add(user)
    await session.commit()
    return user


def auth_header(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}
