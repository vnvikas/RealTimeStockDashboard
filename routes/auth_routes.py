"""
Authentication routes for login, registration, and password management.
"""

import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from app import db
from models.user import User
from models.profile import Profile
from models.login_history import LoginHistory
from models.settings import UserSettings
from utils.validators import validate_email, validate_password_strength, validate_username
from utils.helpers import save_profile_picture, get_client_ip, get_user_agent

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration page.
    Handles both GET (display form) and POST (process registration).
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            full_name = request.form.get('full_name', '').strip()
            mobile = request.form.get('mobile', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validate inputs
            errors = []
            
            if not username:
                errors.append('Username is required.')
            elif not validate_username(username):
                errors.append('Username must be 3-50 characters and contain only letters, numbers, and underscores.')
            
            if not email:
                errors.append('Email is required.')
            elif not validate_email(email):
                errors.append('Please enter a valid email address.')
            
            if not full_name:
                errors.append('Full name is required.')
            
            if not password:
                errors.append('Password is required.')
            else:
                is_valid, message = validate_password_strength(password)
                if not is_valid:
                    errors.append(message)
            
            if password and password != confirm_password:
                errors.append('Passwords do not match.')
            
            # Check if username already exists
            if username and User.query.filter_by(username=username.lower()).first():
                errors.append('Username already taken.')
            
            # Check if email already exists
            if email and User.query.filter_by(email=email.lower()).first():
                errors.append('Email already registered.')
            
            # If there are errors, return to form
            if errors:
                for error in errors:
                    flash(error, 'danger')
                return render_template('register.html', 
                                     username=username, 
                                     email=email, 
                                     full_name=full_name,
                                     mobile=mobile)
            
            # Create new user
            user = User(
                username=username.lower(),
                email=email.lower(),
                password=password
            )
            
            # Add user first to get ID
            db.session.add(user)
            db.session.flush()  # This gets the user.id
            
            # Create profile
            profile = Profile(
                user_id=user.id,
                full_name=full_name,
                mobile_number=mobile
            )
            db.session.add(profile)
            
            # Create user settings
            settings = UserSettings(user_id=user.id)
            db.session.add(settings)
            
            # Handle profile picture upload
            profile_picture = None
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename:
                    filename = save_profile_picture(file, user.id)
                    if filename:
                        profile.profile_picture = filename
                        profile_picture = filename
            
            # Save to database
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Registration error: {str(e)}')
            flash('An unexpected error occurred. Please try again.', 'danger')
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login page.
    Handles both GET (display form) and POST (process login).
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        try:
            # Get form data
            identifier = request.form.get('identifier', '').strip()
            password = request.form.get('password', '')
            remember_me = request.form.get('remember_me', False)
            
            # Validate inputs
            if not identifier or not password:
                flash('Please enter both username/email and password.', 'danger')
                return render_template('login.html')
            
            # Find user by username or email
            user = User.query.filter(
                (User.username == identifier.lower()) | 
                (User.email == identifier.lower())
            ).first()
            
            # Check if user exists and password is correct
            if user and user.check_password(password):
                # Check if user is active
                if not user.is_active:
                    flash('Your account has been deactivated. Please contact support.', 'danger')
                    return render_template('login.html')
                
                # Login user
                login_user(user, remember=bool(remember_me))
                
                # Record login history
                login_history = LoginHistory(
                    user_id=user.id,
                    ip_address=get_client_ip(),
                    user_agent=get_user_agent(),
                    session_id=session.get('_id', None)
                )
                db.session.add(login_history)
                db.session.commit()
                
                flash(f'Welcome back, {user.get_full_name()}!', 'success')
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('dashboard.index'))
            else:
                flash('Invalid username/email or password.', 'danger')
                
        except Exception as e:
            current_app.logger.error(f'Login error: {str(e)}')
            flash('An error occurred during login. Please try again.', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout.
    Records logout time in login history.
    """
    try:
        # Update logout time for current session
        session_id = session.get('_id', None)
        if session_id:
            login_history = LoginHistory.query.filter_by(
                user_id=current_user.id,
                session_id=session_id,
                logout_time=None
            ).order_by(LoginHistory.login_time.desc()).first()
            
            if login_history:
                login_history.logout_time = datetime.utcnow()
                db.session.commit()
        
        # Logout user
        logout_user()
        session.clear()
        flash('You have been logged out successfully.', 'info')
        
    except Exception as e:
        current_app.logger.error(f'Logout error: {str(e)}')
    
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Forgot password page.
    Handles password reset requests.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email or not validate_email(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('forgot_password.html')
        
        # Find user by email
        user = User.query.filter_by(email=email.lower()).first()
        
        if user:
            # In a real application, send password reset email here
            # For demo purposes, we'll just show a message
            flash('Password reset instructions have been sent to your email.', 'success')
            
            # Store user ID in session for reset password
            session['reset_user_id'] = user.id
            return redirect(url_for('auth.reset_password'))
        else:
            flash('No account found with that email address.', 'danger')
    
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """
    Reset password page.
    Handles password reset.
    """
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # Check if user ID is in session
    user_id = session.get('reset_user_id')
    if not user_id:
        flash('Password reset session expired. Please try again.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate password
        if not password:
            flash('Password is required.', 'danger')
            return render_template('reset_password.html')
        
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            flash(message, 'danger')
            return render_template('reset_password.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html')
        
        try:
            # Update password
            user.set_password(password)
            db.session.commit()
            
            # Clear session
            session.pop('reset_user_id', None)
            
            flash('Password has been reset successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Password reset error: {str(e)}')
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('reset_password.html')


@auth_bp.route('/check-availability', methods=['POST'])
def check_availability():
    """
    Check if username or email is available.
    AJAX endpoint for registration form.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'available': True, 'error': 'No data provided'})
            
        field = data.get('field')
        value = data.get('value', '').strip()
        
        if field == 'username':
            exists = User.query.filter_by(username=value.lower()).first() is not None
            return jsonify({'available': not exists})
        elif field == 'email':
            exists = User.query.filter_by(email=value.lower()).first() is not None
            return jsonify({'available': not exists})
        
        return jsonify({'available': True})
        
    except Exception as e:
        current_app.logger.error(f'Availability check error: {str(e)}')
        return jsonify({'available': True, 'error': str(e)})