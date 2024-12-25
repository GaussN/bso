import logging
from functools import partial

from fastapi import FastAPI
from fastapi import Depends
from fastapi import Request

import loggers
import database
from blanks.handlers import router
from blanks.crud import BlankCRUD


# init database
database.init_database(database.DB_PATH)


# fastapi settings
app = FastAPI()
app.state.crud = BlankCRUD(partial(database.get_connection, database.DB_PATH))

@app.middleware("http")
async def add_crud(request: Request, call_next):
    request.state.crud = app.state.crud    
    response = await call_next(request)
    return response

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)