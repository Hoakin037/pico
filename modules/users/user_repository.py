from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Users
from .schemas import  UserBaseID, UserBaseEmail, UserCreate, UserUpdate

class UserRepository:
    async def get_user_by_id(self, user: UserBaseID, session: AsyncSession):
        current_user = await session.execute(select(Users).where(Users.id==user.id))
        current_user = current_user.scalars().first()

        return current_user
    
    async def get_user_by_email(self, user: UserBaseEmail, session: AsyncSession):
        current_user = await session.execute(select(Users).where(Users.email==user.email))
        current_user = current_user.scalars().first()

        return current_user
    
    async def create_user(self, user: UserCreate, session: AsyncSession):
        await session.add(Users(
            name=user.name,
            surname=user.surname,
            email=user.email,
            password_hash = user.password
        ))

    async def update_user_info(self, user: Users, new_user_info: UserUpdate):
        user.name = new_user_info.name if new_user_info.name else user.name
        user.surname = new_user_info.surname if new_user_info.surname else user.surname
        
        return user
