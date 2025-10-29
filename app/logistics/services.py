import asyncio
import os
from typing import List, Optional
from uuid import uuid4
from decimal import Decimal
import httpx
from fastapi import UploadFile, HTTPException

from app.logistics.models import Lead, Order, VehicleType, OrderStatus
from app.logistics.schemas import (
    LeadCreate, LeadUpdate, LeadOut,
    OrderCreate, OrderUpdate, OrderOut, QuoteCalcRequest, QuoteCalcResponse, PriceBreakdown,
)
from app.utils.functions import save_file

import logging

logger = logging.getLogger("app")
WEBHOOK_URL = "https://example.com/webhook"


async def send_webhook(payload: dict, retries: int = 3, backoff_factor: int = 2):
    delay = 1
    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(WEBHOOK_URL, json=payload)
                response.raise_for_status()
            logger.info(f"Webhook sent successfully on attempt {attempt}", extra={"payload": payload})
            return
        except Exception as e:
            logger.warning(f"Webhook attempt {attempt} failed: {e}", extra={"payload": payload})
            if attempt < retries:
                await asyncio.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error("Webhook failed after all retries", extra={"payload": payload, "error": str(e)})


# def _vehicle_type_from_str(s: str) -> VehicleType:
#     return {
#         "sedan": VehicleType.SEDAN,
#         "suv": VehicleType.SUV,
#         "truck": VehicleType.TRUCK,
#     }[s.lower()]
#
#
# def _order_status_from_str(s: str) -> OrderStatus:
#     return {
#         "draft": OrderStatus.DRAFT,
#         "quoted": OrderStatus.QUOTED,
#         "booked": OrderStatus.BOOKED,
#         "delivered": OrderStatus.DELIVERED,
#     }[s.lower()]


class LeadService:
    @staticmethod
    async def create(data: LeadCreate, user_id: int) -> LeadOut:
        payload = data.model_dump(mode="python")
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
        qs = Lead.filter(created_by_id=user_id)

        if origin_zip:
            qs = qs.filter(origin_zip__icontains=origin_zip)
        if dest_zip:
            qs = qs.filter(dest_zip__icontains=dest_zip)
        if vehicle_type:
            qs = qs.filter(vehicle_type=vehicle_type)
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
            upd["vehicle_type"] = upd["vehicle_type"]
        await lead.update_from_dict(upd)
        await lead.save()
        return LeadOut.model_validate(lead)

    @staticmethod
    async def delete(lead_id: int) -> None:
        lead = await Lead.get(id=lead_id)
        await lead.delete()


    @staticmethod
    async def upload_attachment(lead_id: int, file: UploadFile):
        lead = await Lead.get(id=lead_id)

        if not (file.content_type.startswith("image/") or file.content_type == "application/pdf"):
            raise HTTPException(400, "Invalid file type. Only images or PDFs are allowed.")

        content = await file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(400, "File too large. Maximum 5 MB allowed.")
        await file.seek(0)

        ext = file.filename.split(".")[-1]
        object_name = f"{uuid4()}.{ext}"

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_dir = os.path.join(base_dir, "uploads", "attachments")
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, object_name)

        await save_file(file, file_path)

        lead.attachment = os.path.join("uploads", "attachments", object_name)
        await lead.save()
        return {
            "lead_id": lead.id,
            "attachment": lead.attachment,
        }

class OrderService:
    @staticmethod
    async def create(data: OrderCreate) -> OrderOut:
        payload = data.model_dump(mode="python")
        payload["status"] = data.status
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
        qs = Order.all()

        if lead_id:
            qs = qs.filter(lead_id=lead_id)
        if status:
            qs = qs.filter(status=status)

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
            upd["status"] = upd["status"]
        await order.update_from_dict(upd)
        await order.save()
        return OrderOut.model_validate(order)

    @staticmethod
    async def delete(order_id: int) -> None:
        order = await Order.get(id=order_id)
        await order.delete()



    @staticmethod
    def calculate_price(data: QuoteCalcRequest) -> QuoteCalcResponse:
        coeff = Decimal("1.5")

        type_bonus_map = {
            "sedan": Decimal("0"),
            "suv": Decimal("200"),
            "truck": Decimal("400"),
        }
        vehicle_type_bonus = type_bonus_map.get(data.vehicle_type, Decimal("0"))

        # Season bonus
        season_bonus_map = {
            "winter": Decimal("300"),
            "summer": Decimal("150"),
            "normal": Decimal("0"),
        }
        season_bonus = season_bonus_map.get(data.season, Decimal("0"))

        operable_adjustment = Decimal("-100" if data.operable else "200")

        distance_cost = Decimal(data.distance_km) * coeff

        final_price = (
                data.base_price
                + distance_cost
                + vehicle_type_bonus
                + season_bonus
                + operable_adjustment
        )

        breakdown = PriceBreakdown(
            base_price=data.base_price,
            distance_cost=distance_cost,
            vehicle_type_bonus=vehicle_type_bonus,
            season_bonus=season_bonus,
            operable_adjustment=operable_adjustment,
        )

        return QuoteCalcResponse(
            price_breakdown=breakdown,
            final_price=final_price.quantize(Decimal("0.01")),
        )