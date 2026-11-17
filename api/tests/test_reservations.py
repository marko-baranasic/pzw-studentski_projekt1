from decimal import Decimal

from freezegun import freeze_time

from app.models import Boat, Marina
from tests.utils import auth_header, make_user


async def make_boat(session, capacity: int = 6, is_active: bool = True) -> Boat:
    marina = Marina(name="Marina Zadar", city="Zadar")
    session.add(marina)
    await session.flush()
    boat = Boat(
        marina_id=marina.id,
        name="Jadranka",
        type="sailboat",
        capacity=capacity,
        price_per_day=Decimal("180.00"),
        is_active=is_active,
    )
    session.add(boat)
    await session.commit()
    return boat


def booking(boat_id: int, start: str, end: str, guests: int = 2) -> dict:
    return {"boat_id": boat_id, "start_date": start, "end_date": end, "guests": guests}


# --- Stvaranje i poslovna pravila ---


async def test_customer_creates_reservation_with_price(client, session):
    ana = await make_user(session, "ana@test.hr")
    boat = await make_boat(session)

    response = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05"),
        headers=auth_header(ana),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["user_id"] == ana.id
    # 4 dana po 180.00
    assert body["total_price"] == "720.00"


async def test_overlapping_reservation_is_409(client, session):
    ana = await make_user(session, "ana@test.hr")
    ivan = await make_user(session, "ivan@test.hr")
    boat = await make_boat(session)
    await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05"),
        headers=auth_header(ana),
    )

    response = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-03", "2027-07-08"),
        headers=auth_header(ivan),
    )

    assert response.status_code == 409
    assert response.json()["code"] == "boat_unavailable"


async def test_back_to_back_reservations_are_allowed(client, session):
    ana = await make_user(session, "ana@test.hr")
    boat = await make_boat(session)
    await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05"),
        headers=auth_header(ana),
    )

    # Jedna završava 5. 7., druga počinje 5. 7.: kraj raspona nije uključen
    response = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-05", "2027-07-08"),
        headers=auth_header(ana),
    )

    assert response.status_code == 201


async def test_cancelled_reservation_frees_the_slot(client, session):
    ana = await make_user(session, "ana@test.hr")
    admin = await make_user(session, "admin@test.hr", role="admin")
    boat = await make_boat(session)
    first = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05"),
        headers=auth_header(ana),
    )
    await client.post(
        f"/reservations/{first.json()['id']}/cancel", headers=auth_header(admin)
    )

    response = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05"),
        headers=auth_header(ana),
    )

    assert response.status_code == 201


async def test_too_many_guests_is_400(client, session):
    ana = await make_user(session, "ana@test.hr")
    boat = await make_boat(session, capacity=4)

    response = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05", guests=5),
        headers=auth_header(ana),
    )

    assert response.status_code == 400
    assert response.json()["code"] == "capacity_exceeded"


async def test_inactive_boat_cannot_be_booked(client, session):
    ana = await make_user(session, "ana@test.hr")
    boat = await make_boat(session, is_active=False)

    response = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05"),
        headers=auth_header(ana),
    )

    assert response.status_code == 400
    assert response.json()["code"] == "boat_inactive"


async def test_end_before_start_is_422(client, session):
    ana = await make_user(session, "ana@test.hr")
    boat = await make_boat(session)

    response = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-05", "2027-07-01"),
        headers=auth_header(ana),
    )

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


async def test_admin_cannot_create_reservation(client, session):
    admin = await make_user(session, "admin@test.hr", role="admin")
    boat = await make_boat(session)

    response = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05"),
        headers=auth_header(admin),
    )

    assert response.status_code == 403


# --- Vlasništvo ---


async def test_customer_sees_only_own_reservations(client, session):
    ana = await make_user(session, "ana@test.hr")
    ivan = await make_user(session, "ivan@test.hr")
    admin = await make_user(session, "admin@test.hr", role="admin")
    boat = await make_boat(session)
    await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05"),
        headers=auth_header(ana),
    )
    await client.post(
        "/reservations",
        json=booking(boat.id, "2027-08-01", "2027-08-05"),
        headers=auth_header(ivan),
    )

    ana_list = await client.get("/reservations", headers=auth_header(ana))
    admin_list = await client.get("/reservations", headers=auth_header(admin))

    assert [r["user_id"] for r in ana_list.json()] == [ana.id]
    assert len(admin_list.json()) == 2


