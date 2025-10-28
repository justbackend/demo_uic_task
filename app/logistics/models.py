from enum import StrEnum
from tortoise import fields
from tortoise.models import Model
from app.user.models import User


class VehicleType(StrEnum):
    SEDAN = "sedan"
    SUV = "suv"
    TRUCK = "truck"


class OrderStatus(StrEnum):
    DRAFT = "draft"
    QUOTED = "quoted"
    BOOKED = "booked"
    DELIVERED = "delivered"


class Lead(Model):
    name = fields.CharField(max_length=128)
    phone = fields.CharField(max_length=15)
    email = fields.CharField(max_length=254)

    origin_zip = fields.CharField(max_length=20)
    dest_zip = fields.CharField(max_length=20)

    vehicle_type = fields.CharEnumField(
        VehicleType,
        description="sedan | suv | truck",
    )
    operable = fields.BooleanField()

    created_by: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="leads", on_delete=fields.SET_NULL, null=True
    )

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "leads"
        indexes = (
            ("origin_zip", "dest_zip"),
            ("created_by",),
        )
        ordering = ["-created_at"]


class Order(Model):
    lead: fields.ForeignKeyRelation["Lead"] = fields.ForeignKeyField(
        "models.Lead",
        related_name="orders",
        on_delete=fields.CASCADE,
    )

    status = fields.CharEnumField(
        OrderStatus,
        default=OrderStatus.DRAFT,
        description="draft | quoted | booked | delivered",
    )

    base_price = fields.DecimalField(max_digits=12, decimal_places=2, null=True)
    final_price = fields.DecimalField(max_digits=12, decimal_places=2, null=True)
    notes = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "orders"
        indexes = (
            ("lead", "status"),
            ("status",),
            ("created_at",),
        )
        ordering = ["-created_at"]


class AuditLog(Model):
    id = fields.BigIntField(pk=True)
    user_id = fields.BigIntField()
    endpoint = fields.CharField(max_length=255)
    payload_hash = fields.CharField(max_length=64)   # SHA-256 hex
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "audit_logs"
        indexes = (("user_id", "created_at"),)