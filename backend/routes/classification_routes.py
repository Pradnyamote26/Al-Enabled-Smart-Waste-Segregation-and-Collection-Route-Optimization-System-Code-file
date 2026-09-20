"""
Waste Classification API Routes
"""
import os
import uuid
from flask import Blueprint, request, jsonify, session, current_app
from database.models import WasteDetection
from ml_model.predict import WasteClassifier

classification_bp = Blueprint('classification', __name__, url_prefix='/api')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}
classifier = WasteClassifier()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@classification_bp.route('/classify', methods=['POST'])
def classify_waste():
    """Accepts uploaded waste image, runs AI classification, saves record to DB, returns results."""
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image file provided in request.'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected image file.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Invalid image format. Allowed formats: PNG, JPG, JPEG, WEBP.'}), 400

    # Ensure upload directory exists
    upload_dir = os.path.join(current_app.root_path, '..', 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"waste_{uuid.uuid4().hex[:10]}.{ext}"
    saved_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    file.save(saved_path)

    import cloudinary
    import cloudinary.uploader
    try:
        # Run AI Classification Pipeline
        result = classifier.classify_image(saved_path)

        # Upload image to Cloudinary
        cloudinary.config(
            cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME'),
            api_key=current_app.config.get('CLOUDINARY_API_KEY'),
            api_secret=current_app.config.get('CLOUDINARY_API_SECRET'),
            secure=True
        )
        
        upload_result = cloudinary.uploader.upload(saved_path, public_id=unique_filename.split('.')[0])
        cloudinary_url = upload_result.get("secure_url")
        
        # Clean up local file
        if os.path.exists(saved_path):
            os.remove(saved_path)

        # Store Detection Record in Database
        user_id = session.get('user_id')
        
        db_record = WasteDetection.create(
            category_name=result['category_name'],
            waste_type=result['waste_type'],
            bin_color=result['recommended_bin_color'],
            confidence_score=result['confidence_score'],
            image_path=cloudinary_url,
            disposal_suggestion=result['disposal_suggestion'],
            user_id=user_id
        )

        return jsonify({
            'success': True,
            'detection_id': db_record.id,
            'user_id': user_id,
            'category_name': result['category_name'],
            'waste_type': result['waste_type'],
            'recommended_bin_color': result['recommended_bin_color'],
            'disposal_suggestion': result['disposal_suggestion'],
            'confidence_score': result['confidence_score'],
            'confidence_percent': result['confidence_percent'],
            'image_url': cloudinary_url,
            'detected_at': db_record.detected_at,
            'stored_in_db': True
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing image: {str(e)}'
        }), 500


@classification_bp.route('/detections', methods=['GET'])
def get_detections():
    """Fetches recent waste classification records from the database."""
    recent_records = WasteDetection.get_recent(limit=15)
    return jsonify({
        'success': True,
        'count': len(recent_records),
        'detections': [r.to_dict() for r in recent_records]
    }), 200
