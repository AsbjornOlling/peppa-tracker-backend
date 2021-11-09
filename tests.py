# deps
from fastapi.testclient import TestClient

# local imports
import main


client = TestClient(main.app)


def test_register_user():
    """ Users register and log in """
    # register user
    r = client.post(
        "/register_user",
        json={
            "username": "user",
            "password": "pass"
        }
    )
    assert r.status_code == 200

    # login user
    r = client.post(
        "/login",
        json={
            "username": "user",
            "password": "pass"
        }
    )
    assert r.status_code == 200


def test_bad_login():
    """ Logging in with bad credentials should fail with 401 Unauthorized """
    r = client.post(
        "/login",
        json={
            "username": "foo",
            "password": "bar"
        }
    )
    assert r.status_code == 401


def test_register_device():
    """ Registering a device with the proper shared key """
    r = client.post(
        "/register_device",
        json={
            "device_id": "abcd",
            "shared_key": main.DEVICE_SHARED_KEY
        }
    )
    assert r.status_code == 200
