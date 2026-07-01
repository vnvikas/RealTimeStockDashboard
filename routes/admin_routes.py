"""
Admin routes for system administration.
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, desc

from app import db
from models.user import User
from models.profile import Profile
from models.portfolio import Portfolio
from models.watchlist import Watchlist
from models.transaction import Transaction
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """
    Admin dashboard.
    """
    try:
        # Get statistics
        stats = get_admin_stats()
        
        # Get recent users
        recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
        
        # Get recent transactions
        recent_transactions = Transaction.query\
            .order_by(Transaction.transaction_date.desc())\
            .limit(20)\
            .all()
        
        return render_template('admin/admin_dashboard.html',
                             stats=stats,
                             recent_users=recent_users,
                             recent_transactions=recent_transactions)
                             
    except Exception as e:
        current_app.logger.error(f'Admin dashboard error: {str(e)}')
        flash('Error loading admin dashboard.', 'danger')
        return render_template('admin/admin_dashboard.html')


def get_admin_stats():
    """
    Get admin statistics.
    """
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admin_users = User.query.filter_by(is_admin=True).count()
    
    total_portfolios = Portfolio.query.count()
    total_watchlist = Watchlist.query.count()
    total_transactions = Transaction.query.count()
    
    # Users registered in last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users = User.query.filter(User.created_at >= week_ago).count()
    
    # Calculate total portfolio value
    total_investment = db.session.query(func.sum(Portfolio.investment)).scalar() or 0
    total_value = db.session.query(func.sum(Portfolio.current_value)).scalar() or 0
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'new_users': new_users,
        'total_portfolios': total_portfolios,
        'total_watchlist': total_watchlist,
        'total_transactions': total_transactions,
        'total_investment': float(total_investment),
        'total_value': float(total_value)
    }


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """
    User management page.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        users_pagination = User.query.order_by(User.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('admin/admin_users.html', users=users_pagination)
        
    except Exception as e:
        current_app.logger.error(f'Admin users error: {str(e)}')
        flash('Error loading users.', 'danger')
        return render_template('admin/admin_users.html')


@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    """
    Toggle user active status.
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found.'})
        
        if user.id == current_user.id:
            return jsonify({'success': False, 'error': 'Cannot deactivate yourself.'})
        
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User status updated to {"active" if user.is_active else "inactive"}.'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Toggle user error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})


@admin_bp.route('/users/<int:user_id>/delete', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """
    Delete user account.
    """
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found.'})
        
        if user.id == current_user.id:
            return jsonify({'success': False, 'error': 'Cannot delete yourself.'})
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully.'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Delete user error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """
    Admin settings page.
    """
    if request.method == 'POST':
        try:
            # Update system settings (in a real app, store in database)
            settings = {
                'site_name': request.form.get('site_name'),
                'maintenance_mode': request.form.get('maintenance_mode') == 'on',
                'registration_enabled': request.form.get('registration_enabled') == 'on',
                'api_key': request.form.get('api_key'),
                'api_provider': request.form.get('api_provider')
            }
            
            flash('Settings updated successfully.', 'success')
            
        except Exception as e:
            current_app.logger.error(f'Admin settings error: {str(e)}')
            flash('Error updating settings.', 'danger')
    
    return render_template('admin/admin_settings.html')