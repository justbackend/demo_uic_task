from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from .initializer import init_db
from .middleware.user_attach import AuthMiddleware
from .middlewares import AuditMiddleware, RateLimitMiddleware
from .service.redis_service import get_redis, get_cache
from app.user.routes import user_router
from app.logistics.routes import router as logistics_router
from starlette.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Load the redis connection
    _app.redis = await get_redis()

    try:
        redis_cache = await get_cache()
        FastAPICache.init(RedisBackend(redis_cache), prefix="fastapi-cache")
        yield

    finally:
        await _app.redis.close()

app = FastAPI(lifespan=lifespan)
init_db(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthMiddleware)

# app.add_middleware(AuditMiddleware)

app.include_router(user_router)
app.include_router(logistics_router)
