#!/usr/bin/env python3
"""
Utility script to generate secure environment variables for the Banking Transaction System
"""

import secrets
import string
import os

def generate_secret_key():
    """Generate a secure Flask secret key"""
    return secrets.token_hex(32)

def generate_password(length=16):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

def create_env_file():
    """Create a .env file with generated values"""
    secret_key = generate_secret_key()
    db_password = generate_password(12)
    
    env_content = f"""# Environment Variables for Banking Transaction System
# Generated on {os.popen('date').read().strip()}

# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV=development

# Database Configuration
# For local development (SQLite)
DATABASE_URL=sqlite:///banking_system.db

# For PostgreSQL (production) - Update with your actual database details
# DATABASE_URL=postgresql://username:{db_password}@host:port/database

# For Vercel Postgres (example)
# DATABASE_URL=postgresql://postgres:{db_password}@db.vercel.com:5432/banking_system

# Optional: Additional Configuration
DEBUG=True
LOG_LEVEL=INFO
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    return secret_key, db_password

def main():
    print("🔧 Banking Transaction System - Environment Variables Generator")
    print("=" * 60)
    
    # Generate keys
    secret_key = generate_secret_key()
    db_password = generate_password(12)
    
    print("\n🔐 Generated Secure Keys:")
    print(f"SECRET_KEY: {secret_key}")
    print(f"Database Password: {db_password}")
    
    # Create .env file
    print("\n📝 Creating .env file...")
    create_env_file()
    print("✅ .env file created successfully!")
    
    print("\n📋 For Vercel Deployment, use these environment variables:")
    print("=" * 50)
    print(f"SECRET_KEY={secret_key}")
    print(f"DATABASE_URL=postgresql://username:{db_password}@host:port/database")
    print("FLASK_ENV=production")
    
    print("\n🔒 Security Notes:")
    print("- Keep these keys secure and never commit them to version control")
    print("- Use different keys for development, staging, and production")
    print("- Rotate keys regularly for production environments")
    
    print("\n📖 Next Steps:")
    print("1. Review and customize the .env file")
    print("2. Set up your database connection")
    print("3. Configure Vercel environment variables")
    print("4. Test your application locally")
    
    print("\n🎉 Environment setup complete!")

if __name__ == "__main__":
    main() 