from fastapi import Depends
from fastapi import APIRouter, FastAPI
from fastapi.requests import Request
from fastapi.responses import Response

router = APIRouter(prefix="/blank")


@router.get("")
async def _(request: Request):
    pass


@router.post("")
async def _(request: Request):
    pass


@router.post("many")
async def _(request: Request):
    pass


async def _(request: Request):
    pass


@router.patch("")
async def _(request: Request):
    pass


@router.delete("")
async def _(request: Request):
    pass
