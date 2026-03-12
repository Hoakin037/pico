from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Users

class UserRepository:
    async def get_user_by_id(self, id: int, session: AsyncSession) -> Users:
        current_user = await session.execute(select(Users).where(Users.id==id))
        current_user = current_user.scalars().first()

        return current_user
    
    async def get_user_by_email(self, email: str, session: AsyncSession) -> Users:
        current_user = await session.execute(select(Users).where(Users.email==email))
        current_user = current_user.scalars().first()

        return current_user
    
    async def create_user(self, user: Users, session: AsyncSession) -> None:
        await session.add(user)

    async def set_user_activity(self, user: Users, is_active: bool) -> Users:
        user.is_active = is_active
        return user
    
async def get_user_repository():
    return UserRepository()