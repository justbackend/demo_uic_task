from fastapi import FastAPI
from .initializer import init_db
from .logger import setup_logging
from .middleware.audit_log import AuditMiddleware
from .middleware.idempotency import IdempotencyMiddleware
from .middleware.throttling import RateLimitMiddleware
from .middleware.user_attach import AuthMiddleware
from app.user.routes import user_router
from app.logistics.routes import router as logistics_router
from starlette.middleware.cors import CORSMiddleware

logger = setup_logging()

app = FastAPI()
init_db(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)


app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(IdempotencyMiddleware)
app.add_middleware(AuthMiddleware)


app.include_router(user_router)
app.include_router(logistics_router)
