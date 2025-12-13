from dotenv import load_dotenv
import os

load_dotenv()

# Now import Flask and extensions
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# Token blacklist storage
token_blacklist = set()

def create_app():
    app = Flask(__name__)

    print("\n" + "="*70)
    print("🔍 CHECKING ENVIRONMENT VARIABLES")
    print("="*70)
    db_url = os.getenv('DATABASE_URL')
    print(f"DATABASE_URL: {db_url if db_url else '❌ NOT SET'}")
    print(f"JWT_SECRET_KEY: {'✅ SET' if os.getenv('JWT_SECRET_KEY') else '❌ NOT SET'}")
    print(f"SECRET_KEY: {'✅ SET' if os.getenv('SECRET_KEY') else '❌ NOT SET'}")
    print("="*70 + "\n")

    # Load config
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # JWT Configuration - Ensure secret key is set
    jwt_secret_key = os.getenv('JWT_SECRET_KEY')
    if not jwt_secret_key:
        raise ValueError("JWT_SECRET_KEY environment variable is required")
    app.config['JWT_SECRET_KEY'] = jwt_secret_key
    app.config['JWT_ALGORITHM'] = 'HS256'  # Explicitly set algorithm

    # Token location - explicitly set where to look for tokens
    from datetime import timedelta
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Look for token in Authorization header
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'  # Token format: "Bearer <token>"

    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise ValueError("SECRET_KEY environment variable is required")
    app.config['SECRET_KEY'] = secret_key

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000", "http://localhost:5174"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # JWT Configuration
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in token_blacklist

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has expired',
            'message': 'Please login again'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """Handle invalid token errors with detailed message"""
        error_message = str(error) if error else 'Invalid token'
        return jsonify({
            'error': 'Invalid token',
            'message': 'Authentication failed',
            'details': error_message
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Authorization required',
            'message': 'Access token is missing'
        }), 401

    # Register blueprints
    print("📝 Registering routes...")

    try:
        from app.routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp)
        print("✓ Registered auth routes")
    except Exception as e:
        print(f"✗ Error loading auth routes: {e}")

    try:
        from app.routes.user import bp_user as user_bp
        app.register_blueprint(user_bp)
        print("✓ Registered user routes")
    except Exception as e:
        print(f"✗ Error loading user routes: {e}")

    try:
        from app.routes.yoga import bp as yoga_bp
        app.register_blueprint(yoga_bp)
        print("✓ Registered yoga routes")
    except Exception as e:
        print(f"✗ Error loading yoga routes: {e}")

    try:
        from app.routes.workout import bp as workout_bp
        app.register_blueprint(workout_bp)
        print("✓ Registered workout routes")
    except Exception as e:
        print(f"✗ Error loading workout routes: {e}")

    try:
        from app.routes.diet import bp as diet_bp
        app.register_blueprint(diet_bp)
        print("✓ Registered diet routes")
    except Exception as e:
        print(f"✗ Error loading diet routes: {e}")

    try:
        from app.routes.exercise import bp_exercise as exercise_bp
        app.register_blueprint(exercise_bp)
        print("✓ Registered exercise routes")
    except Exception as e:
        print(f"✗ Error loading exercise routes: {e}")

    try:
        from app.routes.chatbot import bp as chatbot_bp
        app.register_blueprint(chatbot_bp)
        print("✓ Registered chatbot routes")
    except Exception as e:
        print(f"✗ Error loading chatbot routes: {e}")

    try:
        from app.routes.challenge import bp as challenge_bp
        app.register_blueprint(challenge_bp)
        print("✓ Registered challenge routes")
    except Exception as e:
        print(f"✗ Error loading challenge routes: {e}")

    print("✓ All routes registered\n")

    return app
