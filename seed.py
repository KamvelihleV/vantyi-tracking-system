"""
Seeds the database with realistic sample data so the system
looks like a real operating business rather than an empty demo.

Run once:
    python seed.py
"""
import random
from datetime import date, timedelta

from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Clear existing data for a clean re-seed
for table in [models.StatusLog, models.Payment, models.TombstoneOrder,
              models.FuneralService, models.FamilyContact, models.Client, models.Staff]:
    db.query(table).delete()
db.commit()

# ---------- Staff ----------
staff_data = [
    ("Thandiwe Vantyi", "Funeral Coordinator", "Vantyi"),
    ("Sipho Vantyi", "Funeral Director", "Vantyi"),
    ("Nomsa Dlamini", "Admin Clerk", "Vantyi"),
    ("Bongani Dee", "Stonemason", "Dee Marble"),
    ("Zanele Dee", "Design Consultant", "Dee Marble"),
    ("Themba Ndlovu", "Installation Technician", "Dee Marble"),
]
staff_objs = []
for name, role, unit in staff_data:
    s = models.Staff(full_name=name, role=role, business_unit=unit,
                      phone=f"082{random.randint(1000000,9999999)}",
                      email=name.lower().replace(" ", ".") + "@example.com")
    db.add(s)
    staff_objs.append(s)
db.commit()

first_names = ["John", "Mary", "Peter", "Nomvula", "David", "Grace", "Samuel",
               "Precious", "Andile", "Lindiwe", "Michael", "Thabo", "Ruth", "Vusi"]
last_names = ["Mahlangu", "Khumalo", "Nkosi", "Zulu", "Mokoena", "Sithole",
              "Mbeki", "Radebe", "Molefe", "Dube"]

materials = ["Black Granite", "Grey Granite", "White Marble", "Dark Marble"]
service_types = ["Full Traditional Service", "Cremation Service", "Memorial Service"]

statuses_order = ["Quoted", "Approved", "In Production", "Ready", "Installed"]

clients_objs = []
today = date.today()

for i in range(25):
    dod = today - timedelta(days=random.randint(20, 400))
    dob = dod - timedelta(days=random.randint(20*365, 85*365))
    client = models.Client(
        full_name=f"{random.choice(first_names)} {random.choice(last_names)}",
        id_number=str(random.randint(6001010000000, 9901010000000)),
        date_of_birth=dob,
        date_of_death=dod,
        gender=random.choice(["Male", "Female"]),
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    clients_objs.append(client)

    # Family contact
    contact = models.FamilyContact(
        client_id=client.client_id,
        full_name=f"{random.choice(first_names)} {client.full_name.split()[-1]}",
        relationship_to_deceased=random.choice(["Son", "Daughter", "Spouse", "Sibling"]),
        phone=f"083{random.randint(1000000,9999999)}",
        is_primary=True,
    )
    db.add(contact)

    # Funeral service (Vantyi)
    service_date = dod + timedelta(days=random.randint(5, 14))
    coordinator = random.choice([s for s in staff_objs if s.business_unit == "Vantyi"])
    service = models.FuneralService(
        client_id=client.client_id,
        coordinator_id=coordinator.staff_id,
        service_type=random.choice(service_types),
        service_date=service_date,
        venue="Vantyi Funeral Parlour Hall",
        burial_site=f"{random.choice(['Westpark', 'Avalon', 'Heroes Acre'])} Cemetery",
        status="Completed" if service_date < today else "Booked",
        total_cost=round(random.uniform(15000, 45000), 2),
    )
    db.add(service)
    db.commit()
    db.refresh(service)

    # Not every funeral leads to an immediate tombstone order (realistic — some delay ordering)
    if random.random() < 0.8:
        order_date = service_date + timedelta(days=random.randint(3, 30))
        staff_member = random.choice([s for s in staff_objs if s.business_unit == "Dee Marble"])

        # Randomly place each order somewhere along the pipeline
        progress = random.randint(0, len(statuses_order) - 1)
        current_status = statuses_order[progress]

        expected_completion = order_date + timedelta(days=random.randint(21, 60))
        actual_completion = None
        if current_status == "Installed":
            # some installs run late, some on time
            actual_completion = expected_completion + timedelta(days=random.randint(-5, 20))

        order = models.TombstoneOrder(
            client_id=client.client_id,
            funeral_service_id=service.service_id,
            assigned_staff_id=staff_member.staff_id,
            material=random.choice(materials),
            design_details="Standard headstone with engraved name, dates and a short epitaph.",
            quote_amount=round(random.uniform(8000, 25000), 2),
            order_date=order_date,
            expected_completion=expected_completion,
            actual_completion=actual_completion,
            installation_site=service.burial_site,
            status=current_status,
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        # Log the status progression realistically
        prev = None
        log_date = order_date
        for st in statuses_order[: progress + 1]:
            log = models.StatusLog(
                entity_type="tombstone_order",
                entity_id=order.order_id,
                old_status=prev,
                new_status=st,
                changed_by=staff_member.staff_id,
                changed_at=log_date,
            )
            db.add(log)
            prev = st
            log_date += timedelta(days=random.randint(3, 12))

        # Payment for the order
        if current_status in ("In Production", "Ready", "Installed"):
            payment = models.Payment(
                client_id=client.client_id,
                order_id=order.order_id,
                amount=order.quote_amount,
                payment_date=order_date + timedelta(days=random.randint(1, 5)),
                method=random.choice(["EFT", "Cash", "Card"]),
                status="Paid",
            )
            db.add(payment)

    # Payment for the funeral service itself
    if service.status == "Completed":
        payment = models.Payment(
            client_id=client.client_id,
            service_id=service.service_id,
            amount=service.total_cost,
            payment_date=service_date + timedelta(days=random.randint(1, 10)),
            method=random.choice(["EFT", "Cash", "Card"]),
            status="Paid",
        )
        db.add(payment)

db.commit()
db.close()

print("Seed complete: 25 clients with linked services, orders, payments and status history.")
