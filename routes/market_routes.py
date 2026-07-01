"""
Market routes for displaying market overview and analysis.
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from datetime import datetime, timedelta

from app import db, cache
from models.stock import Stock
from controllers.market_controller import MarketController

market_bp = Blueprint('market', __name__)


@market_bp.route('/')
@login_required
def index():
    """
    Market overview page.
    """
    try:
        # Get market data
        market_data = MarketController.get_market_overview()
        
        # Get top gainers and losers
        top_gainers = MarketController.get_top_gainers()
        top_losers = MarketController.get_top_losers()
        
        # Get indices data
        indices = MarketController.get_indices_data()
        
        return render_template('market.html',
                             market_data=market_data,
                             top_gainers=top_gainers,
                             top_losers=top_losers,
                             indices=indices)
                             
    except Exception as e:
        current_app.logger.error(f'Market error: {str(e)}')
        return render_template('market.html', error='Unable to load market data')


@market_bp.route('/api/market-data')
@login_required
@cache.cached(timeout=30)
def get_market_data():
    """
    API endpoint for market data.
    """
    try:
        data = {
            'indices': MarketController.get_indices_data(),
            'top_gainers': MarketController.get_top_gainers(),
            'top_losers': MarketController.get_top_losers(),
            'most_active': MarketController.get_most_active_stocks(),
            'market_overview': MarketController.get_market_overview(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        current_app.logger.error(f'Market API error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})