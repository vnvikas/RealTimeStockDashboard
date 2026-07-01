"""
News model for financial and stock news.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app import db


class News(db.Model):
    """News model for financial news"""
    __tablename__ = 'news'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text)
    source = Column(String(100))
    url = Column(String(500))
    image_url = Column(String(500))
    category = Column(String(50))
    published_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    stock = relationship('Stock', back_populates='news')
    
    def __init__(self, title, **kwargs):
        """
        Initialize a new news item.
        
        Args:
            title: News title
        """
        self.title = title
        super().__init__(**kwargs)
    
    def to_dict(self):
        """
        Convert news object to dictionary.
        
        Returns:
            dict: News data
        """
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'stock_symbol': self.stock.symbol if self.stock else None,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'source': self.source,
            'url': self.url,
            'image_url': self.image_url,
            'category': self.category,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<News {self.id} - {self.title[:30]}>'