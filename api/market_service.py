"""
Market API service for fetching market data.
"""

import requests
from datetime import datetime, timedelta
from flask import current_app
import yfinance as yf


class MarketService:
    """
    Service for fetching market data.
    """
    
    @staticmethod
    def get_indices():
        """
        Get major indices data.
        
        Returns:
            list: Indices data
        """
        indices = {
            '^GSPC': 'S&P 500',
            '^IXIC': 'NASDAQ',
            '^DJI': 'Dow Jones',
            '^FTSE': 'FTSE 100',
            '^N225': 'Nikkei 225',
            '^HSI': 'Hang Seng'
        }
        
        result = []
        
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info:
                    result.append({
                        'symbol': symbol,
                        'name': name,
                        'price': info.get('regularMarketPrice', 0),
                        'change': info.get('regularMarketChange', 0),
                        'change_percent': info.get('regularMarketChangePercent', 0),
                        'high': info.get('regularMarketDayHigh', 0),
                        'low': info.get('regularMarketDayLow', 0),
                        'volume': info.get('regularMarketVolume', 0),
                        'previous_close': info.get('regularMarketPreviousClose', 0)
                    })
            except Exception as e:
                current_app.logger.error(f'Error fetching {symbol}: {str(e)}')
                continue
        
        return result
    
    @staticmethod
    def get_market_status():
        """
        Get current market status.
        
        Returns:
            dict: Market status
        """
        now = datetime.utcnow()
        is_weekday = now.weekday() < 5
        is_market_hours = 14 <= now.hour <= 20  # 9:30 AM to 4:00 PM ET (approx)
        
        if is_weekday and is_market_hours:
            status = 'open'
            status_color = 'success'
            message = 'Market is currently open'
        elif is_weekday:
            status = 'closed'
            status_color = 'warning'
            message = 'Market is currently closed'
        else:
            status = 'closed'
            status_color = 'danger'
            message = 'Market is closed for the weekend'
        
        return {
            'status': status,
            'status_color': status_color,
            'message': message,
            'time': now.strftime('%Y-%m-%d %H:%M UTC'),
            'next_open': MarketService._get_next_market_open()
        }
    
    @staticmethod
    def _get_next_market_open():
        """
        Get next market open time.
        
        Returns:
            str: Next market open time
        """
        now = datetime.utcnow()
        
        # Find next weekday at 9:30 AM ET (13:30 UTC)
        days_ahead = 0
        while True:
            next_day = now + timedelta(days=days_ahead)
            if next_day.weekday() < 5:  # Monday to Friday
                next_open = next_day.replace(hour=13, minute=30, second=0, microsecond=0)
                if next_open > now:
                    return next_open.strftime('%Y-%m-%d %H:%M UTC')
            days_ahead += 1
    
    @staticmethod
    def get_top_movers(limit=5):
        """
        Get top moving stocks.
        
        Args:
            limit: Number of stocks
            
        Returns:
            dict: Top gainers and losers
        """
        # Sample data for demo
        gainers = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 175.50, 'change': 3.25, 'change_percent': 1.89},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corp.', 'price': 950.00, 'change': 45.20, 'change_percent': 5.00},
            {'symbol': 'META', 'name': 'Meta Platforms', 'price': 358.00, 'change': 12.50, 'change_percent': 3.62}
        ]
        
        losers = [
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'price': 210.75, 'change': -8.25, 'change_percent': -3.77},
            {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'price': 485.00, 'change': -10.50, 'change_percent': -2.12},
            {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'price': 384.30, 'change': -5.70, 'change_percent': -1.46}
        ]
        
        return {
            'gainers': gainers[:limit],
            'losers': losers[:limit]
        }
    
    @staticmethod
    def get_market_movers():
        """
        Get market movers from yfinance.
        
        Returns:
            dict: Market movers
        """
        try:
            # Get S&P 500 components (simplified - use predefined list)
            sp500 = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX']
            
            movers = []
            for symbol in sp500:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    if info:
                        price = info.get('regularMarketPrice', 0)
                        prev_close = info.get('regularMarketPreviousClose', 1)
                        change = price - prev_close
                        change_percent = (change / prev_close) * 100 if prev_close else 0
                        
                        movers.append({
                            'symbol': symbol,
                            'name': info.get('shortName', symbol),
                            'price': price,
                            'change': change,
                            'change_percent': change_percent
                        })
                except Exception as e:
                    continue
            
            # Sort by change percent
            gainers = sorted([m for m in movers if m['change'] > 0], 
                           key=lambda x: x['change_percent'], reverse=True)
            losers = sorted([m for m in movers if m['change'] < 0], 
                          key=lambda x: x['change_percent'])
            
            return {
                'gainers': gainers[:5],
                'losers': losers[:5]
            }
            
        except Exception as e:
            current_app.logger.error(f'Market movers error: {str(e)}')
            return MarketService.get_top_movers()
    
    @staticmethod
    def get_crypto_markets():
        """
        Get cryptocurrency market data.
        
        Returns:
            list: Crypto market data
        """
        cryptos = [
            {'symbol': 'BTC-USD', 'name': 'Bitcoin'},
            {'symbol': 'ETH-USD', 'name': 'Ethereum'},
            {'symbol': 'SOL-USD', 'name': 'Solana'},
            {'symbol': 'ADA-USD', 'name': 'Cardano'},
            {'symbol': 'BNB-USD', 'name': 'BNB'}
        ]
        
        result = []
        
        for crypto in cryptos:
            try:
                ticker = yf.Ticker(crypto['symbol'])
                info = ticker.info
                
                if info:
                    result.append({
                        'symbol': crypto['symbol'].replace('-USD', ''),
                        'name': crypto['name'],
                        'price': info.get('regularMarketPrice', 0),
                        'change': info.get('regularMarketChange', 0),
                        'change_percent': info.get('regularMarketChangePercent', 0),
                        'market_cap': info.get('marketCap', 0),
                        'volume': info.get('regularMarketVolume', 0)
                    })
            except Exception as e:
                current_app.logger.error(f'Error fetching {crypto["symbol"]}: {str(e)}')
                continue
        
        return result
    
    @staticmethod
    def get_economic_events():
        """
        Get upcoming economic events.
        
        Returns:
            list: Economic events
        """
        # Sample economic events
        events = [
            {
                'title': 'Federal Reserve Interest Rate Decision',
                'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                'time': '14:00',
                'impact': 'High',
                'forecast': '5.50%',
                'previous': '5.50%'
            },
            {
                'title': 'US Unemployment Claims',
                'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'time': '08:30',
                'impact': 'Medium',
                'forecast': '220K',
                'previous': '215K'
            },
            {
                'title': 'Consumer Price Index (CPI)',
                'date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
                'time': '08:30',
                'impact': 'High',
                'forecast': '3.2%',
                'previous': '3.0%'
            },
            {
                'title': 'GDP Growth Rate',
                'date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
                'time': '08:30',
                'impact': 'High',
                'forecast': '2.5%',
                'previous': '2.1%'
            }
        ]
        
        return events