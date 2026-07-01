"""
User model for authentication and user management.
"""

from flask import current_app
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager
from utils.validators import validate_password_strength


class User(UserMixin, db.Model):
    """User model for authentication and user information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    profile = relationship('Profile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    watchlist = relationship('Watchlist', back_populates='user', cascade='all, delete-orphan')
    portfolio = relationship('Portfolio', back_populates='user', cascade='all, delete-orphan')
    transactions = relationship('Transaction', back_populates='user', cascade='all, delete-orphan')
    notifications = relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    login_history = relationship('LoginHistory', back_populates='user', cascade='all, delete-orphan')
    settings = relationship('UserSettings', back_populates='user', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, **kwargs):
        """
        Initialize a new user.
        
        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password (will be hashed)
        """
        self.username = username.lower()
        self.email = email.lower()
        self.set_password(password)
        super().__init__(**kwargs)
    
    def set_password(self, password):
        """
        Set and hash the user's password.
        
        Args:
            password: Plain text password
        """
        # Validate password strength
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            raise ValueError(message)
        
        # Hash the password using pbkdf2:sha256
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """
        Check if the provided password matches the stored hash.
        
        Args:
            password: Plain text password to check
            
        Returns:
            bool: True if password matches, False otherwise
        """
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """
        Get the user's full name from their profile.
        
        Returns:
            str: Full name or username if profile doesn't exist
        """
        if self.profile and self.profile.full_name:
            return self.profile.full_name
        return self.username
    
    def get_profile_picture(self):
        """
        Get the user's profile picture URL.
        
        Returns:
            str: Profile picture URL or default
        """
        if self.profile and self.profile.profile_picture:
            return self.profile.profile_picture
        return 'default.png'
    
    def get_timezone(self):
        """
        Get the user's timezone from settings.
        
        Returns:
            str: Timezone string
        """
        if self.settings:
            return self.settings.timezone
        return 'UTC'
    
    def get_total_portfolio_value(self):
        """
        Calculate the total value of the user's portfolio.
        
        Returns:
            float: Total portfolio value
        """
        if not self.portfolio:
            return 0.0
        
        total = sum(float(p.current_value or 0) for p in self.portfolio)
        return total
    
    def get_total_investment(self):
        """
        Calculate the total investment amount.
        
        Returns:
            float: Total investment
        """
        if not self.portfolio:
            return 0.0
        
        total = sum(float(p.investment or 0) for p in self.portfolio)
        return total
    
    def get_total_profit_loss(self):
        """
        Calculate the total profit/loss.
        
        Returns:
            float: Total profit/loss
        """
        if not self.portfolio:
            return 0.0
        
        total = sum(float(p.profit_loss or 0) for p in self.portfolio)
        return total
    
    def get_watchlist_count(self):
        """
        Get the number of stocks in the user's watchlist.
        
        Returns:
            int: Number of stocks in watchlist
        """
        return len(self.watchlist) if self.watchlist else 0
    
    def get_unread_notifications_count(self):
        """
        Get the number of unread notifications.
        
        Returns:
            int: Number of unread notifications
        """
        if not self.notifications:
            return 0
        
        return sum(1 for n in self.notifications if not n.is_read)
    
    def to_dict(self):
        """
        Convert user object to dictionary.
        
        Returns:
            dict: User data
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.get_full_name(),
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'profile_picture': self.get_profile_picture(),
            'total_portfolio_value': self.get_total_portfolio_value(),
            'total_investment': self.get_total_investment(),
            'total_profit_loss': self.get_total_profit_loss(),
            'watchlist_count': self.get_watchlist_count()
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    """Load user by ID"""
    return User.query.get(int(user_id))