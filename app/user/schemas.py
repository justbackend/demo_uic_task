from typing import Literal

from pydantic import BaseModel


UserRoleLiteral = Literal["admin", "agent"]

class UserCreate(BaseModel):
    username: str
    password: str
    role: UserRoleLiteral


class UpdateUser(BaseModel):
    id: str
    username: str
    password: str


class UserCurrent(BaseModel):
    id: int
    username: str
    role: UserRoleLiteral


class Token(BaseModel):
    id: int
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str