from fastapi import FastAPI

from app.routers import health


def create_app() -> FastAPI:
    '''funkcija koja sastavlja aplikaciju'''
    app = FastAPI(title="Rent a boat API")
    app.include_router(health.router)
    return app


app = create_app()
