from fastapi import Header, HTTPException, status
from conf import settings


def assert_secret(x_secret=Header(default=None)):
    if not settings.DEV_MODE and x_secret != settings.SECRET:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
