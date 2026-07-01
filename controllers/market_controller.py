"""
Market controller for market overview and analysis.
"""

import requests
from datetime import datetime, timedelta
from flask import current_app

from app import db
from models.stock import Stock, StockPrice


class MarketController:
    """
    Controller for market operations.
    """
    
    @staticmethod
    def get_market_overview():
        """
        Get market overview summary.
        
        Returns:
            dict: Market overview data
        """
        # Calculate market statistics
        total_stocks = Stock.query.count()
        total_market_cap = db.session.query(db.func.sum(Stock.market_cap)).scalar() or 0
        
        # Get today's market movers
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get stocks with price data
        stocks = Stock.query.all()
        
        gainers = []
        losers = []
        
        for stock in stocks:
            price_change, price_change_percent = stock.get_price_change()
            current_price = stock.get_current_price()
            
            if current_price:
                if price_change > 0:
                    gainers.append({
                        'symbol': stock.symbol,
                        'name': stock.company_name,
                        'price': current_price,
                        'change': price_change,
                        'change_percent': price_change_percent
                    })
                elif price_change < 0:
                    losers.append({
                        'symbol': stock.symbol,
                        'name': stock.company_name,
                        'price': current_price,
                        'change': price_change,
                        'change_percent': price_change_percent
                    })
        
        # Sort by change percent
        gainers.sort(key=lambda x: x['change_percent'], reverse=True)
        losers.sort(key=lambda x: x['change_percent'])
        
        return {
            'total_stocks': total_stocks,
            'total_market_cap': float(total_market_cap),
            'top_gainers': gainers[:5],
            'top_losers': losers[:5],
            'market_status': 'Open' if MarketController._is_market_open() else 'Closed'
        }
    
    @staticmethod
    def get_top_gainers():
        """
        Get top gaining stocks.
        
        Returns:
            list: Top gainers
        """
        stocks = Stock.query.all()
        gainers = []
        
        for stock in stocks:
            price_change, price_change_percent = stock.get_price_change()
            current_price = stock.get_current_price()
            
            if current_price and price_change > 0:
                gainers.append({
                    'symbol': stock.symbol,
                    'name': stock.company_name,
                    'price': current_price,
                    'change': price_change,
                    'change_percent': price_change_percent
                })
        
        gainers.sort(key=lambda x: x['change_percent'], reverse=True)
        return gainers[:10]
    
    @staticmethod
    def get_top_losers():
        """
        Get top losing stocks.
        
        Returns:
            list: Top losers
        """
        stocks = Stock.query.all()
        losers = []
        
        for stock in stocks:
            price_change, price_change_percent = stock.get_price_change()
            current_price = stock.get_current_price()
            
            if current_price and price_change < 0:
                losers.append({
                    'symbol': stock.symbol,
                    'name': stock.company_name,
                    'price': current_price,
                    'change': price_change,
                    'change_percent': price_change_percent
                })
        
        losers.sort(key=lambda x: x['change_percent'])
        return losers[:10]
    
    @staticmethod
    def get_most_active_stocks():
        """
        Get most actively traded stocks.
        
        Returns:
            list: Most active stocks
        """
        stocks = Stock.query.all()
        active = []
        
        for stock in stocks:
            volume = stock.get_volume()
            if volume > 0:
                active.append({
                    'symbol': stock.symbol,
                    'name': stock.company_name,
                    'volume': int(volume),
                    'price': stock.get_current_price()
                })
        
        active.sort(key=lambda x: x['volume'], reverse=True)
        return active[:10]
    
    @staticmethod
    def get_indices_data():
        """
        Get major indices data.
        
        Returns:
            list: Indices data
        """
        # Try to fetch from API
        try:
            api_key = current_app.config.get('STOCK_API_KEY')
            if api_key and api_key != 'YOUR_ALPHA_VANTAGE_API_KEY':
                indices = MarketController._fetch_indices_alphavantage(api_key)
                if indices:
                    return indices
        except Exception as e:
            current_app.logger.error(f'Indices API error: {str(e)}')
        
        # Return sample data if API fails
        return [
            {'symbol': '^GSPC', 'name': 'S&P 500', 'price': 4500.50, 'change': 0.85},
            {'symbol': '^IXIC', 'name': 'NASDAQ', 'price': 14100.75, 'change': 1.20},
            {'symbol': '^DJI', 'name': 'Dow Jones', 'price': 35120.30, 'change': 0.45},
            {'symbol': '^FTSE', 'name': 'FTSE 100', 'price': 7500.20, 'change': -0.30}
        ]
    
    @staticmethod
    def _fetch_indices_alphavantage(api_key):
        """
        Fetch indices data from Alpha Vantage API.
        """
        indices = []
        index_symbols = ['^GSPC', '^IXIC', '^DJI']
        
        for symbol in index_symbols:
            try:
                url = 'https://www.alphavantage.co/query'
                params = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': symbol,
                    'apikey': api_key
                }
                
                response = requests.get(url, params=params, timeout=5)
                data = response.json()
                
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    indices.append({
                        'symbol': symbol,
                        'name': symbol,
                        'price': float(quote.get('05. price', 0)),
                        'change': float(quote.get('09. change', 0)),
                        'change_percent': float(quote.get('10. change percent', '0%').replace('%', ''))
                    })
            except Exception as e:
                current_app.logger.error(f'Error fetching {symbol}: {str(e)}')
        
        return indices
    
    @staticmethod
    def _is_market_open():
        """
        Check if market is currently open.
        
        Returns:
            bool: True if market is open
        """
        now = datetime.utcnow()
        # Market hours: 9:30 AM to 4:00 PM ET (14:00 to 20:00 UTC)
        # Monday to Friday
        is_weekday = now.weekday() < 5
        is_market_hours = 14 <= now.hour <= 20
        
        return is_weekday and is_market_hours
    
    @staticmethod
    def get_market_news(limit=10):
        """
        Get market news.
        
        Args:
            limit: Number of news items
            
        Returns:
            list: News items
        """
        # Try to fetch from API
        try:
            api_key = current_app.config.get('STOCK_API_KEY')
            if api_key and api_key != 'YOUR_ALPHA_VANTAGE_API_KEY':
                return MarketController._fetch_news_alphavantage(api_key, limit)
        except Exception as e:
            current_app.logger.error(f'News API error: {str(e)}')
        
        # Return sample news
        return [
            {
                'title': 'Market Update: Tech Stocks Rally',
                'description': 'Technology stocks led the market rally today with strong gains across the sector.',
                'source': 'Reuters',
                'published_date': datetime.now() - timedelta(hours=2),
                'url': '#'
            },
            {
                'title': 'Federal Reserve Signals Rate Decision',
                'description': 'The Federal Reserve indicated it may continue its current monetary policy stance.',
                'source': 'Bloomberg',
                'published_date': datetime.now() - timedelta(hours=5),
                'url': '#'
            }
        ]
    
    @staticmethod
    def _fetch_news_alphavantage(api_key, limit):
        """
        Fetch news from Alpha Vantage API.
        """
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'NEWS_SENTIMENT',
            'apikey': api_key,
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'feed' in data:
            news = []
            for item in data['feed'][:limit]:
                news.append({
                    'title': item.get('title', ''),
                    'description': item.get('summary', ''),
                    'source': item.get('source', ''),
                    'url': item.get('url', '#'),
                    'published_date': datetime.fromtimestamp(item.get('time_published', 0))
                })
            return news
        
        return []