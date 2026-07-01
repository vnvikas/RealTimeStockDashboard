"""
Configuration file for the Stock Market Dashboard application.
Contains all configuration settings, environment variables, and API keys.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    TESTING = False
    
    # ============================================
    # DATABASE CONFIGURATION - HARDCODED FOR TESTING
    # ============================================
    DB_HOST = 'Mysql host'  # Use IP instead of localhost
    DB_PORT = "post number"
    DB_USERNAME = 'Mysql username'
    DB_PASSWORD = 'Mysql password'
    DB_NAME = 'Mysql database name'
    
    # SQLAlchemy configuration - Using hardcoded values
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Set to True to see SQL queries in console
    
    # ============================================
    # REST OF YOUR CONFIGURATION
    # ============================================
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-secret-key'
    
    # Flask-Login configuration
    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = 'Please log in to access this page.'
    LOGIN_MESSAGE_CATEGORY = 'info'
    
    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@stockdashboard.com'
    
    # Stock API configuration
    STOCK_API_KEY = os.environ.get('STOCK_API_KEY') or 'YOUR_ALPHA_VANTAGE_API_KEY'
    STOCK_API_PROVIDER = os.environ.get('STOCK_API_PROVIDER') or 'alphavantage'
    FINNHUB_API_KEY = os.environ.get('FINNHUB_API_KEY') or 'YOUR_FINNHUB_API_KEY'
    TWELVEDATA_API_KEY = os.environ.get('TWELVEDATA_API_KEY') or 'YOUR_TWELVEDATA_API_KEY'
    USE_YFINANCE = True
    
    # API endpoints
    ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
    FINNHUB_BASE_URL = 'https://finnhub.io/api/v1'
    TWELVEDATA_BASE_URL = 'https://api.twelvedata.com'
    
    # Application settings
    APP_NAME = 'Real-Time Stock Market Dashboard'
    APP_DESCRIPTION = 'Professional stock market tracking and portfolio management platform'
    APP_VERSION = '1.0.0'
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Cache settings
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Pagination settings
    ITEMS_PER_PAGE = 20
    NEWS_PER_PAGE = 10
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = '100 per minute'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'app.log'
    
    # Security
    BCRYPT_LOG_ROUNDS = 12
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_COMPLEXITY = True
    
    # Timezone
    TIMEZONE = 'UTC'
    
    # Currency
    DEFAULT_CURRENCY = 'USD'
    SUPPORTED_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'INR']
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}