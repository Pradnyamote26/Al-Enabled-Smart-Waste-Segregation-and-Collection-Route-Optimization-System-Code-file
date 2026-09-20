"""
Admin Management & Access Control API Blueprint
"""
from functools import wraps
from flask import Blueprint, request, jsonify, session
from database.models import User, WasteCategory, WasteDetection, Location, Route

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def admin_required(f):
    """Decorator to enforce Admin Role Authorization on routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return jsonify({
                'success': False,
                'message': 'Access denied. Administrative privileges required.'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

# 1. Admin System Summary Statistics
@admin_bp.route('/stats', methods=['GET'])
@admin_required
def admin_stats():
    """Returns overview statistics across all system modules."""
    return jsonify({
        'success': True,
        'counts': {
            'users': len(User.get_all()),
            'detections': len(WasteDetection.get_all()),
            'categories': len(WasteCategory.get_all()),
            'locations': len(Location.get_all()),
            'routes': len(Route.get_all())
        }
    }), 200

# 2. User Management
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """View all registered users."""
    users = User.get_all()
    return jsonify({
        'success': True,
        'users': [u.to_dict() for u in users]
    }), 200

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user account."""
    if user_id == session.get('user_id'):
        return jsonify({'success': False, 'message': 'Cannot delete your own active admin account.'}), 400
    User.delete(user_id)
    return jsonify({'success': True, 'message': f'User #{user_id} deleted successfully.'}), 200

# 3. Waste Detection Log Management
@admin_bp.route('/detections', methods=['GET'])
@admin_required
def get_detections():
    """View all waste detection records."""
    detections = WasteDetection.get_all()
    return jsonify({
        'success': True,
        'detections': [d.to_dict() for d in detections]
    }), 200

@admin_bp.route('/detections/<int:detection_id>', methods=['DELETE'])
@admin_required
def delete_detection(detection_id):
    """Delete a waste detection record."""
    WasteDetection.delete(detection_id)
    return jsonify({'success': True, 'message': f'Detection record #{detection_id} deleted.'}), 200

# 4. Waste Categories Management
@admin_bp.route('/categories', methods=['GET'])
@admin_required
def get_categories():
    """View all waste categories."""
    categories = WasteCategory.get_all()
    return jsonify({
        'success': True,
        'categories': [c.to_dict() for c in categories]
    }), 200

@admin_bp.route('/categories', methods=['POST'])
@admin_required
def add_category():
    """Add a new waste category."""
    data = request.get_json() or {}
    name = data.get('category_name', '').strip()
    waste_type = data.get('waste_type', '').strip()
    color = data.get('recommended_bin_color', 'Blue').strip()
    suggestion = data.get('disposal_suggestion', '').strip()

    if not name or not waste_type or not suggestion:
        return jsonify({'success': False, 'message': 'Name, waste type, and disposal suggestion are required.'}), 400

    new_cat = WasteCategory.create(name, waste_type, color, suggestion)
    return jsonify({'success': True, 'category': new_cat.to_dict()}), 201

@admin_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """Delete a waste category."""
    WasteCategory.delete(category_id)
    return jsonify({'success': True, 'message': f'Category #{category_id} deleted.'}), 200

# 5. Collection Locations Management
@admin_bp.route('/locations', methods=['GET'])
@admin_required
def get_locations():
    """View all collection points."""
    locations = Location.get_all()
    return jsonify({
        'success': True,
        'locations': [l.to_dict() for l in locations]
    }), 200

@admin_bp.route('/locations/<int:location_id>', methods=['DELETE'])
@admin_required
def delete_location(location_id):
    """Delete a collection point."""
    Location.delete(location_id)
    return jsonify({'success': True, 'message': f'Location #{location_id} deleted.'}), 200

# 6. Optimized Routes Management
@admin_bp.route('/routes', methods=['GET'])
@admin_required
def get_routes():
    """View all route optimization logs."""
    routes = Route.get_all()
    return jsonify({
        'success': True,
        'routes': [r.to_dict() for r in routes]
    }), 200

@admin_bp.route('/routes/<int:route_id>', methods=['DELETE'])
@admin_required
def delete_route(route_id):
    """Delete a route optimization log."""
    Route.delete(route_id)
    return jsonify({'success': True, 'message': f'Route log #{route_id} deleted.'}), 200
