from fastapi import APIRouter

from .routes import auth

router = APIRouter(prefix="/api")
router.include_router(auth)