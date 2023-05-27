from os import getenv
from types import SimpleNamespace

import uvicorn
from APIs import WalletRetrieve
from APIs.Tasks import TaskDelete, TaskInsert, TaskRetrieve, TaskUpdate
from conf import settings
from fastapi import Depends, FastAPI, Request
from sqlalchemy import create_engine
from Utility.authentication import assert_secret
from Utility.context import g, request_global
from VarlaLib import Varla, Verbosity
from VarlaLib.Shell import varla_header

engine = create_engine(
    f"mysql+mysqlconnector://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}/{settings.DATABASE_NAME}"
)

app = FastAPI(dependencies=[Depends(assert_secret)], title="Varla-API")

Varla.verbosity = Verbosity.NORMAL


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    initial_g = SimpleNamespace()
    request_global.set(initial_g)

    g().conn = engine.connect()
    g().transaction = g().conn.begin()

    response = await call_next(request)

    if response.status_code >= 400:
        g().transaction.rollback()
    else:
        g().transaction.commit()

    g().conn.close()
    return response


@app.on_event("startup")
async def startup_event():
    Varla.info(f"{settings.APP_NAME} is up!")


@app.on_event("shutdown")
def shutdown_event():
    Varla.info(f"{settings.APP_NAME} is down!")


app.include_router(TaskRetrieve, prefix="/api")
app.include_router(TaskInsert, prefix="/api")
app.include_router(TaskUpdate, prefix="/api")
app.include_router(TaskDelete, prefix="/api")

app.include_router(WalletRetrieve, prefix="/api")


if __name__ == "__main__":
    varla_header()

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEV_MODE,
    )
