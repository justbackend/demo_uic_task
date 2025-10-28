# from inspect import getmembers

from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from .database import TORTOISE_ORM


def init_db(app: FastAPI):

    """
    Init database models.
    :param app:
    :return:
    """
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    )