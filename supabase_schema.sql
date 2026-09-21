-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'CITIZEN', -- SUPER_ADMIN, DUMPYARD_ADMIN, DRIVER, CITIZEN
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Dumpyards Table
CREATE TABLE IF NOT EXISTS dumpyards (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    contact TEXT,
    admin_id INTEGER REFERENCES users (id),
    status TEXT DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Vehicles Table
CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    registration_number TEXT UNIQUE NOT NULL,
    vehicle_type TEXT NOT NULL,
    capacity_kg REAL NOT NULL,
    dumpyard_id INTEGER REFERENCES dumpyards (id),
    status TEXT DEFAULT 'AVAILABLE',
    current_latitude REAL,
    current_longitude REAL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Drivers Table
CREATE TABLE IF NOT EXISTS drivers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    license_number TEXT NOT NULL,
    dumpyard_id INTEGER REFERENCES dumpyards (id),
    status TEXT DEFAULT 'AVAILABLE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Waste Reports Table (Citizen Complaints)
CREATE TABLE IF NOT EXISTS waste_reports (
    id SERIAL PRIMARY KEY,
    citizen_id INTEGER REFERENCES users (id),
    image_url TEXT NOT NULL,
    description TEXT,
    waste_type TEXT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    address TEXT,
    priority INTEGER DEFAULT 1,
    status TEXT DEFAULT 'SUBMITTED',
    assigned_dumpyard_id INTEGER REFERENCES dumpyards (id),
    assigned_vehicle_id INTEGER REFERENCES vehicles (id),
    assigned_driver_id INTEGER REFERENCES drivers (id),
    completion_proof_url TEXT,
    ai_verification_status TEXT,
    confidence_score REAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Collection Tasks Table
CREATE TABLE IF NOT EXISTS collection_tasks (
    id SERIAL PRIMARY KEY,
    dumpyard_id INTEGER REFERENCES dumpyards (id),
    vehicle_id INTEGER REFERENCES vehicles (id),
    driver_id INTEGER REFERENCES drivers (id),
    report_id INTEGER REFERENCES waste_reports (id),
    status TEXT DEFAULT 'PENDING',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Status History Table
CREATE TABLE IF NOT EXISTS status_history (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES waste_reports (id),
    status TEXT NOT NULL,
    remarks TEXT,
    changed_by INTEGER REFERENCES users (id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Optimized Routes Log Table
CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    route_name TEXT NOT NULL,
    depot_lat REAL NOT NULL,
    depot_lng REAL NOT NULL,
    total_distance_km REAL NOT NULL,
    estimated_time_mins REAL NOT NULL,
    fuel_used_liters REAL NOT NULL,
    visited_bins_count INTEGER NOT NULL,
    stops_json TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- DISABLE ROW LEVEL SECURITY (Allows your backend to insert data without error)
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE dumpyards DISABLE ROW LEVEL SECURITY;
ALTER TABLE vehicles DISABLE ROW LEVEL SECURITY;
ALTER TABLE drivers DISABLE ROW LEVEL SECURITY;
ALTER TABLE waste_reports DISABLE ROW LEVEL SECURITY;
ALTER TABLE collection_tasks DISABLE ROW LEVEL SECURITY;
ALTER TABLE status_history DISABLE ROW LEVEL SECURITY;
ALTER TABLE routes DISABLE ROW LEVEL SECURITY;

-- Seed Demo Data
INSERT INTO users (id, username, email, password_hash, role) VALUES
(1, 'superadmin', 'super@admin.com', 'scrypt:32768:8:1$n4tqK43sL3wT2t2w$7f9202164478ec094c97ea8a5624773de2916b7ff2308cfd7be1315582cde4b5', 'SUPER_ADMIN'),
(2, 'dumpadmin', 'dump@admin.com', 'scrypt:32768:8:1$n4tqK43sL3wT2t2w$7f9202164478ec094c97ea8a5624773de2916b7ff2308cfd7be1315582cde4b5', 'DUMPYARD_ADMIN'),
(3, 'driver1', 'driver@demo.com', 'scrypt:32768:8:1$n4tqK43sL3wT2t2w$7f9202164478ec094c97ea8a5624773de2916b7ff2308cfd7be1315582cde4b5', 'DRIVER'),
(4, 'citizen1', 'citizen@demo.com', 'scrypt:32768:8:1$n4tqK43sL3wT2t2w$7f9202164478ec094c97ea8a5624773de2916b7ff2308cfd7be1315582cde4b5', 'CITIZEN')
ON CONFLICT (id) DO NOTHING;

INSERT INTO dumpyards (id, name, address, latitude, longitude, contact, admin_id) VALUES
(1, 'Central Pune Dumpyard', 'Shivaji Nagar, Pune', 18.5204, 73.8567, '9876543210', 2)
ON CONFLICT (id) DO NOTHING;

INSERT INTO vehicles (id, registration_number, vehicle_type, capacity_kg, dumpyard_id, current_latitude, current_longitude) VALUES
(1, 'MH-12-AB-1234', 'Heavy Truck', 2000.0, 1, 18.5204, 73.8567)
ON CONFLICT (id) DO NOTHING;

INSERT INTO drivers (id, user_id, name, phone, email, license_number, dumpyard_id) VALUES
(1, 3, 'Ramesh Driver', '9876543211', 'driver@demo.com', 'DL-MH-2023-123', 1)
ON CONFLICT (id) DO NOTHING;

-- Reset sequence generator to avoid ID collision
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('dumpyards_id_seq', (SELECT MAX(id) FROM dumpyards));
SELECT setval('vehicles_id_seq', (SELECT MAX(id) FROM vehicles));
SELECT setval('drivers_id_seq', (SELECT MAX(id) FROM drivers));
