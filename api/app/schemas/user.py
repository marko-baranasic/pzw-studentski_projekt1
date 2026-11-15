from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    '''Definira kako moraju izgledati podaci koje
    korisnik šalje kada se registrir. Ako bilo koje
    pravilo ispod nije zadovoljeno, FastAPI automatski
    odbija zahtjev s greškom 422'''
    username: str = Field(min_length=3, max_length=100)
    # bcrypt gleda najviše 72 bajta lozinke
    password: str = Field(min_length=8, max_length=72)
    full_name: str = Field(min_length=1, max_length=100)


class UserResponse(BaseModel):
    '''Definira što server šalje natrag klijentu nakon registracije
    ili dohvata profila. Ovdje namjerno nema lozinke
    niti password_hash-a - Pydantic će ih automatski
    izbaciti kako nikad ne bi procurili u odgovoru.'''
    # from_attributes: shema se smije napuniti iz SQLAlchemy objekta
    model_config = ConfigDict(from_attributes=True)
    # Pydantic zna čitati samo iz običnog riječnika gdje se
    # koriste uglate zagrade (user["username"])
    # baza podataka (SQLAlchemy) vraća objekt iz kojeg se podaci
    # čitaju s točkom (user.username). Ta linija samo daje dozvolu Pydanticu
    # da smije čitati podatke s točkom iz objekta koji je stigao iz baze.


    id: int
    username: str
    full_name: str
    role: str
