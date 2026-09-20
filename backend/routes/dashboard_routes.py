"""
Dashboard Analytics API Routes
"""
from flask import Blueprint, jsonify
from database.db import get_db

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """Queries Supabase database to aggregate real-time system statistics and analytics."""
    supabase = get_db()

    # 1. Total Detection Scans
    detections_res = supabase.table("waste_detections").select("id", count="exact").execute()
    total_detections = detections_res.count if detections_res.count else 0

    # 2. Category Distribution Breakdown
    # Supabase REST doesn't support GROUP BY directly without RPC. 
    # Fetching the categories and bin colors to aggregate in Python.
    all_detections_res = supabase.table("waste_detections").select("category_name, bin_color").execute()
    category_counts_dict = {}
    
    for r in all_detections_res.data:
        cat_name = r['category_name']
        bin_color = r['bin_color']
        if cat_name not in category_counts_dict:
            category_counts_dict[cat_name] = {'count': 0, 'bin_color': bin_color}
        category_counts_dict[cat_name]['count'] += 1

    category_labels = []
    category_counts = []
    category_colors = []

    color_map = {
        'Green': '#10b981',
        'Blue': '#3b82f6',
        'Black': '#475569'
    }

    recyclable_count = 0
    wet_count = 0

    for cat_name, data in category_counts_dict.items():
        category_labels.append(cat_name)
        category_counts.append(data['count'])
        category_colors.append(color_map.get(data['bin_color'], '#3b82f6'))

        if 'Recyclable' in cat_name or 'Paper' in cat_name or 'Plastic' in cat_name:
            recyclable_count += data['count']
        if 'Organic' in cat_name or 'Wet' in cat_name:
            wet_count += data['count']

    recycling_rate = round((recyclable_count / total_detections * 100), 1) if total_detections > 0 else 0.0

    # 3. Collection Locations Metrics
    locations_res = supabase.table("locations").select("current_fill_level").execute()
    total_bins = len(locations_res.data)
    overflown_bins = sum(1 for loc in locations_res.data if loc['current_fill_level'] >= 90)
    needs_collection_bins = sum(1 for loc in locations_res.data if 60 <= loc['current_fill_level'] < 90)
    normal_bins = sum(1 for loc in locations_res.data if loc['current_fill_level'] < 60)

    # 4. Recent Detections List
    recent_res = supabase.table("waste_detections").select("id, category_name, waste_type, bin_color, confidence_score, image_path, detected_at").order("id", desc=True).limit(5).execute()
    recent_detections = recent_res.data

    # 5. Latest Optimized Route Summary
    latest_route_res = supabase.table("routes").select("*").order("id", desc=True).limit(1).execute()
    latest_route = latest_route_res.data[0] if latest_route_res.data else None

    # 6. Top High-Priority Bins
    urgent_bins_res = supabase.table("locations").select("id, location_name, current_fill_level, current_weight_kg, priority, status").or_("current_fill_level.gte.60,priority.gte.4").order("current_fill_level", desc=True).limit(5).execute()
    urgent_bins = urgent_bins_res.data

    return jsonify({
        'success': True,
        'summary': {
            'total_detections': total_detections,
            'recycling_rate_percent': recycling_rate,
            'total_bins': total_bins,
            'overflown_bins': overflown_bins,
            'needs_collection_bins': needs_collection_bins,
            'normal_bins': normal_bins
        },
        'chart_category': {
            'labels': category_labels if category_labels else ['No Data Yet'],
            'counts': category_counts if category_counts else [0],
            'colors': category_colors if category_colors else ['#475569']
        },
        'chart_bin_status': {
            'labels': ['Overflown (>=90%)', 'Needs Collection (>=60%)', 'Normal (<60%)'],
            'counts': [overflown_bins, needs_collection_bins, normal_bins],
            'colors': ['#ef4444', '#f59e0b', '#10b981']
        },
        'recent_detections': recent_detections,
        'urgent_bins': urgent_bins,
        'latest_route': latest_route
    }), 200
