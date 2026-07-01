"""
Portfolio routes for managing user stock holdings.
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func

from app import db
from models.portfolio import Portfolio
from models.stock import Stock
from models.transaction import Transaction
from controllers.stock_controller import StockController  # Add this import
from utils.validators import validate_positive_number

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/')
@login_required
def index():
    """
    Portfolio page.
    Displays user's stock holdings and performance.
    """
    try:
        portfolio_entries = Portfolio.query.filter_by(user_id=current_user.id).all()
        
        # Calculate portfolio summary
        total_investment = sum(p.investment or 0 for p in portfolio_entries)
        total_current_value = sum(p.current_value or 0 for p in portfolio_entries)
        total_profit_loss = total_current_value - total_investment
        
        profit_loss_percent = 0
        if total_investment > 0:
            profit_loss_percent = (total_profit_loss / total_investment) * 100
        
        return render_template('portfolio.html',
                             portfolio_entries=portfolio_entries,
                             total_investment=total_investment,
                             total_current_value=total_current_value,
                             total_profit_loss=total_profit_loss,
                             profit_loss_percent=profit_loss_percent)
                             
    except Exception as e:
        current_app.logger.error(f'Portfolio error: {str(e)}')
        flash('Error loading portfolio.', 'danger')
        return render_template('portfolio.html', portfolio_entries=[])


@portfolio_bp.route('/add', methods=['POST'])
@login_required
def add_stock():
    """
    Add stock to portfolio.
    """
    try:
        # Get form data
        stock_symbol = request.form.get('stock_symbol', '').strip().upper()
        quantity = request.form.get('quantity', 0)
        buy_price = request.form.get('buy_price', 0)
        buy_date = request.form.get('buy_date')
        notes = request.form.get('notes', '')
        
        # Validate inputs
        if not stock_symbol:
            return jsonify({'success': False, 'error': 'Stock symbol is required.'})
        
        try:
            quantity = float(quantity)
            buy_price = float(buy_price)
        except ValueError:
            return jsonify({'success': False, 'error': 'Quantity and price must be valid numbers.'})
        
        if quantity <= 0:
            return jsonify({'success': False, 'error': 'Quantity must be greater than 0.'})
        
        if buy_price <= 0:
            return jsonify({'success': False, 'error': 'Buy price must be greater than 0.'})
        
        # Find or create stock
        stock = Stock.query.filter_by(symbol=stock_symbol).first()
        if not stock:
            # Try to fetch stock info from API
            stock = StockController.fetch_stock_info(stock_symbol)
            if not stock:
                return jsonify({'success': False, 'error': 'Stock not found.'})
            db.session.add(stock)
            db.session.flush()
        
        # Check if stock already in portfolio
        existing = Portfolio.query.filter_by(
            user_id=current_user.id,
            stock_id=stock.id
        ).first()
        
        if existing:
            return jsonify({'success': False, 'error': 'Stock already in portfolio. Update existing entry instead.'})
        
        # Parse buy date
        try:
            buy_date = datetime.strptime(buy_date, '%Y-%m-%d').date() if buy_date else datetime.now().date()
        except ValueError:
            buy_date = datetime.now().date()
        
        # Create portfolio entry
        portfolio = Portfolio(
            user_id=current_user.id,
            stock_id=stock.id,
            quantity=quantity,
            buy_price=buy_price,
            buy_date=buy_date,
            notes=notes
        )
        
        # Update calculated values
        portfolio.update_values()
        
        # Create transaction record
        transaction = Transaction(
            user_id=current_user.id,
            stock_id=stock.id,
            transaction_type='BUY',
            quantity=quantity,
            price=buy_price,
            notes=f'Initial purchase - {notes}'
        )
        
        db.session.add(portfolio)
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Stock added to portfolio successfully.',
            'portfolio': portfolio.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Add portfolio error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})


@portfolio_bp.route('/update/<int:portfolio_id>', methods=['POST'])
@login_required
def update_stock(portfolio_id):
    """
    Update portfolio entry.
    """
    try:
        portfolio = Portfolio.query.get(portfolio_id)
        
        if not portfolio:
            return jsonify({'success': False, 'error': 'Portfolio entry not found.'})
        
        if portfolio.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized access.'})
        
        # Get form data
        quantity = request.form.get('quantity', portfolio.quantity)
        buy_price = request.form.get('buy_price', portfolio.buy_price)
        notes = request.form.get('notes', portfolio.notes)
        
        try:
            quantity = float(quantity)
            buy_price = float(buy_price)
        except ValueError:
            return jsonify({'success': False, 'error': 'Quantity and price must be valid numbers.'})
        
        if quantity <= 0:
            return jsonify({'success': False, 'error': 'Quantity must be greater than 0.'})
        
        if buy_price <= 0:
            return jsonify({'success': False, 'error': 'Buy price must be greater than 0.'})
        
        # Update portfolio
        portfolio.quantity = quantity
        portfolio.buy_price = buy_price
        portfolio.notes = notes
        portfolio.update_values()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Portfolio updated successfully.',
            'portfolio': portfolio.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Update portfolio error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})


@portfolio_bp.route('/delete/<int:portfolio_id>', methods=['DELETE'])
@login_required
def delete_stock(portfolio_id):
    """
    Remove stock from portfolio.
    """
    try:
        portfolio = Portfolio.query.get(portfolio_id)
        
        if not portfolio:
            return jsonify({'success': False, 'error': 'Portfolio entry not found.'})
        
        if portfolio.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized access.'})
        
        db.session.delete(portfolio)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Stock removed from portfolio successfully.'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Delete portfolio error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})


@portfolio_bp.route('/api/portfolio-data')
@login_required
def get_portfolio_data():
    """
    API endpoint for portfolio data.
    """
    try:
        portfolio_entries = Portfolio.query.filter_by(user_id=current_user.id).all()
        
        data = {
            'entries': [p.to_dict() for p in portfolio_entries],
            'summary': {
                'total_investment': sum(p.investment or 0 for p in portfolio_entries),
                'total_current_value': sum(p.current_value or 0 for p in portfolio_entries),
                'total_profit_loss': sum(p.profit_loss or 0 for p in portfolio_entries),
                'total_stocks': len(portfolio_entries)
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        current_app.logger.error(f'Portfolio API error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})