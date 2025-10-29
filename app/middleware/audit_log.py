import hashlib
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.logistics.models import AuditLog


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return await call_next(request)

        body = await request.body()

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        request._receive = receive

        response = await call_next(request)

        user_id = getattr(request.user, "id", None)
        if not user_id:
            return response

        payload_hash = hashlib.sha256(body).hexdigest() if body else ""

        await AuditLog.create(
            user_id=user_id,
            endpoint=f"{request.method} {request.url.path}",
            payload_hash=payload_hash,
        )

        return response
