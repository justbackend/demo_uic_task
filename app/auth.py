from typing import Annotated

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.util import await_only
from starlette import status
from starlette.requests import Request

from app.config import settings
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.user.models import User
from app.utils.constants import local_tz

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")
bearer_scheme = HTTPBearer(auto_error=False)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRE

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=local_tz) + expires_delta
    else:
        expire = datetime.now(tz=local_tz) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# async def current_user(token: str = Depends(oauth2_scheme)):
#     user_id = decode_access_token(token)
#     if user_id is None:
#         raise credentials_exception
#     user = await User.filter(id=user_id).first()
#     if user is None:
#         raise credentials_exception
#     return user

# async def current_user(request: Request, token: str = Depends(oauth2_scheme)):
#     if hasattr(request.state, "user") and request.state.user:
#         return request.state.user
#
#     user_id = decode_access_token(token)
#     if user_id is None:
#         raise credentials_exception
#
#     user = await User.filter(id=user_id).first()
#
#     if user is None:
#         raise credentials_exception
#
#     request.state.user = user
#     return user
#


# async def current_user(request: Request, token: str = Depends(oauth2_scheme)):
#     if hasattr(request.state, "user") and request.state.user:
#         return request.state.user
#
#     user_id = decode_access_token(token)
#     if user_id is None:
#         raise credentials_exception
#
#     user = await User.filter(id=user_id).first()
#
#     if user is None:
#         raise credentials_exception
#
#     request.state.user = user
#     return user




async def current_user(request: Request):
    user = request.scope["user"]
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    return user
# CurrentUser = Annotated[User, Depends(current_user)]
