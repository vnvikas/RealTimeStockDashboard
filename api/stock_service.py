"""
Stock API service for fetching stock data from various providers.
"""

import requests
import time
from datetime import datetime, timedelta
from flask import current_app
import pandas as pd
import yfinance as yf


class StockService:
    """
    Service for fetching stock data from APIs.
    """
    
    @staticmethod
    def get_quote(symbol):
        """
        Get real-time stock quote.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            dict: Stock quote data
        """
        symbol = symbol.upper()
        
        # Try yfinance first (free and reliable)
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if info:
                return {
                    'symbol': symbol,
                    'name': info.get('shortName', symbol),
                    'price': info.get('regularMarketPrice', 0),
                    'change': info.get('regularMarketChange', 0),
                    'change_percent': info.get('regularMarketChangePercent', 0),
                    'open': info.get('regularMarketOpen', 0),
                    'high': info.get('regularMarketDayHigh', 0),
                    'low': info.get('regularMarketDayLow', 0),
                    'volume': info.get('regularMarketVolume', 0),
                    'previous_close': info.get('regularMarketPreviousClose', 0),
                    'market_cap': info.get('marketCap', 0),
                    'pe_ratio': info.get('trailingPE', 0),
                    'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                    'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                    'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            current_app.logger.error(f'yfinance quote error for {symbol}: {str(e)}')
        
        # Try Alpha Vantage as fallback
        try:
            api_key = current_app.config.get('STOCK_API_KEY')
            if api_key and api_key != 'YOUR_ALPHA_VANTAGE_API_KEY':
                return StockService._get_quote_alphavantage(symbol, api_key)
        except Exception as e:
            current_app.logger.error(f'Alpha Vantage quote error: {str(e)}')
        
        return None
    
    @staticmethod
    def _get_quote_alphavantage(symbol, api_key):
        """
        Get stock quote from Alpha Vantage API.
        """
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Global Quote' in data:
            quote = data['Global Quote']
            return {
                'symbol': quote.get('01. symbol', symbol),
                'name': quote.get('01. symbol', symbol),
                'price': float(quote.get('05. price', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': float(quote.get('10. change percent', '0%').replace('%', '')),
                'open': float(quote.get('02. open', 0)),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0)),
                'volume': int(quote.get('06. volume', 0)),
                'previous_close': float(quote.get('08. previous close', 0)),
                'timestamp': datetime.utcnow().isoformat()
            }
        
        return None
    
    @staticmethod
    def get_historical_data(symbol, period='1mo', interval='1d'):
        """
        Get historical stock data.
        
        Args:
            symbol: Stock ticker symbol
            period: Period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            list: Historical data
        """
        symbol = symbol.upper()
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if not hist.empty:
                data = []
                for date, row in hist.iterrows():
                    data.append({
                        'date': date.strftime('%Y-%m-%d %H:%M:%S'),
                        'open': float(row['Open']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'close': float(row['Close']),
                        'volume': int(row['Volume']),
                        'adj_close': float(row.get('Adj Close', row['Close']))
                    })
                return data
        except Exception as e:
            current_app.logger.error(f'yfinance historical error: {str(e)}')
        
        # Try Alpha Vantage as fallback
        try:
            api_key = current_app.config.get('STOCK_API_KEY')
            if api_key and api_key != 'YOUR_ALPHA_VANTAGE_API_KEY':
                return StockService._get_historical_alphavantage(symbol, period, api_key)
        except Exception as e:
            current_app.logger.error(f'Alpha Vantage historical error: {str(e)}')
        
        return []
    
    @staticmethod
    def _get_historical_alphavantage(symbol, period, api_key):
        """
        Get historical data from Alpha Vantage API.
        """
        # Map period to Alpha Vantage parameters
        period_map = {
            '1d': ('TIME_SERIES_INTRADAY', '5min'),
            '5d': ('TIME_SERIES_INTRADAY', '15min'),
            '1mo': ('TIME_SERIES_DAILY', None),
            '3mo': ('TIME_SERIES_DAILY', None),
            '6mo': ('TIME_SERIES_DAILY', None),
            '1y': ('TIME_SERIES_DAILY', None),
        }
        
        function, interval = period_map.get(period, ('TIME_SERIES_DAILY', None))
        
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': api_key,
            'outputsize': 'compact'
        }
        
        if interval:
            params['interval'] = interval
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # Different response structures for intraday vs daily
        if 'Time Series (Daily)' in data:
            time_series = data['Time Series (Daily)']
        elif f'Time Series ({interval})' in data:
            time_series = data[f'Time Series ({interval})']
        else:
            return []
        
        result = []
        for date_str, values in time_series.items():
            result.append({
                'date': date_str,
                'open': float(values.get('1. open', 0)),
                'high': float(values.get('2. high', 0)),
                'low': float(values.get('3. low', 0)),
                'close': float(values.get('4. close', 0)),
                'volume': int(values.get('5. volume', 0))
            })
        
        return sorted(result, key=lambda x: x['date'])
    
    @staticmethod
    def get_company_info(symbol):
        """
        Get company information.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            dict: Company information
        """
        symbol = symbol.upper()
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if info:
                return {
                    'symbol': symbol,
                    'name': info.get('shortName', symbol),
                    'long_name': info.get('longName', ''),
                    'sector': info.get('sector', ''),
                    'industry': info.get('industry', ''),
                    'market_cap': info.get('marketCap', 0),
                    'pe_ratio': info.get('trailingPE', 0),
                    'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                    'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                    'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                    'description': info.get('longBusinessSummary', ''),
                    'website': info.get('website', ''),
                    'ceo': info.get('companyOfficers', [{}])[0].get('name', '') if info.get('companyOfficers') else '',
                    'employees': info.get('fullTimeEmployees', 0),
                    'exchange': info.get('exchange', ''),
                    'currency': info.get('currency', 'USD'),
                    'logo_url': f'https://logo.clearbit.com/{info.get("website", "").replace("http://", "").replace("https://", "").split("/")[0]}'
                }
        except Exception as e:
            current_app.logger.error(f'yfinance company info error: {str(e)}')
        
        return None
    
    @staticmethod
    def search_stocks(query):
        """
        Search for stocks.
        
        Args:
            query: Search query
            
        Returns:
            list: Matching stocks
        """
        query = query.upper()
        
        try:
            # Use yfinance to search
            ticker = yf.Ticker(query)
            info = ticker.info
            
            if info and info.get('symbol'):
                return [{
                    'symbol': info.get('symbol', query),
                    'name': info.get('shortName', info.get('longName', query)),
                    'exchange': info.get('exchange', ''),
                    'currency': info.get('currency', 'USD')
                }]
        except Exception as e:
            current_app.logger.error(f'yfinance search error: {str(e)}')
        
        # Try Alpha Vantage
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
                    results = []
                    for match in data['bestMatches'][:10]:
                        results.append({
                            'symbol': match.get('1. symbol', ''),
                            'name': match.get('2. name', ''),
                            'exchange': match.get('3. type', ''),
                            'currency': match.get('8. currency', 'USD')
                        })
                    return results
        except Exception as e:
            current_app.logger.error(f'Alpha Vantage search error: {str(e)}')
        
        return []
    
    @staticmethod
    def get_multiple_quotes(symbols):
        """
        Get quotes for multiple stocks.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            dict: Quotes by symbol
        """
        result = {}
        
        for symbol in symbols:
            quote = StockService.get_quote(symbol)
            if quote:
                result[symbol] = quote
            time.sleep(0.2)  # Rate limiting
        
        return result
    
    @staticmethod
    def calculate_indicators(data):
        """
        Calculate technical indicators from price data.
        
        Args:
            data: List of price data
            
        Returns:
            dict: Technical indicators
        """
        if not data or len(data) < 20:
            return {}
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        indicators = {}
        
        # Simple Moving Average (20-day)
        if len(df) >= 20:
            indicators['sma_20'] = float(df['close'].rolling(window=20).mean().iloc[-1])
            indicators['sma_50'] = float(df['close'].rolling(window=50).mean().iloc[-1]) if len(df) >= 50 else None
        
        # Exponential Moving Average (12-day)
        if len(df) >= 12:
            indicators['ema_12'] = float(df['close'].ewm(span=12, adjust=False).mean().iloc[-1])
            indicators['ema_26'] = float(df['close'].ewm(span=26, adjust=False).mean().iloc[-1]) if len(df) >= 26 else None
        
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