from pydantic import BaseModel, EmailStr, Field
from fastapi.responses import JSONResponse
class UserBaseID(BaseModel):
    id: int

class UserBaseEmail(BaseModel):
    email: EmailStr = Field(max_length=144)

class UserRegister(UserBaseEmail):
    name: str = Field(max_length=36)
    surname: str = Field(max_length=36)
    email: EmailStr = Field(max_length=144)
    password: str = Field(max_length=36)

class UserAuth(UserBaseEmail):
    password: str = Field(max_length=36)

class UserTokens(UserBaseID):
    access_token: str
    refresh_token: str

class UserLogOut(UserBaseID):
    refresh_token: str