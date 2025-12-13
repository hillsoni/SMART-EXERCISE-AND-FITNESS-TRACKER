import os
import secrets
from datetime import timedelta

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Gemini
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # MinIO
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
    MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')
    MINIO_SECURE = os.getenv('MINIO_SECURE', 'False') == 'True'
    
    # Flask Security
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_urlsafe(32)
    
    # Security Headers
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Additional Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    @staticmethod
    def validate_config():
        """Validate required configuration"""
        required_vars = [
            'DATABASE_URL',
            'JWT_SECRET_KEY', 
            'SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Validate secret key strength
        secret_key = os.getenv('SECRET_KEY', '')
        if len(secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        
        jwt_secret = os.getenv('JWT_SECRET_KEY', '')
        if len(jwt_secret) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")