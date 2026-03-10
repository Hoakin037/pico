from fastapi import APIRouter

from .auth import auth

rout = APIRouter(prefix="/api")
rout.include_router(auth)
