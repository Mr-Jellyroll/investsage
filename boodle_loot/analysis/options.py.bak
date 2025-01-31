import pandas as pd
import numpy as np
from scipy.stats import norm
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OptionContract:
    symbol: str
    expiration: datetime
    strike: float
    option_type: str  # 'call' or 'put'
    bid: float
    ask: float
    implied_volatility: float
    open_interest: int
    volume: int

class OptionsAnalyzer:
    """Options analysis capabilities"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.risk_free_rate = 0.03  # 3% annual risk-free rate

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def analyze_options_chain(self, symbol: str) -> Dict:
        """
        Analyze full options chain
        """
        try:
            with self.get_connection() as conn:
                # Get current stock price
                current_price = pd.read_sql_query("""
                    SELECT close 
                    FROM historical_prices 
                    WHERE symbol = ? 
                    ORDER BY date DESC 
                    LIMIT 1
                """, conn, params=[symbol]).iloc[0]['close']
                
                # Get options chain data
                options_data = pd.read_sql_query("""
                    SELECT *
                    FROM options_chain
                    WHERE symbol = ?
                    AND expiration_date > date('now')
                    ORDER BY expiration_date, strike
                """, conn, params=[symbol])
                
                if options_data.empty:
                    return {}
                
                # Calculate key metrics
                analysis = {
                    'implied_volatility_surface': self._calculate_iv_surface(options_data),
                    'greeks': self._calculate_chain_greeks(options_data, current_price),
                    'put_call_ratio': self._calculate_put_call_ratio(options_data),
                    'volume_analysis': self._analyze_options_volume(options_data),
                    'open_interest_analysis': self._analyze_open_interest(options_data),
                    'strike_clustering': self._analyze_strike_clustering(options_data, current_price)
                }
                
                return analysis
                
        except Exception as e:
            logger.error(f"Error analyzing options chain: {str(e)}")
            return {}

    def analyze_strategy(self, symbol: str, strategy: str, 
                        params: Dict = None) -> Dict:
        """
        Analyze options trading strategy
        """
        try:
            with self.get_connection() as conn:
                current_price = pd.read_sql_query("""
                    SELECT close 
                    FROM historical_prices 
                    WHERE symbol = ? 
                    ORDER BY date DESC 
                    LIMIT 1
                """, conn, params=[symbol]).iloc[0]['close']
                
                if strategy == 'covered_call':
                    return self._analyze_covered_call(symbol, current_price, params)
                elif strategy == 'iron_condor':
                    return self._analyze_iron_condor(symbol, current_price, params)
                elif strategy == 'butterfly':
                    return self._analyze_butterfly(symbol, current_price, params)
                else:
                    return self._analyze_custom_strategy(symbol, current_price, params)
                    
        except Exception as e:
            logger.error(f"Error analyzing options strategy: {str(e)}")
            return {}

    def calculate_greeks(self, option: OptionContract, 
                        current_price: float) -> Dict:
        """
        Calculate option Greeks
        """
        try:
            time_to_expiry = (option.expiration - datetime.now()).days / 365.0
            
            if time_to_expiry <= 0:
                return {}
            
            # Calculate Greeks
            delta = self._calculate_delta(
                current_price, 
                option.strike, 
                time_to_expiry,
                option.implied_volatility,
                option.option_type
            )
            
            gamma = self._calculate_gamma(
                current_price, 
                option.strike, 
                time_to_expiry,
                option.implied_volatility
            )
            
            theta = self._calculate_theta(
                current_price, 
                option.strike, 
                time_to_expiry,
                option.implied_volatility,
                option.option_type
            )
            
            vega = self._calculate_vega(
                current_price, 
                option.strike, 
                time_to_expiry,
                option.implied_volatility
            )
            
            rho = self._calculate_rho(
                current_price, 
                option.strike, 
                time_to_expiry,
                option.implied_volatility,
                option.option_type
            )
            
            return {
                'delta': float(delta),
                'gamma': float(gamma),
                'theta': float(theta),
                'vega': float(vega),
                'rho': float(rho)
            }
            
        except Exception as e:
            logger.error(f"Error calculating Greeks: {str(e)}")
            return {}

    def analyze_volatility_surface(self, symbol: str) -> Dict:
        """
        Analyze implied volatility surface
        """
        try:
            with self.get_connection() as conn:
                options_data = pd.read_sql_query("""
                    SELECT *
                    FROM options_chain
                    WHERE symbol = ?
                    AND expiration_date > date('now')
                    ORDER BY expiration_date, strike
                """, conn, params=[symbol])
                
                if options_data.empty:
                    return {}
                
                # Calculate volatility surface
                surface = self._calculate_iv_surface(options_data)
                
                # Analyze skew
                skew = self._analyze_volatility_skew(options_data)
                
                # Analyze term structure
                term_structure = self._analyze_term_structure(options_data)
                
                return {
                    'surface': surface,
                    'skew': skew,
                    'term_structure': term_structure,
                    'summary': self._summarize_volatility_analysis(surface, skew, term_structure)
                }
                
        except Exception as e:
            logger.error(f"Error analyzing volatility surface: {str(e)}")
            return {}

    def _calculate_iv_surface(self, options_data: pd.DataFrame) -> Dict:
        """Calculate implied volatility surface"""
        try:
            # Group by expiration and strike
            grouped = options_data.groupby(['expiration_date', 'strike'])['implied_volatility'].mean()
            
            # Create surface matrix
            expirations = sorted(options_data['expiration_date'].unique())
            strikes = sorted(options_data['strike'].unique())
            surface = pd.DataFrame(index=strikes, columns=expirations)
            
            for (exp, strike), iv in grouped.items():
                surface.loc[strike, exp] = iv
            
            return {
                'surface_data': surface.to_dict(),
                'expirations': expirations,
                'strikes': strikes
            }
            
        except Exception as e:
            logger.error(f"Error calculating IV surface: {str(e)}")
            return {}

    def _calculate_chain_greeks(self, options_data: pd.DataFrame, 
                              current_price: float) -> Dict:
        """Calculate Greeks for entire options chain"""
        greeks = {
            'total_delta': 0.0,
            'total_gamma': 0.0,
            'total_theta': 0.0,
            'total_vega': 0.0,
            'by_expiration': {}
        }
        
        for _, row in options_data.iterrows():
            option = OptionContract(
                symbol=row['symbol'],
                expiration=datetime.strptime(row['expiration_date'], '%Y-%m-%d'),
                strike=row['strike'],
                option_type=row['option_type'],
                bid=row['bid'],
                ask=row['ask'],
                implied_volatility=row['implied_volatility'],
                open_interest=row['open_interest'],
                volume=row['volume']
            )
            
            option_greeks = self.calculate_greeks(option, current_price)
            
            # Update totals
            greeks['total_delta'] += option_greeks.get('delta', 0) * row['open_interest']
            greeks['total_gamma'] += option_greeks.get('gamma', 0) * row['open_interest']
            greeks['total_theta'] += option_greeks.get('theta', 0) * row['open_interest']
            greeks['total_vega'] += option_greeks.get('vega', 0) * row['open_interest']
            
            # Update by expiration
            exp = row['expiration_date']
            if exp not in greeks['by_expiration']:
                greeks['by_expiration'][exp] = {
                    'delta': 0.0,
                    'gamma': 0.0,
                    'theta': 0.0,
                    'vega': 0.0
                }
            
            greeks['by_expiration'][exp]['delta'] += option_greeks.get('delta', 0) * row['open_interest']
            greeks['by_expiration'][exp]['gamma'] += option_greeks.get('gamma', 0) * row['open_interest']
            greeks['by_expiration'][exp]['theta'] += option_greeks.get('theta', 0) * row['open_interest']
            greeks['by_expiration'][exp]['vega'] += option_greeks.get('vega', 0) * row['open_interest']
        
        return greeks

    def _calculate_put_call_ratio(self, options_data: pd.DataFrame) -> float:
        """Calculate put/call ratio"""
        call_volume = options_data[options_data['option_type'] == 'call']['volume'].sum()
        put_volume = options_data[options_data['option_type'] == 'put']['volume'].sum()
        return put_volume / call_volume if call_volume > 0 else 0

    def _analyze_options_volume(self, options_data: pd.DataFrame) -> Dict:
        """Analyze options trading volume"""
        return {
            'total_volume': int(options_data['volume'].sum()),
            'call_volume': int(options_data[options_data['option_type'] == 'call']['volume'].sum()),
            'put_volume': int(options_data[options_data['option_type'] == 'put']['volume'].sum()),
            'volume_by_expiration': options_data.groupby('expiration_date')['volume'].sum().to_dict(),
            'volume_by_strike': options_data.groupby('strike')['volume'].sum().to_dict()
        }

    def _analyze_open_interest(self, options_data: pd.DataFrame) -> Dict:
        """Analyze open interest distribution"""
        return {
            'total_open_interest': int(options_data['open_interest'].sum()),
            'call_open_interest': int(options_data[options_data['option_type'] == 'call']['open_interest'].sum()),
            'put_open_interest': int(options_data[options_data['option_type'] == 'put']['open_interest'].sum()),
            'open_interest_by_expiration': options_data.groupby('expiration_date')['open_interest'].sum().to_dict(),
            'open_interest_by_strike': options_data.groupby('strike')['open_interest'].sum().to_dict()
        }

    def _analyze_strike_clustering(self, options_data: pd.DataFrame, 
                                 current_price: float) -> Dict:
        """Analyze strike price clustering"""
        strike_volume = options_data.groupby('strike')[['volume', 'open_interest']].sum()
        
        # Find strike clusters
        clusters = []
        rolling_volume = strike_volume['volume'].rolling(window=3, center=True).mean()
        rolling_oi = strike_volume['open_interest'].rolling(window=3, center=True).mean()
        
        for strike in strike_volume.index:
            if abs(strike - current_price) / current_price <= 0.1:  # Within 10% of current price
                if rolling_volume[strike] > strike_volume['volume'].mean() * 1.5:
                    clusters.append({
                        'strike': float(strike),
                        'volume': int(strike_volume.loc[strike, 'volume']),
                        'open_interest': int(strike_volume.loc[strike, 'open_interest']),
                        'distance_to_price': float(strike - current_price)
                    })
        
        return {
            'clusters': clusters,
            'avg_volume_per_strike': float(strike_volume['volume'].mean()),
            'max_volume_strike': float(strike_volume['volume'].idxmax()),
            'max_oi_strike': float(strike_volume['open_interest'].idxmax())
        }

    # Greek calculation methods
    def _calculate_delta(self, S: float, K: float, T: float, 
                        sigma: float, option_type: str) -> float:
        """Calculate option delta"""
        d1 = self._calculate_d1(S, K, T, sigma)
        if option_type.lower() == 'call':
            return norm.cdf(d1)
        else:
            return norm.cdf(d1) - 1

    def _calculate_gamma(self, S: float, K: float, T: float, sigma: float) -> float:
        """Calculate option gamma"""
        d1 = self._calculate_d1(S, K, T, sigma)
        return norm.pdf(d1) / (S * sigma * np.sqrt(T))

    def _calculate_theta(self, S: float, K: float, T: float, 
                        sigma: float, option_type: str) -> float:
        """Calculate option theta"""
        d1 = self._calculate_d1(S, K, T, sigma)
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type.lower() == 'call':
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - 
                    self.risk_free_rate * K * np.exp(-self.risk_free_rate * T) * norm.cdf(d2))
        else:
            theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + 
                    self.risk_free_rate * K * np.exp(-self.risk_free_rate * T) * norm.cdf(-d2))
            
        return theta

    def _calculate_vega(self, S: float, K: float, T: float, sigma: float) -> float:
        """Calculate option vega"""
        d1 = self._calculate_d1(S, K, T, sigma)
        return S * np.sqrt(T) * norm.pdf(d1)
    
    def _calculate_rho(self, S: float, K: float, T: float, 
                      sigma: float, option_type: str) -> float:
        """Calculate option rho"""
        d1 = self._calculate_d1(S, K, T, sigma)
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type.lower() == 'call':
            return K * T * np.exp(-self.risk_free_rate * T) * norm.cdf(d2)
        else:
            return -K * T * np.exp(-self.risk_free_rate * T) * norm.cdf(-d2)

    def _calculate_d1(self, S: float, K: float, T: float, sigma: float) -> float:
        """Calculate d1 for Black-Scholes formula"""
        return (np.log(S/K) + (self.risk_free_rate + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))

    def _analyze_volatility_skew(self, options_data: pd.DataFrame) -> Dict:
        """Analyze volatility skew"""
        try:
            # Group by expiration date
            skew_by_expiry = {}
            
            for expiry in options_data['expiration_date'].unique():
                expiry_data = options_data[options_data['expiration_date'] == expiry]
                
                # Calculate ATM volatility
                atm_vol = expiry_data[expiry_data['moneyness'].abs() < 0.01]['implied_volatility'].mean()
                
                # Calculate OTM put and call volatilities
                otm_put_vol = expiry_data[(expiry_data['moneyness'] < -0.05) & 
                                        (expiry_data['option_type'] == 'put')]['implied_volatility'].mean()
                otm_call_vol = expiry_data[(expiry_data['moneyness'] > 0.05) & 
                                         (expiry_data['option_type'] == 'call')]['implied_volatility'].mean()
                
                skew_by_expiry[expiry] = {
                    'atm_vol': float(atm_vol),
                    'otm_put_vol': float(otm_put_vol),
                    'otm_call_vol': float(otm_call_vol),
                    'put_skew': float(otm_put_vol - atm_vol) if not np.isnan(otm_put_vol) else 0,
                    'call_skew': float(otm_call_vol - atm_vol) if not np.isnan(otm_call_vol) else 0
                }
            
            return {
                'skew_by_expiry': skew_by_expiry,
                'average_put_skew': np.mean([data['put_skew'] for data in skew_by_expiry.values()]),
                'average_call_skew': np.mean([data['call_skew'] for data in skew_by_expiry.values()])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volatility skew: {str(e)}")
            return {}

    def _analyze_term_structure(self, options_data: pd.DataFrame) -> Dict:
        """Analyze volatility term structure"""
        try:
            # Group by expiration and calculate ATM volatility
            term_structure = {}
            
            for expiry in sorted(options_data['expiration_date'].unique()):
                expiry_data = options_data[options_data['expiration_date'] == expiry]
                atm_vol = expiry_data[expiry_data['moneyness'].abs() < 0.01]['implied_volatility'].mean()
                
                term_structure[expiry] = {
                    'atm_vol': float(atm_vol),
                    'days_to_expiry': (datetime.strptime(expiry, '%Y-%m-%d') - datetime.now()).days
                }
            
            # Calculate term structure slope
            days = [data['days_to_expiry'] for data in term_structure.values()]
            vols = [data['atm_vol'] for data in term_structure.values()]
            
            if len(days) > 1:
                slope = np.polyfit(days, vols, 1)[0]
            else:
                slope = 0
            
            return {
                'term_structure': term_structure,
                'slope': float(slope),
                'short_term_vol': float(min(vols)) if vols else 0,
                'long_term_vol': float(max(vols)) if vols else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing term structure: {str(e)}")
            return {}

    def _analyze_covered_call(self, symbol: str, current_price: float, 
                            params: Dict) -> Dict:
        """Analyze covered call strategy"""
        try:
            expiry = params.get('expiration')
            strike = params.get('strike')
            
            with self.get_connection() as conn:
                # Get call option data
                option_data = pd.read_sql_query("""
                    SELECT *
                    FROM options_chain
                    WHERE symbol = ?
                    AND expiration_date = ?
                    AND strike = ?
                    AND option_type = 'call'
                """, conn, params=[symbol, expiry, strike])
                
                if option_data.empty:
                    return {}
                
                option = option_data.iloc[0]
                
                # Calculate metrics
                premium = (option['bid'] + option['ask']) / 2
                max_profit = premium + (strike - current_price)
                max_loss = current_price - premium
                breakeven = current_price - premium
                
                # Calculate Greeks
                greeks = self.calculate_greeks(
                    OptionContract(
                        symbol=symbol,
                        expiration=datetime.strptime(expiry, '%Y-%m-%d'),
                        strike=strike,
                        option_type='call',
                        bid=option['bid'],
                        ask=option['ask'],
                        implied_volatility=option['implied_volatility'],
                        open_interest=option['open_interest'],
                        volume=option['volume']
                    ),
                    current_price
                )
                
                return {
                    'premium': float(premium),
                    'max_profit': float(max_profit),
                    'max_loss': float(max_loss),
                    'breakeven': float(breakeven),
                    'yield': float(premium / current_price * 100),
                    'greeks': greeks,
                    'probability_profit': self._calculate_probability_profit(
                        current_price, strike, option['implied_volatility'], 
                        (datetime.strptime(expiry, '%Y-%m-%d') - datetime.now()).days / 365.0
                    )
                }
                
        except Exception as e:
            logger.error(f"Error analyzing covered call: {str(e)}")
            return {}

    def _calculate_probability_profit(self, S: float, K: float, 
                                   sigma: float, T: float) -> float:
        """Calculate probability of profit"""
        try:
            d2 = (np.log(S/K) + (self.risk_free_rate - 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
            return float(norm.cdf(d2))
        except:
            return 0.0

if __name__ == "__main__":
    # Example usage
    analyzer = OptionsAnalyzer("./data/investsage.db")
    
    # Analyze options chain
    chain_analysis = analyzer.analyze_options_chain("AAPL")
    print("\nOptions Chain Analysis:")
    print(chain_analysis)
    
    # Analyze volatility surface
    vol_surface = analyzer.analyze_volatility_surface("AAPL")
    print("\nVolatility Surface Analysis:")
    print(vol_surface)
    
    # Analyze covered call strategy
    strategy_params = {
        'expiration': '2024-02-16',
        'strike': 190.0
    }
    covered_call = analyzer.analyze_strategy("AAPL", "covered_call", strategy_params)
    print("\nCovered Call Analysis:")
    print(covered_call)