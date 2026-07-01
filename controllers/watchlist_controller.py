"""
Watchlist controller for watchlist management logic.
"""

from flask import current_app

from app import db
from models.watchlist import Watchlist
from models.stock import Stock
from controllers.stock_controller import StockController


class WatchlistController:
    """
    Controller for watchlist operations.
    """
    
    @staticmethod
    def get_watchlist(user_id):
        """
        Get user's watchlist.
        
        Args:
            user_id: User ID
            
        Returns:
            list: Watchlist entries
        """
        entries = Watchlist.query.filter_by(user_id=user_id)\
            .order_by(Watchlist.is_favorite.desc(), Watchlist.added_date.desc()).all()
        
        return [entry.to_dict() for entry in entries]
    
    @staticmethod
    def add_stock(user_id, symbol, notes='', price_alert=None):
        """
        Add stock to watchlist.
        
        Args:
            user_id: User ID
            symbol: Stock symbol
            notes: Notes
            price_alert: Price alert threshold
            
        Returns:
            tuple: (success, message, watchlist_entry)
        """
        symbol = symbol.upper()
        
        # Find or create stock
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            stock = StockController.fetch_stock_info(symbol)
            if not stock:
                return False, 'Stock not found.', None
            db.session.add(stock)
            db.session.flush()
        
        # Check if already in watchlist
        existing = Watchlist.query.filter_by(
            user_id=user_id,
            stock_id=stock.id
        ).first()
        
        if existing:
            return False, 'Stock already in watchlist.', None
        
        try:
            watchlist = Watchlist(
                user_id=user_id,
                stock_id=stock.id,
                notes=notes
            )
            
            if price_alert and price_alert > 0:
                watchlist.price_alert = price_alert
                watchlist.alert_enabled = True
            
            db.session.add(watchlist)
            db.session.commit()
            
            return True, 'Stock added to watchlist.', watchlist
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Add watchlist error: {str(e)}')
            return False, str(e), None
    
    @staticmethod
    def remove_stock(watchlist_id, user_id):
        """
        Remove stock from watchlist.
        
        Args:
            watchlist_id: Watchlist entry ID
            user_id: User ID
            
        Returns:
            tuple: (success, message)
        """
        watchlist = Watchlist.query.get(watchlist_id)
        
        if not watchlist:
            return False, 'Watchlist entry not found.'
        
        if watchlist.user_id != user_id:
            return False, 'Unauthorized access.'
        
        try:
            db.session.delete(watchlist)
            db.session.commit()
            return True, 'Stock removed from watchlist.'
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Remove watchlist error: {str(e)}')
            return False, str(e)
    
    @staticmethod
    def toggle_favorite(watchlist_id, user_id):
        """
        Toggle favorite status.
        
        Args:
            watchlist_id: Watchlist entry ID
            user_id: User ID
            
        Returns:
            tuple: (success, message, is_favorite)
        """
        watchlist = Watchlist.query.get(watchlist_id)
        
        if not watchlist:
            return False, 'Watchlist entry not found.', None
        
        if watchlist.user_id != user_id:
            return False, 'Unauthorized access.', None
        
        try:
            watchlist.is_favorite = not watchlist.is_favorite
            db.session.commit()
            return True, 'Favorite status updated.', watchlist.is_favorite
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Toggle favorite error: {str(e)}')
            return False, str(e), None
    
    @staticmethod
    def update_price_alert(watchlist_id, user_id, price_alert, enabled=True):
        """
        Update price alert.
        
        Args:
            watchlist_id: Watchlist entry ID
            user_id: User ID
            price_alert: Price alert threshold
            enabled: Enable/disable alert
            
        Returns:
            tuple: (success, message)
        """
        watchlist = Watchlist.query.get(watchlist_id)
        
        if not watchlist:
            return False, 'Watchlist entry not found.'
        
        if watchlist.user_id != user_id:
            return False, 'Unauthorized access.'
        
        try:
            watchlist.price_alert = price_alert if price_alert > 0 else None
            watchlist.alert_enabled = enabled
            db.session.commit()
            return True, 'Price alert updated.'
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Update price alert error: {str(e)}')
            return False, str(e)
    
    @staticmethod
    def check_price_alerts():
        """
        Check and trigger price alerts.
        
        Returns:
            list: Alerts triggered
        """
        triggered = []
        
        try:
            watchlist_entries = Watchlist.query.filter_by(alert_enabled=True).all()
            
            for entry in watchlist_entries:
                if entry.stock:
                    current_price = entry.stock.get_current_price()
                    if current_price and entry.price_alert:
                        # Check if price crossed threshold
                        if current_price >= entry.price_alert:
                            triggered.append({
                                'user_id': entry.user_id,
                                'symbol': entry.stock.symbol,
                                'current_price': current_price,
                                'alert_price': entry.price_alert
                            })
            
            return triggered
            
        except Exception as e:
            current_app.logger.error(f'Check price alerts error: {str(e)}')
            return []