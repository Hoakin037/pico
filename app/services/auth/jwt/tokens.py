from jwt import encode, decode, ExpiredSignatureError, InvalidSignatureError, DecodeError
from fastapi import HTTPException, Depends
from datetime import datetime, timezone, timedelta
from typing import Literal
from functools import lru_cache

from core import JWTConfig, get_jwt_config


class JWTManager:
    def __init__(self, config: JWTConfig):
        self.config = config

    async def create_token(self, payload: dict, token_type: Literal["refresh", "access"]):
        payload_copy = payload.copy()
        if token_type=="refresh":
            expires_delta = timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS)
        else:
            expires_delta = timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MIN)
        expire = datetime.now(timezone.utc) + expires_delta
        payload_copy.update({
            'type': token_type, 
            'exp': expire.timestamp(), # Срок действия
            "iat": datetime.now(timezone.utc).timestamp() # Время выпуска
            })

        return encode(
            payload_copy, 
            self.config.JWT_SECRET_KEY, 
            algorithm=self.config.JWT_ALGORITHM
        )
    
    async def verify_token(self, token: str):
        try:
            payload = decode(token, self.config.JWT_SECRET_KEY, self.config.JWT_ALGORITHM)
            user_id = payload.get("sub")
        except (ExpiredSignatureError, InvalidSignatureError, DecodeError):
            raise HTTPException(status_code=401, detail="Ошибка валидации jwt токена.")
        return user_id



def get_jwt_manager(config: JWTConfig = Depends(get_jwt_config)):
    return JWTManager(config)