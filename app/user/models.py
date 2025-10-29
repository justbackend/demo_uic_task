from enum import StrEnum

from tortoise import fields
from tortoise.models import Model


class Role(StrEnum):
    ADMIN = 'admin'
    AGENT = 'agent'


class User(Model):
    username = fields.CharField(max_length=32)
    password = fields.CharField(max_length=255)
    role = fields.CharEnumField(Role, default=Role.AGENT)

    class Meta:
        table = "users"
        indexes = (
            ("username",),
            ("role",),
        )
