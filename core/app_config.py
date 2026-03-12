from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    from core import init_redis_client, get_redis_config
    from database import db_manager

    redis_config = get_redis_config()
    redis_client = init_redis_client(redis_config)
    app.state.redis_client = redis_client

    await db_manager.database_init()
    print("База данных и Redis успешно инициализированы.")

    yield

    await redis_client.close()
    await redis_client.connection_pool.disconnect()

def app_fabric() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],    
    )
    #добавить импорт роута

    return app