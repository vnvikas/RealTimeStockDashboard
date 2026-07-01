"""
Stock routes for detailed stock information.
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required
from datetime import datetime, timedelta

from app import db, cache
from models.stock import Stock, StockPrice
from models.news import News
from controllers.stock_controller import StockController

stock_bp = Blueprint('stock', __name__)


@stock_bp.route('/<symbol>')
@login_required
def details(symbol):
    """
    Stock details page.
    Displays detailed information about a specific stock.
    """
    try:
        symbol = symbol.upper()
        stock = Stock.query.filter_by(symbol=symbol).first()
        
        if not stock:
            # Try to fetch from API
            stock = StockController.fetch_stock_info(symbol)
            if not stock:
                flash('Stock not found.', 'danger')
                return redirect(url_for('market.index'))
            db.session.add(stock)
            db.session.commit()
        
        # Get price history
        price_history = StockPrice.query.filter_by(stock_id=stock.id)\
            .order_by(StockPrice.date.desc())\
            .limit(90)\
            .all()
        
        # Get news for this stock
        news = News.query.filter_by(stock_id=stock.id)\
            .order_by(News.published_date.desc())\
            .limit(10)\
            .all()
        
        # Get technical indicators
        indicators = StockController.calculate_indicators(stock.id)
        
        # Get analyst recommendations (simulated)
        recommendations = {
            'buy': 8,
            'hold': 5,
            'sell': 2,
            'strong_buy': 4
        }
        
        return render_template('stock_details.html',
                             stock=stock,
                             price_history=price_history,
                             news=news,
                             indicators=indicators,
                             recommendations=recommendations)
                             
    except Exception as e:
        current_app.logger.error(f'Stock details error: {str(e)}')
        flash('Error loading stock details.', 'danger')
        return redirect(url_for('market.index'))


@stock_bp.route('/api/stock-data/<symbol>')
@login_required
@cache.cached(timeout=30)
def get_stock_data(symbol):
    """
    API endpoint for stock data.
    """
    try:
        symbol = symbol.upper()
        stock = Stock.query.filter_by(symbol=symbol).first()
        
        if not stock:
            return jsonify({'success': False, 'error': 'Stock not found.'})
        
        data = stock.to_dict(include_prices=True)
        
        # Add additional data
        data['indicators'] = StockController.calculate_indicators(stock.id)
        data['news'] = [n.to_dict() for n in News.query.filter_by(stock_id=stock.id)
                       .order_by(News.published_date.desc()).limit(5).all()]
        
        return jsonify({
            'success': True,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f'Stock API error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})


@stock_bp.route('/search')
@login_required
def search():
    """
    Search for stocks.
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'success': False, 'error': 'Search query required.'})
    
    try:
        # Search in database
        stocks = Stock.query.filter(
            (Stock.symbol.ilike(f'%{query}%')) |
            (Stock.company_name.ilike(f'%{query}%'))
        ).limit(10).all()
        
        results = [stock.to_dict() for stock in stocks]
        
        # If no results, try API search
        if not results:
            api_results = StockController.search_stocks(query)
            if api_results:
                results = api_results
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        current_app.logger.error(f'Stock search error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})