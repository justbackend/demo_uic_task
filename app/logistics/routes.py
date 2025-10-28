# app/logistics/routes.py
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from app.logistics.services import LeadService, OrderService
from app.logistics.schemas import (
    LeadCreate, LeadOut, LeadUpdate,
    OrderCreate, OrderOut, OrderUpdate,
)
from app.user.models import User
from app.auth import current_user as get_current_user

router = APIRouter(prefix="/logistics", tags=["logistics"])


@router.post("/leads", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: LeadCreate,
    user: User = Depends(get_current_user),
):
    print(user)
    return await LeadService.create(payload, user_id=user.id)


@router.get("/leads/{lead_id}", response_model=LeadOut)
async def read_lead(lead_id: int):
    lead = await LeadService.get(lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")
    return lead


@router.get("/leads", response_model=List[LeadOut])
async def list_leads(
    user: User = Depends(get_current_user),
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
async def update_lead(lead_id: int, payload: LeadUpdate):
    if not await LeadService.get(lead_id):
        raise HTTPException(404, "Lead not found")
    return await LeadService.update(lead_id, payload)


@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: int):
    if not await LeadService.get(lead_id):
        raise HTTPException(404, "Lead not found")
    await LeadService.delete(lead_id)


@router.post("/orders", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate):
    return await OrderService.create(payload)


@router.get("/orders/{order_id}", response_model=OrderOut)
async def read_order(order_id: int):
    order = await OrderService.get(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order


@router.get("/orders", response_model=List[OrderOut])
async def list_orders(
    lead_id: Optional[int] = Query(None),
    order_status: Optional[str] = Query(None, regex="^(draft|quoted|booked|delivered)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List orders with optional filters & pagination.
    """
    return await OrderService.list(
        lead_id=lead_id,
        status=order_status,
        limit=limit,
        offset=offset,
    )


@router.patch("/orders/{order_id}", response_model=OrderOut)
async def update_order(order_id: int, payload: OrderUpdate):
    if not await OrderService.get(order_id):
        raise HTTPException(404, "Order not found")
    return await OrderService.update(order_id, payload)


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int):
    if not await OrderService.get(order_id):
        raise HTTPException(404, "Order not found")
    await OrderService.delete(order_id)