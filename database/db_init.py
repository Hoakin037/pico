from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.tables import Base
from core import get_database_settings

settings = get_database_settings()
engine = create_async_engine(url=settings.get_database_url, pool_pre_ping=True)

async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def init_db():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        print("База данных успешно создана.")
    await engine.dispose()

async def get_session():
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            raise Exception(f"Ошибка бд: {e}")

            