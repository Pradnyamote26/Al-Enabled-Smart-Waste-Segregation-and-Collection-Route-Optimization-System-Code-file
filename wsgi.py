import os
from backend.app import app

if __name__ == "__main__":
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting production server on 0.0.0.0:{port} using Waitress...")
    serve(app, host='0.0.0.0', port=port)
