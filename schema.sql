-- ============================================================
-- Vantyi Funeral Parlour & Dee Marble and Granite
-- Client, Service & Order Tracking System
-- Database Schema (SQL Server / Azure SQL syntax)
-- ============================================================

-- Staff across BOTH businesses (shared table shows the two
-- businesses operating as one connected entity)
CREATE TABLE staff (
    staff_id        INT IDENTITY(1,1) PRIMARY KEY,
    full_name       NVARCHAR(100) NOT NULL,
    role            NVARCHAR(50)  NOT NULL,       -- e.g. 'Funeral Coordinator', 'Stonemason', 'Admin'
    business_unit   NVARCHAR(20)  NOT NULL,       -- 'Vantyi' or 'Dee Marble'
    phone           NVARCHAR(20),
    email           NVARCHAR(100)
);

-- The deceased / core client record
CREATE TABLE clients (
    client_id       INT IDENTITY(1,1) PRIMARY KEY,
    full_name       NVARCHAR(100) NOT NULL,
    id_number       NVARCHAR(20),
    date_of_birth   DATE,
    date_of_death   DATE,
    gender          NVARCHAR(10),
    created_at      DATETIME DEFAULT GETDATE()
);

-- Next of kin / family contact handling the arrangements
CREATE TABLE family_contacts (
    contact_id      INT IDENTITY(1,1) PRIMARY KEY,
    client_id       INT NOT NULL FOREIGN KEY REFERENCES clients(client_id),
    full_name       NVARCHAR(100) NOT NULL,
    relationship    NVARCHAR(50),                 -- e.g. 'Son', 'Wife'
    phone           NVARCHAR(20),
    email           NVARCHAR(100),
    is_primary      BIT DEFAULT 1
);

-- Funeral service booking (Vantyi side)
CREATE TABLE funeral_services (
    service_id          INT IDENTITY(1,1) PRIMARY KEY,
    client_id           INT NOT NULL FOREIGN KEY REFERENCES clients(client_id),
    coordinator_id       INT FOREIGN KEY REFERENCES staff(staff_id),
    service_type        NVARCHAR(50),              -- e.g. 'Full Service', 'Cremation'
    service_date         DATE,
    venue                NVARCHAR(150),
    burial_site          NVARCHAR(150),
    status               NVARCHAR(30) DEFAULT 'Booked',  -- Booked, Completed, Cancelled
    total_cost           DECIMAL(10,2),
    created_at           DATETIME DEFAULT GETDATE()
);

-- Tombstone order (Dee Marble side) — linked back to the
-- funeral_service where relevant, which is the key HANDOFF POINT
-- between the two businesses
CREATE TABLE tombstone_orders (
    order_id             INT IDENTITY(1,1) PRIMARY KEY,
    client_id            INT NOT NULL FOREIGN KEY REFERENCES clients(client_id),
    funeral_service_id   INT NULL FOREIGN KEY REFERENCES funeral_services(service_id),
    assigned_staff_id    INT FOREIGN KEY REFERENCES staff(staff_id),
    material             NVARCHAR(50),              -- e.g. 'Granite', 'Marble'
    design_details        NVARCHAR(500),
    quote_amount          DECIMAL(10,2),
    order_date            DATE DEFAULT GETDATE(),
    expected_completion   DATE,
    actual_completion     DATE,
    installation_site      NVARCHAR(150),
    status                NVARCHAR(30) DEFAULT 'Quoted',
    -- Quoted -> Approved -> In Production -> Ready -> Installed
    created_at             DATETIME DEFAULT GETDATE()
);

-- Payments — can apply to either a funeral service or a tombstone order
CREATE TABLE payments (
    payment_id       INT IDENTITY(1,1) PRIMARY KEY,
    client_id        INT NOT NULL FOREIGN KEY REFERENCES clients(client_id),
    service_id       INT NULL FOREIGN KEY REFERENCES funeral_services(service_id),
    order_id         INT NULL FOREIGN KEY REFERENCES tombstone_orders(order_id),
    amount           DECIMAL(10,2) NOT NULL,
    payment_date     DATE DEFAULT GETDATE(),
    method           NVARCHAR(30),      -- Cash, EFT, Card
    status           NVARCHAR(20) DEFAULT 'Paid'  -- Paid, Pending, Partial
);

-- Status change log — THIS is what powers the future dashboard.
-- Every time an order or service status changes, we log it here,
-- so we can later calculate real metrics like:
-- "average days from funeral completion to tombstone installation"
CREATE TABLE status_log (
    log_id           INT IDENTITY(1,1) PRIMARY KEY,
    entity_type      NVARCHAR(20) NOT NULL,   -- 'funeral_service' or 'tombstone_order'
    entity_id        INT NOT NULL,
    old_status        NVARCHAR(30),
    new_status        NVARCHAR(30),
    changed_by        INT FOREIGN KEY REFERENCES staff(staff_id),
    changed_at        DATETIME DEFAULT GETDATE()
);
