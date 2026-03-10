from .jwt import get_jwt_manager, get_redis_manager, JWTManager, RedisManager
from pwdlib import PasswordHash
from pydantic import BaseModel
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class UserCreate(BaseModel):
    name: str
    surname: str
    email: str
    password: str

class UserAuth(BaseModel):
    id: int
    password: str
    email: str

class UserBase(BaseModel):
    email: str

db = {} # mock
counter = 0

security = HTTPBearer(auto_error=False)

class AuthService:
    def __init__(self,  jwt_manager: JWTManager):
        #self.redis_manager = redis_manager
        self.jwt_manager = jwt_manager
        self.password_hash = PasswordHash.recommended()

    async def register_new_user(self, user: UserCreate, counter=counter):
        if user.email not in db:
            password_hash = self.password_hash.hash(user.password)
            db[user.email] = {
                "id": counter,
                "name": user.name,
                "surname": user.surname,
                "password_hash": password_hash,
                "refresh_token": None
            }
            counter += 1
            # Это все моковое
            return {
                "id": counter - 1,
                "name": user.name,
                "surname": user.surname,
                "email": user.email
            }
        return HTTPException(status_code=400, detail=f"Пользователь с email {user.email} уже существует.")
    
    async def authenticate_user(self, user: UserAuth):
        # мок
        if user.email in db:
            password_hash = db[user.email]["password_hash"]
            if  self.password_hash.verify(user.password, password_hash):
                payload = {"sub": str(user.id)}
                access_token = await self.jwt_manager.create_token(payload, "access")
                refresh_token = await self.jwt_manager.create_token(payload, "refresh")
                db[user.email]["refresh_token"] = refresh_token

                return access_token, refresh_token
            raise HTTPException(status_code=401, detail="Неверный пароль.")
        raise HTTPException(status_code=404, detail="Пользователь не найден.")        


async def get_current_user(
        jwt_manager: JWTManager = Depends(get_jwt_manager), 
        credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
    if not credentials:
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Bearer"})
    token = credentials.credentials
    user_id = await jwt_manager.verify_token(token)
    for user in db.values():
        if int(user_id) == user["id"]:
            return True
        
        
    raise HTTPException(status_code=404, detail="Пользователь не найден.")


def get_auth_service(
        jwt_manager: JWTManager = Depends(get_jwt_manager)
    ):
    return AuthService(jwt_manager)
        

    


