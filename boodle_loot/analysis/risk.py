import pandas as pd
import numpy as np
from scipy import stats
import sqlite3
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RiskMetrics:
    volatility: float
    var: float  # Value at Risk
    cvar: float  # Conditional VaR
    beta: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    correlation: Dict[str, float]

class RiskAnalyzer:
    """Risk analysis capabilities"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.risk_free_rate = 0.03  # 3% annual risk-free rate
        self.market_symbol = "SPY"   # S&P 500 as market proxy

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def analyze_risk(self, symbol: str, days: int = 252) -> Dict:
        """
        Comprehensive risk analysis for a single symbol
        """
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
                
                # Calculate returns
                df['returns'] = df['close'].pct_change()
                market_df['returns'] = market_df['close'].pct_change()
                
                # Join market returns
                merged_df = df.merge(market_df, on='date', suffixes=('', '_market'))
                
                return {
                    'basic_metrics': self._calculate_basic_risk_metrics(merged_df),
                    'tail_risk': self._analyze_tail_risk(merged_df['returns']),
                    'stress_test': self._perform_stress_test(merged_df),
                    'scenario_analysis': self._perform_scenario_analysis(merged_df),
                    'correlation_analysis': self._analyze_correlations(symbol, days),
                    'risk_decomposition': self._decompose_risk(merged_df)
                }
                
        except Exception as e:
            logger.error(f"Error in risk analysis: {str(e)}")
            return {}

    def analyze_portfolio_risk(self, positions: List[Dict]) -> Dict:
        """
        Analyze portfolio-level risk
        """
        try:
            with self.get_connection() as conn:
                # Get returns for all positions
                returns_data = {}
                weights = {}
                
                for position in positions:
                    df = pd.read_sql_query("""
                        SELECT date, close
                        FROM historical_prices 
                        WHERE symbol = ? 
                        ORDER BY date
                    """, conn, params=[position['symbol']])
                    
                    returns_data[position['symbol']] = df.set_index('date')['close'].pct_change()
                    weights[position['symbol']] = position['weight']
                
                returns_df = pd.DataFrame(returns_data)
                
                return {
                    'portfolio_metrics': self._calculate_portfolio_metrics(returns_df, weights),
                    'diversification': self._analyze_diversification(returns_df),
                    'risk_contribution': self._calculate_risk_contribution(returns_df, weights),
                    'factor_exposure': self._analyze_factor_exposure(positions),
                    'scenario_impact': self._analyze_scenario_impact(returns_df, weights)
                }
                
        except Exception as e:
            logger.error(f"Error in portfolio risk analysis: {str(e)}")
            return {}

    def _calculate_basic_risk_metrics(self, df: pd.DataFrame) -> RiskMetrics:
        """Calculate basic risk metrics"""
        returns = df['returns'].dropna()
        market_returns = df['returns_market'].dropna()
        
        volatility = returns.std() * np.sqrt(252)  # Annualized
        beta = self._calculate_beta(returns, market_returns)
        
        return RiskMetrics(
            volatility=float(volatility),
            var=float(self._calculate_var(returns)),
            cvar=float(self._calculate_cvar(returns)),
            beta=float(beta),
            sharpe_ratio=float(self._calculate_sharpe_ratio(returns)),
            sortino_ratio=float(self._calculate_sortino_ratio(returns)),
            max_drawdown=float(self._calculate_max_drawdown(returns)),
            correlation={'market': float(returns.corr(market_returns))}
        )

    def _analyze_tail_risk(self, returns: pd.Series) -> Dict:
        """Analyze tail risk using various methods"""
        try:
            # Calculate tail risk metrics
            var_95 = self._calculate_var(returns, confidence=0.95)
            var_99 = self._calculate_var(returns, confidence=0.99)
            cvar_95 = self._calculate_cvar(returns, confidence=0.95)
            
            # Fit distributions for tail analysis
            normal_params = stats.norm.fit(returns)
            t_params = stats.t.fit(returns)
            
            return {
                'var_95': float(var_95),
                'var_99': float(var_99),
                'cvar_95': float(cvar_95),
                'tail_ratios': {
                    'left_tail_ratio': float(len(returns[returns < -3 * returns.std()]) / len(returns)),
                    'right_tail_ratio': float(len(returns[returns > 3 * returns.std()]) / len(returns))
                },
                'distribution_fit': {
                    'normal': {
                        'mean': float(normal_params[0]),
                        'std': float(normal_params[1])
                    },
                    'student_t': {
                        'df': float(t_params[0]),
                        'loc': float(t_params[1]),
                        'scale': float(t_params[2])
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error in tail risk analysis: {str(e)}")
            return {}

    def _perform_stress_test(self, df: pd.DataFrame) -> Dict:
        """Perform stress testing under various scenarios"""
        try:
            returns = df['returns'].dropna()
            
            scenarios = {
                'market_crash': -0.20,  # 20% market drop
                'high_volatility': 2.0,  # Double volatility
                'correlation_breakdown': 0.5,  # 50% correlation breakdown
                'liquidity_crisis': -0.15  # 15% drop due to liquidity
            }
            
            results = {}
            for scenario, shock in scenarios.items():
                if scenario == 'high_volatility':
                    results[scenario] = self._simulate_high_volatility(returns, shock)
                elif scenario == 'correlation_breakdown':
                    results[scenario] = self._simulate_correlation_breakdown(df, shock)
                else:
                    results[scenario] = self._simulate_market_shock(returns, shock)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in stress testing: {str(e)}")
            return {}

    def _perform_scenario_analysis(self, df: pd.DataFrame) -> Dict:
        """Analyze historical scenarios and their impact"""
        try:
            # Historical scenarios to analyze
            scenarios = {
                'covid_crash': ('2020-02-19', '2020-03-23'),
                'financial_crisis': ('2008-09-15', '2009-03-09'),
                'tech_bubble': ('2000-03-10', '2002-10-09'),
                'flash_crash': ('2010-05-06', '2010-05-06')
            }
            
            results = {}
            for scenario, (start_date, end_date) in scenarios.items():
                scenario_returns = self._get_scenario_returns(df['symbol'], start_date, end_date)
                if not scenario_returns.empty:
                    results[scenario] = {
                        'total_return': float(scenario_returns.prod() - 1),
                        'max_drawdown': float(self._calculate_max_drawdown(scenario_returns)),
                        'volatility': float(scenario_returns.std() * np.sqrt(252)),
                        'var_95': float(self._calculate_var(scenario_returns))
                    }
            
            return results
            
        except Exception as e:
            logger.error(f"Error in scenario analysis: {str(e)}")
            return {}

    def _analyze_correlations(self, symbol: str, days: int) -> Dict:
        """Analyze correlations with various market factors"""
        try:
            with self.get_connection() as conn:
                # Get returns for symbol and market factors
                factors = ['SPY', 'TLT', 'GLD', 'DXY']  # Market, Bonds, Gold, Dollar
                
                returns_data = {}
                for factor in factors:
                    df = pd.read_sql_query("""
                        SELECT date, close
                        FROM historical_prices 
                        WHERE symbol = ? 
                        AND date >= date('now', ?)
                    """, conn, params=[factor, f'-{days} days'])
                    
                    returns_data[factor] = df.set_index('date')['close'].pct_change()
                
                # Calculate correlation matrix
                returns_df = pd.DataFrame(returns_data)
                corr_matrix = returns_df.corr()
                
                return {
                    'correlation_matrix': corr_matrix.to_dict(),
                    'rolling_correlations': self._calculate_rolling_correlations(returns_df),
                    'correlation_stability': self._analyze_correlation_stability(returns_df)
                }
                
        except Exception as e:
            logger.error(f"Error in correlation analysis: {str(e)}")
            return {}

    def _decompose_risk(self, df: pd.DataFrame) -> Dict:
        """Decompose risk into systematic and idiosyncratic components"""
        try:
            returns = df['returns'].dropna()
            market_returns = df['returns_market'].dropna()
            
            # Perform regression
            beta = self._calculate_beta(returns, market_returns)
            systematic_returns = beta * market_returns
            idiosyncratic_returns = returns - systematic_returns
            
            return {
                'systematic_risk': float(systematic_returns.std() * np.sqrt(252)),
                'idiosyncratic_risk': float(idiosyncratic_returns.std() * np.sqrt(252)),
                'r_squared': float(returns.corr(market_returns) ** 2),
                'risk_decomposition': {
                    'systematic': float(systematic_returns.var() / returns.var()),
                    'idiosyncratic': float(idiosyncratic_returns.var() / returns.var())
                }
            }
            
        except Exception as e:
            logger.error(f"Error in risk decomposition: {str(e)}")
            return {}

    # Helper methods for risk calculations
    def _calculate_var(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        return abs(np.percentile(returns, (1 - confidence) * 100))

    def _calculate_cvar(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        var = self._calculate_var(returns, confidence)
        return abs(returns[returns <= -var].mean())

    def _calculate_beta(self, returns: pd.Series, market_returns: pd.Series) -> float:
        """Calculate beta coefficient"""
        covar = returns.cov(market_returns)
        market_var = market_returns.var()
        return covar / market_var if market_var != 0 else 1.0

    def _calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = returns - self.risk_free_rate/252  # Daily risk-free rate
        return np.sqrt(252) * excess_returns.mean() / returns.std()

    def _calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate Sortino ratio"""
        excess_returns = returns - self.risk_free_rate/252
        downside_returns = returns[returns < 0]
        downside_std = np.sqrt(np.mean(downside_returns**2))
        return np.sqrt(252) * excess_returns.mean() / downside_std if downside_std != 0 else 0

    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cum_returns = (1 + returns).cumprod()
        running_max = cum_returns.expanding().max()
        drawdowns = cum_returns / running_max - 1
        return abs(drawdowns.min())

if __name__ == "__main__":
    # Example usage
    analyzer = RiskAnalyzer("./data/investsage.db")
    
    # Single stock risk analysis
    risk_analysis = analyzer.analyze_risk("AAPL")
    print("\nRisk Analysis for AAPL:")
    print(risk_analysis)
    
    # Portfolio risk analysis
    portfolio = [
        {'symbol': 'AAPL', 'weight': 0.4},
        {'symbol': 'MSFT', 'weight': 0.3},
        {'symbol': 'GOOGL', 'weight': 0.3}
    ]
    portfolio_risk = analyzer.analyze_portfolio_risk(portfolio)
    print("\nPortfolio Risk Analysis:")
    print(portfolio_risk)