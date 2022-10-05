import contextvars
import types
from os import getenv

import mysql.connector
import uvicorn
from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException, Request
from jsql import sql
from sqlalchemy import create_engine

from utility.authentication import assert_secret
from utility.context import g, request_global

load_dotenv()

DATABASE_NAME = getenv("DATABASE_NAME")
DATABASE_PASSWORD = getenv("DATABASE_PASSWORD")
DATABASE_USER = getenv("DATABASE_USER")
DATABASE_HOST = getenv("DATABASE_HOST")
PORT = int(getenv("PORT"))
MODE = getenv("MODE")

engine = create_engine(f'mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}')

app = FastAPI(dependencies=[Depends(assert_secret)])

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    initial_g = types.SimpleNamespace()
    request_global.set(initial_g)

    g().conn = engine.connect()   
    g().transaction = g().conn.begin()

    response = await call_next(request)
    
    if (response.status_code >= 400):
        g().transaction.rollback()
    else:
        g().transaction.commit()

    g().conn.close()
    return response


from APIs.Tasks import TaskRetrieve,TaskInsert,TaskUpdate,TaskDelete
app.include_router(TaskRetrieve,prefix="/api")
app.include_router(TaskInsert,prefix="/api")
app.include_router(TaskUpdate,prefix="/api")
app.include_router(TaskDelete,prefix="/api")

if __name__ == "__main__":
    uvicorn.run("main:app", port = PORT, reload = bool(MODE=="DEV"))
    