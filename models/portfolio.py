"""
Portfolio model for user stock holdings.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Date, Text, DateTime
from sqlalchemy.orm import relationship

from app import db


class Portfolio(db.Model):
    """User portfolio model"""
    __tablename__ = 'portfolio'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    quantity = Column(DECIMAL(15, 4), nullable=False)
    buy_price = Column(DECIMAL(15, 4), nullable=False)
    buy_date = Column(Date, nullable=False)
    current_price = Column(DECIMAL(15, 4))
    investment = Column(DECIMAL(15, 4))
    current_value = Column(DECIMAL(15, 4))
    profit_loss = Column(DECIMAL(15, 4))
    profit_loss_percentage = Column(DECIMAL(10, 2))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='portfolio')
    stock = relationship('Stock', back_populates='portfolio')
    
    def __init__(self, user_id, stock_id, quantity, buy_price, buy_date, **kwargs):
        """
        Initialize a new portfolio entry.
        
        Args:
            user_id: ID of the user
            stock_id: ID of the stock
            quantity: Number of shares
            buy_price: Purchase price per share
            buy_date: Purchase date
        """
        self.user_id = user_id
        self.stock_id = stock_id
        self.quantity = quantity
        self.buy_price = buy_price
        self.buy_date = buy_date
        self.update_values()
        super().__init__(**kwargs)
    
    def update_values(self):
        """Update calculated values based on current price"""
        # Get current price from stock
        current_price = self.stock.get_current_price() if self.stock else self.buy_price
        
        if current_price:
            self.current_price = current_price
            self.current_value = self.quantity * current_price
        else:
            self.current_price = self.buy_price
            self.current_value = self.quantity * self.buy_price
        
        self.investment = self.quantity * self.buy_price
        self.profit_loss = self.current_value - self.investment
        
        if self.investment and self.investment > 0:
            self.profit_loss_percentage = (self.profit_loss / self.investment) * 100
        else:
            self.profit_loss_percentage = 0
    
    def to_dict(self):
        """
        Convert portfolio object to dictionary.
        
        Returns:
            dict: Portfolio data
        """
        self.update_values()
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'stock_id': self.stock_id,
            'stock_symbol': self.stock.symbol if self.stock else None,
            'stock_name': self.stock.company_name if self.stock else None,
            'quantity': float(self.quantity),
            'buy_price': float(self.buy_price),
            'buy_date': self.buy_date.isoformat() if self.buy_date else None,
            'current_price': float(self.current_price) if self.current_price else None,
            'investment': float(self.investment) if self.investment else 0,
            'current_value': float(self.current_value) if self.current_value else 0,
            'profit_loss': float(self.profit_loss) if self.profit_loss else 0,
            'profit_loss_percentage': float(self.profit_loss_percentage) if self.profit_loss_percentage else 0,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Portfolio {self.user_id} - {self.stock_id}>'