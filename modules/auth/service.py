from pwdlib import PasswordHash
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from modules.users import UserCreate, UserBaseID, get_user_service
from core import JWTManager, get_jwt_manager
from core import RedisManager, get_redis_manager
from .schemas import UserAuth, UserBaseEmail, UserBaseID, UserRegister, UserTokens, UserLogOut
from modules.users import UserProvider

security = HTTPBearer()

class AuthService:
    def __init__(self, jwt_manager: JWTManager, redis_manager: RedisManager, user_provider: UserProvider):
        self._jwt_manager = jwt_manager
        self._redis_manager = redis_manager
        self._pwd_context = PasswordHash.recommended()
        self._user_provider = user_provider

    async def register_user(self, user: UserRegister) -> UserCreate:
        if not await self._user_provider.get_user_by_email(UserBaseEmail(email=user.email)):
            password_hash = self._pwd_context.hash(user.password)
            new_user = UserCreate(
                email=user.email,
                name=user.name,
                surname=user.surname,
                password_hash=password_hash
            )
            
            return new_user
        
        raise HTTPException(status_code=400, detail=f"Пользователь с таким email: {user.email} уже сущетсвует.")

    async def login_user(self, user: UserAuth) -> UserTokens:
        current_user = await self._user_provider.get_user_by_email(UserBaseEmail(email=user.email))

        if current_user:
            password_hash = await self._user_provider.get_user_password_hash(UserBaseEmail(email=user.email)) 

            if self._pwd_context.verify(user.password, password_hash):
                user_login_response = await self.create_tokens(current_user.id)

                return user_login_response
            
            raise HTTPException(status_code=401, detail="Неверный пароль.")
        raise HTTPException(status_code=404, detail="Пользователь не найден.")

    async def create_tokens(self, user_id: int) -> UserTokens:
        payload = {"sub": str(user_id)}
        access_token = await self._jwt_manager.create_token(payload, "access")
        refresh_token = await self._jwt_manager.create_token(payload, "refresh")
        # ttl_seconds = self._jwt_manager.get_refresh_token_ttl_seconds
                # await self._redis_manager.create_session(str(current_user.id), refresh_token, ttl_seconds)

        # mock
        await self._redis_manager.create_session(str(user_id), refresh_token, 3 * 60)

        return UserTokens(
            id=user_id,
            access_token=access_token,
            refresh_token=refresh_token    
        )

    async def logout_user(self, user: UserLogOut) -> None:
        if await self._user_provider.get_user_by_id(UserBaseID(id=user.id)):
            if await self._redis_manager.get_session(user.refresh_token):
                await self._redis_manager.revoke_session(user.refresh_token)
                return
            raise HTTPException(status_code=404, detail="Пользователь уже вышел из аккаунта на данном устройстве.")
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    
    async def refresh_tokens(self, refresh_token: str) -> UserTokens:
        print("в рефреше")
        user_id = await self._jwt_manager.verify_token(refresh_token)
        current_user = await self._user_provider.get_user_by_id(UserBaseID(id=user_id))
        user_session = await self._redis_manager.get_session(refresh_token)
        
        if current_user and user_session:
            await self._redis_manager.revoke_session(refresh_token)
            
            return await self.create_tokens(user_id)
        raise HTTPException(status_code=401, detail="Не корректный токен или пользователь не сущетсвует.")
            

async def get_auth_service(
    jwt_manager: JWTManager = Depends(get_jwt_manager), redis_manager: RedisManager = Depends(get_redis_manager),
    user_provider: UserProvider = Depends(get_user_service)
    ) -> AuthService:
    
    return AuthService(
        jwt_manager=jwt_manager, 
        redis_manager=redis_manager,
        user_provider=user_provider
    )

async def get_current_user(
    jwt_manager: JWTManager = Depends(get_jwt_manager),
    credentials: HTTPAuthorizationCredentials = Depends(security), user_provider= Depends(get_user_service)
) -> UserBaseID:
    if credentials:
        access_token = credentials.credentials
        user_id = await jwt_manager.verify_token(access_token)
        current_user = await user_provider.get_user_by_id(UserBaseID(id=user_id))
        
        return UserBaseID(id=current_user.id)
    
    raise HTTPException(status_code=401, detail="Токен некорректный или отсутсвует")
        