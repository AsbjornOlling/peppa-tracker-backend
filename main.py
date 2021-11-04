# std library
import os

# 3rd party deps
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()
DEVICE_SHARED_KEY = os.getenv("DEVICE_SHARED_KEY", "changeme123")


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
    # TODO: check that the username does not exit
    #       then hash the password
    #       and put stuff into database
    NotImplemented


@app.post("/login")
def login(data: UserLogin):
    # TODO: hash the password and compare to entry in db
    #       set cookie if they match.
    #       all other endpoints should 401 if a cookie is missing 
    NotImplemented
