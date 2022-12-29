from os import getenv
from types import SimpleNamespace

import uvicorn
from APIs.Tasks import TaskDelete, TaskInsert, TaskRetrieve, TaskUpdate
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from sqlalchemy import create_engine
from Utility.authentication import assert_secret
from Utility.context import g, request_global
from VarlaLib import Varla, Verbosity


load_dotenv()

DATABASE_NAME = getenv("DATABASE_NAME")
DATABASE_PASSWORD = getenv("DATABASE_PASSWORD")
DATABASE_USER = getenv("DATABASE_USER")
DATABASE_HOST = getenv("DATABASE_HOST")
PORT = int(getenv("API_PORT"))
MODE = getenv("MODE")

engine = create_engine(
    f"mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
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
    Varla.info("Varla-API is up!")


app.include_router(TaskRetrieve, prefix="/api")
app.include_router(TaskInsert, prefix="/api")
app.include_router(TaskUpdate, prefix="/api")
app.include_router(TaskDelete, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", port=PORT, reload=bool(MODE == "DEV"))
