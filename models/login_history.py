"""
Login History model for tracking user login activity.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app import db


class LoginHistory(db.Model):
    """Login history model for tracking user logins"""
    __tablename__ = 'login_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    login_time = Column(DateTime, default=datetime.utcnow)
    logout_time = Column(DateTime)
    session_id = Column(String(255))
    is_successful = Column(Boolean, default=True)
    
    # Relationship
    user = relationship('User', back_populates='login_history')
    
    def __init__(self, user_id, **kwargs):
        """
        Initialize a new login history record.
        
        Args:
            user_id: ID of the user
        """
        self.user_id = user_id
        super().__init__(**kwargs)
    
    def to_dict(self):
        """
        Convert login history object to dictionary.
        
        Returns:
            dict: Login history data
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'logout_time': self.logout_time.isoformat() if self.logout_time else None,
            'session_id': self.session_id,
            'is_successful': self.is_successful
        }
    
    def __repr__(self):
        return f'<LoginHistory {self.user_id} - {self.login_time}>'