from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from app.auth import get_password_hash, create_access_token, verify_password
from app.user.models import User


class UserService:

    @staticmethod
    async def register(form):
        user = await User.filter(username=form.username).first()
        if user:
            raise HTTPException(status_code=400, detail="Username already registered")

        hashed_password = get_password_hash(form.password)
        user = await User.create(username=form.username, password=hashed_password, role=form.role)

        access_token = create_access_token({'id': user.id})
        return access_token


    @staticmethod
    async def login(form: OAuth2PasswordRequestForm):
        user = await User.filter(username=form.username).first()
        if not user or not verify_password(form.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return create_access_token(data={"sub": str(user.id)})