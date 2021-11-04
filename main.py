# std library
import os
from dataclasses import dataclass 

# 3rd party deps
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
DEVICE_SHARED_KEY = os.getenv("DEVICE_SHARED_KEY", "changeme123")


@dataclass
class DeviceRegistration(BaseModel):
    device_id: str
    shared_key: str


@dataclass
class UserRegistration(BaseModel):
    username: str
    password: str
    device_id: str


@app.get("/")
def hello_world():
    return "Hello, world!"


@app.post("/register_device")
def register_device(data: DeviceRegistration):
    # TODO: check shared key, write device into database
    NotImplemented


@app.post("/register_user")
def register_user(data: UserRegistration):
    # TODO: check that device_id exists,
    #       and that the username does not exit
    #       put stuff into database
    NotImplemented
