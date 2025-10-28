from fastapi import HTTPException

from app.auth import get_password_hash, create_access_token
from app.user.models import User


async def register(form):
    user = await User.filter(username=form.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(form.password)
    user = await User.create(username=form.username, password=hashed_password)

    access_token = create_access_token({'id': user.id})
    return access_token
