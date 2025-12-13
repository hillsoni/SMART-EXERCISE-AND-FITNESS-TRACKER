from dotenv import load_dotenv
import os

load_dotenv()

from app import create_app, db
from flask import jsonify

app = create_app()

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Welcome to AI Fitness Tracker API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'docs': '/api/docs',
            'auth': '/api/auth',
            'users': '/api/users',
            'yoga': '/api/yoga',
            'workouts': '/api/workouts',
            'diet': '/api/diet',
            'exercise': '/api/exercise',
            'chatbot': '/api/chatbot'
        }
    })

@app.route('/api/docs')
def docs():
    """API Documentation"""
    return jsonify({
        'api_name': 'AI Fitness Tracker API',
        'version': '1.0.0',
        'description': 'Complete fitness tracking API with AI-powered features',
        'base_url': '/api',
        'authentication': 'JWT Bearer Token',
        'endpoints': {
            'Authentication': {
                'POST /auth/register': 'Register new user',
                'POST /auth/login': 'Login user',
                'POST /auth/logout': 'Logout user',
                'GET /auth/profile': 'Get user profile',
                'PUT /auth/profile': 'Update profile',
                'POST /auth/change-password': 'Change password',
                'GET /auth/verify': 'Verify JWT token'
            },
            'Diet Plans': {
                'POST /diet/generate': 'Generate AI diet plan',
                'GET /diet/': 'Get all user diet plans',
                'GET /diet/<id>': 'Get specific diet plan',
                'PUT /diet/<id>': 'Update diet plan',
                'DELETE /diet/<id>': 'Delete diet plan',
                'GET /diet/latest': 'Get latest diet plan',
                'GET /diet/statistics': 'Get diet statistics'
            },
            'Chatbot': {
                'POST /chatbot/query': 'Send question to AI',
                'GET /chatbot/history': 'Get chat history',
                'GET /chatbot/<id>': 'Get specific query',
                'DELETE /chatbot/<id>': 'Delete query',
                'DELETE /chatbot/history': 'Clear history',
                'GET /chatbot/statistics': 'Get chat statistics',
                'POST /chatbot/quick-ask': 'Quick ask without saving'
            },
            'Yoga': {
                'GET /yoga/': 'Get all yoga poses',
                'GET /yoga/<id>': 'Get specific pose',
                'POST /yoga/': 'Create pose (Admin)',
                'PUT /yoga/<id>': 'Update pose (Admin)',
                'DELETE /yoga/<id>': 'Delete pose (Admin)',
                'GET /yoga/difficulty/<level>': 'Get by difficulty'
            },
            'Workouts': {
                'GET /workouts/': 'Get all workouts',
                'GET /workouts/<id>': 'Get specific workout',
                'POST /workouts/': 'Create workout (Admin)',
                'PUT /workouts/<id>': 'Update workout (Admin)',
                'DELETE /workouts/<id>': 'Delete workout (Admin)'
            },
            'Exercise Plans': {
                'POST /exercise/generate': 'Generate exercise plan',
                'GET /exercise/': 'Get all user exercise plans',
                'GET /exercise/<id>': 'Get specific plan',
                'PUT /exercise/<id>': 'Update plan',
                'DELETE /exercise/<id>': 'Delete plan'
            },
            'Users': {
                'GET /users/': 'Get all users (Admin)',
                'GET /users/<id>': 'Get user by ID',
                'PUT /users/<id>': 'Update user',
                'DELETE /users/<id>': 'Delete user (Admin)',
                'GET /users/<id>/stats': 'Get user statistics',
                'GET /users/search': 'Search users (Admin)'
            }
        }
    })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'api': 'running'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Get configuration
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')

    print("\n" + "="*70)
    print("🚀 STARTING AI FITNESS TRACKER API")
    print("="*70)
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug: {debug_mode}")
    print(f"🌍 Environment: {os.getenv('FLASK_ENV', 'development')}")
    print("="*70)

    # Initialize database tables
    with app.app_context():
        try:
            print("\n📦 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully\n")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}\n")

    print("="*70)
    print("✅ SERVER READY!")
    print("="*70)
    print(f"\n👉 API Base URL: http://localhost:{port}/")
    print(f"👉 Health Check: http://localhost:{port}/health")
    print(f"👉 API Docs: http://localhost:{port}/api/docs")
    print("\n" + "="*70 + "\n")

    app.run(debug=debug_mode, host=host, port=port)
