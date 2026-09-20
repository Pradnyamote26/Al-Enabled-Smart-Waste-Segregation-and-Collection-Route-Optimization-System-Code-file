"""
Route Optimization Engine using Nearest Neighbor Algorithm & Haversine Distance
"""
import math

class RouteOptimizer:
    def __init__(self, vehicle_capacity_kg=1000.0, avg_speed_kmh=30.0, fuel_consumption_per_km=0.15):
        self.vehicle_capacity_kg = vehicle_capacity_kg
        self.avg_speed_kmh = avg_speed_kmh  # Average urban collection truck speed in km/h
        self.fuel_consumption_per_km = fuel_consumption_per_km  # Average fuel usage in Liters/km

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculates Great-Circle distance between two (lat, lon) coordinates in kilometers
        using the Haversine formula.
        """
        R = 6371.0  # Radius of Earth in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def optimize(self, depot_location, collection_points):
        """
        Calculates an efficient collection route using Nearest Neighbor heuristic
        weighted by fill level priority and vehicle payload capacity constraints.
        
        depot_location: dict with 'lat', 'lng', 'name'
        collection_points: list of dicts with 'id', 'location_name', 'latitude', 'longitude', 'current_fill_level', 'current_weight_kg', 'priority'
        """
        if not collection_points:
            return {
                'total_distance_km': 0.0,
                'estimated_time_mins': 0.0,
                'fuel_used_liters': 0.0,
                'visited_bins_count': 0,
                'stops': []
            }

        # Filter and sort bins: priority to bins requiring collection (fill level >= 50% or high priority)
        urgent_points = [p for p in collection_points if p.get('current_fill_level', 0) >= 50.0 or p.get('priority', 1) >= 4]
        other_points = [p for p in collection_points if p not in urgent_points]

        # Combine priority list followed by remaining points
        unvisited = urgent_points + other_points
        
        current_lat = depot_location['lat']
        current_lng = depot_location['lng']
        
        ordered_stops = []
        total_distance = 0.0
        current_vehicle_load = 0.0
        stop_number = 1

        # Add Depot as starting point
        ordered_stops.append({
            'stop_number': stop_number,
            'type': 'depot_start',
            'name': depot_location.get('name', 'Central Waste Depot'),
            'latitude': current_lat,
            'longitude': current_lng,
            'distance_from_prev_km': 0.0
        })

        while unvisited:
            nearest_point = None
            min_dist = float('inf')

            # Find closest unvisited bin to current location
            for point in unvisited:
                dist = self.haversine_distance(current_lat, current_lng, point['latitude'], point['longitude'])
                if dist < min_dist:
                    min_dist = dist
                    nearest_point = point

            if nearest_point is None:
                break

            bin_weight = nearest_point.get('current_weight_kg', 50.0)

            # Check capacity constraint
            if current_vehicle_load + bin_weight > self.vehicle_capacity_kg:
                # Return to depot to unload, then resume
                depot_dist = self.haversine_distance(current_lat, current_lng, depot_location['lat'], depot_location['lng'])
                total_distance += depot_dist
                stop_number += 1
                ordered_stops.append({
                    'stop_number': stop_number,
                    'type': 'depot_unload',
                    'name': 'Depot (Mid-route Unload)',
                    'latitude': depot_location['lat'],
                    'longitude': depot_location['lng'],
                    'distance_from_prev_km': round(depot_dist, 2)
                })
                current_lat = depot_location['lat']
                current_lng = depot_location['lng']
                current_vehicle_load = 0.0

            # Travel to nearest bin
            total_distance += min_dist
            current_vehicle_load += bin_weight
            current_lat = nearest_point['latitude']
            current_lng = nearest_point['longitude']

            stop_number += 1
            ordered_stops.append({
                'stop_number': stop_number,
                'type': 'collection_bin',
                'bin_id': nearest_point.get('id'),
                'name': nearest_point['location_name'],
                'latitude': current_lat,
                'longitude': current_lng,
                'fill_level': nearest_point.get('current_fill_level', 0),
                'weight_kg': bin_weight,
                'priority': nearest_point.get('priority', 1),
                'distance_from_prev_km': round(min_dist, 2)
            })

            unvisited.remove(nearest_point)

        # Return to depot at end of collection route
        final_depot_dist = self.haversine_distance(current_lat, current_lng, depot_location['lat'], depot_location['lng'])
        total_distance += final_depot_dist
        stop_number += 1
        ordered_stops.append({
            'stop_number': stop_number,
            'type': 'depot_finish',
            'name': depot_location.get('name', 'Central Waste Depot (Finish)'),
            'latitude': depot_location['lat'],
            'longitude': depot_location['lng'],
            'distance_from_prev_km': round(final_depot_dist, 2)
        })

        # Calculations
        travel_time_hours = total_distance / self.avg_speed_kmh
        estimated_time_mins = round(travel_time_hours * 60, 1)
        fuel_used_liters = round(total_distance * self.fuel_consumption_per_km, 2)
        visited_count = len([s for s in ordered_stops if s['type'] == 'collection_bin'])

        return {
            'total_distance_km': round(total_distance, 2),
            'estimated_time_mins': estimated_time_mins,
            'fuel_used_liters': fuel_used_liters,
            'visited_bins_count': visited_count,
            'stops': ordered_stops
        }
