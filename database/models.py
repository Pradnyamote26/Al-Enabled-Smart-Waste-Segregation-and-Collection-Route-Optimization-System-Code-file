import json
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db

class User:
    def __init__(self, id, username, email, password_hash, role='CITIZEN', created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': str(self.created_at) if self.created_at else None
        }

    @classmethod
    def create(cls, username, email, password, role='CITIZEN'):
        supabase = get_db()
        hashed_password = cls.hash_password(password)
        data = {
            "username": username,
            "email": email,
            "password_hash": hashed_password,
            "role": role
        }
        response = supabase.table("users").insert(data).execute()
        if not response.data:
            return None
        row = response.data[0]
        return cls(**row)

    @classmethod
    def get_by_username(cls, username):
        supabase = get_db()
        response = supabase.table("users").select("*").eq("username", username).execute()
        if response.data:
            return cls(**response.data[0])
        return None


class Dumpyard:
    def __init__(self, id, name, address, latitude, longitude, contact, admin_id, status='ACTIVE', created_at=None):
        self.id = id
        self.name = name
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.contact = contact
        self.admin_id = admin_id
        self.status = status
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'contact': self.contact,
            'admin_id': self.admin_id,
            'status': self.status,
            'created_at': str(self.created_at) if self.created_at else None
        }

    @classmethod
    def get_all(cls):
        supabase = get_db()
        response = supabase.table("dumpyards").select("*").order("id").execute()
        return [cls(**row) for row in response.data]

    @classmethod
    def get_by_id(cls, id):
        supabase = get_db()
        response = supabase.table("dumpyards").select("*").eq("id", id).execute()
        return cls(**response.data[0]) if response.data else None


class Vehicle:
    def __init__(self, id, registration_number, vehicle_type, capacity_kg, dumpyard_id, status='AVAILABLE', current_latitude=None, current_longitude=None, last_updated=None):
        self.id = id
        self.registration_number = registration_number
        self.vehicle_type = vehicle_type
        self.capacity_kg = capacity_kg
        self.dumpyard_id = dumpyard_id
        self.status = status
        self.current_latitude = current_latitude
        self.current_longitude = current_longitude
        self.last_updated = last_updated

    def to_dict(self):
        return {
            'id': self.id,
            'registration_number': self.registration_number,
            'vehicle_type': self.vehicle_type,
            'capacity_kg': self.capacity_kg,
            'dumpyard_id': self.dumpyard_id,
            'status': self.status,
            'current_latitude': self.current_latitude,
            'current_longitude': self.current_longitude,
            'last_updated': str(self.last_updated) if self.last_updated else None
        }

    @classmethod
    def get_all(cls):
        supabase = get_db()
        response = supabase.table("vehicles").select("*").order("id").execute()
        return [cls(**row) for row in response.data]

    @classmethod
    def get_by_dumpyard(cls, dumpyard_id):
        supabase = get_db()
        response = supabase.table("vehicles").select("*").eq("dumpyard_id", dumpyard_id).execute()
        return [cls(**row) for row in response.data]


class Driver:
    def __init__(self, id, user_id, name, phone, email, license_number, dumpyard_id, status='AVAILABLE', created_at=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.email = email
        self.license_number = license_number
        self.dumpyard_id = dumpyard_id
        self.status = status
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'license_number': self.license_number,
            'dumpyard_id': self.dumpyard_id,
            'status': self.status,
            'created_at': str(self.created_at) if self.created_at else None
        }

    @classmethod
    def get_by_user_id(cls, user_id):
        supabase = get_db()
        response = supabase.table("drivers").select("*").eq("user_id", user_id).execute()
        return cls(**response.data[0]) if response.data else None


