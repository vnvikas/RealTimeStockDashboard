"""
Routes package initialization.
Contains all route blueprints for the application.
"""

from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.portfolio_routes import portfolio_bp
from routes.watchlist_routes import watchlist_bp
from routes.market_routes import market_bp
from routes.stock_routes import stock_bp
from routes.admin_routes import admin_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'portfolio_bp',
    'watchlist_bp',
    'market_bp',
    'stock_bp',
    'admin_bp'
]