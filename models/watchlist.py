"""
Watchlist model for user stock tracking.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Boolean, Text, DECIMAL, DateTime
from sqlalchemy.orm import relationship

from app import db


class Watchlist(db.Model):
    """User watchlist model"""
    __tablename__ = 'watchlist'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    is_favorite = Column(Boolean, default=False)
    notes = Column(Text)
    price_alert = Column(DECIMAL(15, 4))
    alert_enabled = Column(Boolean, default=False)
    added_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='watchlist')
    stock = relationship('Stock', back_populates='watchlist')
    
    def __init__(self, user_id, stock_id, **kwargs):
        """
        Initialize a new watchlist entry.
        
        Args:
            user_id: ID of the user
            stock_id: ID of the stock
        """
        self.user_id = user_id
        self.stock_id = stock_id
        super().__init__(**kwargs)
    
    def to_dict(self):
        """
        Convert watchlist object to dictionary.
        
        Returns:
            dict: Watchlist data
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'stock_id': self.stock_id,
            'stock_symbol': self.stock.symbol if self.stock else None,
            'stock_name': self.stock.company_name if self.stock else None,
            'is_favorite': self.is_favorite,
            'notes': self.notes,
            'price_alert': float(self.price_alert) if self.price_alert else None,
            'alert_enabled': self.alert_enabled,
            'added_date': self.added_date.isoformat() if self.added_date else None,
            'current_price': self.stock.get_current_price() if self.stock else None,
            'price_change': self.stock.get_price_change()[0] if self.stock else 0,
            'price_change_percent': self.stock.get_price_change()[1] if self.stock else 0
        }
    
    def __repr__(self):
        return f'<Watchlist {self.user_id} - {self.stock_id}>'