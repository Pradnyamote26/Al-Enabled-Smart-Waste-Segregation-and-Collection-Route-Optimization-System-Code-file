from backend.app import app

if __name__ == "__main__":
    from waitress import serve
    print("Starting production server on http://127.0.0.1:5000 using Waitress...")
    serve(app, host='127.0.0.1', port=5000)
