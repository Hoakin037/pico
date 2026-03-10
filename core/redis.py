from .configs_settings import RedisConfig, get_redis_config

from redis import RedisError, ConnectionError
from redis.asyncio import Redis
from fastapi import Depends
import json
from typing import Dict, Any


class RedisManager:
    def __init__(self, config: RedisConfig):
        self.prefix = config.prefix
        try:
            self.client = Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                password=config.REDIS_PASSWORD,
                decode_responses=config.REDIS_DECODE_RESPONSES,
                socket_connect_timeout=5,
                socket_timeout=5
            )
        except ConnectionError as e:
            raise Exception(f"{e}")

    def _get_token_key(self, token: str):
        return f"{self.prefix}:refresh:{token}"

    def _get_user_sessions_key(self, user_id: str):
        return f"{self.prefix}:user_sessions:{user_id}"

    def create_session(self, user_id: str, token: str, device_info: Dict[str, Any], ttl_seconds: int):
       
        token_key = self._get_token_key(token)
        user_sessions_key = self._get_user_sessions_key(user_id)
        
        session_data = json.dumps({
            "user_id": user_id,
            **device_info
        })

        try:
            pipe = self.client.pipeline()
            pipe.setex(token_key, ttl_seconds, session_data)
            # Добавляем токен в множество сессий пользователя 
            pipe.sadd(user_sessions_key, token)
            # Устанавливаем TTL на множество сессий
            pipe.expire(user_sessions_key, ttl_seconds + 60) 
            pipe.execute()
            return True
        except RedisError as e:
            raise Exception(f"{e}")

    def get_session(self, token: str):
        token_key = self._get_token_key(token)
        try:
            user_data = self.client.get(token_key)
            if not user_data:
                return None
            return json.loads(user_data)
        except RedisError as e:
            raise Exception(f"{e}")
        except json.JSONDecodeError as e:
            raise Exception(f"{e}")

    def revoke_session(self, token: str):
        token_key = self._get_token_key(token)
        try:
            # Сначала получаем user_id, чтобы почистить обратный индекс
            data = self.client.get(token_key)
            if data:
                session_data = json.loads(data)
                user_id = session_data.get("user_id")
                
                pipe = self.client.pipeline()
                pipe.delete(token_key)
                if user_id:
                    pipe.srem(self._get_user_sessions_key(user_id), token)
                pipe.execute()
            else:
                # Если токена нет, просто пробуем удалить (на случай гонки)
                self.client.delete(token_key)
            
            return True
        except Exception:
            return False

    def revoke_all_user_sessions(self, user_id: str):
        user_sessions_key = self._get_user_sessions_key(user_id)
        try:
            # Получаем все токены пользователя
            tokens = self.client.smembers(user_sessions_key)
            if not tokens:
                return 0
            
            pipe = self.client.pipeline()
            # Удаляем ключи токенов
            for token in tokens:
                pipe.delete(self._get_token_key(token))
            # Удаляем само множество сессий
            pipe.delete(user_sessions_key)
            pipe.execute()
            
            return len(tokens)
        except RedisError as e:
            raise Exception(f"{e}")

    def close(self):
        self.client.close()



def get_redis_manager(config: RedisConfig = Depends(get_redis_config)):
    return RedisManager(config)