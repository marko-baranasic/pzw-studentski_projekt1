from tests.utils import auth_header, make_user

MARINA = {"name": "Marina Zadar", "city": "Zadar"}


async def test_create_marina_without_token_is_401(client):
    response = await client.post("/marinas", json=MARINA)

    assert response.status_code == 401


async def test_customer_cannot_create_marina(client, session):
    customer = await make_user(session, "ana@test.hr", role="customer")

    response = await client.post(
        "/marinas", json=MARINA, headers=auth_header(customer)
    )

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


async def test_admin_creates_marina(client, session):
    admin = await make_user(session, "admin@test.hr", role="admin")

    response = await client.post("/marinas", json=MARINA, headers=auth_header(admin))

    assert response.status_code == 201
    assert response.json()["name"] == "Marina Zadar"


async def test_duplicate_marina_name_is_409(client, session):
    admin = await make_user(session, "admin@test.hr", role="admin")
    await client.post("/marinas", json=MARINA, headers=auth_header(admin))

    response = await client.post("/marinas", json=MARINA, headers=auth_header(admin))

    assert response.status_code == 409
    assert response.json()["code"] == "duplicate"


async def test_patch_changes_only_sent_fields(client, session):
    admin = await make_user(session, "admin@test.hr", role="admin")
    created = await client.post("/marinas", json=MARINA, headers=auth_header(admin))
    marina_id = created.json()["id"]

    response = await client.patch(
        f"/marinas/{marina_id}", json={"city": "Šibenik"}, headers=auth_header(admin)
    )

    assert response.status_code == 200
    assert response.json()["city"] == "Šibenik"
    assert response.json()["name"] == "Marina Zadar"


async def test_missing_marina_is_404(client):
    response = await client.get("/marinas/999")

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"
