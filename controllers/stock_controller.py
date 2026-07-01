"""
Stock controller for stock-related business logic.
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import current_app
from sqlalchemy import desc

from app import db
from models.stock import Stock, StockPrice


class StockController:
    """
    Controller for stock operations including fetching data from APIs
    and calculating technical indicators.
    """
    
    @staticmethod
    def fetch_stock_info(symbol):
        """
        Fetch stock information from API.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Stock object or None
        """
        symbol = symbol.upper()
        
        # Try to get from database first
        stock = Stock.query.filter_by(symbol=symbol).first()
        if stock:
            return stock
        
        # Try Alpha Vantage API
        try:
            api_key = current_app.config.get('STOCK_API_KEY')
            if api_key and api_key != 'YOUR_ALPHA_VANTAGE_API_KEY':
                return StockController._fetch_from_alphavantage(symbol, api_key)
        except Exception as e:
            current_app.logger.error(f'Alpha Vantage error: {str(e)}')
        
        # Try Finnhub API
        try:
            api_key = current_app.config.get('FINNHUB_API_KEY')
            if api_key and api_key != 'YOUR_FINNHUB_API_KEY':
                return StockController._fetch_from_finnhub(symbol, api_key)
        except Exception as e:
            current_app.logger.error(f'Finnhub error: {str(e)}')
        
        # Try Twelve Data API
        try:
            api_key = current_app.config.get('TWELVEDATA_API_KEY')
            if api_key and api_key != 'YOUR_TWELVEDATA_API_KEY':
                return StockController._fetch_from_twelvedata(symbol, api_key)
        except Exception as e:
            current_app.logger.error(f'Twelve Data error: {str(e)}')
        
        # If all APIs fail, create a basic stock record
        return StockController._create_basic_stock(symbol)
    
    @staticmethod
    def _fetch_from_alphavantage(symbol, api_key):
        """
        Fetch stock info from Alpha Vantage API.
        """
        url = f'https://www.alphavantage.co/query'
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Global Quote' in data:
            quote = data['Global Quote']
            stock = Stock(
                symbol=symbol,
                company_name=symbol,
                last_updated=datetime.utcnow()
            )
            return stock
        
        # Try to get company overview
        params['function'] = 'OVERVIEW'
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Symbol' in data:
            stock = Stock(
                symbol=data.get('Symbol', symbol),
                company_name=data.get('Name', symbol),
                sector=data.get('Sector'),
                industry=data.get('Industry'),
                market_cap=data.get('MarketCapitalization'),
                pe_ratio=data.get('PERatio'),
                dividend_yield=data.get('DividendYield'),
                fifty_two_week_high=data.get('52WeekHigh'),
                fifty_two_week_low=data.get('52WeekLow'),
                description=data.get('Description'),
                exchange=data.get('Exchange'),
                last_updated=datetime.utcnow()
            )
            return stock
        
        return None
    
    @staticmethod
    def _fetch_from_finnhub(symbol, api_key):
        """
        Fetch stock info from Finnhub API.
        """
        url = f'https://finnhub.io/api/v1/stock/profile2'
        params = {
            'symbol': symbol,
            'token': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'ticker' in data:
            stock = Stock(
                symbol=data.get('ticker', symbol),
                company_name=data.get('name', symbol),
                sector=data.get('finnhubIndustry'),
                logo_url=data.get('logo'),
                exchange=data.get('exchange'),
                last_updated=datetime.utcnow()
            )
            return stock
        
        return None
    
    @staticmethod
    def _fetch_from_twelvedata(symbol, api_key):
        """
        Fetch stock info from Twelve Data API.
        """
        url = f'https://api.twelvedata.com/stocks'
        params = {
            'symbol': symbol,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'data' in data and data['data']:
            info = data['data'][0]
            stock = Stock(
                symbol=info.get('symbol', symbol),
                company_name=info.get('name', symbol),
                exchange=info.get('exchange'),
                last_updated=datetime.utcnow()
            )
            return stock
        
        return None
    
    @staticmethod
    def _create_basic_stock(symbol):
        """
        Create a basic stock record when API is not available.
        """
        stock = Stock(
            symbol=symbol,
            company_name=symbol,
            last_updated=datetime.utcnow()
        )
        return stock
    
    @staticmethod
    def fetch_price_history(symbol, days=90):
        """
        Fetch price history from API.
        
        Args:
            symbol: Stock ticker symbol
            days: Number of days of history
            
        Returns:
            list: Price history data
        """
        symbol = symbol.upper()
        
        # Try yfinance first
        try:
            import yfinance as yf
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if not hist.empty:
                prices = []
                for date, row in hist.iterrows():
                    prices.append({
                        'date': date.date(),
                        'open': row['Open'],
                        'high': row['High'],
                        'low': row['Low'],
                        'close': row['Close'],
                        'volume': row['Volume'],
                        'adj_close': row.get('Adj Close', row['Close'])
                    })
                return prices
        except Exception as e:
            current_app.logger.error(f'yfinance error: {str(e)}')
        
        # Try Alpha Vantage
        try:
            api_key = current_app.config.get('STOCK_API_KEY')
            if api_key and api_key != 'YOUR_ALPHA_VANTAGE_API_KEY':
                url = 'https://www.alphavantage.co/query'
                params = {
                    'function': 'TIME_SERIES_DAILY',
                    'symbol': symbol,
                    'apikey': api_key,
                    'outputsize': 'compact'
                }
                
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                if 'Time Series (Daily)' in data:
                    prices = []
                    for date, values in data['Time Series (Daily)'].items():
                        prices.append({
                            'date': datetime.strptime(date, '%Y-%m-%d').date(),
                            'open': float(values['1. open']),
                            'high': float(values['2. high']),
                            'low': float(values['3. low']),
                            'close': float(values['4. close']),
                            'volume': int(values['5. volume'])
                        })
                    
                    # Sort by date
                    prices.sort(key=lambda x: x['date'])
                    return prices[-days:]
        except Exception as e:
            current_app.logger.error(f'Alpha Vantage history error: {str(e)}')
        
        return []
    
    @staticmethod
    def calculate_indicators(stock_id):
        """
        Calculate technical indicators for a stock.
        
        Args:
            stock_id: Stock ID
            
        Returns:
            dict: Technical indicators
        """
        # Get price data
        prices = StockPrice.query.filter_by(stock_id=stock_id)\
            .order_by(StockPrice.date.desc())\
            .limit(100)\
            .all()
        
        if len(prices) < 20:
            return {
                'sma': None,
                'ema': None,
                'rsi': None,
                'macd': None,
                'bollinger_bands': None
            }
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'date': p.date,
            'close': float(p.close) if p.close else 0,
            'high': float(p.high) if p.high else 0,
            'low': float(p.low) if p.low else 0,
            'volume': p.volume or 0
        } for p in prices])
        
        df = df.sort_values('date')
        
        # Calculate indicators
        indicators = {}
        
        # Simple Moving Average (20-day)
        if len(df) >= 20:
            indicators['sma'] = float(df['close'].rolling(window=20).mean().iloc[-1])
        
        # Exponential Moving Average (12-day)
        if len(df) >= 12:
            indicators['ema'] = float(df['close'].ewm(span=12, adjust=False).mean().iloc[-1])
        
        # RSI (14-day)
        if len(df) >= 14:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi'] = float(rsi.iloc[-1])
        
        # MACD
        if len(df) >= 26:
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            indicators['macd'] = {
                'macd': float(macd.iloc[-1]),
                'signal': float(signal.iloc[-1]),
                'histogram': float((macd - signal).iloc[-1])
            }
        
        # Bollinger Bands
        if len(df) >= 20:
            sma = df['close'].rolling(window=20).mean()
            std = df['close'].rolling(window=20).std()
            indicators['bollinger_bands'] = {
                'upper': float((sma + 2 * std).iloc[-1]),
                'middle': float(sma.iloc[-1]),
                'lower': float((sma - 2 * std).iloc[-1])
            }
        
        return indicators
    
    @staticmethod
    def search_stocks(query):
        """
        Search for stocks by symbol or name.
        
        Args:
            query: Search query
            
        Returns:
            list: List of matching stocks
        """
        query = query.upper()
        
        # Search in database
        stocks = Stock.query.filter(
            (Stock.symbol.ilike(f'%{query}%')) |
            (Stock.company_name.ilike(f'%{query}%'))
        ).limit(10).all()
        
        results = [stock.to_dict() for stock in stocks]
        
        # If no results and using Alpha Vantage, try API
        if not results:
            try:
                api_key = current_app.config.get('STOCK_API_KEY')
                if api_key and api_key != 'YOUR_ALPHA_VANTAGE_API_KEY':
                    url = 'https://www.alphavantage.co/query'
                    params = {
                        'function': 'SYMBOL_SEARCH',
                        'keywords': query,
                        'apikey': api_key
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    data = response.json()
                    
                    if 'bestMatches' in data:
                        for match in data['bestMatches'][:5]:
                            results.append({
                                'symbol': match.get('1. symbol', ''),
                                'company_name': match.get('2. name', ''),
                                'exchange': match.get('3. type', ''),
                                'currency': match.get('8. currency', 'USD')
                            })
            except Exception as e:
                current_app.logger.error(f'API search error: {str(e)}')
        
        return results