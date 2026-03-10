from pydantic import BaseModel, EmailStr, Field

class UserBaseID(BaseModel):
    id: int

class UserBaseEmail(BaseModel):
    email: EmailStr = Field(max_length=144)

class UserCreate(UserBaseEmail):
    name: str = Field(max_length=36)
    surname: str = Field(max_length=36)
    email: EmailStr = Field(max_length=144)
    password: str = Field(max_length=36)

class UserAuth(UserBaseEmail):
    email: EmailStr = Field(max_length=144)
    password: str = Field(max_length=36)

