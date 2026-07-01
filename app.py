"""
Main application file for Real-Time Stock Market Dashboard.
Initializes Flask app, database, extensions, and registers blueprints.
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from flask_cors import CORS
from flask_mail import Mail
from werkzeug.middleware.proxy_fix import ProxyFix

# Import configuration
from config import config, DevelopmentConfig

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
cache = Cache()
mail = Mail()
cors = CORS()

def create_app(config_name=None):
    """
    Application factory function.
    Creates and configures the Flask application.
    
    Args:
        config_name: Configuration environment (development, production, testing)
    
    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    
    # Configure session
    Session(app)
    
    # Configure logging
    configure_logging(app)
    
    # Add proxy fix for production
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register context processors
    register_context_processors(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create upload directory if it doesn't exist
    create_upload_directory(app)
    
    @app.before_request
    def before_request():
        """Execute before each request"""
        g.request_start_time = datetime.utcnow()
        g.user = current_user
        
        # Set user timezone from session or default
        if current_user.is_authenticated:
            g.timezone = current_user.get_timezone() if hasattr(current_user, 'get_timezone') else 'UTC'
        else:
            g.timezone = app.config.get('TIMEZONE', 'UTC')
    
    @app.after_request
    def after_request(response):
        """Execute after each request"""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Log request duration
        if hasattr(g, 'request_start_time'):
            duration = (datetime.utcnow() - g.request_start_time).total_seconds()
            app.logger.info(f'Request duration: {duration:.3f}s')
        
        return response
    
    return app

def configure_logging(app):
    """Configure application logging"""
    if not app.debug:
        # Set logging level
        app.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)

def register_blueprints(app):
    """Register all application blueprints"""
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.portfolio_routes import portfolio_bp
    from routes.watchlist_routes import watchlist_bp
    from routes.market_routes import market_bp
    from routes.stock_routes import stock_bp
    from routes.admin_routes import admin_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(portfolio_bp, url_prefix='/portfolio')
    app.register_blueprint(watchlist_bp, url_prefix='/watchlist')
    app.register_blueprint(market_bp, url_prefix='/market')
    app.register_blueprint(stock_bp, url_prefix='/stock')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Main routes
    @app.route('/')
    def index():
        """Home page route"""
        return render_template('index.html')
    
    @app.route('/about')
    def about():
        """About page route"""
        return render_template('about.html')

def register_context_processors(app):
    """Register template context processors"""
    
    @app.context_processor
    def utility_processor():
        """Add utility functions to templates"""
        def format_currency(amount, currency='USD'):
            """Format amount as currency"""
            if amount is None:
                return '$0.00'
            return f'${amount:,.2f}'
        
        def format_percentage(value):
            """Format value as percentage"""
            if value is None:
                return '0.00%'
            return f'{value:,.2f}%'
        
        def format_date(date, format='%Y-%m-%d %H:%M'):
            """Format datetime object"""
            if date is None:
                return ''
            return date.strftime(format)
        
        def get_time_ago(date):
            """Get time ago string"""
            if date is None:
                return ''
            now = datetime.utcnow()
            diff = now - date
            
            if diff.days > 365:
                return f'{diff.days // 365} year(s) ago'
            elif diff.days > 30:
                return f'{diff.days // 30} month(s) ago'
            elif diff.days > 0:
                return f'{diff.days} day(s) ago'
            elif diff.seconds > 3600:
                return f'{diff.seconds // 3600} hour(s) ago'
            elif diff.seconds > 60:
                return f'{diff.seconds // 60} minute(s) ago'
            else:
                return 'Just now'
        
        return {
            'format_currency': format_currency,
            'format_percentage': format_percentage,
            'format_date': format_date,
            'get_time_ago': get_time_ago,
            'app_name': app.config.get('APP_NAME', 'Stock Dashboard'),
            'app_version': app.config.get('APP_VERSION', '1.0.0')
        }

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors"""
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        """Handle 401 errors"""
        return render_template('errors/401.html'), 401

def create_upload_directory(app):
    """Create upload directory if it doesn't exist"""
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder and not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

# Create application instance
app = create_app(os.environ.get('FLASK_CONFIG', 'default'))

# Login manager user loader
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    from models.user import User
    return User.query.get(int(user_id))

# Main entry point
if __name__ == '__main__':
    print("=" * 50)
    print("DATABASE CONFIGURATION DEBUG")
    print("=" * 50)
    print(f"DB_HOST: {app.config.get('DB_HOST', 'Not Set')}")
    print(f"DB_PORT: {app.config.get('DB_PORT', 'Not Set')}")
    print(f"DB_USERNAME: {app.config.get('DB_USERNAME', 'Not Set')}")
    print(f"DB_NAME: {app.config.get('DB_NAME', 'Not Set')}")
    print(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not Set')}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)