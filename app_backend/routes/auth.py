# app/routes/auth.py - Complete Authentication System

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from app import db
from app.models.user import User
from app.models.role import Role
from email_validator import validate_email, EmailNotValidError

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Token blacklist (in production, use Redis)
token_blacklist = set()

# ============= REGISTER =============
@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate email format
        try:
            valid = validate_email(data['email'])
            email = valid.email
        except EmailNotValidError as e:
            return jsonify({'error': str(e)}), 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 409

        # Get or create default role
        default_role = Role.query.filter_by(role_name='user').first()
        if not default_role:
            default_role = Role(role_name='user', description='Regular user')
            db.session.add(default_role)
            db.session.commit()

        # Create new user
        user = User(
            username=data['username'],
            email=email,
            mobile_number=data.get('mobile_number'),
            height=data.get('height'),  # ✅ ADD
            weight=data.get('weight'),  # ✅ ADD
            age=data.get('age'),        # ✅ ADD (optional)
            gender=data.get('gender'),   # ✅ ADD (optional)
            role_id=default_role.id
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Create access token
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
        'message': 'Registration successful',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'mobile_number': user.mobile_number,
            'height': user.height,    # ✅ INCLUDE
            'weight': user.weight,    # ✅ INCLUDE
            'age': user.age,          # ✅ INCLUDE
            'gender': user.gender     # ✅ INCLUDE
        }
    }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= LOGIN =============
@bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token"""
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400

        # Find user
        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Create access token
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.role_name
            },
            'access_token': access_token
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= LOGOUT =============
@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user by blacklisting token"""
    try:
        jti = get_jwt()['jti']
        token_blacklist.add(jti)

        return jsonify({'message': 'Logout successful'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= GET PROFILE =============
@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'mobile_number': user.mobile_number,
            'height': user.height,
            'weight': user.weight,
            'role': user.role.role_name,
            'created_at': user.created_at.isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= UPDATE PROFILE =============
@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Update allowed fields
        if 'username' in data:
            # Check if username is already taken by another user
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user_id:
                return jsonify({'error': 'Username already taken'}), 409
            user.username = data['username']

        if 'mobile_number' in data:
            user.mobile_number = data['mobile_number']

        if 'height' in data:
            user.height = float(data['height']) if data['height'] else None

        if 'weight' in data:
            user.weight = float(data['weight']) if data['weight'] else None

        if 'password' in data:
            user.set_password(data['password'])

        db.session.commit()

        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'mobile_number': user.mobile_number,
                'height': user.height,
                'weight': user.weight
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= CHANGE PASSWORD =============
@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        if not data.get('old_password') or not data.get('new_password'):
            return jsonify({'error': 'Old and new password required'}), 400

        # Verify old password
        if not user.check_password(data['old_password']):
            return jsonify({'error': 'Invalid old password'}), 401

        # Update password
        user.set_password(data['new_password'])
        db.session.commit()

        return jsonify({'message': 'Password changed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============= VERIFY TOKEN =============
@bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify if JWT token is valid"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'valid': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.role_name
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= DEBUG TOKEN INFO =============
@bp.route('/debug-token', methods=['POST'])
def debug_token():
    """Debug endpoint to check token format and configuration"""
    from flask import current_app
    try:
        import jwt as pyjwt
    except ImportError:
        # PyJWT is a dependency of Flask-JWT-Extended, but handle gracefully
        return jsonify({
            'error': 'PyJWT not available',
            'hint': 'Install PyJWT: pip install PyJWT'
        }), 500

    try:
        auth_header = request.headers.get('Authorization', '')

        if not auth_header:
            return jsonify({
                'error': 'No Authorization header found',
                'hint': 'Send token as: Authorization: Bearer <your_token>'
            }), 400

        # Check if Bearer prefix is present
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Invalid Authorization header format',
                'received': auth_header[:50] + '...' if len(auth_header) > 50 else auth_header,
                'expected': 'Bearer <token>',
                'hint': 'Token must start with "Bearer " prefix'
            }), 400

        token = auth_header.replace('Bearer ', '').strip()

        # Try to decode token
        try:
            # Get JWT secret from config
            jwt_secret = current_app.config.get('JWT_SECRET_KEY')
            if not jwt_secret:
                return jsonify({
                    'error': 'JWT_SECRET_KEY not configured in app',
                    'hint': 'Check your .env file and ensure JWT_SECRET_KEY is set'
                }), 500

            # Decode without verification first to see token structure
            unverified = pyjwt.decode(token, options={"verify_signature": False})

            # Now try to verify
            try:
                decoded = pyjwt.decode(token, jwt_secret, algorithms=['HS256'])
                return jsonify({
                    'status': 'Token is valid',
                    'decoded': decoded,
                    'config': {
                        'jwt_secret_set': bool(jwt_secret),
                        'jwt_secret_length': len(jwt_secret) if jwt_secret else 0,
                        'algorithm': 'HS256'
                    }
                }), 200
            except pyjwt.InvalidSignatureError:
                return jsonify({
                    'error': 'Token signature is invalid',
                    'hint': 'The JWT_SECRET_KEY used to sign this token does not match the one in your server configuration',
                    'token_info': unverified
                }), 401
            except Exception as e:
                return jsonify({
                    'error': 'Token verification failed',
                    'details': str(e),
                    'token_info': unverified
                }), 401

        except pyjwt.DecodeError as e:
            return jsonify({
                'error': 'Token is malformed',
                'details': str(e),
                'hint': 'Token should be a valid JWT format'
            }), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
