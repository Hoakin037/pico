from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Users

from . import UserAuth, UserBaseID, UserBaseEmail, UserCreate

class UserRepository:

    async def get_user_by_id(self, user: UserBaseID, session: AsyncSession):
        current_user = await session.execute(select(Users).where(Users.id)==user.id)
        current_user = current_user.scalars().first()

        return current_user
    
    async def get_user_by_email(self, user: UserBaseEmail, session: AsyncSession):
        current_user = session.execute(select(Users).where(Users.email)==user.email)
        current_user = current_user.scalars().first()

        return current_user
    
    
