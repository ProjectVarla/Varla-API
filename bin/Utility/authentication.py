from os import getenv

from fastapi import Header, HTTPException, status

SECRET = getenv("SECRET")
MODE = getenv("MODE")


def assert_secret(x_secret=Header(default=None)):
    if MODE != "DEV" and x_secret != SECRET:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
