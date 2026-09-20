import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

class Config:
    # Secret key for session signing (no hardcoded fallback to ensure security)
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY and os.getenv('FLASK_ENV') == 'production':
        raise ValueError("No SECRET_KEY set for Flask application in production")
        
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']

    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

    # Default Municipal Depot Coordinates (Pune Central Depot)
    DEFAULT_DEPOT_LAT = 18.5204
    DEFAULT_DEPOT_LNG = 73.8567
