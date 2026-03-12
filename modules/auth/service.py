from pwdlib import PasswordHash
from fastapi import Depends, HTTPException
from typing import Tuple

from users import UserService, UserCreate
from .jwt import JWTManager, get_jwt_manager
from core import RedisManager, get_redis_manager
from schemas import UserAuth, UserBaseEmail, UserBaseID, UserRegister, UserLogOut

class AuthService:
    def __init__(self, jwt_manager: JWTManager, redis_manager: RedisManager):
        self._jwt_manager = jwt_manager
        self._redis_manager = redis_manager
        self._pwd_context = PasswordHash.recommended()

    async def register_user(self, user: UserRegister, user_service: UserService) -> UserCreate:
        if not await user_service.get_user_by_email(UserBaseEmail(email=user.email)):
            password_hash = self._pwd_context.hash(user.password)
            new_user = UserCreate(
                email=user.email,
                name=user.name,
                surname=user.surname,
                password_hash=password_hash
            )
            
            return new_user
        
        raise HTTPException(status_code=400, detail=f"Пользователь с таким email: {user.email} уже сущетсвует.")

    async def login_user(self, user: UserAuth, user_service: UserService) -> Tuple[str, str]:
        current_user = await user_service.get_user_by_email(user.email)

        if current_user:
            password_hash = user_service.get_user_password_hash(UserBaseEmail(email=user.email))

            if self._pwd_context.verify(user.password, password_hash):
                payload = {"id": current_user.id}
                access_token = self._jwt_manager.create_token(payload, "access")
                refresh_token = self._jwt_manager.create_token(payload, "refresh")

                ttl_seconds = self._jwt_manager.get_refresh_token_ttl_seconds
                await self._redis_manager.create_session(str(current_user.id), refresh_token, ttl_seconds)

                return access_token, refresh_token
            
            raise HTTPException(status_code=401, detail="Неверный пароль.")
        raise HTTPException(status_code=404, detail="Пользователь не найден.")

    async def logout_user(self, user: UserLogOut, user_service: UserService) -> None:
        if await user_service.get_user_by_id(user.id):
            await self._redis_manager.revoke_session(user.token)
            return
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    

async def get_auth_service(jwt_manager: JWTManager = Depends(get_jwt_manager), redis_manager: RedisManager = Depends(get_redis_manager)) -> AuthService:
    return AuthService(jwt_manager=jwt_manager, redis_manager=redis_manager)
