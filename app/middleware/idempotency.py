import json

from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from app.service.redis_service import get_redis
import logging

logger = logging.getLogger("app")


class IdempotencyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, ttl: int = 300):
        super().__init__(app)
        self.ttl = ttl

    async def dispatch(self, request, call_next):
        if request.method not in {"POST", "PUT", "PATCH"}:
            return await call_next(request)

        idempotency_key = request.headers.get("Idempotency-Key")
        if not idempotency_key:
            return await call_next(request)

        redis: Redis = await get_redis()
        redis_key = f"idempotency:{idempotency_key}"

        cached = await redis.get(redis_key)

        if cached:
            data = json.loads(cached)
            return JSONResponse(content=data)

        response: Response = await call_next(request)

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        response.body_iterator = iter([body])

        if 200 <= response.status_code < 300:
            try:
                decoded = body.decode()
                await redis.set(redis_key, decoded, ex=self.ttl)
            except Exception as e:
                logger.exception("⚠️ Idempotency cache error:", e)

        return response
