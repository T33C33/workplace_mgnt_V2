import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database Configuration (using Railway MySQL)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # MySQL Database URL - Replace with your cloud MySQL URL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://username:password@host:port/database_name'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'teeceeiheukwumere@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'qkqt vffv ksfb gnqp'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME') or 'teeceeiheukwumere@gmail.com'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
