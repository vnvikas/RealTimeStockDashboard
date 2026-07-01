"""
News API service for fetching financial news.
"""

import requests
from datetime import datetime, timedelta
from flask import current_app


class NewsService:
    """
    Service for fetching news from APIs.
    """
    
    @staticmethod
    def get_news(symbol=None, category='all', limit=20):
        """
        Get financial news.
        
        Args:
            symbol: Stock symbol (optional)
            category: News category
            limit: Number of news items
            
        Returns:
            list: News items
        """
        # Try Alpha Vantage
        try:
            api_key = current_app.config.get('STOCK_API_KEY')
            if api_key and api_key != 'YOUR_ALPHA_VANTAGE_API_KEY':
                return NewsService._get_news_alphavantage(symbol, limit)
        except Exception as e:
            current_app.logger.error(f'Alpha Vantage news error: {str(e)}')
        
        # Try Finnhub
        try:
            api_key = current_app.config.get('FINNHUB_API_KEY')
            if api_key and api_key != 'YOUR_FINNHUB_API_KEY':
                return NewsService._get_news_finnhub(symbol, limit)
        except Exception as e:
            current_app.logger.error(f'Finnhub news error: {str(e)}')
        
        # Return sample news if APIs fail
        return NewsService._get_sample_news()
    
    @staticmethod
    def _get_news_alphavantage(symbol, limit):
        """
        Get news from Alpha Vantage API.
        """
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'NEWS_SENTIMENT',
            'apikey': current_app.config.get('STOCK_API_KEY'),
            'limit': limit
        }
        
        if symbol:
            params['symbol'] = symbol
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'feed' in data:
            news = []
            for item in data['feed'][:limit]:
                news.append({
                    'id': item.get('url', ''),
                    'title': item.get('title', ''),
                    'description': item.get('summary', ''),
                    'content': item.get('summary', ''),
                    'source': item.get('source', ''),
                    'url': item.get('url', '#'),
                    'image_url': item.get('banner_image', ''),
                    'category': NewsService._categorize_news(item.get('title', '')),
                    'published_date': datetime.fromtimestamp(int(item.get('time_published', 0)) / 1000) if item.get('time_published') else datetime.utcnow()
                })
            return news
        
        return []
    
    @staticmethod
    def _get_news_finnhub(symbol, limit):
        """
        Get news from Finnhub API.
        """
        url = 'https://finnhub.io/api/v1/news'
        params = {
            'category': 'general',
            'token': current_app.config.get('FINNHUB_API_KEY')
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data:
            news = []
            for item in data[:limit]:
                news.append({
                    'id': item.get('id', ''),
                    'title': item.get('headline', ''),
                    'description': item.get('summary', ''),
                    'content': item.get('summary', ''),
                    'source': item.get('source', ''),
                    'url': item.get('url', '#'),
                    'image_url': item.get('image', ''),
                    'category': NewsService._categorize_news(item.get('headline', '')),
                    'published_date': datetime.fromtimestamp(item.get('datetime', 0)) if item.get('datetime') else datetime.utcnow()
                })
            return news
        
        return []
    
    @staticmethod
    def _categorize_news(title):
        """
        Categorize news based on title.
        
        Args:
            title: News title
            
        Returns:
            str: Category
        """
        title = title.lower()
        
        categories = {
            'technology': ['tech', 'software', 'apple', 'google', 'microsoft', 'amazon', 'meta', 'nvidia', 'ai', 'digital'],
            'crypto': ['bitcoin', 'ethereum', 'crypto', 'blockchain', 'coin', 'defi'],
            'business': ['business', 'economy', 'market', 'stock', 'investment', 'financial'],
            'healthcare': ['health', 'pharma', 'medical', 'biotech', 'covid', 'vaccine'],
            'energy': ['oil', 'gas', 'energy', 'solar', 'wind', 'renewable']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title for keyword in keywords):
                return category
        
        return 'general'
    
    @staticmethod
    def _get_sample_news():
        """
        Get sample news when API is not available.
        """
        return [
            {
                'id': '1',
                'title': 'Stock Market Update: Tech Stocks Rally',
                'description': 'Technology stocks led the market rally today with strong gains across the sector. Apple, Microsoft, and Google all reported positive results.',
                'content': 'Technology stocks led the market rally today with strong gains across the sector. Apple, Microsoft, and Google all reported positive results. The NASDAQ composite index rose 1.2% to close at 14,100.75.',
                'source': 'Reuters',
                'url': '#',
                'image_url': '',
                'category': 'technology',
                'published_date': datetime.now() - timedelta(hours=2)
            },
            {
                'id': '2',
                'title': 'Federal Reserve Signals Rate Decision',
                'description': 'The Federal Reserve indicated it may continue its current monetary policy stance, providing stability to financial markets.',
                'content': 'The Federal Reserve indicated it may continue its current monetary policy stance, providing stability to financial markets. The central bank\'s minutes show cautious optimism about the economic outlook.',
                'source': 'Bloomberg',
                'url': '#',
                'image_url': '',
                'category': 'business',
                'published_date': datetime.now() - timedelta(hours=5)
            },
            {
                'id': '3',
                'title': 'Bitcoin Surges Past $60,000',
                'description': 'Bitcoin price surged past $60,000 for the first time in months, driven by institutional adoption and positive market sentiment.',
                'content': 'Bitcoin price surged past $60,000 for the first time in months, driven by institutional adoption and positive market sentiment. Ethereum and other major cryptocurrencies also saw gains.',
                'source': 'CoinDesk',
                'url': '#',
                'image_url': '',
                'category': 'crypto',
                'published_date': datetime.now() - timedelta(hours=8)
            },
            {
                'id': '4',
                'title': 'Global Economy Shows Signs of Recovery',
                'description': 'Latest economic data suggests a gradual recovery in global markets, with improvements in manufacturing and employment indicators.',
                'content': 'Latest economic data suggests a gradual recovery in global markets, with improvements in manufacturing and employment indicators. The World Bank has revised its growth forecast upward.',
                'source': 'Financial Times',
                'url': '#',
                'image_url': '',
                'category': 'business',
                'published_date': datetime.now() - timedelta(hours=12)
            }
        ]
    
    @staticmethod
    def get_crypto_news(limit=10):
        """
        Get cryptocurrency news.
        
        Args:
            limit: Number of news items
            
        Returns:
            list: Crypto news
        """
        news = NewsService.get_news(limit=limit)
        return [n for n in news if n.get('category') == 'crypto']
    
    @staticmethod
    def get_market_news(limit=10):
        """
        Get market news.
        
        Args:
            limit: Number of news items
            
        Returns:
            list: Market news
        """
        news = NewsService.get_news(limit=limit)
        return [n for n in news if n.get('category') in ['business', 'general']]
    
    @staticmethod
    def get_stock_news(symbol, limit=10):
        """
        Get news for a specific stock.
        
        Args:
            symbol: Stock symbol
            limit: Number of news items
            
        Returns:
            list: Stock news
        """
        return NewsService.get_news(symbol=symbol, limit=limit)