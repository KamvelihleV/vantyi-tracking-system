"""
Vantyi Funeral Parlour & Dee Marble and Granite
Client, Service & Order Tracking API

Run locally:
    uvicorn main:app --reload

Docs available at http://127.0.0.1:8000/docs
"""
from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vantyi / Dee Marble Tracking System",
    description="Client, funeral service and tombstone order tracking across two related businesses.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def log_status_change(db: Session, entity_type: str, entity_id: int,
                       old_status: Optional[str], new_status: Optional[str],
                       changed_by: Optional[int]):
    if old_status == new_status:
        return
    entry = models.StatusLog(
        entity_type=entity_type,
        entity_id=entity_id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
    )
    db.add(entry)


# ============================================================
# Staff
# ============================================================
@app.post("/staff", response_model=schemas.StaffOut)
def create_staff(staff: schemas.StaffCreate, db: Session = Depends(get_db)):
    obj = models.Staff(**staff.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/staff", response_model=List[schemas.StaffOut])
def list_staff(business_unit: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.Staff)
    if business_unit:
        q = q.filter(models.Staff.business_unit == business_unit)
    return q.all()


# ============================================================
# Clients
# ============================================================
@app.post("/clients", response_model=schemas.ClientOut)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    obj = models.Client(**client.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/clients", response_model=List[schemas.ClientOut])
def list_clients(db: Session = Depends(get_db)):
    return db.query(models.Client).all()


@app.get("/clients/{client_id}", response_model=schemas.ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Client).filter(models.Client.client_id == client_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Client not found")
    return obj


# ============================================================
# Family Contacts
# ============================================================
@app.post("/family-contacts", response_model=schemas.FamilyContactOut)
def create_family_contact(contact: schemas.FamilyContactCreate, db: Session = Depends(get_db)):
    obj = models.FamilyContact(**contact.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/clients/{client_id}/family-contacts", response_model=List[schemas.FamilyContactOut])
def list_family_contacts(client_id: int, db: Session = Depends(get_db)):
    return db.query(models.FamilyContact).filter(models.FamilyContact.client_id == client_id).all()


# ============================================================
# Funeral Services
# ============================================================
@app.post("/funeral-services", response_model=schemas.FuneralServiceOut)
def create_funeral_service(service: schemas.FuneralServiceCreate, db: Session = Depends(get_db)):
    obj = models.FuneralService(**service.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    log_status_change(db, "funeral_service", obj.service_id, None, obj.status, service.coordinator_id)
    db.commit()
    return obj


@app.get("/funeral-services", response_model=List[schemas.FuneralServiceOut])
def list_funeral_services(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.FuneralService)
    if status:
        q = q.filter(models.FuneralService.status == status)
    return q.all()


@app.patch("/funeral-services/{service_id}", response_model=schemas.FuneralServiceOut)
def update_funeral_service(service_id: int, update: schemas.FuneralServiceUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.FuneralService).filter(models.FuneralService.service_id == service_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Funeral service not found")

    old_status = obj.status
    data = update.model_dump(exclude_unset=True, exclude={"changed_by"})
    for key, value in data.items():
        setattr(obj, key, value)

    if update.status and update.status != old_status:
        log_status_change(db, "funeral_service", service_id, old_status, update.status, update.changed_by)

    db.commit()
    db.refresh(obj)
    return obj


# ============================================================
# Tombstone Orders
# ============================================================
@app.post("/tombstone-orders", response_model=schemas.TombstoneOrderOut)
def create_tombstone_order(order: schemas.TombstoneOrderCreate, db: Session = Depends(get_db)):
    obj = models.TombstoneOrder(**order.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    log_status_change(db, "tombstone_order", obj.order_id, None, obj.status, order.assigned_staff_id)
    db.commit()
    return obj


@app.get("/tombstone-orders", response_model=List[schemas.TombstoneOrderOut])
def list_tombstone_orders(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.TombstoneOrder)
    if status:
        q = q.filter(models.TombstoneOrder.status == status)
    return q.all()


@app.patch("/tombstone-orders/{order_id}", response_model=schemas.TombstoneOrderOut)
def update_tombstone_order(order_id: int, update: schemas.TombstoneOrderUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.TombstoneOrder).filter(models.TombstoneOrder.order_id == order_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Tombstone order not found")

    old_status = obj.status
    data = update.model_dump(exclude_unset=True, exclude={"changed_by"})
    for key, value in data.items():
        setattr(obj, key, value)

    if update.status and update.status != old_status:
        log_status_change(db, "tombstone_order", order_id, old_status, update.status, update.changed_by)

    db.commit()
    db.refresh(obj)
    return obj


# ============================================================
# Payments
# ============================================================
@app.post("/payments", response_model=schemas.PaymentOut)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    obj = models.Payment(**payment.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@app.get("/payments", response_model=List[schemas.PaymentOut])
def list_payments(db: Session = Depends(get_db)):
    return db.query(models.Payment).all()


# ============================================================
# Status Log (audit trail)
# ============================================================
@app.get("/status-log", response_model=List[schemas.StatusLogOut])
def list_status_log(entity_type: Optional[str] = None, entity_id: Optional[int] = None,
                     db: Session = Depends(get_db)):
    q = db.query(models.StatusLog)
    if entity_type:
        q = q.filter(models.StatusLog.entity_type == entity_type)
    if entity_id:
        q = q.filter(models.StatusLog.entity_id == entity_id)
    return q.order_by(models.StatusLog.changed_at).all()


# ============================================================
# Metrics — feeds directly into the future Power BI dashboard
# ============================================================
@app.get("/metrics/summary")
def metrics_summary(db: Session = Depends(get_db)):
    total_services = db.query(models.FuneralService).count()
    total_orders = db.query(models.TombstoneOrder).count()
    completed_orders = db.query(models.TombstoneOrder).filter(
        models.TombstoneOrder.status == "Installed"
    ).all()

    # Average days from funeral service date to tombstone installation
    gaps = []
    for order in completed_orders:
        if order.funeral_service and order.funeral_service.service_date and order.actual_completion:
            delta = (order.actual_completion - order.funeral_service.service_date).days
            gaps.append(delta)

    avg_handoff_days = round(sum(gaps) / len(gaps), 1) if gaps else None

    revenue = db.query(models.Payment).filter(models.Payment.status == "Paid").all()
    total_revenue = float(sum(p.amount for p in revenue)) if revenue else 0.0

    return {
        "total_funeral_services": total_services,
        "total_tombstone_orders": total_orders,
        "completed_tombstone_orders": len(completed_orders),
        "average_days_funeral_to_installation": avg_handoff_days,
        "total_revenue_collected": total_revenue,
    }


@app.get("/")
def root():
    return {"message": "Vantyi / Dee Marble Tracking API. Visit /docs for interactive API documentation."}
