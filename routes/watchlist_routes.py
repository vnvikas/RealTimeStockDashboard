"""
Watchlist routes for managing user watchlists.
"""

from flask import Blueprint, render_template, request, jsonify, flash, current_app
from flask_login import login_required, current_user

from app import db
from models.watchlist import Watchlist
from models.stock import Stock
from controllers.stock_controller import StockController

watchlist_bp = Blueprint('watchlist', __name__)


@watchlist_bp.route('/')
@login_required
def index():
    """
    Watchlist page.
    Displays user's watchlist stocks.
    """
    try:
        watchlist_entries = Watchlist.query.filter_by(user_id=current_user.id)\
            .order_by(Watchlist.is_favorite.desc(), Watchlist.added_date.desc()).all()
        
        return render_template('watchlist.html', watchlist_entries=watchlist_entries)
        
    except Exception as e:
        current_app.logger.error(f'Watchlist error: {str(e)}')
        flash('Error loading watchlist.', 'danger')
        return render_template('watchlist.html', watchlist_entries=[])


@watchlist_bp.route('/add', methods=['POST'])
@login_required
def add_stock():
    """
    Add stock to watchlist.
    """
    try:
        data = request.get_json()
        stock_symbol = data.get('symbol', '').strip().upper()
        notes = data.get('notes', '')
        price_alert = data.get('price_alert')
        
        if not stock_symbol:
            return jsonify({'success': False, 'error': 'Stock symbol is required.'})
        
        # Find or create stock
        stock = Stock.query.filter_by(symbol=stock_symbol).first()
        if not stock:
            stock = StockController.fetch_stock_info(stock_symbol)
            if not stock:
                return jsonify({'success': False, 'error': 'Stock not found.'})
            db.session.add(stock)
            db.session.flush()
        
        # Check if already in watchlist
        existing = Watchlist.query.filter_by(
            user_id=current_user.id,
            stock_id=stock.id
        ).first()
        
        if existing:
            return jsonify({'success': False, 'error': 'Stock already in watchlist.'})
        
        # Add to watchlist
        watchlist = Watchlist(
            user_id=current_user.id,
            stock_id=stock.id,
            notes=notes
        )
        
        if price_alert and float(price_alert) > 0:
            watchlist.price_alert = float(price_alert)
            watchlist.alert_enabled = True
        
        db.session.add(watchlist)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Stock added to watchlist.',
            'watchlist': watchlist.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Add watchlist error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})


@watchlist_bp.route('/remove/<int:watchlist_id>', methods=['DELETE'])
@login_required
def remove_stock(watchlist_id):
    """
    Remove stock from watchlist.
    """
    try:
        watchlist = Watchlist.query.get(watchlist_id)
        
        if not watchlist:
            return jsonify({'success': False, 'error': 'Watchlist entry not found.'})
        
        if watchlist.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized access.'})
        
        db.session.delete(watchlist)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Stock removed from watchlist.'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Remove watchlist error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})


@watchlist_bp.route('/favorite/<int:watchlist_id>', methods=['POST'])
@login_required
def toggle_favorite(watchlist_id):
    """
    Toggle favorite status for watchlist item.
    """
    try:
        watchlist = Watchlist.query.get(watchlist_id)
        
        if not watchlist:
            return jsonify({'success': False, 'error': 'Watchlist entry not found.'})
        
        if watchlist.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized access.'})
        
        watchlist.is_favorite = not watchlist.is_favorite
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Favorite status updated.',
            'is_favorite': watchlist.is_favorite
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Toggle favorite error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})


@watchlist_bp.route('/alert/<int:watchlist_id>', methods=['POST'])
@login_required
def update_price_alert(watchlist_id):
    """
    Update price alert for watchlist item.
    """
    try:
        data = request.get_json()
        watchlist = Watchlist.query.get(watchlist_id)
        
        if not watchlist:
            return jsonify({'success': False, 'error': 'Watchlist entry not found.'})
        
        if watchlist.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized access.'})
        
        price = data.get('price', 0)
        enabled = data.get('enabled', True)
        
        if price and float(price) > 0:
            watchlist.price_alert = float(price)
        else:
            watchlist.price_alert = None
        
        watchlist.alert_enabled = enabled
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Price alert updated.'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update price alert error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})