from decimal import Decimal

from app.models import Boat, Marina
from tests.utils import auth_header, make_user


async def make_fleet(session) -> tuple[Marina, Marina]:
    zadar = Marina(name="Marina Zadar", city="Zadar")
    kornati = Marina(name="Marina Kornati", city="Biograd na Moru")
    session.add_all([zadar, kornati])
    await session.flush()
    session.add_all(
        [
            Boat(
                marina_id=zadar.id,
                name="Jadranka",
                type="sailboat",
                capacity=6,
                price_per_day=Decimal("180.00"),
            ),
            Boat(
                marina_id=zadar.id,
                name="Bura",
                type="motorboat",
                capacity=4,
                price_per_day=Decimal("250.00"),
            ),
            Boat(
                marina_id=kornati.id,
                name="Maestral",
                type="catamaran",
                capacity=10,
                price_per_day=Decimal("520.00"),
            ),
        ]
    )
    await session.commit()
    return zadar, kornati


def new_boat(marina_id: int) -> dict:
    return {
        "marina_id": marina_id,
        "name": "Levant",
        "type": "motorboat",
        "capacity": 5,
        "price_per_day": "300.00",
    }


async def test_list_boats_is_paginated(client, session):
    await make_fleet(session)

    first_page = await client.get("/boats", params={"limit": 2, "offset": 0})
    second_page = await client.get("/boats", params={"limit": 2, "offset": 2})

    assert [b["name"] for b in first_page.json()] == ["Jadranka", "Bura"]
    assert [b["name"] for b in second_page.json()] == ["Maestral"]


async def test_limit_above_maximum_is_422(client):
    response = await client.get("/boats", params={"limit": 101})

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


async def test_filter_boats_by_type_and_marina(client, session):
    zadar, _ = await make_fleet(session)

    by_type = await client.get("/boats", params={"type": "catamaran"})
    by_marina = await client.get("/boats", params={"marina_id": zadar.id})

    assert [b["name"] for b in by_type.json()] == ["Maestral"]
    assert [b["name"] for b in by_marina.json()] == ["Jadranka", "Bura"]


async def test_customer_cannot_create_boat(client, session):
    zadar, _ = await make_fleet(session)
    customer = await make_user(session, "ana@test.hr")

    response = await client.post(
        "/boats", json=new_boat(zadar.id), headers=auth_header(customer)
    )

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


async def test_admin_creates_boat(client, session):
    zadar, _ = await make_fleet(session)
    admin = await make_user(session, "admin@test.hr", role="admin")

    response = await client.post(
        "/boats", json=new_boat(zadar.id), headers=auth_header(admin)
    )

    assert response.status_code == 201
    assert response.json()["price_per_day"] == "300.00"
    assert response.json()["is_active"] is True


async def test_boat_in_missing_marina_is_404(client, session):
    admin = await make_user(session, "admin@test.hr", role="admin")

    response = await client.post(
        "/boats", json=new_boat(999), headers=auth_header(admin)
    )

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


async def test_boat_with_zero_capacity_is_422(client, session):
    zadar, _ = await make_fleet(session)
    admin = await make_user(session, "admin@test.hr", role="admin")
    data = new_boat(zadar.id) | {"capacity": 0}

    response = await client.post("/boats", json=data, headers=auth_header(admin))

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
