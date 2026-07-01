from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Staff(Base):
    __tablename__ = "staff"

    staff_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    business_unit = Column(String(20), nullable=False)  # 'Vantyi' or 'Dee Marble'
    phone = Column(String(20))
    email = Column(String(100))


class Client(Base):
    __tablename__ = "clients"

    client_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    id_number = Column(String(20))
    date_of_birth = Column(Date)
    date_of_death = Column(Date)
    gender = Column(String(10))
    created_at = Column(DateTime, server_default=func.now())

    family_contacts = relationship("FamilyContact", back_populates="client")
    funeral_services = relationship("FuneralService", back_populates="client")
    tombstone_orders = relationship("TombstoneOrder", back_populates="client")


class FamilyContact(Base):
    __tablename__ = "family_contacts"

    contact_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    full_name = Column(String(100), nullable=False)
    relationship_to_deceased = Column("relationship", String(50))
    phone = Column(String(20))
    email = Column(String(100))
    is_primary = Column(Boolean, default=True)

    client = relationship("Client", back_populates="family_contacts")


class FuneralService(Base):
    __tablename__ = "funeral_services"

    service_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    coordinator_id = Column(Integer, ForeignKey("staff.staff_id"))
    service_type = Column(String(50))
    service_date = Column(Date)
    venue = Column(String(150))
    burial_site = Column(String(150))
    status = Column(String(30), default="Booked")
    total_cost = Column(Numeric(10, 2))
    created_at = Column(DateTime, server_default=func.now())

    client = relationship("Client", back_populates="funeral_services")
    tombstone_orders = relationship("TombstoneOrder", back_populates="funeral_service")


class TombstoneOrder(Base):
    __tablename__ = "tombstone_orders"

    order_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    funeral_service_id = Column(Integer, ForeignKey("funeral_services.service_id"), nullable=True)
    assigned_staff_id = Column(Integer, ForeignKey("staff.staff_id"))
    material = Column(String(50))
    design_details = Column(String(500))
    quote_amount = Column(Numeric(10, 2))
    order_date = Column(Date, server_default=func.now())
    expected_completion = Column(Date)
    actual_completion = Column(Date)
    installation_site = Column(String(150))
    status = Column(String(30), default="Quoted")
    created_at = Column(DateTime, server_default=func.now())

    client = relationship("Client", back_populates="tombstone_orders")
    funeral_service = relationship("FuneralService", back_populates="tombstone_orders")


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.client_id"), nullable=False)
    service_id = Column(Integer, ForeignKey("funeral_services.service_id"), nullable=True)
    order_id = Column(Integer, ForeignKey("tombstone_orders.order_id"), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, server_default=func.now())
    method = Column(String(30))
    status = Column(String(20), default="Paid")


class StatusLog(Base):
    __tablename__ = "status_log"

    log_id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(20), nullable=False)  # 'funeral_service' or 'tombstone_order'
    entity_id = Column(Integer, nullable=False)
    old_status = Column(String(30))
    new_status = Column(String(30))
    changed_by = Column(Integer, ForeignKey("staff.staff_id"))
    changed_at = Column(DateTime, server_default=func.now())
