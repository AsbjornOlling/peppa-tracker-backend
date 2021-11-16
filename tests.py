# std lib
import uuid
import asyncio

# deps
import pytest
# from fastapi.testclient import TestClient
from httpx import AsyncClient

# local imports
import main


new_client = lambda: AsyncClient(app=main.app, base_url="http://localhost:8080")


@pytest.mark.asyncio
async def test_hello_world():
    async with new_client() as client:
        r = await client.get("/")
    assert 200 == r.status_code 
    assert "Hello, world!" in r.text


@pytest.fixture
async def logged_in_user():
    """ Users register and log in """
    client = new_client()

    username = str(uuid.uuid4())
    password = "really great password"

    # register user
    r = await client.post(
        "/register_user",
        json={
            "username": username,
            "password": password
        }
    )
    assert r.status_code == 200, "Failed registering new user"

    # login user
    r = await client.post(
        "/login",
        json={
            "username": username,
            "password": password
        }
    )
    assert r.status_code == 200, "Could not sign in new user"
    assert "session" in client.cookies

    return username, password, client


@pytest.fixture
async def registered_device():
    """ Registering a device with the proper shared key """
    client = new_client()
    device_id = str(uuid.uuid4())
    r = await client.post(
        "/register_device",
        json={
            "device_id": device_id,
            "shared_key": main.DEVICE_SHARED_KEY
        }
    )
    assert r.status_code == 200
    return device_id, client


@pytest.mark.asyncio
async def test_client_login_logout(logged_in_user):
    username, password, client = logged_in_user
    assert "session" in client.cookies
    await client.post("/logout")
    assert "session" not in client.cookies
    await client.aclose()


@pytest.mark.asyncio
async def test_bad_login():
    """ Logging in with bad credentials should fail with 401 Unauthorized """
    async with new_client() as client:
        r = await client.post(
            "/login",
            json={
                "username": "foo",
                "password": "bar"
            }
        )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_pair_device(logged_in_user, registered_device):
    username, password, client = logged_in_user
    device_id, device_client = registered_device
    await device_client.aclose()

    r = await client.post(f"/pair_device/{device_id}")
    assert r.status_code == 200, f"Failed to pair device: {r.text}"

    r = await client.get("/paired_devices")
    assert r.status_code == 200, "Failed listing paired devices"
    paired_device_ids = r.json()
    assert device_id in paired_device_ids, "Didn't find expected device id"
    await client.aclose()


@pytest.mark.asyncio
async def test_unauthorized_pair_device(registered_device):
    device_id, client = registered_device
    r = await client.post(f"/pair_device/{device_id}")
    assert r.status_code == 401
    await client.aclose()
