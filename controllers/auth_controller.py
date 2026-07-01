"""
Authentication controller for user authentication logic.
"""

from datetime import datetime
from flask import current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from models.user import User
from models.profile import Profile
from models.login_history import LoginHistory
from models.settings import UserSettings
from utils.validators import validate_email, validate_password_strength, validate_username
from utils.helpers import get_client_ip, get_user_agent


class AuthController:
    """
    Controller for authentication operations.
    """
    
    @staticmethod
    def register_user(username, email, full_name, password, confirm_password, profile_picture=None, mobile=None):
        """
        Register a new user.
        
        Args:
            username: Username
            email: Email address
            full_name: Full name
            password: Password
            confirm_password: Password confirmation
            profile_picture: Profile picture file
            mobile: Mobile number
            
        Returns:
            tuple: (success, message, user)
        """
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
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if username exists
        if username and User.query.filter_by(username=username.lower()).first():
            errors.append('Username already taken.')
        
        # Check if email exists
        if email and User.query.filter_by(email=email.lower()).first():
            errors.append('Email already registered.')
        
        if errors:
            return False, errors, None
        
        try:
            # Create user
            user = User(
                username=username.lower(),
                email=email.lower(),
                password=password
            )
            
            db.session.add(user)
            db.session.flush()
            
            # Create profile
            profile = Profile(
                user_id=user.id,
                full_name=full_name,
                mobile_number=mobile
            )
            
            db.session.add(profile)
            
            # Create settings
            settings = UserSettings(user_id=user.id)
            db.session.add(settings)
            
            db.session.commit()
            
            return True, 'Registration successful!', user
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Registration error: {str(e)}')
            return False, ['An error occurred during registration.'], None
    
    @staticmethod
    def login_user(identifier, password, remember_me=False):
        """
        Login a user.
        
        Args:
            identifier: Username or email
            password: Password
            remember_me: Remember me flag
            
        Returns:
            tuple: (success, message, user)
        """
        if not identifier or not password:
            return False, 'Please enter both username/email and password.', None
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == identifier.lower()) | 
            (User.email == identifier.lower())
        ).first()
        
        if not user:
            return False, 'Invalid username/email or password.', None
        
        if not user.check_password(password):
            return False, 'Invalid username/email or password.', None
        
        if not user.is_active:
            return False, 'Your account has been deactivated. Please contact support.', None
        
        try:
            # Login user
            login_user(user, remember=remember_me)
            
            # Record login history
            login_history = LoginHistory(
                user_id=user.id,
                ip_address=get_client_ip(),
                user_agent=get_user_agent(),
                session_id=session.get('_id', None)
            )
            db.session.add(login_history)
            db.session.commit()
            
            return True, 'Login successful!', user
            
        except Exception as e:
            current_app.logger.error(f'Login error: {str(e)}')
            return False, 'An error occurred during login.', None
    
    @staticmethod
    def logout_user():
        """
        Logout a user.
        """
        try:
            # Update logout time
            session_id = session.get('_id', None)
            if session_id and current_user.is_authenticated:
                login_history = LoginHistory.query.filter_by(
                    user_id=current_user.id,
                    session_id=session_id,
                    logout_time=None
                ).order_by(LoginHistory.login_time.desc()).first()
                
                if login_history:
                    login_history.logout_time = datetime.utcnow()
                    db.session.commit()
            
            logout_user()
            session.clear()
            return True, 'Logged out successfully.'
            
        except Exception as e:
            current_app.logger.error(f'Logout error: {str(e)}')
            return False, 'An error occurred during logout.'
    
    @staticmethod
    def reset_password(email, new_password, confirm_password):
        """
        Reset user password.
        
        Args:
            email: User email
            new_password: New password
            confirm_password: Password confirmation
            
        Returns:
            tuple: (success, message)
        """
        if not email:
            return False, 'Email is required.'
        
        if not new_password:
            return False, 'Password is required.'
        
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            return False, message
        
        if new_password != confirm_password:
            return False, 'Passwords do not match.'
        
        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            return False, 'User not found.'
        
        try:
            user.set_password(new_password)
            db.session.commit()
            return True, 'Password reset successfully.'
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Password reset error: {str(e)}')
            return False, 'An error occurred while resetting password.'
    
    @staticmethod
    def change_password(user_id, current_password, new_password, confirm_password):
        """
        Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            confirm_password: Password confirmation
            
        Returns:
            tuple: (success, message)
        """
        user = User.query.get(user_id)
        if not user:
            return False, 'User not found.'
        
        if not user.check_password(current_password):
            return False, 'Current password is incorrect.'
        
        is_valid, message = validate_password_strength(new_password)
        if not is_valid:
            return False, message
        
        if new_password != confirm_password:
            return False, 'Passwords do not match.'
        
        try:
            user.set_password(new_password)
            db.session.commit()
            return True, 'Password changed successfully.'
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Password change error: {str(e)}')
            return False, 'An error occurred while changing password.'
    
    @staticmethod
    def update_profile(user_id, data):
        """
        Update user profile.
        
        Args:
            user_id: User ID
            data: Profile data dict
            
        Returns:
            tuple: (success, message)
        """
        user = User.query.get(user_id)
        if not user:
            return False, 'User not found.'
        
        try:
            # Update user
            if 'username' in data and data['username']:
                if data['username'] != user.username:
                    existing = User.query.filter_by(username=data['username'].lower()).first()
                    if existing and existing.id != user_id:
                        return False, 'Username already taken.'
                    user.username = data['username'].lower()
            
            if 'email' in data and data['email']:
                if data['email'] != user.email:
                    if not validate_email(data['email']):
                        return False, 'Invalid email address.'
                    existing = User.query.filter_by(email=data['email'].lower()).first()
                    if existing and existing.id != user_id:
                        return False, 'Email already registered.'
                    user.email = data['email'].lower()
            
            # Update profile
            if user.profile:
                if 'full_name' in data:
                    user.profile.full_name = data['full_name']
                if 'mobile_number' in data:
                    user.profile.mobile_number = data['mobile_number']
                if 'bio' in data:
                    user.profile.bio = data['bio']
                if 'date_of_birth' in data and data['date_of_birth']:
                    from datetime import datetime
                    user.profile.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                if 'address' in data:
                    user.profile.address = data['address']
                if 'city' in data:
                    user.profile.city = data['city']
                if 'country' in data:
                    user.profile.country = data['country']
                if 'timezone' in data:
                    user.profile.timezone = data['timezone']
            
            db.session.commit()
            return True, 'Profile updated successfully.'
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Profile update error: {str(e)}')
            return False, 'An error occurred while updating profile.'
    
    @staticmethod
    def delete_account(user_id, password):
        """
        Delete user account.
        
        Args:
            user_id: User ID
            password: Password confirmation
            
        Returns:
            tuple: (success, message)
        """
        user = User.query.get(user_id)
        if not user:
            return False, 'User not found.'
        
        if not user.check_password(password):
            return False, 'Incorrect password.'
        
        try:
            db.session.delete(user)
            db.session.commit()
            return True, 'Account deleted successfully.'
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Account deletion error: {str(e)}')
            return False, 'An error occurred while deleting account.'