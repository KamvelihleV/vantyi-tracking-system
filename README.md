# Vantyi Funeral Parlour & Dee Marble and Granite — Client & Order Tracking System
🔗 **Live demo:** https://vantyi-tracking-app-frcucjahcxcxbxfq.southafricanorth-01.azurewebsites.net/docs
A backend system built to solve a real operational problem: **Vantyi Funeral
Parlour** (funeral services) and **Dee Marble and Granite** (tombstones)
operate as two connected businesses with no shared system to track a client
from the funeral service through to the tombstone being installed. This
causes delays and lost visibility at the handoff point between the two.

## What this project demonstrates
- **System Development**: relational database design, a full REST API
  (FastAPI + SQLAlchemy), status-tracking business logic
- **Data Analytics**: a status-change audit log (`status_log`) that captures
  every stage transition, enabling real operational metrics (e.g. average
  days from funeral to tombstone installation)
- **Cloud Computing**: designed to deploy directly to Azure App Service +
  Azure SQL Database (see `database.py` for the swap)

## Architecture
- `schema.sql` — full relational schema (also mirrored in `models.py`)
- `backend/models.py` — SQLAlchemy ORM models
- `backend/schemas.py` — Pydantic request/response validation
- `backend/main.py` — FastAPI app with CRUD endpoints + `/metrics/summary`
- `backend/seed.py` — generates realistic sample data (25 clients, linked
  services, tombstone orders at various pipeline stages, payments, and a
  full status history)

## Key design decision: the handoff link
`tombstone_orders.funeral_service_id` links a tombstone order back to the
funeral service that triggered it. This is the exact point of friction
identified in the business — previously handled informally with no shared
record. Making it a first-class foreign key means the system can report on
handoff delays directly.

## Running locally
```bash
cd backend
pip install -r requirements.txt
python seed.py          # populates sample data
uvicorn main:app --reload
```
Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## Example insight from the data
```
GET /metrics/summary
{
  "total_funeral_services": 25,
  "total_tombstone_orders": 21,
  "completed_tombstone_orders": 4,
  "average_days_funeral_to_installation": 51.8,
  "total_revenue_collected": 888708.54
}
```
This is the kind of number that turns into a business recommendation —
e.g. investigating why the average gap is over 7 weeks and whether it can
be shortened.

## Next steps (planned)
- Deployed to Azure App Service (live demo linked above)
- Build a simple frontend (React) for staff to use day-to-day
- Power BI dashboard built directly on `status_log` and `tombstone_orders`
  to visualise the pipeline and flag orders that are overdue
