from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


# ---------- Staff ----------
class StaffBase(BaseModel):
    full_name: str
    role: str
    business_unit: str
    phone: Optional[str] = None
    email: Optional[str] = None


class StaffCreate(StaffBase):
    pass


class StaffOut(StaffBase):
    model_config = ConfigDict(from_attributes=True)
    staff_id: int


# ---------- Client ----------
class ClientBase(BaseModel):
    full_name: str
    id_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None
    gender: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientOut(ClientBase):
    model_config = ConfigDict(from_attributes=True)
    client_id: int
    created_at: Optional[datetime] = None


# ---------- Family Contact ----------
class FamilyContactBase(BaseModel):
    client_id: int
    full_name: str
    relationship_to_deceased: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_primary: bool = True


class FamilyContactCreate(FamilyContactBase):
    pass


class FamilyContactOut(FamilyContactBase):
    model_config = ConfigDict(from_attributes=True)
    contact_id: int


# ---------- Funeral Service ----------
class FuneralServiceBase(BaseModel):
    client_id: int
    coordinator_id: Optional[int] = None
    service_type: Optional[str] = None
    service_date: Optional[date] = None
    venue: Optional[str] = None
    burial_site: Optional[str] = None
    status: str = "Booked"
    total_cost: Optional[Decimal] = None


class FuneralServiceCreate(FuneralServiceBase):
    pass


class FuneralServiceUpdate(BaseModel):
    status: Optional[str] = None
    service_date: Optional[date] = None
    venue: Optional[str] = None
    total_cost: Optional[Decimal] = None
    changed_by: Optional[int] = None  # staff_id making the change, for status_log


class FuneralServiceOut(FuneralServiceBase):
    model_config = ConfigDict(from_attributes=True)
    service_id: int
    created_at: Optional[datetime] = None


# ---------- Tombstone Order ----------
class TombstoneOrderBase(BaseModel):
    client_id: int
    funeral_service_id: Optional[int] = None
    assigned_staff_id: Optional[int] = None
    material: Optional[str] = None
    design_details: Optional[str] = None
    quote_amount: Optional[Decimal] = None
    expected_completion: Optional[date] = None
    actual_completion: Optional[date] = None
    installation_site: Optional[str] = None
    status: str = "Quoted"


class TombstoneOrderCreate(TombstoneOrderBase):
    pass


class TombstoneOrderUpdate(BaseModel):
    status: Optional[str] = None
    actual_completion: Optional[date] = None
    changed_by: Optional[int] = None  # staff_id making the change, for status_log


class TombstoneOrderOut(TombstoneOrderBase):
    model_config = ConfigDict(from_attributes=True)
    order_id: int
    order_date: Optional[date] = None
    created_at: Optional[datetime] = None


# ---------- Payment ----------
class PaymentBase(BaseModel):
    client_id: int
    service_id: Optional[int] = None
    order_id: Optional[int] = None
    amount: Decimal
    method: Optional[str] = None
    status: str = "Paid"


class PaymentCreate(PaymentBase):
    pass


class PaymentOut(PaymentBase):
    model_config = ConfigDict(from_attributes=True)
    payment_id: int
    payment_date: Optional[date] = None


# ---------- Status Log ----------
class StatusLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    log_id: int
    entity_type: str
    entity_id: int
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    changed_by: Optional[int] = None
    changed_at: Optional[datetime] = None
