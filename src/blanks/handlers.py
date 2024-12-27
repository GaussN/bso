"""
FastAPI instance that will include the router
should have middleware that 
set request.state.crud: BlankCRUD
"""
import json
import datetime as dt
from typing import Annotated, Optional

from fastapi import Query
from fastapi import HTTPException
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import Response, JSONResponse

import blanks.models as models
from blanks.crud import BlankAdapter


router = APIRouter(prefix="/blank")


@router.get(
    "", 
    description="You can only use one query parameter",
)
async def get_blanks(
        request: Request, 
        blank_id: Optional[int] = Query(default=None, description="ID in database"), 
        number: Optional[str] = Query(default=None, description="<series><number>\nSQL-like pattern"), 
        date: Optional[dt.date] = Query(default=None, description="YYYY-MM-DD")
    ):
    crud = request.state.crud
    if not any((blank_id, number, date)):
        return crud.read()
    result = None
    if blank_id:
        result = crud.get(blank_id)
    elif number:
        result = crud.read_with_filter("WHERE series||number LIKE ?", (number,))
    elif date:
        result = crud.read_with_filter("WHERE date = ?", (BlankAdapter.strftime(date),))
    if result:
        return result 
    raise HTTPException(status_code=404)


@router.post("")
async def create_blanks(request: Request, range_: models.BlankRangeInDTO):
    try:
        request.state.crud.create_from_range(range_)
    except:
        return Response(status_code=400, content="Ivalid range")
    return Response(status_code=201) 


@router.patch("")
async def update_blank(request: Request, updates: models.BlankUpdateDTO):
    if not request.state.crud.update(updates):
        raise HTTPException(status_code=404)


@router.delete("")
async def delete_blank(request: Request, id: int):
    if not request.state.crud.delete(id):
        raise HTTPException(status_code=404)
