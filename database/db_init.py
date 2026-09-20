"""
Database Initialization Script with Seed Data
"""
from backend.app import app
from database.models import db, WastePoint, CollectionVehicle

def init_db():
    with app.app_context():
        db.create_all()
        
        # Seed initial waste collection points if empty
        if WastePoint.query.count() == 0:
            sample_points = [
                WastePoint(name="Bin #1 - Sector A", latitude=18.5204, longitude=73.8567, waste_category="plastic", fill_level_percent=85.0, estimated_weight_kg=120.0, priority=4),
                WastePoint(name="Bin #2 - Campus Library", latitude=18.5250, longitude=73.8600, waste_category="paper", fill_level_percent=90.0, estimated_weight_kg=150.0, priority=5),
                WastePoint(name="Bin #3 - Cafeteria Wet Waste", latitude=18.5180, longitude=73.8520, waste_category="organic_wet", fill_level_percent=95.0, estimated_weight_kg=200.0, priority=5),
                WastePoint(name="Bin #4 - Residential Gate 2", latitude=18.5300, longitude=73.8650, waste_category="glass", fill_level_percent=40.0, estimated_weight_kg=50.0, priority=2),
            ]
            db.session.bulk_save_objects(sample_points)

        # Seed collection vehicle if empty
        if CollectionVehicle.query.count() == 0:
            sample_vehicle = CollectionVehicle(vehicle_number="MH-12-AB-1234", capacity_kg=1000.0, driver_name="John Doe", status="Available")
            db.session.add(sample_vehicle)

        db.session.commit()
        print("Database initialized and seeded successfully.")

if __name__ == '__main__':
    init_db()
