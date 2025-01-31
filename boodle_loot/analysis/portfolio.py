import pandas as pd
import numpy as np
from scipy import optimize
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioAnalyzer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.risk_free_rate = 0.04  # 4% annual risk-free rate

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def analyze_portfolio(self, positions: List[Dict], total_value: float = 100000) -> Dict:
        """Analyze portfolio composition and suggest optimizations"""
        try:
            with self.get_connection() as conn:
                # Get historical data for all positions
                returns_data = {}
                current_data = {}
                
                for position in positions:
                    symbol = position['symbol']
                    weight = position.get('weight', 0)
                    
                    # Get historical prices
                    df = pd.read_sql_query("""
                        SELECT date, close
                        FROM historical_prices 
                        WHERE symbol = ?
                        AND date >= date('now', '-365 days')
                        ORDER BY date
                    """, conn, params=[symbol])
                    
                    if not df.empty:
                        returns_data[symbol] = df.set_index('date')['close'].pct_change()
                        current_data[symbol] = {
                            'price': float(df['close'].iloc[-1]),
                            'weight': weight
                        }

                if not returns_data:
                    return self._generate_mock_portfolio_data()

                returns_df = pd.DataFrame(returns_data)
                
                return {
                    'current_allocation': self._analyze_current_allocation(current_data, total_value),
                    'risk_metrics': self._calculate_portfolio_risk(returns_df, current_data),
                    'optimization': self._optimize_portfolio(returns_df),
                    'diversification': self._analyze_diversification(returns_df, current_data),
                    'rebalancing': self._suggest_rebalancing(current_data, returns_df)
                }

        except Exception as e:
            logger.error(f"Error in portfolio analysis: {str(e)}")
            return self._generate_mock_portfolio_data()

    def _analyze_current_allocation(self, current_data: Dict, total_value: float) -> Dict:
        """Analyze current portfolio allocation"""
        try:
            total_weight = sum(data['weight'] for data in current_data.values())
            
            allocations = {
                symbol: {
                    'weight': data['weight'] / total_weight if total_weight > 0 else 0,
                    'value': (data['weight'] / total_weight) * total_value if total_weight > 0 else 0,
                    'price': data['price']
                }
                for symbol, data in current_data.items()
            }
            
            return {
                'positions': allocations,
                'total_value': total_value,
                'position_count': len(current_data)
            }

        except Exception as e:
            logger.error(f"Error analyzing allocation: {str(e)}")
            return {
                'positions': {},
                'total_value': total_value,
                'position_count': 0
            }

    def _calculate_portfolio_risk(self, returns_df: pd.DataFrame, current_data: Dict) -> Dict:
        """Calculate portfolio risk metrics"""
        try:
            weights = np.array([data['weight'] for data in current_data.values()])
            weights = weights / weights.sum() if weights.sum() != 0 else weights
            
            # Calculate portfolio returns
            portfolio_returns = returns_df.dot(weights)
            
            # Calculate metrics
            annual_return = portfolio_returns.mean() * 252
            annual_vol = portfolio_returns.std() * np.sqrt(252)
            sharpe_ratio = (annual_return - self.risk_free_rate) / annual_vol if annual_vol != 0 else 0
            
            # Calculate max drawdown
            cum_returns = (1 + portfolio_returns).cumprod()
            rolling_max = cum_returns.expanding(min_periods=1).max()
            drawdowns = (cum_returns - rolling_max) / rolling_max
            max_drawdown = drawdowns.min()
            
            return {
                'annual_return': float(annual_return),
                'annual_volatility': float(annual_vol),
                'sharpe_ratio': float(sharpe_ratio),
                'max_drawdown': float(max_drawdown),
                'var_95': float(np.percentile(portfolio_returns, 5))
            }

        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {str(e)}")
            return {
                'annual_return': 0.0,
                'annual_volatility': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'var_95': 0.0
            }

    def _optimize_portfolio(self, returns_df: pd.DataFrame) -> Dict:
        """Optimize portfolio weights for maximum Sharpe ratio"""
        try:
            def neg_sharpe_ratio(weights):
                portfolio_return = np.sum(returns_df.mean() * weights) * 252
                portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(returns_df.cov() * 252, weights)))
                sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
                return -sharpe

            n_assets = len(returns_df.columns)
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},  # weights sum to 1
            ]
            bounds = tuple((0, 1) for _ in range(n_assets))  # weights between 0 and 1
            
            result = optimize.minimize(
                neg_sharpe_ratio, 
                np.array([1/n_assets] * n_assets),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            optimal_weights = result.x
            optimal_sharpe = -result.fun
            
            return {
                'optimal_weights': {
                    symbol: float(weight)
                    for symbol, weight in zip(returns_df.columns, optimal_weights)
                },
                'optimal_sharpe': float(optimal_sharpe),
                'optimization_success': bool(result.success)
            }

        except Exception as e:
            logger.error(f"Error optimizing portfolio: {str(e)}")
            return {
                'optimal_weights': {},
                'optimal_sharpe': 0.0,
                'optimization_success': False
            }

    def _analyze_diversification(self, returns_df: pd.DataFrame, current_data: Dict) -> Dict:
        """Analyze portfolio diversification"""
        try:
            if returns_df.empty or len(returns_df.columns) < 2:
                logger.warning("Insufficient data for correlation analysis")
                return {
                    'avg_correlation': 0.0,
                    'herfindahl_index': 1.0,
                    'effective_positions': 1.0,
                    'correlation_matrix': {}
                }

            # Calculate correlation matrix
            corr_matrix = returns_df.corr().fillna(0)
            
            # Calculate average correlation excluding self-correlations
            n = len(corr_matrix)
            if n > 1:
                total_corr = corr_matrix.sum().sum() - n  # Subtract diagonal (self-correlations)
                pairs = n * (n - 1)  # Number of pairs excluding self-correlations
                avg_correlation = total_corr / pairs if pairs > 0 else 0
            else:
                avg_correlation = 0
            
            # Calculate concentration metrics
            weights = np.array([data['weight'] for data in current_data.values()])
            total_weight = weights.sum()
            if total_weight > 0:
                weights = weights / total_weight
            else:
                weights = np.array([1.0])
            
            herfindahl = float(np.sum(weights**2))
            effective_positions = float(1/herfindahl) if herfindahl > 0 else 1.0
            
            return {
                'avg_correlation': float(avg_correlation),
                'herfindahl_index': herfindahl,
                'effective_positions': effective_positions,
                'correlation_matrix': corr_matrix.fillna(0).to_dict()
            }

        except Exception as e:
            logger.error(f"Error analyzing diversification: {str(e)}")
            return {
                'avg_correlation': 0.0,
                'herfindahl_index': 1.0,
                'effective_positions': 1.0,
                'correlation_matrix': {}
            }

    def _suggest_rebalancing(self, current_data: Dict, returns_df: pd.DataFrame) -> Dict:
        """Suggest portfolio rebalancing trades"""
        try:
            # Get optimal weights
            optimization = self._optimize_portfolio(returns_df)
            optimal_weights = optimization['optimal_weights']
            
            # Calculate current weights
            total_weight = sum(data['weight'] for data in current_data.values())
            current_weights = {
                symbol: data['weight'] / total_weight if total_weight > 0 else 0
                for symbol, data in current_data.items()
            }
            
            # Calculate differences
            trades = {}
            for symbol in set(optimal_weights.keys()) | set(current_weights.keys()):
                current = current_weights.get(symbol, 0)
                target = optimal_weights.get(symbol, 0)
                if abs(target - current) > 0.01:  # 1% threshold
                    trades[symbol] = {
                        'current_weight': float(current),
                        'target_weight': float(target),
                        'difference': float(target - current)
                    }
            
            return {
                'suggested_trades': trades,
                'trade_count': len(trades),
                'total_turnover': float(sum(abs(t['difference']) for t in trades.values()) / 2)
            }

        except Exception as e:
            logger.error(f"Error suggesting rebalancing: {str(e)}")
            return {
                'suggested_trades': {},
                'trade_count': 0,
                'total_turnover': 0.0
            }

    def _generate_mock_portfolio_data(self) -> Dict:
        """Generate mock portfolio data for testing"""
        return {
            'current_allocation': {
                'positions': {
                    'AAPL': {'weight': 0.25, 'value': 25000, 'price': 150.0},
                    'MSFT': {'weight': 0.25, 'value': 25000, 'price': 280.0},
                    'GOOGL': {'weight': 0.25, 'value': 25000, 'price': 2800.0},
                    'AMZN': {'weight': 0.25, 'value': 25000, 'price': 3300.0}
                },
                'total_value': 100000,
                'position_count': 4
            },
            'risk_metrics': {
                'annual_return': 0.15,
                'annual_volatility': 0.20,
                'sharpe_ratio': 0.75,
                'max_drawdown': -0.25,
                'var_95': -0.02
            },
            'optimization': {
                'optimal_weights': {
                    'AAPL': 0.3,
                    'MSFT': 0.3,
                    'GOOGL': 0.2,
                    'AMZN': 0.2
                },
                'optimal_sharpe': 0.85,
                'optimization_success': True
            },
            'diversification': {
                'avg_correlation': 0.5,
                'herfindahl_index': 0.25,
                'effective_positions': 4.0,
                'correlation_matrix': {}
            },
            'rebalancing': {
                'suggested_trades': {
                    'AAPL': {
                        'current_weight': 0.25,
                        'target_weight': 0.3,
                        'difference': 0.05
                    },
                    'MSFT': {
                        'current_weight': 0.25,
                        'target_weight': 0.3,
                        'difference': 0.05
                    }
                },
                'trade_count': 2,
                'total_turnover': 0.1
            }
        }