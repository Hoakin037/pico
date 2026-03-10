from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from pydantic import BaseModel

from app.services.auth import get_auth_service, AuthService, get_current_user

class UserCreate(BaseModel):
    name: str
    surname: str
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserAuth(BaseModel):
    id: int
    password: str
    email: str

class UserBase(BaseModel):
    email: str

auth = APIRouter(tags=["Auth"], prefix="/auth")

@auth.post("/register")
async def register_new_user(user: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.register_new_user(user)

@auth.post("/authenticate")
async def authenticate_user(
    user: UserAuth, 
    auth_service: AuthService = Depends(get_auth_service),
    response: Response = None
    ):
    access_token, refresh_token = await auth_service.authenticate_user(user)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=3 * 24 * 60 * 60,
        samesite="lax",
        secure=True,
        path="/api/auth"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

#mock
@auth.post("/check_jwt")
async def check_jwt_works(
    current_user: bool = Depends(get_current_user)
    ):
    if current_user:
        return {
            "access": True
        }
    