async def test_customer_cannot_read_others_reservation(client, session):
    ana = await make_user(session, "ana@test.hr")
    ivan = await make_user(session, "ivan@test.hr")
    boat = await make_boat(session)
    created = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05"),
        headers=auth_header(ana),
    )

    response = await client.get(
        f"/reservations/{created.json()['id']}", headers=auth_header(ivan)
    )

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


async def test_customer_cannot_cancel_others_reservation(client, session):
    ana = await make_user(session, "ana@test.hr")
    ivan = await make_user(session, "ivan@test.hr")
    boat = await make_boat(session)
    created = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05"),
        headers=auth_header(ana),
    )

    response = await client.post(
        f"/reservations/{created.json()['id']}/cancel", headers=auth_header(ivan)
    )

    assert response.status_code == 403


# --- Statusi ---


async def test_only_admin_can_confirm(client, session):
    ana = await make_user(session, "ana@test.hr")
    admin = await make_user(session, "admin@test.hr", role="admin")
    boat = await make_boat(session)
    created = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05"),
        headers=auth_header(ana),
    )
    url = f"/reservations/{created.json()['id']}/confirm"

    by_customer = await client.post(url, headers=auth_header(ana))
    by_admin = await client.post(url, headers=auth_header(admin))

    assert by_customer.status_code == 403
    assert by_admin.status_code == 200
    assert by_admin.json()["status"] == "confirmed"


async def test_confirm_twice_is_invalid_status(client, session):
    ana = await make_user(session, "ana@test.hr")
    admin = await make_user(session, "admin@test.hr", role="admin")
    boat = await make_boat(session)
    created = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05"),
        headers=auth_header(ana),
    )
    url = f"/reservations/{created.json()['id']}/confirm"
    await client.post(url, headers=auth_header(admin))

    response = await client.post(url, headers=auth_header(admin))

    assert response.status_code == 400
    assert response.json()["code"] == "invalid_status"


async def test_cannot_confirm_cancelled_reservation(client, session):
    ana = await make_user(session, "ana@test.hr")
    admin = await make_user(session, "admin@test.hr", role="admin")
    boat = await make_boat(session)
    created = await client.post(
        "/reservations",
        json=booking(boat.id, "2027-07-01", "2027-07-05"),
        headers=auth_header(ana),
    )
    reservation_id = created.json()["id"]
    await client.post(
        f"/reservations/{reservation_id}/cancel", headers=auth_header(admin)
    )

    response = await client.post(
        f"/reservations/{reservation_id}/confirm", headers=auth_header(admin)
    )

    assert response.status_code == 400
    assert response.json()["code"] == "invalid_status"


# --- Rok za otkaz (zamrznuto vrijeme) ---
# Najam počinje 1. 7. 2027. u 00:00 UTC, pa je rok 28. 6. 2027. u 23:59 i 59 s.


async def test_customer_can_cancel_just_before_deadline(client, session):
    ana = await make_user(session, "ana@test.hr")
    boat = await make_boat(session)

    with freeze_time("2027-06-28 23:59:00"):
        headers = auth_header(ana)
        created = await client.post(
            "/reservations",
            json=booking(boat.id, "2027-07-01", "2027-07-05"),
            headers=headers,
        )
        response = await client.post(
            f"/reservations/{created.json()['id']}/cancel", headers=headers
        )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


async def test_customer_cannot_cancel_after_deadline(client, session):
    ana = await make_user(session, "ana@test.hr")
    boat = await make_boat(session)

    with freeze_time("2027-06-29 00:01:00"):
        headers = auth_header(ana)
        created = await client.post(
            "/reservations",
            json=booking(boat.id, "2027-07-01", "2027-07-05"),
            headers=headers,
        )
        response = await client.post(
            f"/reservations/{created.json()['id']}/cancel", headers=headers
        )

    assert response.status_code == 400
    assert response.json()["code"] == "cancellation_deadline_passed"


async def test_admin_can_cancel_after_deadline(client, session):
    ana = await make_user(session, "ana@test.hr")
    admin = await make_user(session, "admin@test.hr", role="admin")
    boat = await make_boat(session)

    with freeze_time("2027-06-30 12:00:00"):
        created = await client.post(
            "/reservations",
            json=booking(boat.id, "2027-07-01", "2027-07-05"),
            headers=auth_header(ana),
        )
        response = await client.post(
            f"/reservations/{created.json()['id']}/cancel",
            headers=auth_header(admin),
        )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
