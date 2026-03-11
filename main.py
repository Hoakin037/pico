from app.database import init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routes import rout


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:5173", "http://192.168.0.109","http://192.168.0.109:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,               
)

app.include_router(rout)