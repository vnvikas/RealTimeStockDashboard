"""
User Settings model for storing user preferences.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app import db


class UserSettings(db.Model):
    """User settings model for preferences"""
    __tablename__ = 'user_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    theme = Column(String(20), default='light')
    dark_mode = Column(Boolean, default=False)
    auto_refresh = Column(Boolean, default=True)
    refresh_interval = Column(Integer, default=30)
    email_notifications = Column(Boolean, default=True)
    price_alerts = Column(Boolean, default=True)
    news_notifications = Column(Boolean, default=True)
    language = Column(String(10), default='en')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship('User', back_populates='settings')
    
    def __init__(self, user_id, **kwargs):
        """
        Initialize new user settings.
        
        Args:
            user_id: ID of the user
        """
        self.user_id = user_id
        super().__init__(**kwargs)
    
    def to_dict(self):
        """
        Convert settings object to dictionary.
        
        Returns:
            dict: Settings data
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'theme': self.theme,
            'dark_mode': self.dark_mode,
            'auto_refresh': self.auto_refresh,
            'refresh_interval': self.refresh_interval,
            'email_notifications': self.email_notifications,
            'price_alerts': self.price_alerts,
            'news_notifications': self.news_notifications,
            'language': self.language,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def toggle_dark_mode(self):
        """Toggle dark mode setting"""
        self.dark_mode = not self.dark_mode
        self.theme = 'dark' if self.dark_mode else 'light'
    
    def __repr__(self):
        return f'<UserSettings {self.user_id}>'