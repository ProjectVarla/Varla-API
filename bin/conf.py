from ipaddress import IPv4Address
from os import getenv
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings, validator

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "Varla-API"

    API_HOST: str
    API_PORT: int

    @validator("API_PORT", always=True)
    def api_port_validator(cls, v):
        return int(getenv("API_PORT"))

    @validator("API_HOST", always=True)
    def api_host_validator(cls, v):
        return str(IPv4Address(getenv("API_HOST")))


settings = Settings()
