from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .tables import Base, Users


URL = f"postgresql+asyncpg://postgres:fimoZNyiYe6an@localhost:5432/pico"
engine = create_async_engine(url=URL, pool_pre_ping=True)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

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
            await session.rollback()
            raise Exception(f"Ошибка с бд: {e}")
        finally:
            session.close()
