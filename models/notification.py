"""
Notification model for user alerts and messages.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app import db


class Notification(db.Model):
    """Notification model for user alerts"""
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    link = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship('User', back_populates='notifications')
    
    def __init__(self, user_id, title, message, **kwargs):
        """
        Initialize a new notification.
        
        Args:
            user_id: ID of the user
            title: Notification title
            message: Notification message
        """
        self.user_id = user_id
        self.title = title
        self.message = message
        super().__init__(**kwargs)
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
    
    def to_dict(self):
        """
        Convert notification object to dictionary.
        
        Returns:
            dict: Notification data
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'link': self.link,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Notification {self.id} - {self.title[:30]}>'