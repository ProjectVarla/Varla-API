from types import SimpleNamespace
from contextvars import ContextVar

request_global = ContextVar("request_global", default=SimpleNamespace())


def g():
    return request_global.get()
