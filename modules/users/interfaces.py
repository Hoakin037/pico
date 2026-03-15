from typing import Protocol
from ..auth.schemas import UserBaseEmail, UserBaseID

class UserProvider(Protocol):
    async def get_user_password_hash(self, user:  UserBaseEmail):
        pass
    
    async def get_user_by_id(self, user: UserBaseID):
        pass

    async def get_user_by_email(self, user: UserBaseEmail):
        pass