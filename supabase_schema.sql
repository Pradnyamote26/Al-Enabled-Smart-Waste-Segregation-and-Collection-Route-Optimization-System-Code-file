-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Waste Categories Master Table
CREATE TABLE IF NOT EXISTS waste_categories (
    id SERIAL PRIMARY KEY,
    category_name TEXT UNIQUE NOT NULL,
    waste_type TEXT NOT NULL,
    recommended_bin_color TEXT NOT NULL,
    disposal_suggestion TEXT NOT NULL
);

-- 3. Waste Detections Log Table
CREATE TABLE IF NOT EXISTS waste_detections (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users (id),
    category_name TEXT NOT NULL,
    waste_type TEXT NOT NULL,
    bin_color TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    image_path TEXT NOT NULL,
    disposal_suggestion TEXT NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Waste Collection Locations / Bins Table
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    location_name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    capacity_kg REAL DEFAULT 100.0,
    current_fill_level REAL DEFAULT 0.0,
    current_weight_kg REAL DEFAULT 0.0,
    priority INTEGER DEFAULT 1,
    status TEXT DEFAULT 'Normal',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Optimized Routes Log Table
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
ALTER TABLE waste_categories DISABLE ROW LEVEL SECURITY;
ALTER TABLE waste_detections DISABLE ROW LEVEL SECURITY;
ALTER TABLE locations DISABLE ROW LEVEL SECURITY;
ALTER TABLE routes DISABLE ROW LEVEL SECURITY;

-- Seed Categories
INSERT INTO waste_categories (category_name, waste_type, recommended_bin_color, disposal_suggestion) VALUES
('Organic (Wet)', 'Wet Waste', 'Green', 'Dispose in Green Compost Bin. Ideal for kitchen scraps, food waste, and organic materials.'),
('Recyclable Plastic', 'Recyclable Waste', 'Blue', 'Rinse and place in Blue Recycling Bin. Suitable for plastic container remanufacturing.'),
('Dry Paper & Cardboard', 'Dry Waste', 'Blue', 'Flatten boxes and keep dry. Dispose in Blue Bin for paper pulp recycling.'),
('Recyclable Glass', 'Recyclable Waste', 'Blue', 'Clean glass containers and place in Blue Bin. Handle with care to prevent breakage.'),
('Recyclable Metal', 'Recyclable Waste', 'Blue', 'Rinse metal cans and place in Blue Bin for metal smelting and recycling.'),
('Non-Recyclable Trash', 'General Waste', 'Black', 'Dispose in Black General Waste Bin for landfill processing.')
ON CONFLICT (category_name) DO NOTHING;

-- Seed Locations
INSERT INTO locations (location_name, latitude, longitude, capacity_kg, current_fill_level, current_weight_kg, priority, status) VALUES
('Bin #1 - Academic Block A', 18.5204, 73.8567, 100.0, 85.0, 75.0, 4, 'Needs Collection'),
('Bin #2 - Campus Cafeteria', 18.5245, 73.8610, 150.0, 95.0, 130.0, 5, 'Overflown'),
('Bin #3 - Student Hostel Gate 1', 18.5180, 73.8520, 120.0, 70.0, 80.0, 3, 'Needs Collection'),
('Bin #4 - Library Complex', 18.5290, 73.8650, 100.0, 40.0, 35.0, 2, 'Normal'),
('Bin #5 - Sports Complex', 18.5150, 73.8590, 100.0, 90.0, 88.0, 5, 'Overflown');
