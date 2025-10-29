# app/middleware/auth.py
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth import decode_access_token
from app.user.models import User


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        authorization: str | None = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)

        user = None
        if scheme.lower() == "bearer" and token:
            user_id = decode_access_token(token)
            if user_id:
                user = await User.get_or_none(id=user_id)

        request.scope["user"] = user
        response = await call_next(request)
        return response