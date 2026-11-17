from typing import Annotated

from fastapi import APIRouter, Query

from app.core.deps import CurrentUser, CustomerUser, SessionDep
from app.models import Reservation
from app.schemas.reservation import (
    ReservationCreate,
    ReservationResponse,
    ReservationStatus,
)
from app.services import reservation as reservation_service

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("", response_model=list[ReservationResponse])
async def list_reservations(
    session: SessionDep,
    user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    status: ReservationStatus | None = None,
) -> list[Reservation]:
    return await reservation_service.list_reservations(
        session, user, limit, offset, status
    )


@router.post("", status_code=201, response_model=ReservationResponse)
async def create_reservation(
    data: ReservationCreate, session: SessionDep, user: CustomerUser
) -> Reservation:
    return await reservation_service.create_reservation(session, user, data)


@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: int, session: SessionDep, user: CurrentUser
) -> Reservation:
    return await reservation_service.get_reservation(session, user, reservation_id)
