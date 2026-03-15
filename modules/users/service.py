from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException

from database import get_session, Users
from .schemas import UserCreate, UserBaseID, UserBaseEmail, UserUpdate, UserResponse
from .repository import UserRepository, get_user_repository
from .interfaces import UserProvider

class UserService(UserProvider):
    def __init__(self, session: AsyncSession, repository: UserRepository):
        self._session = session
        self._repository = repository

    async def get_user_by_id(self, user: UserBaseID) -> UserResponse:
        current_user = await self._repository.get_user_by_id(user.id, self._session)
        if current_user:
            return UserResponse(
                id=current_user.id,
                email=current_user.email,
                name=current_user.name,
                surname=current_user.surname
            )

    async def get_user_by_email(self, user: UserBaseEmail) -> UserResponse:
        current_user = await self._repository.get_user_by_email(user.email, self._session)
        
        if current_user:
            return UserResponse(
                id=current_user.id,
                email=current_user.email,
                name=current_user.name,
                surname=current_user.surname
            )

    async def get_user_password_hash(self, user: UserBaseEmail):
        user = await self._repository.get_user_by_email(user.email, self._session)
        
        return user.password_hash

    async def create_user(self, user: UserCreate) -> UserResponse:
        user = Users(
            name=user.name,
            surname=user.surname,
            password_hash=user.password_hash,
            email=user.email
        )
        await self._repository.create_user(user, self._session)
        await self._session.commit()
        await self._session.refresh(user)
        user = await self.get_user_by_email(UserBaseEmail(email=user.email))

        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            surname=user.surname    
        )


    # async def update_user_info(self, user: UserUpdate) -> Users:
    #     current_user = await 
    #     user.name = new_user_info.name if new_user_info.name else user.name
    #     user.surname = new_user_info.surname if new_user_info.surname else user.surname
        
    #     return user

 
async def get_user_service(session: AsyncSession = Depends(get_session), repository: UserRepository = Depends(get_user_repository)):
    return UserService(session, repository)
