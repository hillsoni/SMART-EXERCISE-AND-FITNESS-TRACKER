#!/usr/bin/env python3
"""
Generate secure secret keys for Flask application
"""
import secrets
import string
import os

def generate_secret_key(length=64):
    """Generate a cryptographically secure secret key"""
    alphabet = string.ascii_letters + string.digits + '-_'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_jwt_secret(length=64):
    """Generate a secure JWT secret key"""
    return secrets.token_urlsafe(length)

def generate_password(length=16):
    """Generate a secure password"""
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    print("🔐 Generating Secure Secret Keys for AI Fitness App")
    print("=" * 60)
    
    # Generate keys
    flask_secret = generate_secret_key()
    jwt_secret = generate_jwt_secret()
    db_password = generate_password(16)
    admin_password = generate_password(12)
    
    print("\n📋 Generated Keys:")
    print(f"Flask SECRET_KEY: {flask_secret}")
    print(f"JWT_SECRET_KEY: {jwt_secret}")
    print(f"Database Password: {db_password}")
    print(f"Admin Password: {admin_password}")
    
    print("\n📝 Add these to your .env file:")
    print("-" * 40)
    print(f"SECRET_KEY={flask_secret}")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print(f"POSTGRES_PASSWORD={db_password}")
    print(f"PGADMIN_DEFAULT_PASSWORD={admin_password}")
    
    # Optionally create .env file
    create_env = input("\n❓ Create .env file automatically? (y/n): ").lower().strip()
    
    if create_env == 'y':
        env_content = f"""# Database Configuration
POSTGRES_USER=fitness_user
POSTGRES_PASSWORD={db_password}
POSTGRES_DB=fitness_tracker

# PgAdmin Configuration
PGADMIN_DEFAULT_EMAIL=admin@fitness.com
PGADMIN_DEFAULT_PASSWORD={admin_password}

# JWT Configuration
JWT_SECRET_KEY={jwt_secret}
SECRET_KEY={flask_secret}

# Gemini AI Configuration (Required - Get from https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your-gemini-api-key-here

# MinIO Configuration
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=fitness-app
MINIO_SECURE=False

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=False
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("\n✅ .env file created successfully!")
        print("⚠️  Remember to add your GEMINI_API_KEY before running the application.")
    
    print("\n🔒 Security Notes:")
    print("- Keep these keys secure and never commit them to version control")
    print("- Use different keys for development and production")
    print("- Rotate keys periodically in production")
    print("- Store production keys securely (e.g., AWS Secrets Manager)")

if __name__ == "__main__":
    main()
