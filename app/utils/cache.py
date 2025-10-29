import hashlib
import json
from functools import wraps
from fastapi import Request
from redis.asyncio import Redis

from app.service.redis_service import get_redis

def make_cache_key(request: Request):
    raw_key = f"{request.url.path}?{request.url.query}&method={request.method}"
    return hashlib.sha256(raw_key.encode()).hexdigest()

def redis_cache(ttl: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request | None = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get("request")

            if not request:
                return await func(*args, **kwargs)

            cache_key = make_cache_key(request)

            redis: Redis = await get_redis()

            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)

            response = await func(*args, **kwargs)

            try:
                await redis.set(cache_key, json.dumps(response), ex=ttl)
            except Exception:
                pass

            return response
        return wrapper
    return decorator
