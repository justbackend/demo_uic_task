from app.config import settings

TORTOISE_ORM = {
    "connections": {
        "default": settings.postgres_url_tortoise,
    },
    "apps": {
        "models": {
            "models": ["app.user.models", "app.logistics.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
