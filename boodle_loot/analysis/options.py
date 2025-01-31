import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import sqlite3
from scipy.stats import norm
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptionsAnalyzer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.risk_free_rate = 0.04  # 4% risk-free rate

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def analyze_options_chain(self, symbol: str) -> Dict:
        """Analyze full options chain"""
        try:
            with self.get_connection() as conn:
                # Get current stock price
                current_price = self._get_current_price(conn, symbol)
                if not current_price:
                    return self._generate_mock_options_data()

                # Get volatility from historical data
                historical_volatility = self._calculate_historical_volatility(conn, symbol)

                # Generate mock options chain data since we don't have real options data yet
                chain_data = self._generate_options_chain(current_price, historical_volatility)

                return {
                    'summary': {
                        'current_price': current_price,
                        'implied_volatility': historical_volatility,
                        'put_call_ratio': self._calculate_put_call_ratio(chain_data),
                        'most_active_strikes': self._find_most_active_strikes(chain_data)
                    },
                    'calls': chain_data['calls'],
                    'puts': chain_data['puts'],
                    'greeks': self._calculate_chain_greeks(chain_data, current_price),
                    'volume_distribution': self._analyze_volume_distribution(chain_data)
                }

        except Exception as e:
            logger.error(f"Error analyzing options chain: {str(e)}")
            return self._generate_mock_options_data()

    def _get_current_price(self, conn: sqlite3.Connection, symbol: str) -> Optional[float]:
        """Get current stock price"""
        try:
            df = pd.read_sql_query("""
                SELECT close 
                FROM historical_prices 
                WHERE symbol = ? 
                ORDER BY date DESC 
                LIMIT 1
            """, conn, params=[symbol])
            return float(df['close'].iloc[0]) if not df.empty else None
        except Exception as e:
            logger.error(f"Error getting current price: {str(e)}")
            return None

    def _calculate_historical_volatility(self, conn: sqlite3.Connection, symbol: str) -> float:
        """Calculate historical volatility"""
        try:
            df = pd.read_sql_query("""
                SELECT close 
                FROM historical_prices 
                WHERE symbol = ? 
                ORDER BY date DESC 
                LIMIT 30
            """, conn, params=[symbol])
            
            if df.empty:
                return 0.3  # Default volatility

            returns = np.log(df['close'] / df['close'].shift(1))
            return float(returns.std() * np.sqrt(252))
        except Exception as e:
            logger.error(f"Error calculating volatility: {str(e)}")
            return 0.3

    def _calculate_option_price(self, S: float, K: float, T: float, r: float, 
                              sigma: float, option_type: str) -> float:
        """Calculate option price using Black-Scholes"""
        try:
            d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
            d2 = d1 - sigma*np.sqrt(T)
            
            if option_type == 'call':
                price = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
            else:
                price = K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
                
            return float(price)
        except Exception as e:
            logger.error(f"Error calculating option price: {str(e)}")
            return 0.0

    def _calculate_greeks(self, S: float, K: float, T: float, r: float, 
                         sigma: float, option_type: str) -> Dict:
        """Calculate option Greeks"""
        try:
            d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma*np.sqrt(T))
            d2 = d1 - sigma*np.sqrt(T)
            
            # Calculate Greeks
            if option_type == 'call':
                delta = norm.cdf(d1)
                gamma = norm.pdf(d1)/(S*sigma*np.sqrt(T))
                theta = (-S*norm.pdf(d1)*sigma/(2*np.sqrt(T)) - 
                        r*K*np.exp(-r*T)*norm.cdf(d2))
                vega = S*np.sqrt(T)*norm.pdf(d1)
                rho = K*T*np.exp(-r*T)*norm.cdf(d2)
            else:
                delta = norm.cdf(d1) - 1
                gamma = norm.pdf(d1)/(S*sigma*np.sqrt(T))
                theta = (-S*norm.pdf(d1)*sigma/(2*np.sqrt(T)) + 
                        r*K*np.exp(-r*T)*norm.cdf(-d2))
                vega = S*np.sqrt(T)*norm.pdf(d1)
                rho = -K*T*np.exp(-r*T)*norm.cdf(-d2)
            
            return {
                'delta': float(delta),
                'gamma': float(gamma),
                'theta': float(theta),
                'vega': float(vega),
                'rho': float(rho)
            }
        except Exception as e:
            logger.error(f"Error calculating Greeks: {str(e)}")
            return {
                'delta': 0.0,
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'rho': 0.0
            }

    def _generate_options_chain(self, current_price: float, volatility: float) -> Dict:
        """Generate synthetic options chain data"""
        strikes = np.linspace(current_price * 0.8, current_price * 1.2, 10)
        expiry_days = [30, 60, 90]
        
        calls = []
        puts = []
        
        for days in expiry_days:
            T = days / 365.0
            for K in strikes:
                # Generate call option
                call_price = self._calculate_option_price(
                    current_price, K, T, self.risk_free_rate, volatility, 'call'
                )
                call_greeks = self._calculate_greeks(
                    current_price, K, T, self.risk_free_rate, volatility, 'call'
                )
                
                calls.append({
                    'strike': float(K),
                    'expiry_days': days,
                    'bid': float(call_price * 0.98),
                    'ask': float(call_price * 1.02),
                    'volume': int(np.random.normal(1000, 200)),
                    'open_interest': int(np.random.normal(2000, 500)),
                    'implied_volatility': volatility,
                    'greeks': call_greeks
                })
                
                # Generate put option
                put_price = self._calculate_option_price(
                    current_price, K, T, self.risk_free_rate, volatility, 'put'
                )
                put_greeks = self._calculate_greeks(
                    current_price, K, T, self.risk_free_rate, volatility, 'put'
                )
                
                puts.append({
                    'strike': float(K),
                    'expiry_days': days,
                    'bid': float(put_price * 0.98),
                    'ask': float(put_price * 1.02),
                    'volume': int(np.random.normal(800, 200)),
                    'open_interest': int(np.random.normal(1500, 500)),
                    'implied_volatility': volatility,
                    'greeks': put_greeks
                })
        
        return {'calls': calls, 'puts': puts}

    def _calculate_put_call_ratio(self, chain_data: Dict) -> float:
        """Calculate put/call ratio"""
        call_volume = sum(call['volume'] for call in chain_data['calls'])
        put_volume = sum(put['volume'] for put in chain_data['puts'])
        return put_volume / call_volume if call_volume > 0 else 1.0

    def _find_most_active_strikes(self, chain_data: Dict) -> List[Dict]:
        """Find most actively traded strikes"""
        all_options = chain_data['calls'] + chain_data['puts']
        sorted_options = sorted(all_options, key=lambda x: x['volume'], reverse=True)
        return sorted_options[:5]

    def _calculate_chain_greeks(self, chain_data: Dict, current_price: float) -> Dict:
        """Calculate aggregate Greeks for the entire chain"""
        total_greeks = {
            'delta': 0.0,
            'gamma': 0.0,
            'theta': 0.0,
            'vega': 0.0,
            'rho': 0.0
        }
        
        for option in chain_data['calls'] + chain_data['puts']:
            for greek in total_greeks:
                total_greeks[greek] += option['greeks'][greek] * option['open_interest']
        
        return total_greeks

    def _analyze_volume_distribution(self, chain_data: Dict) -> Dict:
        """Analyze volume distribution across strikes and expiries"""
        volume_by_expiry = {}
        volume_by_strike = {}
        
        for option in chain_data['calls'] + chain_data['puts']:
            # Group by expiry
            expiry = str(option['expiry_days'])
            volume_by_expiry[expiry] = volume_by_expiry.get(expiry, 0) + option['volume']
            
            # Group by strike
            strike = str(option['strike'])
            volume_by_strike[strike] = volume_by_strike.get(strike, 0) + option['volume']
        
        return {
            'by_expiry': volume_by_expiry,
            'by_strike': volume_by_strike
        }

    def _generate_mock_options_data(self) -> Dict:
        """Generate mock options data for testing"""
        mock_price = 100.0
        mock_vol = 0.3
        return self._generate_options_chain(mock_price, mock_vol)