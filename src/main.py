import logging
from functools import partial

from fastapi import FastAPI
from fastapi import Request

import loggers
import database
import blanks.handlers
from blanks.crud import BlankCRUD
from report_service import ReportService


# init database
database.init_database(database.DB_PATH)
get_connection = partial(database.get_connection, database.DB_PATH)


# fastapi settings
app = FastAPI()
app.state.crud = BlankCRUD(get_connection)

# forward BlankCRUD instance to handler
@app.middleware("http")
async def add_crud(request: Request, call_next):
    request.state.crud = app.state.crud    
    response = await call_next(request)
    return response

app.include_router(blanks.handlers.router)


@app.get("/report")
async def get_report(
    request: Request,
    year: int,
    month: int
):
    report_service = ReportService(get_connection)
    return report_service.get_report(year, month)
