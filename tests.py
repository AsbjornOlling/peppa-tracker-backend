# std lib
import uuid

# deps
import pytest
from fastapi.testclient import TestClient

# local imports
import main



@pytest.fixture
def logged_in_user():
    """ Users register and log in """
    client = TestClient(main.app)

    username = str(uuid.uuid4())
    password = "really great password"

    # register user
    r = client.post(
        "/register_user",
        json={
            "username": username,
            "password": password
        }
    )
    assert r.status_code == 200, "Failed registering new user"

    # login user
    r = client.post(
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
def registered_device():
    """ Registering a device with the proper shared key """
    client = TestClient(main.app)
    device_id = str(uuid.uuid4())
    r = client.post(
        "/register_device",
        json={
            "device_id": device_id,
            "shared_key": main.DEVICE_SHARED_KEY
        }
    )
    assert r.status_code == 200
    return device_id, client


def test_client_login_logout(logged_in_user):
    username, password, client = logged_in_user
    assert "session" in client.cookies
    client.post("/logout")
    assert "session" not in client.cookies


def test_bad_login():
    """ Logging in with bad credentials should fail with 401 Unauthorized """
    client = TestClient(main.app)
    r = client.post(
        "/login",
        json={
            "username": "foo",
            "password": "bar"
        }
    )
    assert r.status_code == 401


def test_pair_device(logged_in_user, registered_device):
    username, password, client = logged_in_user
    device_id, _ = registered_device

    r = client.post(f"/pair_device/{device_id}")
    assert r.status_code == 200, f"Failed to pair device: {r.text}"

    r = client.get("/paired_devices")
    assert r.status_code == 200, "Failed listing paired devices"
    paired_device_ids = r.json()
    assert device_id in paired_device_ids, "Didn't find expected device id"


def test_unauthorized_pair_device(registered_device):
    device_id, client = registered_device
    r = client.post(f"/pair_device/{device_id}")
    assert r.status_code == 401
