from enum import IntEnum

from tortoise import fields
from tortoise.models import Model


class Role(IntEnum):
    ADMIN = 1
    AGENT = 2


class User(Model):
    username = fields.CharField(max_length=32)
    password = fields.CharField(max_length=255)
    role = fields.IntEnumField(Role, default=Role.AGENT)

    class Meta:
        table = "users"
        indexes = (
            ("username",),
            ("role",),
        )
