from fastapi import FastAPI

from app.core.errors import register_error_handlers
from app.routers import auth, boats, health, marinas


def create_app() -> FastAPI:
    '''funkcija koja sastavlja aplikaciju'''
    app = FastAPI(title="Rent a boat API")
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(marinas.router)
    app.include_router(boats.router)
    return app


app = create_app()
