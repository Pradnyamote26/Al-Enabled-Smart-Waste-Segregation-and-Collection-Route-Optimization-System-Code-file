"""
Database Models Module (User, WasteCategory, WasteDetection, Location, Route)
"""
import json
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db

class User:
    def __init__(self, id, username, email, password_hash, role='user', created_at=None):
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
    def create(cls, username, email, password, role='user'):
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
    def get_all(cls):
        supabase = get_db()
        response = supabase.table("users").select("*").order("id").execute()
        return [cls(**row) for row in response.data]

    @classmethod
    def get_by_username(cls, username):
        supabase = get_db()
        response = supabase.table("users").select("*").eq("username", username).execute()
        if response.data:
            return cls(**response.data[0])
        return None

    @classmethod
    def get_by_email(cls, email):
        supabase = get_db()
        response = supabase.table("users").select("*").eq("email", email).execute()
        if response.data:
            return cls(**response.data[0])
        return None

    @classmethod
    def get_by_id(cls, user_id):
        supabase = get_db()
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        if response.data:
            return cls(**response.data[0])
        return None

    @classmethod
    def delete(cls, user_id):
        supabase = get_db()
        supabase.table("users").delete().eq("id", user_id).execute()
        return True


class WasteCategory:
    def __init__(self, id, category_name, waste_type, recommended_bin_color, disposal_suggestion):
        self.id = id
        self.category_name = category_name
        self.waste_type = waste_type
        self.recommended_bin_color = recommended_bin_color
        self.disposal_suggestion = disposal_suggestion

    def to_dict(self):
        return {
            'id': self.id,
            'category_name': self.category_name,
            'waste_type': self.waste_type,
            'recommended_bin_color': self.recommended_bin_color,
            'disposal_suggestion': self.disposal_suggestion
        }

    @classmethod
    def get_all(cls):
        supabase = get_db()
        response = supabase.table("waste_categories").select("*").order("id").execute()
        return [cls(**row) for row in response.data]

    @classmethod
    def create(cls, category_name, waste_type, recommended_bin_color, disposal_suggestion):
        supabase = get_db()
        data = {
            "category_name": category_name,
            "waste_type": waste_type,
            "recommended_bin_color": recommended_bin_color,
            "disposal_suggestion": disposal_suggestion
        }
        response = supabase.table("waste_categories").insert(data).execute()
        if not response.data:
            return None
        return cls(**response.data[0])

    @classmethod
    def delete(cls, category_id):
        supabase = get_db()
        supabase.table("waste_categories").delete().eq("id", category_id).execute()
        return True


class WasteDetection:
    def __init__(self, id, user_id, category_name, waste_type, bin_color, confidence_score, image_path, disposal_suggestion, detected_at):
        self.id = id
        self.user_id = user_id
        self.category_name = category_name
        self.waste_type = waste_type
        self.bin_color = bin_color
        self.confidence_score = confidence_score
        self.image_path = image_path
        self.disposal_suggestion = disposal_suggestion
        self.detected_at = detected_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_name': self.category_name,
            'waste_type': self.waste_type,
            'bin_color': self.bin_color,
            'confidence_score': self.confidence_score,
            'image_path': self.image_path,
            'disposal_suggestion': self.disposal_suggestion,
            'detected_at': str(self.detected_at) if self.detected_at else None
        }

    @classmethod
    def create(cls, category_name, waste_type, bin_color, confidence_score, image_path, disposal_suggestion, user_id=None):
        supabase = get_db()
        data = {
            "user_id": user_id,
            "category_name": category_name,
            "waste_type": waste_type,
            "bin_color": bin_color,
            "confidence_score": confidence_score,
            "image_path": image_path,
            "disposal_suggestion": disposal_suggestion
        }
        response = supabase.table("waste_detections").insert(data).execute()
        if not response.data:
            return None
        return cls(**response.data[0])

    @classmethod
    def get_all(cls):
        supabase = get_db()
        response = supabase.table("waste_detections").select("*").order("id", desc=True).execute()
        return [cls(**row) for row in response.data]

    @classmethod
    def get_recent(cls, limit=15):
        supabase = get_db()
        # Note: supabase-py limit() syntax is .limit(limit)
        response = supabase.table("waste_detections").select("*").order("id", desc=True).limit(limit).execute()
        return [cls(**row) for row in response.data]

    @classmethod
    def delete(cls, detection_id):
        supabase = get_db()
        supabase.table("waste_detections").delete().eq("id", detection_id).execute()
        return True


class Location:
    def __init__(self, id, location_name, latitude, longitude, capacity_kg=100.0, current_fill_level=0.0, current_weight_kg=0.0, priority=1, status='Normal', created_at=None):
        self.id = id
        self.location_name = location_name
        self.latitude = latitude
        self.longitude = longitude
        self.capacity_kg = capacity_kg
        self.current_fill_level = current_fill_level
        self.current_weight_kg = current_weight_kg
        self.priority = priority
        self.status = status
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'location_name': self.location_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'capacity_kg': self.capacity_kg,
            'current_fill_level': self.current_fill_level,
            'current_weight_kg': self.current_weight_kg,
            'priority': self.priority,
            'status': self.status,
            'created_at': str(self.created_at) if self.created_at else None
        }

    @classmethod
    def create(cls, location_name, latitude, longitude, capacity_kg=100.0, current_fill_level=0.0, current_weight_kg=0.0, priority=1):
        supabase = get_db()
        status = 'Overflown' if current_fill_level >= 90.0 else ('Needs Collection' if current_fill_level >= 60.0 else 'Normal')
        data = {
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "capacity_kg": capacity_kg,
            "current_fill_level": current_fill_level,
            "current_weight_kg": current_weight_kg,
            "priority": priority,
            "status": status
        }
        response = supabase.table("locations").insert(data).execute()
        if not response.data:
            return None
        return cls(**response.data[0])

    @classmethod
    def get_all(cls):
        supabase = get_db()
        response = supabase.table("locations").select("*").order("id").execute()
        return [cls(**row) for row in response.data]

    @classmethod
    def delete(cls, location_id):
        supabase = get_db()
        supabase.table("locations").delete().eq("id", location_id).execute()
        return True


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
        if not response.data:
            return None
        return cls(**response.data[0])

    @classmethod
    def get_all(cls):
        supabase = get_db()
        response = supabase.table("routes").select("*").order("id", desc=True).execute()
        return [cls(**row) for row in response.data]

    @classmethod
    def get_recent(cls, limit=5):
        supabase = get_db()
        response = supabase.table("routes").select("*").order("id", desc=True).limit(limit).execute()
        return [cls(**row) for row in response.data]

    @classmethod
    def delete(cls, route_id):
        supabase = get_db()
        supabase.table("routes").delete().eq("id", route_id).execute()
        return True
