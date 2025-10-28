# app/logistics/services.py
from typing import List, Optional
from tortoise.expressions import Q
from tortoise.functions import Lower
from app.logistics.models import Lead, Order, VehicleType, OrderStatus
from app.logistics.schemas import (
    LeadCreate, LeadUpdate, LeadOut,
    OrderCreate, OrderUpdate, OrderOut,
)


# --------------------------------------------------------------------------- #
#  Helper: enum from string (used when Pydantic gives us a str)
# --------------------------------------------------------------------------- #
def _vehicle_type_from_str(s: str) -> VehicleType:
    return {
        "sedan": VehicleType.SEDAN,
        "suv": VehicleType.SUV,
        "truck": VehicleType.TRUCK,
    }[s.lower()]


def _order_status_from_str(s: str) -> OrderStatus:
    return {
        "draft": OrderStatus.DRAFT,
        "quoted": OrderStatus.QUOTED,
        "booked": OrderStatus.BOOKED,
        "delivered": OrderStatus.DELIVERED,
    }[s.lower()]


# --------------------------------------------------------------------------- #
#  LeadService
# --------------------------------------------------------------------------- #
class LeadService:
    @staticmethod
    async def create(data: LeadCreate, user_id: int) -> LeadOut:
        payload = data.model_dump(mode="python")               # keep enum objects
        payload["vehicle_type"] = _vehicle_type_from_str(data.vehicle_type)
        payload["created_by_id"] = user_id
        lead = await Lead.create(**payload)
        return LeadOut.model_validate(lead)

    @staticmethod
    async def get(lead_id: int) -> Optional[LeadOut]:
        lead = await Lead.get_or_none(id=lead_id).prefetch_related("created_by")
        return LeadOut.model_validate(lead) if lead else None

    @staticmethod
    async def list(
        user_id: int,
        *,
        origin_zip: Optional[str] = None,
        dest_zip: Optional[str] = None,
        vehicle_type: Optional[str] = None,
        operable: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[LeadOut]:
        """
        List leads for a user with optional filters + pagination.
        Uses selectinload to avoid N+1 on `created_by`.
        """
        qs = Lead.filter(created_by_id=user_id)

        if origin_zip:
            qs = qs.filter(origin_zip__icontains=origin_zip)
        if dest_zip:
            qs = qs.filter(dest_zip__icontains=dest_zip)
        if vehicle_type:
            qs = qs.filter(vehicle_type=_vehicle_type_from_str(vehicle_type))
        if operable is not None:
            qs = qs.filter(operable=operable)

        leads = await qs.order_by("-created_at") \
            .offset(offset) \
            .limit(limit) \
            .select_related("created_by")

        return [LeadOut.model_validate(l) for l in leads]

    @staticmethod
    async def update(lead_id: int, data: LeadUpdate) -> LeadOut:
        lead = await Lead.get(id=lead_id)
        upd = data.model_dump(exclude_unset=True, mode="python")
        if "vehicle_type" in upd:
            upd["vehicle_type"] = _vehicle_type_from_str(upd["vehicle_type"])
        lead.update_from_dict(upd)
        await lead.save()
        return LeadOut.model_validate(lead)

    @staticmethod
    async def delete(lead_id: int) -> None:
        lead = await Lead.get(id=lead_id)
        await lead.delete()


# --------------------------------------------------------------------------- #
#  OrderService
# --------------------------------------------------------------------------- #
class OrderService:
    @staticmethod
    async def create(data: OrderCreate) -> OrderOut:
        payload = data.model_dump(mode="python")
        payload["status"] = _order_status_from_str(data.status)
        order = await Order.create(**payload)
        return OrderOut.model_validate(order)

    @staticmethod
    async def get(order_id: int) -> Optional[OrderOut]:
        order = await Order.get_or_none(id=order_id) \
            .prefetch_related("lead__created_by")
        return OrderOut.model_validate(order) if order else None

    @staticmethod
    async def list(
        lead_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[OrderOut]:
        """
        List orders with optional filters + pagination.
        Eager-loads `lead` and `lead.created_by` → no N+1.
        """
        qs = Order.all()

        if lead_id:
            qs = qs.filter(lead_id=lead_id)
        if status:
            qs = qs.filter(status=_order_status_from_str(status))

        orders = await qs.order_by("-created_at") \
            .offset(offset) \
            .limit(limit) \
            .select_related("lead__created_by")

        return [OrderOut.model_validate(o) for o in orders]

    @staticmethod
    async def update(order_id: int, data: OrderUpdate) -> OrderOut:
        order = await Order.get(id=order_id)
        upd = data.model_dump(exclude_unset=True, mode="python")
        if "status" in upd:
            upd["status"] = _order_status_from_str(upd["status"])
        order.update_from_dict(upd)
        await order.save()
        return OrderOut.model_validate(order)

    @staticmethod
    async def delete(order_id: int) -> None:
        order = await Order.get(id=order_id)
        await order.delete()