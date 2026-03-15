from pydantic import BaseModel, EmailStr, Field

class UserBaseID(BaseModel):
    id: int

class UserBaseEmail(BaseModel):
    email: EmailStr = Field(max_length=144)

class UserCreate(UserBaseEmail):
    name: str = Field(max_length=36)
    surname: str = Field(max_length=36)
    email: EmailStr = Field(max_length=144)
    password_hash: str = Field(max_length=300)

class UserUpdate(UserBaseID):
    name: str | None = Field(max_length=36)
    surname: str | None = Field(max_length=36)

class UserResponse(UserBaseID, UserBaseEmail):
    name: str = Field(max_length=36)
    surname: str = Field(max_length=36)
