"""
Stock models for storing stock information and price history.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, BigInteger, Text, DateTime, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship

from app import db


class Stock(db.Model):
    """Stock model for company information"""
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(BigInteger)
    pe_ratio = Column(DECIMAL(10, 2))
    dividend_yield = Column(DECIMAL(10, 2))
    fifty_two_week_high = Column(DECIMAL(15, 2))
    fifty_two_week_low = Column(DECIMAL(15, 2))
    logo_url = Column(String(255))
    description = Column(Text)
    website = Column(String(255))
    ceo = Column(String(100))
    employees = Column(Integer)
    exchange = Column(String(50))
    currency = Column(String(10), default='USD')
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prices = relationship('StockPrice', back_populates='stock', cascade='all, delete-orphan')
    watchlist = relationship('Watchlist', back_populates='stock', cascade='all, delete-orphan')
    portfolio = relationship('Portfolio', back_populates='stock', cascade='all, delete-orphan')
    transactions = relationship('Transaction', back_populates='stock', cascade='all, delete-orphan')
    news = relationship('News', back_populates='stock', cascade='all, delete-orphan')
    
    def __init__(self, symbol, company_name, **kwargs):
        """
        Initialize a new stock.
        
        Args:
            symbol: Stock ticker symbol
            company_name: Full company name
        """
        self.symbol = symbol.upper()
        self.company_name = company_name
        super().__init__(**kwargs)
    
    def get_current_price(self):
        """
        Get the latest price for this stock.
        
        Returns:
            float: Current price or None
        """
        latest_price = StockPrice.query.filter_by(stock_id=self.id)\
            .order_by(StockPrice.date.desc())\
            .first()
        
        if latest_price:
            return latest_price.close
        return None
    
    def get_price_change(self, days=1):
        """
        Get price change over a specified number of days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            tuple: (change_amount, change_percentage)
        """
        prices = StockPrice.query.filter_by(stock_id=self.id)\
            .order_by(StockPrice.date.desc())\
            .limit(days + 1)\
            .all()
        
        if len(prices) < 2:
            return 0.0, 0.0
        
        current_price = prices[0].close
        previous_price = prices[-1].close
        
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100 if previous_price else 0
        
        return change, change_percent
    
    def get_historical_data(self, days=30):
        """
        Get historical price data.
        
        Args:
            days: Number of days of data
            
        Returns:
            list: List of price data dictionaries
        """
        prices = StockPrice.query.filter_by(stock_id=self.id)\
            .order_by(StockPrice.date.desc())\
            .limit(days)\
            .all()
        
        return [price.to_dict() for price in prices]
    
    def get_volume(self, days=30):
        """
        Get average volume over a period.
        
        Args:
            days: Number of days
            
        Returns:
            float: Average volume
        """
        prices = StockPrice.query.filter_by(stock_id=self.id)\
            .order_by(StockPrice.date.desc())\
            .limit(days)\
            .all()
        
        if not prices:
            return 0
        
        total_volume = sum(p.volume for p in prices if p.volume)
        return total_volume / len(prices)
    
    def to_dict(self, include_prices=False):
        """
        Convert stock object to dictionary.
        
        Args:
            include_prices: Whether to include price history
            
        Returns:
            dict: Stock data
        """
        data = {
            'id': self.id,
            'symbol': self.symbol,
            'company_name': self.company_name,
            'sector': self.sector,
            'industry': self.industry,
            'market_cap': float(self.market_cap) if self.market_cap else None,
            'pe_ratio': float(self.pe_ratio) if self.pe_ratio else None,
            'dividend_yield': float(self.dividend_yield) if self.dividend_yield else None,
            'fifty_two_week_high': float(self.fifty_two_week_high) if self.fifty_two_week_high else None,
            'fifty_two_week_low': float(self.fifty_two_week_low) if self.fifty_two_week_low else None,
            'logo_url': self.logo_url,
            'description': self.description,
            'website': self.website,
            'ceo': self.ceo,
            'employees': self.employees,
            'exchange': self.exchange,
            'currency': self.currency,
            'current_price': self.get_current_price(),
            'price_change': self.get_price_change()[0],
            'price_change_percent': self.get_price_change()[1],
            'volume': self.get_volume(),
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
        
        if include_prices:
            data['prices'] = self.get_historical_data(90)
        
        return data
    
    def __repr__(self):
        return f'<Stock {self.symbol}>'


class StockPrice(db.Model):
    """Stock price history model"""
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(DECIMAL(15, 4))
    high = Column(DECIMAL(15, 4))
    low = Column(DECIMAL(15, 4))
    close = Column(DECIMAL(15, 4))
    volume = Column(BigInteger)
    adj_close = Column(DECIMAL(15, 4))
    
    # Relationship
    stock = relationship('Stock', back_populates='prices')
    
    def __init__(self, stock_id, date, **kwargs):
        """
        Initialize a new stock price record.
        
        Args:
            stock_id: ID of the stock
            date: Date of the price
        """
        self.stock_id = stock_id
        self.date = date
        super().__init__(**kwargs)
    
    def to_dict(self):
        """
        Convert stock price object to dictionary.
        
        Returns:
            dict: Price data
        """
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'date': self.date.isoformat() if self.date else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume,
            'adj_close': float(self.adj_close) if self.adj_close else None
        }
    
    def __repr__(self):
        return f'<StockPrice {self.stock_id} {self.date}>'