from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.logistics.models import OrderStatus, VehicleType


VehicleTypeLiteral = Literal["sedan", "suv", "truck"]
OrderStatusLiteral = Literal["draft", "quoted", "booked", "delivered"]


class LeadBase(BaseModel):
    name: str = Field(..., max_length=128)
    phone: str = Field(..., max_length=15)
    email: EmailStr = Field(..., max_length=254)

    origin_zip: str = Field(..., max_length=20)
    dest_zip: str = Field(..., max_length=20)

    vehicle_type: VehicleTypeLiteral
    operable: bool = True

    model_config = ConfigDict(use_enum_values=True)


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=128)
    phone: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None

    origin_zip: Optional[str] = Field(None, max_length=20)
    dest_zip: Optional[str] = Field(None, max_length=20)

    vehicle_type: Optional[VehicleTypeLiteral] = None
    operable: Optional[bool] = None


class LeadOut(LeadBase):
    id: int
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    lead_id: int
    status: OrderStatusLiteral = OrderStatus.DRAFT
    base_price: Optional[Decimal] = Field(
        None, decimal_places=2, max_digits=12, ge=0
    )
    final_price: Optional[Decimal] = Field(
        None, decimal_places=2, max_digits=12, ge=0
    )
    notes: Optional[str] = None

    model_config = ConfigDict(use_enum_values=True)


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[OrderStatusLiteral] = None
    base_price: Optional[Decimal] = Field(
        None, decimal_places=2, max_digits=12, ge=0
    )
    final_price: Optional[Decimal] = Field(
        None, decimal_places=2, max_digits=12, ge=0
    )
    notes: Optional[str] = None


class OrderOut(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuoteCalcRequest(BaseModel):
    base_price: Decimal = Field(...)
    distance_km: float = Field(...)
    vehicle_type: Literal["sedan", "suv", "truck"]
    operable: bool
    season: Optional[str] = Field("normal")


class PriceBreakdown(BaseModel):
    base_price: Decimal
    distance_cost: Decimal
    vehicle_type_bonus: Decimal
    season_bonus: Decimal
    operable_adjustment: Decimal


class QuoteCalcResponse(BaseModel):
    price_breakdown: PriceBreakdown
    final_price: Decimal


class RepriceResponse(BaseModel):
    task_id: str
    message: str = "Repricing task queued"