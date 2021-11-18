# std library
import os
import hashlib
import functools
from typing import Optional

# 3rd party deps
import jwt
from fastapi import (
    FastAPI,
    HTTPException,
    Response,
    Request,
    Cookie
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import motor.motor_asyncio

# secrets sshhhh
DEVICE_SHARED_KEY: str = os.getenv("DEVICE_SHARED_KEY", "changeme123")
JWT_SECRET: str = os.urandom(64).hex()

# lets go fastapi
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")



async def get_db():
    """ Make client for mongo db. """
    dbclient = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_CONNECTION_STRING", "mongodb://db"))
    db = dbclient.peppa
    return db


def check_auth(session: Optional[str]) -> dict:
    if not session:
        raise HTTPException(status_code=401, detail="No session cookie found.")
    try:
        return jwt.decode(session, JWT_SECRET, algorithms=["HS512"])
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid JWT: {e}")


@app.get("/", response_class=HTMLResponse)
def index():
    """ Send out the front-end """
    with open("static/index.html") as f:
        # XXX: reading from disk on each request is really slow / bad
        #      especially when we could easily just keep it in memory
        #      BUT it's convenient when working on the html stuff
        #      because we then don't have to reload on each change
        html = f.read()

    return html


@app.get("/helloworld")
def helloworld():
    return "Hello, world!"


class DeviceRegistration(BaseModel):
    device_id: str
    shared_key: str


@app.post("/register_device")
async def register_device(data: DeviceRegistration):
    """ Endpoint used by the tracker device, on first boot.  """
    # check shared key, write device into database
    if data.shared_key != DEVICE_SHARED_KEY:
        raise HTTPException(status_code=401, detail="Incorrect shared_key.")

    # put new device_id in db
    db = await get_db()
    await db.devices.insert_one({"device_id": data.device_id})


class UserRegistration(BaseModel):
    username: str
    password: str


@app.post("/register_user")
async def register_user(data: UserRegistration):
    """ check that the username does not exit
        then hash the password and put stuff into database
    """
    db = await get_db()
    if await db.users.count_documents({"username": data.username}, limit=1):
        raise HTTPException(status_code=409, detail="Username already taken.")  # 409 Conflict

    await db.users.insert_one({
        "username": data.username,
        "password": hashlib.sha256(data.password.encode()).hexdigest()
    })


class UserLogin(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(data: UserLogin, response: Response):
    """ Hash the password and compare to entry in db
        set cookie if they match.
    """
    db = await get_db()
    result = await db.users.count_documents(
        {
            "username": data.username,
            "password": hashlib.sha256(data.password.encode()).hexdigest()
        },
        limit=1
    )

    # return 401 on bad credentials
    if not result:
        raise HTTPException(status_code=401, detail="Credentials not found in database.")

    # set session cookie
    jwt_cookie = jwt.encode({"username": data.username}, JWT_SECRET, algorithm="HS512")
    response.set_cookie(key="session", value=jwt_cookie)


@app.post("/logout")
async def logout(response: Response):
    """ Delete cookie when logging out """
    response.delete_cookie(key="session")


@app.get("/auth_status")
async def auth_status(session: Optional[str] = Cookie(None)):
    """ 200 if authenticated, 401 if not """
    # this will abort w/ 401 if session invalid or missing
    session_data = check_auth(session)
    return session_data


@app.post("/pair_device/{device_id}")
async def pair_device(device_id: str, session: Optional[str] = Cookie(None)):
    """ Pair device with user """
    session_data = check_auth(session)

    # check that device_id exists
    db = await get_db()
    if not await db.devices.count_documents({"device_id": device_id}, limit=1):
        raise HTTPException(status_code=404, detail="device_id not found.")

    await db.pairings.insert_one({
        "username": session_data["username"],
        "device_id": device_id
    })


@app.get("/paired_devices")
async def paired_devices(session: Optional[str] = Cookie(None)):
    """ List paired devices for user """
    session_data = check_auth(session)
    db = await get_db()
    cursor = db.pairings.find({"username": session_data["username"]})
    results = await cursor.to_list(length=None)
    return [r["device_id"] for r in results]
