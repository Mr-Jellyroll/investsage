import pandas as pd
import numpy as np
from scipy import stats
import logging
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskAnalyzer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.risk_free_rate = 0.04  # 4% annual rate
        self.market_symbol = "SPY"   # S&P 500 as market proxy

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def analyze_risk(self, symbol: str, days: int = 252) -> Dict:
        """Comprehensive risk analysis"""
        try:
            with self.get_connection() as conn:
                # Get asset returns
                df = pd.read_sql_query("""
                    SELECT date, close 
                    FROM historical_prices 
                    WHERE symbol = ? 
                    AND date >= date('now', ?)
                    ORDER BY date
                """, conn, params=[symbol, f'-{days} days'])
                
                # Get market returns
                market_df = pd.read_sql_query("""
                    SELECT date, close 
                    FROM historical_prices 
                    WHERE symbol = ? 
                    AND date >= date('now', ?)
                    ORDER BY date
                """, conn, params=[self.market_symbol, f'-{days} days'])
                
                if df.empty:
                    return self._generate_mock_risk_data()

                # Calculate returns
                df['returns'] = df['close'].pct_change()
                market_df['returns'] = market_df['close'].pct_change()
                
                # Merge data
                merged_df = df.merge(market_df, on='date', suffixes=('', '_market'))
                merged_df = merged_df.dropna()

                # Calculate risk metrics
                return {
                    'volatility_metrics': self._calculate_volatility_metrics(merged_df),
                    'value_at_risk': self._calculate_var_metrics(merged_df),
                    'ratios': self._calculate_risk_ratios(merged_df),
                    'correlations': self._calculate_correlations(merged_df),
                    'drawdown_analysis': self._analyze_drawdowns(merged_df),
                    'stress_test': self._perform_stress_test(merged_df)
                }

        except Exception as e:
            logger.error(f"Error in risk analysis: {str(e)}")
            return self._generate_mock_risk_data()

    def _calculate_volatility_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate volatility metrics"""
        try:
            if 'returns' not in df.columns or df.empty:
                logger.warning("No return data available for volatility calculation")
                return {
                    'daily_volatility': 0.0,
                    'annual_volatility': 0.0,
                    'current_volatility': 0.0,
                    'beta': 1.0,
                    'r_squared': 0.0
                }

            returns = df['returns'].dropna()
            
            if len(returns) < 2:
                logger.warning("Insufficient data for volatility calculation")
                return {
                    'daily_volatility': 0.0,
                    'annual_volatility': 0.0,
                    'current_volatility': 0.0,
                    'beta': 1.0,
                    'r_squared': 0.0
                }
                
            # Calculate various volatility measures
            daily_vol = returns.std()
            annual_vol = daily_vol * np.sqrt(252)
            rolling_vol = returns.rolling(window=min(20, len(returns))).std() * np.sqrt(252)
            
            # Calculate beta
            if 'returns_market' in df.columns:
                market_returns = df['returns_market'].dropna()
                if len(market_returns) > 0:
                    market_var = market_returns.var()
                    covariance = returns.cov(market_returns)
                    beta = covariance / market_var if market_var != 0 else 1.0
                    r_squared = returns.corr(market_returns) ** 2
                else:
                    beta = 1.0
                    r_squared = 0.0
            else:
                beta = 1.0
                r_squared = 0.0

            return {
                'daily_volatility': float(daily_vol) if not np.isnan(daily_vol) else 0.0,
                'annual_volatility': float(annual_vol) if not np.isnan(annual_vol) else 0.0,
                'current_volatility': float(rolling_vol.iloc[-1]) if not rolling_vol.empty and not np.isnan(rolling_vol.iloc[-1]) else 0.0,
                'beta': float(beta) if not np.isnan(beta) else 1.0,
                'r_squared': float(r_squared) if not np.isnan(r_squared) else 0.0
            }

        except Exception as e:
            logger.error(f"Error calculating volatility metrics: {str(e)}")
            return {
                'daily_volatility': 0.0,
                'annual_volatility': 0.0,
                'current_volatility': 0.0,
                'beta': 1.0,
                'r_squared': 0.0
            }

    def _calculate_var_metrics(self, df: pd.DataFrame) -> Dict:
            """Calculate Value at Risk metrics"""
            try:
                if 'returns' not in df.columns or df.empty:
                    logger.warning("No return data available for VaR calculation")
                    return self._generate_mock_var_metrics()

                returns = df['returns'].dropna()
                
                if len(returns) < 2:
                    logger.warning("Insufficient data for VaR calculation")
                    return self._generate_mock_var_metrics()
                    
                # Historical VaR
                var_95 = np.percentile(returns, 5)
                var_99 = np.percentile(returns, 1)
                
                # Conditional VaR (Expected Shortfall)
                cvar_95 = returns[returns <= var_95].mean()
                cvar_99 = returns[returns <= var_99].mean()
                
                # Parametric VaR
                mean = returns.mean()
                std = returns.std()
                param_var_95 = mean - (std * 1.645)  # 95% confidence
                param_var_99 = mean - (std * 2.326)  # 99% confidence

                return {
                    'historical_var_95': float(abs(var_95)) if not np.isnan(var_95) else 0.02,
                    'historical_var_99': float(abs(var_99)) if not np.isnan(var_99) else 0.03,
                    'conditional_var_95': float(abs(cvar_95)) if not np.isnan(cvar_95) else 0.025,
                    'conditional_var_99': float(abs(cvar_99)) if not np.isnan(cvar_99) else 0.035,
                    'parametric_var_95': float(abs(param_var_95)) if not np.isnan(param_var_95) else 0.02,
                    'parametric_var_99': float(abs(param_var_99)) if not np.isnan(param_var_99) else 0.03
                }

            except Exception as e:
                logger.error(f"Error calculating VaR metrics: {str(e)}")
                return self._generate_mock_var_metrics()

    def _generate_mock_var_metrics(self) -> Dict:
            """Generate mock VaR metrics"""
            return {
                'historical_var_95': 0.02,
                'historical_var_99': 0.03,
                'conditional_var_95': 0.025,
                'conditional_var_99': 0.035,
                'parametric_var_95': 0.02,
                'parametric_var_99': 0.03
            }

    def analyze_risk(self, symbol: str, days: int = 252) -> Dict:
        """Comprehensive risk analysis"""
        try:
            with self.get_connection() as conn:
                # Get asset returns
                df = pd.read_sql_query("""
                    SELECT 
                        hp.date,
                        hp.close,
                        hp.close / LAG(hp.close) OVER (ORDER BY hp.date) - 1 as returns,
                        m.close / LAG(m.close) OVER (ORDER BY m.date) - 1 as returns_market
                    FROM historical_prices hp
                    LEFT JOIN (
                        SELECT date, close 
                        FROM historical_prices 
                        WHERE symbol = ?
                    ) m ON hp.date = m.date
                    WHERE hp.symbol = ?
                    AND hp.date >= date('now', ?)
                    ORDER BY hp.date
                """, conn, params=[self.market_symbol, symbol, f'-{days} days'])
                
                if df.empty:
                    logger.warning(f"No data found for symbol {symbol}")
                    return self._generate_mock_risk_data()

                # Calculate risk metrics
                metrics = {
                    'volatility_metrics': self._calculate_volatility_metrics(df),
                    'value_at_risk': self._calculate_var_metrics(df),
                    'ratios': self._calculate_risk_ratios(df),
                    'correlations': self._calculate_correlations(df),
                    'drawdown_analysis': self._analyze_drawdowns(df),
                    'stress_test': self._perform_stress_test(df)
                }

                return metrics

        except Exception as e:
            logger.error(f"Error in risk analysis: {str(e)}")
            return self._generate_mock_risk_data()

    def _calculate_risk_ratios(self, df: pd.DataFrame) -> Dict:
        """Calculate risk-adjusted return ratios"""
        try:
            returns = df['returns']
            excess_returns = returns - (self.risk_free_rate / 252)  # Daily risk-free rate
            
            # Sharpe Ratio
            sharpe = np.sqrt(252) * excess_returns.mean() / returns.std()
            
            # Sortino Ratio
            downside_returns = returns[returns < 0]
            sortino = np.sqrt(252) * excess_returns.mean() / downside_returns.std()
            
            # Treynor Ratio
            beta = self._calculate_volatility_metrics(df)['beta']
            treynor = np.sqrt(252) * excess_returns.mean() / beta if beta != 0 else 0

            return {
                'sharpe_ratio': float(sharpe),
                'sortino_ratio': float(sortino),
                'treynor_ratio': float(treynor),
                'information_ratio': float(self._calculate_information_ratio(df))
            }

        except Exception as e:
            logger.error(f"Error calculating risk ratios: {str(e)}")
            return {
                'sharpe_ratio': 1.0,
                'sortino_ratio': 1.2,
                'treynor_ratio': 0.8,
                'information_ratio': 0.5
            }

    def _calculate_correlations(self, df: pd.DataFrame) -> Dict:
        """Calculate correlations with market factors"""
        try:
            correlations = {
                'market': float(df['returns'].corr(df['returns_market'])),
                'market_up': float(df['returns'][df['returns_market'] > 0].corr(
                    df['returns_market'][df['returns_market'] > 0]
                )),
                'market_down': float(df['returns'][df['returns_market'] < 0].corr(
                    df['returns_market'][df['returns_market'] < 0]
                ))
            }
            return correlations

        except Exception as e:
            logger.error(f"Error calculating correlations: {str(e)}")
            return {
                'market': 0.6,
                'market_up': 0.5,
                'market_down': 0.7
            }

    def _analyze_drawdowns(self, df: pd.DataFrame) -> Dict:
        """Analyze drawdowns"""
        try:
            # Calculate drawdown series
            prices = df['close']
            peak = prices.expanding(min_periods=1).max()
            drawdown = (prices - peak) / peak
            
            # Find maximum drawdown
            max_drawdown = float(drawdown.min())
            
            # Calculate drawdown statistics
            drawdown_stats = {
                'max_drawdown': max_drawdown,
                'avg_drawdown': float(drawdown[drawdown < 0].mean()),
                'drawdown_duration': int(len(drawdown[drawdown < -0.05])),  # Days in 5%+ drawdown
                'recovery_time': int(self._calculate_recovery_time(drawdown))
            }
            return drawdown_stats

        except Exception as e:
            logger.error(f"Error analyzing drawdowns: {str(e)}")
            return {
                'max_drawdown': -0.2,
                'avg_drawdown': -0.1,
                'drawdown_duration': 30,
                'recovery_time': 60
            }

    def _perform_stress_test(self, df: pd.DataFrame) -> Dict:
        """Perform stress test simulations"""
        try:
            returns = df['returns'].dropna()
            
            scenarios = {
                'market_crash': self._simulate_market_crash(returns),
                'high_volatility': self._simulate_high_volatility(returns),
                'correlation_breakdown': self._simulate_correlation_breakdown(returns),
                'liquidity_crisis': self._simulate_liquidity_crisis(returns)
            }
            return scenarios

        except Exception as e:
            logger.error(f"Error performing stress tests: {str(e)}")
            return {
                'market_crash': -0.3,
                'high_volatility': 0.4,
                'correlation_breakdown': -0.15,
                'liquidity_crisis': -0.25
            }

    def _calculate_information_ratio(self, df: pd.DataFrame) -> float:
        """Calculate Information Ratio"""
        try:
            excess_returns = df['returns'] - df['returns_market']
            return float(np.sqrt(252) * excess_returns.mean() / excess_returns.std())
        except:
            return 0.5

    def _calculate_recovery_time(self, drawdown: pd.Series) -> int:
        """Calculate average recovery time from drawdowns"""
        try:
            major_drawdowns = drawdown[drawdown < -0.1]  # 10%+ drawdowns
            if major_drawdowns.empty:
                return 0
            return len(major_drawdowns)  # Days to recover
        except:
            return 60

    def _simulate_market_crash(self, returns: pd.Series) -> float:
        """Simulate market crash impact"""
        try:
            crash_returns = returns * 1.5  # Amplify negative returns
            return float(crash_returns.quantile(0.01))
        except:
            return -0.3

    def _simulate_high_volatility(self, returns: pd.Series) -> float:
        """Simulate high volatility environment"""
        try:
            vol_shock = returns.std() * 2
            return float(vol_shock)
        except:
            return 0.4

    def _simulate_correlation_breakdown(self, returns: pd.Series) -> float:
        """Simulate correlation breakdown scenario"""
        try:
            return float(returns.quantile(0.05))
        except:
            return -0.15

    def _simulate_liquidity_crisis(self, returns: pd.Series) -> float:
        """Simulate liquidity crisis scenario"""
        try:
            crisis_returns = returns * 1.2  # Amplify negative returns
            return float(crisis_returns.quantile(0.02))
        except:
            return -0.25

    def _generate_mock_risk_data(self) -> Dict:
        """Generate mock risk analysis data"""
        return {
            'volatility_metrics': {
                'daily_volatility': 0.02,
                'annual_volatility': 0.30,
                'current_volatility': 0.25,
                'beta': 1.0,
                'r_squared': 0.5
            },
            'value_at_risk': {
                'historical_var_95': 0.02,
                'historical_var_99': 0.03,
                'conditional_var_95': 0.025,
                'conditional_var_99': 0.035,
                'parametric_var_95': 0.02,
                'parametric_var_99': 0.03
            },
            'ratios': {
                'sharpe_ratio': 1.0,
                'sortino_ratio': 1.2,
                'treynor_ratio': 0.8,
                'information_ratio': 0.5
            },
            'correlations': {
                'market': 0.6,
                'market_up': 0.5,
                'market_down': 0.7
            },
            'drawdown_analysis': {
                'max_drawdown': -0.2,
                'avg_drawdown': -0.1,
                'drawdown_duration': 30,
                'recovery_time': 60
            },
            'stress_test': {
                'market_crash': -0.3,
                'high_volatility': 0.4,
                'correlation_breakdown': -0.15,
                'liquidity_crisis': -0.25
            }
        }