class WasteReport:
    def __init__(self, id, citizen_id, image_url, description, waste_type, latitude, longitude, address, priority=1, status='SUBMITTED', assigned_dumpyard_id=None, assigned_vehicle_id=None, assigned_driver_id=None, completion_proof_url=None, ai_verification_status=None, confidence_score=None, created_at=None):
        self.id = id
        self.citizen_id = citizen_id
        self.image_url = image_url
        self.description = description
        self.waste_type = waste_type
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.priority = priority
        self.status = status
        self.assigned_dumpyard_id = assigned_dumpyard_id
        self.assigned_vehicle_id = assigned_vehicle_id
        self.assigned_driver_id = assigned_driver_id
        self.completion_proof_url = completion_proof_url
        self.ai_verification_status = ai_verification_status
        self.confidence_score = confidence_score
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'citizen_id': self.citizen_id,
            'image_url': self.image_url,
            'description': self.description,
            'waste_type': self.waste_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'priority': self.priority,
            'status': self.status,
            'assigned_dumpyard_id': self.assigned_dumpyard_id,
            'assigned_vehicle_id': self.assigned_vehicle_id,
            'assigned_driver_id': self.assigned_driver_id,
            'completion_proof_url': self.completion_proof_url,
            'ai_verification_status': self.ai_verification_status,
            'confidence_score': self.confidence_score,
            'created_at': str(self.created_at) if self.created_at else None
        }

    @classmethod
    def create(cls, citizen_id, image_url, description, waste_type, latitude, longitude, address):
        supabase = get_db()
        data = {
            "citizen_id": citizen_id,
            "image_url": image_url,
            "description": description,
            "waste_type": waste_type,
            "latitude": latitude,
            "longitude": longitude,
            "address": address
        }
        response = supabase.table("waste_reports").insert(data).execute()
        return cls(**response.data[0]) if response.data else None

    @classmethod
    def get_all(cls):
        supabase = get_db()
        response = supabase.table("waste_reports").select("*").order("id", desc=True).execute()
        return [cls(**row) for row in response.data]

    @classmethod
    def update_status(cls, report_id, status, dumpyard_id=None, vehicle_id=None, driver_id=None, completion_proof_url=None, ai_verification_status=None):
        supabase = get_db()
        data = {"status": status}
        if dumpyard_id is not None: data["assigned_dumpyard_id"] = dumpyard_id
        if vehicle_id is not None: data["assigned_vehicle_id"] = vehicle_id
        if driver_id is not None: data["assigned_driver_id"] = driver_id
        if completion_proof_url is not None: data["completion_proof_url"] = completion_proof_url
        if ai_verification_status is not None: data["ai_verification_status"] = ai_verification_status
        response = supabase.table("waste_reports").update(data).eq("id", report_id).execute()
        return cls(**response.data[0]) if response.data else None


class CollectionTask:
    def __init__(self, id, dumpyard_id, vehicle_id, driver_id, report_id, status='PENDING', created_at=None):
        self.id = id
        self.dumpyard_id = dumpyard_id
        self.vehicle_id = vehicle_id
        self.driver_id = driver_id
        self.report_id = report_id
        self.status = status
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'dumpyard_id': self.dumpyard_id,
            'vehicle_id': self.vehicle_id,
            'driver_id': self.driver_id,
            'report_id': self.report_id,
            'status': self.status,
            'created_at': str(self.created_at) if self.created_at else None
        }

    @classmethod
    def create(cls, dumpyard_id, vehicle_id, driver_id, report_id):
        supabase = get_db()
        data = {
            "dumpyard_id": dumpyard_id,
            "vehicle_id": vehicle_id,
            "driver_id": driver_id,
            "report_id": report_id
        }
        response = supabase.table("collection_tasks").insert(data).execute()
        return cls(**response.data[0]) if response.data else None


class StatusHistory:
    def __init__(self, id, report_id, status, remarks, changed_by, created_at=None):
        self.id = id
        self.report_id = report_id
        self.status = status
        self.remarks = remarks
        self.changed_by = changed_by
        self.created_at = created_at

    @classmethod
    def create(cls, report_id, status, remarks=None, changed_by=None):
        supabase = get_db()
        data = {
            "report_id": report_id,
            "status": status,
            "remarks": remarks,
            "changed_by": changed_by
        }
        response = supabase.table("status_history").insert(data).execute()
        return cls(**response.data[0]) if response.data else None


class Route:
    def __init__(self, id, route_name, depot_lat, depot_lng, total_distance_km, estimated_time_mins, fuel_used_liters, visited_bins_count, stops_json, created_at=None):
        self.id = id
        self.route_name = route_name
        self.depot_lat = depot_lat
        self.depot_lng = depot_lng
        self.total_distance_km = total_distance_km
        self.estimated_time_mins = estimated_time_mins
        self.fuel_used_liters = fuel_used_liters
        self.visited_bins_count = visited_bins_count
        self.stops_json = stops_json
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'route_name': self.route_name,
            'depot_lat': self.depot_lat,
            'depot_lng': self.depot_lng,
            'total_distance_km': self.total_distance_km,
            'estimated_time_mins': self.estimated_time_mins,
            'fuel_used_liters': self.fuel_used_liters,
            'visited_bins_count': self.visited_bins_count,
            'stops': json.loads(self.stops_json) if isinstance(self.stops_json, str) else self.stops_json,
            'created_at': str(self.created_at) if self.created_at else None
        }

    @classmethod
    def create(cls, route_name, depot_lat, depot_lng, total_distance_km, estimated_time_mins, fuel_used_liters, visited_bins_count, stops_list):
        supabase = get_db()
        stops_str = json.dumps(stops_list)
        data = {
            "route_name": route_name,
            "depot_lat": depot_lat,
            "depot_lng": depot_lng,
            "total_distance_km": total_distance_km,
            "estimated_time_mins": estimated_time_mins,
            "fuel_used_liters": fuel_used_liters,
            "visited_bins_count": visited_bins_count,
            "stops_json": stops_str
        }
        response = supabase.table("routes").insert(data).execute()
        return cls(**response.data[0]) if response.data else None

    @classmethod
    def get_recent(cls, limit=5):
        supabase = get_db()
        response = supabase.table("routes").select("*").order("id", desc=True).limit(limit).execute()
        return [cls(**row) for row in response.data]
