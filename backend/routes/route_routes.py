"""
Waste Collection Route Optimization API Routes
"""
from flask import Blueprint, request, jsonify
from database.models import Location, Route
from route_optimization.optimizer import RouteOptimizer
from config.settings import Config

route_bp = Blueprint('route', __name__, url_prefix='/api')
optimizer = RouteOptimizer()

@route_bp.route('/locations', methods=['GET'])
def get_locations():
    """Fetches all waste collection locations/bins from database."""
    locations = Location.get_all()
    return jsonify({
        'success': True,
        'count': len(locations),
        'locations': [loc.to_dict() for loc in locations]
    }), 200

@route_bp.route('/locations', methods=['POST'])
def add_location():
    """Adds a new waste collection point location."""
    data = request.get_json() or {}

    location_name = data.get('location_name', '').strip()
    try:
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Valid numeric latitude and longitude are required.'}), 400

    if not location_name:
        return jsonify({'success': False, 'message': 'Location name is required.'}), 400

    capacity_kg = float(data.get('capacity_kg', 100.0))
    current_fill_level = float(data.get('current_fill_level', 0.0))
    current_weight_kg = float(data.get('current_weight_kg', 0.0))
    priority = int(data.get('priority', 1))

    new_loc = Location.create(
        location_name=location_name,
        latitude=latitude,
        longitude=longitude,
        capacity_kg=capacity_kg,
        current_fill_level=current_fill_level,
        current_weight_kg=current_weight_kg,
        priority=priority
    )

    return jsonify({
        'success': True,
        'message': 'Collection point added successfully!',
        'location': new_loc.to_dict()
    }), 201

@route_bp.route('/locations/<int:location_id>', methods=['DELETE'])
def delete_location(location_id):
    """Deletes a collection point from database."""
    Location.delete(location_id)
    return jsonify({'success': True, 'message': 'Collection point deleted.'}), 200

@route_bp.route('/optimize_route', methods=['POST'])
def optimize_route():
    """
    Computes optimal collection route using VRP Nearest Neighbor algorithm,
    saves route record in database, and returns route coordinates & metrics.
    """
    data = request.get_json(silent=True) or {}

    depot_lat = float(data.get('depot_lat', Config.DEFAULT_DEPOT_LAT))
    depot_lng = float(data.get('depot_lng', Config.DEFAULT_DEPOT_LNG))
    depot_name = data.get('depot_name', 'Central Waste Depot')

    depot = {
        'lat': depot_lat,
        'lng': depot_lng,
        'name': depot_name
    }

    # Fetch available collection points from database
    db_locations = Location.get_all()
    points = [loc.to_dict() for loc in db_locations]

    if not points:
        return jsonify({
            'success': False,
            'message': 'No collection points available in database. Add locations first.'
        }), 400

    # Run Optimization Engine
    result = optimizer.optimize(depot, points)

    # Save Route Log into Database
    route_name = f"Route Plan - {len(result['stops'])} Stops"
    saved_route = Route.create(
        route_name=route_name,
        depot_lat=depot_lat,
        depot_lng=depot_lng,
        total_distance_km=result['total_distance_km'],
        estimated_time_mins=result['estimated_time_mins'],
        fuel_used_liters=result['fuel_used_liters'],
        visited_bins_count=result['visited_bins_count'],
        stops_list=result['stops']
    )

    return jsonify({
        'success': True,
        'route_id': saved_route.id,
        'route_name': route_name,
        'depot': depot,
        'total_distance_km': result['total_distance_km'],
        'estimated_time_mins': result['estimated_time_mins'],
        'fuel_used_liters': result['fuel_used_liters'],
        'visited_bins_count': result['visited_bins_count'],
        'stops': result['stops'],
        'algorithm_used': "Nearest Neighbor Algorithm with Haversine Distance & Priority Weighting"
    }), 200

@route_bp.route('/routes', methods=['GET'])
def get_recent_routes():
    """Fetches recent route logs from database."""
    routes = Route.get_recent(limit=5)
    return jsonify({
        'success': True,
        'count': len(routes),
        'routes': [r.to_dict() for r in routes]
    }), 200
