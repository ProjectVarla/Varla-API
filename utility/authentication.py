from fastapi import Header,status,HTTPException
from os import getenv
SECRET = getenv("SECRET")
MODE = getenv("MODE")


def assert_secret(x_secret=Header(default=None)):
    if MODE != "DEV" and x_secret != SECRET:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
