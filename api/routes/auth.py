from fastapi import APIRouter, Depends, Cookie, HTTPException
from fastapi.responses import JSONResponse, Response

from modules.auth import AuthService, get_auth_service, UserAuth, UserLogOut, UserRegister, UserBaseID, get_current_user
from modules.users import UserResponse, UserService, get_user_service

auth = APIRouter(prefix="/auth", tags=["Auth"])

@auth.post(path="/signup", response_model=UserResponse, status_code=201)
async def register_new_user(
    user: UserRegister,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.register_user(user)
    user = await user_service.create_user(user)
    
    return user

@auth.post(path="/login", status_code=200)
async def login_user(
    user: UserAuth,
    auth_service: AuthService = Depends(get_auth_service),
    response: Response = None
):
    user_tokens = await auth_service.login_user(user)

    user_login_response = {
        "user_id": user_tokens.id,
        "access_token": user_tokens.access_token,
        "token_type": "Bearer"
    }
    response.set_cookie(
        key="refresh_token", 
        value=user_tokens.refresh_token, 
        httponly=True, 
        secure=False, 
        samesite="lax", 
        max_age=3600
    )

    return user_login_response

@auth.post(path="/logout", status_code=204)
async def logout_user(
    refresh_token: str = Cookie(None),
    auth_service: AuthService = Depends(get_auth_service),
    current_user: UserBaseID = Depends(get_current_user)
):
    if refresh_token:
        await auth_service.logout_user(UserLogOut(id=current_user.id, refresh_token=refresh_token))
        return 
    raise HTTPException(status_code=401, detail="Токен некорректный или отсутсвует")

@auth.post(path="/refresh_tokens", status_code=200)
async def refresh_tokens(
        refresh_token: str = Cookie(None),
        auth_service: AuthService = Depends(get_auth_service),
        response: Response = None
):
    if refresh_token:
        user_new_tokens = await auth_service.refresh_tokens(refresh_token)
        user_refresh_tokens_response = {
            "user_id": user_new_tokens.id,
            "access_token": user_new_tokens.access_token,
            "token_type": "Bearer"
        }
        response.set_cookie(
            key="refresh_token", 
            value=user_new_tokens.refresh_token,
            max_age=3600,
            secure=False,
            samesite="lax",
            httponly=True
        )
        return user_refresh_tokens_response
    
    raise HTTPException(status_code=401, detail="refresh токен не передан.")       
    
@auth.get(path="/check_jwt", status_code=200)
async def check_jwt(
    current_user: UserBaseID = Depends(get_current_user)
):
    if current_user:
        return {
            "user_id": current_user.id
        }
    raise HTTPException(status_code=404, detail="Пользователь не найден")