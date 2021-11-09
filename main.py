# std library
import os
import hashlib

# 3rd party deps
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient


DEVICE_SHARED_KEY = os.getenv("DEVICE_SHARED_KEY", "changeme123")
dbclient = MongoClient(os.getenv("MONGO_CONNECTION_STRONG", "mongodb://db"))
db = dbclient.peppa
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
    if db.users.find({"username": data.username}).count():
        raise HTTPException(status_code=401, detail="Username already taken.")

    db.users.insert_one({
        "username": data.username,
        "password": hashlib.sha256(data.password.encode()).hexdigest()
    })


@app.post("/login")
def login(data: UserLogin):
    # TODO: hash the password and compare to entry in db
    #       set cookie if they match.
    #       all other endpoints should 401 if a cookie is missing 
    result = db.users.find_one({
        "username": data.username,
        "password": hashlib.sha256(data.password.encode()).hexdigest()
    })
    if not result:
        raise HTTPException(status_code=401, detail="Credentials not found in database.")

    # TODO: set session cookie
