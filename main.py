# std library
import os
import hashlib
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
from pydantic import BaseModel
from pymongo import MongoClient

# secrets sshhhh
DEVICE_SHARED_KEY: str = os.getenv("DEVICE_SHARED_KEY", "changeme123")
JWT_SECRET: str = os.urandom(64).hex()

# mongo stuff
dbclient = MongoClient(os.getenv("MONGO_CONNECTION_STRONG", "mongodb://db"))
db = dbclient.peppa

# lets go fastapi
app = FastAPI()


class DeviceRegistration(BaseModel):
    device_id: str
    shared_key: str


class UserRegistration(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


async def check_auth(session: Optional[Cookie]) -> dict:
    if not session:
        raise HTTPException(status_code=401, description="Not authenticated")
    try:
        return jwt.decode(str(session), JWT_SECRET)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, description="Not authenticated")


@app.get("/")
def index():
    # TODO: if session cookie is set, show main page with list of kids
    #       if session cookie is not set, show login page
    return "Hello, world!"


@app.post("/register_device")
def register_device(data: DeviceRegistration):
    # TODO: check shared key, write device into database
    NotImplemented


@app.post("/register_user")
def register_user(data: UserRegistration):
    """ check that the username does not exit
        then hash the password and put stuff into database
    """
    if db.users.count_documents({"username": data.username}, limit=1):
        raise HTTPException(status_code=401, detail="Username already taken.")

    db.users.insert_one({
        "username": data.username,
        "password": hashlib.sha256(data.password.encode()).hexdigest()
    })


@app.post("/login")
def login(data: UserLogin, response: Response):
    """ Hash the password and compare to entry in db
        set cookie if they match.
    """
    result = db.users.count_documents(
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
    jwt_cookie = jwt.encode({"username": data.username}, JWT_SECRET)
    response.set_cookie(key="session", value=jwt_cookie)


@app.post("/logout")
def logout(response: Response):
    """ Delete cookie when logging out """
    response.delete_cookie(key="session")
