"""
Authentication API Blueprint (Register, Login, Logout, Profile)
"""
from flask import Blueprint, request, jsonify, session
from database.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
    data = request.get_json() or {}

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'user').lower()

    # Validation
    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'Username, email, and password are required.'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters long.'}), 400

    if role not in ['user', 'driver', 'admin']:
        role = 'user'

    # Uniqueness checks
    if User.get_by_username(username):
        return jsonify({'success': False, 'message': 'Username is already taken.'}), 409

    if User.get_by_email(email):
        return jsonify({'success': False, 'message': 'Email address is already registered.'}), 409

    # Create User with Hashed Password
    user = User.create(username=username, email=email, password=password, role=role)

    return jsonify({
        'success': True,
        'message': 'User registered successfully!',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user credentials and create session."""
    data = request.get_json() or {}

    username_or_email = data.get('username_or_email', '').strip()
    password = data.get('password', '')

    if not username_or_email or not password:
        return jsonify({'success': False, 'message': 'Please provide username/email and password.'}), 400

    # Search user by username or email
    user = User.get_by_username(username_or_email) or User.get_by_email(username_or_email.lower())

    # Verify password against stored hash
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'message': 'Invalid username/email or password.'}), 401

    # Store user identity in session
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role

    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Clear active user session."""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully.'
    }), 200


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get profile details of the currently logged-in user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'authenticated': False, 'message': 'No active user session.'}), 401

    user = User.get_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({'authenticated': False, 'message': 'User session invalid.'}), 401

    return jsonify({
        'authenticated': True,
        'user': user.to_dict()
    }), 200
