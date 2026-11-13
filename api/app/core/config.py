'''
čita .env i provjerava da je sve na broju
'''

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# config.py -> core -> app -> api -> korijen repozitorija
ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ENV_FILE, extra="ignore")

    env: str = "dev"
    database_url: str # nemaju zadanu vrijednost
    jwt_secret: str # nemaju zadanu vrijednost
    # ako ih nema u .env, aplikacija se neće ni pokrenuti, 
    # što je bolje nego da adne na prvom zahtjevu


settings = Settings()
