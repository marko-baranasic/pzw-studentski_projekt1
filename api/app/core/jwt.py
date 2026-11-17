from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.errors import AppError

ALGORITHM = "HS256"
ACCESS_TTL = timedelta(minutes=15)
REFRESH_TTL = timedelta(days=7)


def create_token(user_id: int, token_type: str, ttl: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),  # označava kome pripada token (id korisnika)
        "type": token_type,  # access ili refresh
        "iat": now,  # issued at, bilježi vrijeme izdavanja tokena
        "exp": now + ttl,  # expiration time
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def create_access_token(user_id: int) -> str:
    return create_token(user_id, "access", ACCESS_TTL)


def create_refresh_token(user_id: int) -> str:
    return create_token(user_id, "refresh", REFRESH_TTL)


def decode_token(token: str, expected_type: str) -> int:
    try:
        # settings.jwt_secret provjerava poklapa li se potpis s tajnim ključem
        # algorithms=[ALGORITHM] Provjerava koristi li token dopušteni algoritam
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AppError("token_expired", "Token je istekao", 401) from None
    except jwt.InvalidTokenError:
        raise AppError("invalid_credentials", "Neispravan token", 401) from None
    if payload.get("type") != expected_type:
        raise AppError("invalid_credentials", "Neispravan token", 401)
    return int(payload["sub"])
