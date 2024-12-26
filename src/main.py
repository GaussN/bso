import logging
from typing import Annotated
from functools import partial

from fastapi import FastAPI
from fastapi import Request
from pydantic import AfterValidator

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

@app.middleware("http")
async def add_crud(request: Request, call_next):
    request.state.crud = app.state.crud    
    response = await call_next(request)
    return response

app.include_router(blanks.handlers.router)


def month_validator(month):
    if 1 <= month <= 12:
        return month
    raise ValueError("month value should be in range [1,12]")


@app.get("/report")
async def get_report(
    request: Request,
    year: int,
    month: Annotated[int, AfterValidator(month_validator)]
):
    report_service = ReportService(get_connection)
    return report_service.get_report(year, month)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)