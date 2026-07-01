"""
Portfolio controller for portfolio management logic.
"""

from datetime import datetime
from flask import current_app
from sqlalchemy import func

from app import db
from models.portfolio import Portfolio
from models.transaction import Transaction
from models.stock import Stock
from controllers.stock_controller import StockController


class PortfolioController:
    """
    Controller for portfolio operations.
    """
    
    @staticmethod
    def get_portfolio_summary(user_id):
        """
        Get portfolio summary for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Portfolio summary
        """
        entries = Portfolio.query.filter_by(user_id=user_id).all()
        
        if not entries:
            return {
                'total_investment': 0,
                'total_current_value': 0,
                'total_profit_loss': 0,
                'profit_loss_percent': 0,
                'total_stocks': 0,
                'stocks': []
            }
        
        total_investment = sum(float(p.investment or 0) for p in entries)
        total_current_value = sum(float(p.current_value or 0) for p in entries)
        total_profit_loss = total_current_value - total_investment
        
        profit_loss_percent = 0
        if total_investment > 0:
            profit_loss_percent = (total_profit_loss / total_investment) * 100
        
        stocks = []
        for entry in entries:
            entry.update_values()
            stocks.append(entry.to_dict())
        
        return {
            'total_investment': total_investment,
            'total_current_value': total_current_value,
            'total_profit_loss': total_profit_loss,
            'profit_loss_percent': profit_loss_percent,
            'total_stocks': len(entries),
            'stocks': stocks
        }
    
    @staticmethod
    def add_stock(user_id, symbol, quantity, buy_price, buy_date=None, notes=''):
        """
        Add stock to portfolio.
        
        Args:
            user_id: User ID
            symbol: Stock symbol
            quantity: Number of shares
            buy_price: Purchase price
            buy_date: Purchase date
            notes: Notes
            
        Returns:
            tuple: (success, message, portfolio_entry)
        """
        symbol = symbol.upper()
        
        # Validate inputs
        if quantity <= 0:
            return False, 'Quantity must be greater than 0.', None
        
        if buy_price <= 0:
            return False, 'Buy price must be greater than 0.', None
        
        # Find or create stock
        stock = Stock.query.filter_by(symbol=symbol).first()
        if not stock:
            stock = StockController.fetch_stock_info(symbol)
            if not stock:
                return False, 'Stock not found.', None
            db.session.add(stock)
            db.session.flush()
        
        # Check if already in portfolio
        existing = Portfolio.query.filter_by(
            user_id=user_id,
            stock_id=stock.id
        ).first()
        
        if existing:
            return False, 'Stock already in portfolio.', None
        
        # Parse date
        if buy_date:
            try:
                buy_date = datetime.strptime(buy_date, '%Y-%m-%d').date()
            except ValueError:
                buy_date = datetime.now().date()
        else:
            buy_date = datetime.now().date()
        
        try:
            # Create portfolio entry
            portfolio = Portfolio(
                user_id=user_id,
                stock_id=stock.id,
                quantity=quantity,
                buy_price=buy_price,
                buy_date=buy_date,
                notes=notes
            )
            portfolio.update_values()
            
            # Create transaction
            transaction = Transaction(
                user_id=user_id,
                stock_id=stock.id,
                transaction_type='BUY',
                quantity=quantity,
                price=buy_price,
                notes=f'Initial purchase - {notes}'
            )
            
            db.session.add(portfolio)
            db.session.add(transaction)
            db.session.commit()
            
            return True, 'Stock added to portfolio.', portfolio
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Add portfolio error: {str(e)}')
            return False, str(e), None
    
    @staticmethod
    def update_stock(portfolio_id, user_id, quantity, buy_price, notes=''):
        """
        Update portfolio entry.
        
        Args:
            portfolio_id: Portfolio entry ID
            user_id: User ID
            quantity: New quantity
            buy_price: New buy price
            notes: New notes
            
        Returns:
            tuple: (success, message, portfolio_entry)
        """
        portfolio = Portfolio.query.get(portfolio_id)
        
        if not portfolio:
            return False, 'Portfolio entry not found.', None
        
        if portfolio.user_id != user_id:
            return False, 'Unauthorized access.', None
        
        if quantity <= 0:
            return False, 'Quantity must be greater than 0.', None
        
        if buy_price <= 0:
            return False, 'Buy price must be greater than 0.', None
        
        try:
            portfolio.quantity = quantity
            portfolio.buy_price = buy_price
            portfolio.notes = notes
            portfolio.update_values()
            
            db.session.commit()
            return True, 'Portfolio updated successfully.', portfolio
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Update portfolio error: {str(e)}')
            return False, str(e), None
    
    @staticmethod
    def delete_stock(portfolio_id, user_id):
        """
        Remove stock from portfolio.
        
        Args:
            portfolio_id: Portfolio entry ID
            user_id: User ID
            
        Returns:
            tuple: (success, message)
        """
        portfolio = Portfolio.query.get(portfolio_id)
        
        if not portfolio:
            return False, 'Portfolio entry not found.'
        
        if portfolio.user_id != user_id:
            return False, 'Unauthorized access.'
        
        try:
            db.session.delete(portfolio)
            db.session.commit()
            return True, 'Stock removed from portfolio.'
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Delete portfolio error: {str(e)}')
            return False, str(e)
    
    @staticmethod
    def get_portfolio_metrics(user_id):
        """
        Get portfolio metrics for analysis.
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Portfolio metrics
        """
        entries = Portfolio.query.filter_by(user_id=user_id).all()
        
        if not entries:
            return {
                'sector_distribution': {},
                'stock_performance': [],
                'total_gainers': 0,
                'total_losers': 0,
                'best_performer': None,
                'worst_performer': None
            }
        
        sector_distribution = {}
        stock_performance = []
        
        for entry in entries:
            entry.update_values()
            stock = entry.stock
            
            if stock and stock.sector:
                sector = stock.sector or 'Other'
                sector_distribution[sector] = sector_distribution.get(sector, 0) + float(entry.current_value or 0)
            
            if entry.profit_loss is not None:
                stock_performance.append({
                    'symbol': stock.symbol if stock else 'Unknown',
                    'name': stock.company_name if stock else 'Unknown',
                    'profit_loss': float(entry.profit_loss),
                    'profit_loss_percent': float(entry.profit_loss_percentage or 0),
                    'current_value': float(entry.current_value or 0)
                })
        
        # Sort by profit_loss_percent
        stock_performance.sort(key=lambda x: x['profit_loss_percent'], reverse=True)
        
        total_gainers = sum(1 for p in stock_performance if p['profit_loss'] > 0)
        total_losers = sum(1 for p in stock_performance if p['profit_loss'] < 0)
        
        return {
            'sector_distribution': sector_distribution,
            'stock_performance': stock_performance,
            'total_gainers': total_gainers,
            'total_losers': total_losers,
            'best_performer': stock_performance[0] if stock_performance else None,
            'worst_performer': stock_performance[-1] if stock_performance else None
        }
    
    @staticmethod
    def calculate_returns(user_id, days=30):
        """
        Calculate portfolio returns over time.
        
        Args:
            user_id: User ID
            days: Number of days
            
        Returns:
            list: Daily returns data
        """
        # This would require historical price data
        # For now, return sample data
        from datetime import timedelta
        import random
        
        entries = Portfolio.query.filter_by(user_id=user_id).all()
        if not entries:
            return []
        
        data = []
        start_date = datetime.now().date() - timedelta(days=days)
        
        total_investment = sum(float(p.investment or 0) for p in entries)
        if total_investment == 0:
            return []
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            # Simulate returns (in a real app, would calculate from actual prices)
            returns = random.uniform(-0.03, 0.05)
            data.append({
                'date': date.isoformat(),
                'returns': returns,
                'cumulative_returns': (1 + returns) ** (i + 1) - 1
            })
        
        return data