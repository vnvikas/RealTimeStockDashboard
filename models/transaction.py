"""
Transaction model for buy/sell records.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship

from app import db


class Transaction(db.Model):
    """Transaction model for buy/sell records"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    transaction_type = Column(Enum('BUY', 'SELL'), nullable=False)
    quantity = Column(DECIMAL(15, 4), nullable=False)
    price = Column(DECIMAL(15, 4), nullable=False)
    total_amount = Column(DECIMAL(15, 4), nullable=False)
    commission = Column(DECIMAL(15, 4), default=0)
    transaction_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    user = relationship('User', back_populates='transactions')
    stock = relationship('Stock', back_populates='transactions')
    
    def __init__(self, user_id, stock_id, transaction_type, quantity, price, **kwargs):
        """
        Initialize a new transaction.
        
        Args:
            user_id: ID of the user
            stock_id: ID of the stock
            transaction_type: 'BUY' or 'SELL'
            quantity: Number of shares
            price: Price per share
        """
        self.user_id = user_id
        self.stock_id = stock_id
        self.transaction_type = transaction_type.upper()
        self.quantity = quantity
        self.price = price
        self.total_amount = quantity * price
        super().__init__(**kwargs)
    
    def to_dict(self):
        """
        Convert transaction object to dictionary.
        
        Returns:
            dict: Transaction data
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'stock_id': self.stock_id,
            'stock_symbol': self.stock.symbol if self.stock else None,
            'stock_name': self.stock.company_name if self.stock else None,
            'transaction_type': self.transaction_type,
            'quantity': float(self.quantity),
            'price': float(self.price),
            'total_amount': float(self.total_amount),
            'commission': float(self.commission) if self.commission else 0,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<Transaction {self.id} - {self.transaction_type}>'