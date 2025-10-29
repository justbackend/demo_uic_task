from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.sql.functions import current_user
from starlette import status

from app.auth import create_access_token, verify_password, get_current_user
from app.user.models import User

from app.user.schemas import UserCreate, UserCurrent
from fastapi import HTTPException

from app.user.services import UserService

user_router = APIRouter(
    prefix='/user'
)


@user_router.post("/register")
async def register_endpoint(form: UserCreate):
    access_token = await UserService.register(form)
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.post('/login')
async def login_for_access_token(form: OAuth2PasswordRequestForm = Depends()):
    access_token = await UserService.login(form)
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.post('/me')
async def me(user: UserCurrent =  Depends(get_current_user)):
    return user