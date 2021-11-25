# std lib
import io
import uuid
import asyncio

# deps
import pytest
from httpx import AsyncClient
from pydub import AudioSegment
from pydub.generators import WhiteNoise

# local imports
import main


new_client = lambda: AsyncClient(app=main.app, base_url="http://localhost:8080")


@pytest.mark.asyncio
async def test_hello_world():
    async with new_client() as client:
        r = await client.get("/helloworld")
    assert 200 == r.status_code 
    assert "Hello, world!" in r.text


@pytest.mark.asyncio
async def test_html():
    async with new_client() as client:
        r = await client.get("/")
    assert 200 == r.status_code
    assert r.headers['content-type'] == 'text/html; charset=utf-8'


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


@pytest.mark.asyncio
async def test_taken_username(logged_in_user):
    username, _, _client = logged_in_user
    await _client.aclose()

    async with new_client() as client:
        r = await client.post(
            "/register_user",
            json={
                "username": username,
                "password": "whatever",
            }
        )
    assert r.status_code == 409  # Conflict


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
async def test_unauthenticated_device_register():
    """ Registering a device with the proper shared key """
    device_id = str(uuid.uuid4())
    async with new_client() as client:
        r = await client.post(
            "/register_device",
            json={
                "device_id": device_id,
                "shared_key": "not-the-key"
            }
        )
    assert r.status_code == 401


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


@pytest.fixture
async def paired_user_and_device(logged_in_user, registered_device):
    _, _, client = logged_in_user
    device_id, device_client = registered_device
    r = await client.post(f"/pair_device/{device_id}")
    assert r.status_code == 200, f"Failed to pair device: {r.text}"
    return (logged_in_user, registered_device)


@pytest.mark.asyncio
async def test_pair_device(paired_user_and_device):
    (username, password, client), (device_id, device_client) = paired_user_and_device
    await device_client.aclose()

    r = await client.get("/paired_devices")
    assert r.status_code == 200, "Failed listing paired devices"
    assert device_id in r.json(), "Didn't find expected device id"
    await client.aclose()


@pytest.mark.asyncio
async def test_unauthorized_pair_device(registered_device):
    device_id, client = registered_device
    r = await client.post(f"/pair_device/{device_id}")
    assert r.status_code == 401
    await client.aclose()


@pytest.mark.asyncio
async def test_pair_unknown_device(logged_in_user):
    _, _, client = logged_in_user
    r = await client.post(f"/pair_device/not-a-real-device")
    assert r.status_code == 404
    await client.aclose()


@pytest.mark.asyncio
async def test_invalid_session():
    async with new_client() as client:
        client.cookies["session"] = "foobar"
        r = await client.get("/paired_devices")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_auth_status(logged_in_user):
    _, _, client = logged_in_user
    r = await client.get("/auth_status")
    assert r.status_code == 200
    await client.aclose()


@pytest.mark.asyncio
async def test_send_audio_to_kid(paired_user_and_device):
    (username, password, client), (device_id, device_client) = paired_user_and_device

    # make 5 seconds of white noise mp3 (duration is measured in ms)
    audio_seg: AudioSegment = WhiteNoise().to_audio_segment(duration=5000)
    mp3_filelike: io.BytesIO = io.BytesIO()
    audio_seg.export(mp3_filelike, format="mp3")
    mp3_bytes: bytes = mp3_filelike.read()

    # send the audio
    r = await client.post(
        f"/send_message/{device_id}",
        data=mp3_bytes,
        headers={"Content-Type": "audio/mpeg"}
    )
    assert r.status_code == 200
    message_id = r.text
    assert len(message_id) == 36, "Did not receive uuid for message"
    await client.aclose()

    # list new messages for device
    r = await device_client.get("/messages")
    assert r.status_code == 200, "Failed listing device messages"
    assert isinstance(r.json(), list)
    assert len(r.json()) == 1
    assert r.json()[0] == {"from": username, "to": device_id, "message_id": message_id}

    # fetch the audio message
    r = await device_client.get(f"/messages/{message_id}")
    assert r.status_code == 200, "Failed fetching message"
    assert r["Content-Type"] == "audio/mpeg"
    assert r.data == mp3_bytes

    # now delete the message
    r = await device_client.post(f"/delete_message/{message_id}")
    assert r.status_code == 200

    # check that it is gone
    r = await device_client.get("/messages")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) == 0
    await device_client.aclose()
