"""
Decorator utility functions.
"""

from functools import wraps
from flask import flash, redirect, url_for, abort, session
from flask_login import current_user
from datetime import datetime


def login_required(f):
    """
    Decorator to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin privileges.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(limit=10, period=60):
    """
    Decorator for rate limiting.
    
    Args:
        limit: Maximum requests allowed
        period: Time period in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple implementation using session
            key = f'rate_limit_{f.__name__}'
            
            if key not in session:
                session[key] = {'count': 0, 'reset': datetime.utcnow().timestamp() + period}
            
            data = session[key]
            now = datetime.utcnow().timestamp()
            
            if now > data['reset']:
                data['count'] = 0
                data['reset'] = now + period
            
            if data['count'] >= limit:
                flash('Too many requests. Please try again later.', 'danger')
                return redirect(url_for('dashboard.index'))
            
            data['count'] += 1
            session[key] = data
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def cache_control(max_age=300):
    """
    Decorator to set cache control headers.
    
    Args:
        max_age: Cache max age in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            response.cache_control.max_age = max_age
            response.cache_control.public = True
            return response
        return decorated_function
    return decorator


def timeit(f):
    """
    Decorator to log function execution time.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start = datetime.utcnow()
        result = f(*args, **kwargs)
        end = datetime.utcnow()
        duration = (end - start).total_seconds()
        
        from flask import current_app
        current_app.logger.debug(f'Function {f.__name__} took {duration:.3f}s')
        
        return result
    return decorated_function