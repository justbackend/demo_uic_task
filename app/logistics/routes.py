# app/logistics/routes.py
import asyncio

from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from typing import List, Optional

from starlette.requests import Request

from app.auth import get_admin
from app.logistics.models import OrderStatus, Lead
from app.logistics.services import LeadService, OrderService, send_webhook
from app.logistics.schemas import (
    LeadCreate, LeadOut, LeadUpdate,
    OrderCreate, OrderOut, OrderUpdate, QuoteCalcResponse, QuoteCalcRequest, RepriceResponse,
)
from app.logistics.tasks import enqueue_reprice
from app.user.models import User
from app.utils.cache import redis_cache

router = APIRouter(prefix="/logistics", tags=["logistics"])


@router.post("/leads", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: LeadCreate,
    user: User = Depends(get_admin),
):
    return await LeadService.create(payload, user_id=user.id)


@router.get("/leads/{lead_id}", response_model=LeadOut)
async def read_lead(lead_id: int, user: User = Depends(get_admin),):
    lead = await LeadService.get(lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    return lead

@router.get("/leads", response_model=List[LeadOut])
@redis_cache(ttl=60)
async def list_leads(
    request: Request,
    user: User = Depends(get_admin),
    origin_zip: Optional[str] = Query(None, max_length=20),
    dest_zip: Optional[str] = Query(None, max_length=20),
    vehicle_type: Optional[str] = Query(None, regex="^(sedan|suv|truck)$"),
    operable: Optional[bool] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return await LeadService.list(
        user_id=user.id,
        origin_zip=origin_zip,
        dest_zip=dest_zip,
        vehicle_type=vehicle_type,
        operable=operable,
        limit=limit,
        offset=offset,
    )


@router.patch("/leads/{lead_id}", response_model=LeadOut)
async def update_lead(lead_id: int, payload: LeadUpdate, user: User = Depends(get_admin)):
    if not await LeadService.get(lead_id):
        raise HTTPException(404, "Lead not found")
    return await LeadService.update(lead_id, payload)


@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: int, user: User = Depends(get_admin)):
    if not await LeadService.get(lead_id):
        raise HTTPException(404, "Lead not found")
    await LeadService.delete(lead_id)


@router.post("/leads/{lead_id}/attachments", response_model=dict)
async def upload_lead_attachment(lead_id: int, file: UploadFile = File(...), user: User = Depends(get_admin)):
    if not await LeadService.get(lead_id):
        raise HTTPException(404, "Lead not found")
    return await LeadService.upload_attachment(lead_id, file)



@router.post("/orders", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, user: User = Depends(get_admin)):
    return await OrderService.create(payload)


@router.get("/orders/{order_id}", response_model=OrderOut)
async def read_order(order_id: int, user: User = Depends(get_admin)):
    order = await OrderService.get(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order


@router.get("/orders", response_model=List[OrderOut])
@redis_cache(ttl=60)
async def list_orders(
    request: Request,
    lead_id: Optional[int] = Query(None),
    order_status: Optional[str] = Query(None, regex="^(draft|quoted|booked|delivered)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_admin),
):
    return await OrderService.list(
        lead_id=lead_id,
        status=order_status,
        limit=limit,
        offset=offset,
    )


@router.patch("/orders/{order_id}", response_model=OrderOut)
async def update_order(order_id: int, payload: OrderUpdate, user: User = Depends(get_admin)):
    order = await OrderService.get(order_id)
    if not order:
        raise HTTPException(404, "Order not found")

    updated_order = await OrderService.update(order_id, payload)

    if updated_order.status in {OrderStatus.QUOTED, OrderStatus.BOOKED}:
        webhook_payload = {
            "order_id": updated_order.id,
            "final_price": float(updated_order.final_price or 0),
        }
        asyncio.create_task(send_webhook(webhook_payload))

    return updated_order


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, user: User = Depends(get_admin)):
    if not await OrderService.get(order_id):
        raise HTTPException(404, "Order not found")
    await OrderService.delete(order_id)


@router.post("/calc", response_model=QuoteCalcResponse)
@redis_cache(ttl=60)
async def calc_quote(data: QuoteCalcRequest):
    return OrderService.calculate_price(data)


@router.post("/orders/{order_id}/reprice", response_model=RepriceResponse)
async def reprice_order(order_id: int, data: QuoteCalcRequest):
    task_id = await enqueue_reprice(order_id, data.dict())
    return RepriceResponse(task_id=task_id)