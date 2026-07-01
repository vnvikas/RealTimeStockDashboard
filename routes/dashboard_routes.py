"""
Dashboard routes for the main dashboard page.
"""

from flask import Blueprint, render_template, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta

from app import db, cache
from models.portfolio import Portfolio
from models.watchlist import Watchlist
from models.stock import Stock, StockPrice
from models.notification import Notification
from controllers.stock_controller import StockController

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """
    Main dashboard page.
    Displays portfolio summary, market overview, and charts.
    """
    try:
        # Get user statistics
        portfolio_summary = get_portfolio_summary()
        watchlist_summary = get_watchlist_summary()
        market_status = get_market_status()
        
        # Get recent notifications
        recent_notifications = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).order_by(Notification.created_at.desc()).limit(10).all()
        
        return render_template('dashboard.html',
                             portfolio_summary=portfolio_summary,
                             watchlist_summary=watchlist_summary,
                             market_status=market_status,
                             recent_notifications=recent_notifications,
                             notifications_count=len(recent_notifications))
                             
    except Exception as e:
        current_app.logger.error(f'Dashboard error: {str(e)}')
        return render_template('dashboard.html', error='Unable to load dashboard data')


def get_portfolio_summary():
    """
    Get portfolio summary for current user.
    """
    portfolio_entries = Portfolio.query.filter_by(user_id=current_user.id).all()
    
    if not portfolio_entries:
        return {
            'total_investment': 0,
            'total_current_value': 0,
            'total_profit_loss': 0,
            'total_profit_loss_percent': 0,
            'total_stocks': 0
        }
    
    total_investment = sum(float(p.investment or 0) for p in portfolio_entries)
    total_current_value = sum(float(p.current_value or 0) for p in portfolio_entries)
    total_profit_loss = total_current_value - total_investment
    
    profit_loss_percent = 0
    if total_investment > 0:
        profit_loss_percent = (total_profit_loss / total_investment) * 100
    
    return {
        'total_investment': total_investment,
        'total_current_value': total_current_value,
        'total_profit_loss': total_profit_loss,
        'total_profit_loss_percent': profit_loss_percent,
        'total_stocks': len(portfolio_entries)
    }


def get_watchlist_summary():
    """
    Get watchlist summary for current user.
    """
    watchlist_entries = Watchlist.query.filter_by(user_id=current_user.id).all()
    return {
        'total_stocks': len(watchlist_entries),
        'favorites': sum(1 for w in watchlist_entries if w.is_favorite)
    }


def get_market_status():
    """
    Get current market status.
    """
    now = datetime.utcnow()
    is_weekday = now.weekday() < 5
    is_market_hours = 14 <= now.hour <= 20
    
    if is_weekday and is_market_hours:
        status = 'open'
        status_color = 'success'
        message = 'Market is currently open'
    elif is_weekday:
        status = 'closed'
        status_color = 'warning'
        message = 'Market is currently closed'
    else:
        status = 'closed'
        status_color = 'danger'
        message = 'Market is closed for the weekend'
    
    return {
        'status': status,
        'status_color': status_color,
        'message': message,
        'time': now.strftime('%Y-%m-%d %H:%M UTC')
    }


@dashboard_bp.route('/api/dashboard-data')
@login_required
def get_dashboard_data():
    """
    API endpoint for dashboard data.
    Returns JSON data for charts and updates.
    """
    try:
        # Get portfolio data for chart
        portfolio_data = get_portfolio_chart_data()
        
        # Get market data
        market_data = get_market_data()
        
        # Get top stocks
        top_stocks = get_top_stocks()
        
        return jsonify({
            'success': True,
            'portfolio': portfolio_data,
            'market': market_data,
            'top_stocks': top_stocks,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f'Dashboard API error: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        })


def get_portfolio_chart_data():
    """
    Get portfolio data for charts.
    """
    portfolio_entries = Portfolio.query.filter_by(user_id=current_user.id).all()
    
    labels = []
    investments = []
    current_values = []
    profit_loss = []
    
    for entry in portfolio_entries:
        if entry.stock:
            labels.append(entry.stock.symbol)
            investments.append(float(entry.investment or 0))
            current_values.append(float(entry.current_value or 0))
            profit_loss.append(float(entry.profit_loss or 0))
    
    return {
        'labels': labels,
        'investments': investments,
        'current_values': current_values,
        'profit_loss': profit_loss
    }


def get_market_data():
    """
    Get market data for indices.
    """
    return {
        'indices': [
            {'name': 'S&P 500', 'value': 4500.50, 'change': 0.85},
            {'name': 'NASDAQ', 'value': 14100.75, 'change': 1.20},
            {'name': 'DOW', 'value': 35120.30, 'change': 0.45}
        ]
    }


def get_top_stocks():
    """
    Get top performing stocks.
    """
    stocks = Stock.query.limit(10).all()
    top_stocks = []
    
    for stock in stocks:
        change, change_percent = stock.get_price_change()
        top_stocks.append({
            'symbol': stock.symbol,
            'name': stock.company_name,
            'price': stock.get_current_price(),
            'change': change,
            'change_percent': change_percent
        })
    
    top_stocks.sort(key=lambda x: x['change_percent'] or 0, reverse=True)
    return top_stocks[:5]