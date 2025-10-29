from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
from redis.asyncio import Redis
from starlette.responses import JSONResponse

from app.service.redis_service import get_redis

RATE_LIMIT = 100
WINDOW_SECONDS = 600


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        user = request.scope.get("user")
        if not user:
            return await call_next(request)

        redis: Redis = await get_redis()
        key = f"rate_limit:user:{user.id}"
        now = int(time.time())

        script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])

        local count = redis.call('INCR', key)
        if count == 1 then
            redis.call('EXPIRE', key, window)
        end
        if count > limit then
            local ttl = redis.call('TTL', key)
            return {count, ttl}
        end
        return {count, -1}
        """

        result = await redis.eval(script, 1, key, now, WINDOW_SECONDS, RATE_LIMIT)
        count, ttl = result

        if ttl > 0:
            return JSONResponse(
                status_code=429,
                content={"detail": f"Rate limit exceeded. Retry after {ttl}s"},
                headers={"Retry-After": str(ttl)},
            )

        response = await call_next(request)
        response.headers.update({
            "X-RateLimit-Limit": str(RATE_LIMIT),
            "X-RateLimit-Remaining": str(RATE_LIMIT - count),
            "X-RateLimit-Reset": str(now + WINDOW_SECONDS),
        })
        return response
