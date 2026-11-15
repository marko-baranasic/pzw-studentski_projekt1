from pydantic import BaseModel  # ako podaci nisu prisutni ili ispravnog tipa

# sama sama vraća grešku 422 Unprocessable Entity


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
