import os
from flask import g, current_app
from supabase import create_client, Client
from config.settings import Config

def get_db() -> Client:
    """Returns per-request Supabase client connection."""
    if 'db' not in g:
        url = current_app.config.get('SUPABASE_URL', Config.SUPABASE_URL) if current_app else Config.SUPABASE_URL
        key = current_app.config.get('SUPABASE_KEY', Config.SUPABASE_KEY) if current_app else Config.SUPABASE_KEY
        
        if not url or not key:
            raise ValueError("SUPABASE_URL or SUPABASE_KEY is not set.")
            
        g.db = create_client(url, key)
    return g.db

def close_db(e=None):
    """Cleanup logic if needed (Supabase client doesn't need explicit closing)."""
    g.pop('db', None)

def init_db(app):
    """Registers database teardown."""
    app.teardown_appcontext(close_db)
