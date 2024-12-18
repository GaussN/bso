import logging

from fastapi import FastAPI

import loggers
from web.handlers import router


# TODO: add depends
app = FastAPI()
app.include_router(router)