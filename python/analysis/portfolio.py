from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import logging
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TaxLot:
    shares: float
    cost_basis: float
    purchase_date: datetime
    is_long_term: bool = False

@dataclass
class Position:
    symbol: str
    weight: float
    current_price: float = 0.0
    tax_lots: List[TaxLot] = None
    
    def __post_init__(self):
        if self.tax_lots is None:
            self.tax_lots = []
    
    @property
    def shares(self) -> float:
        return sum(lot.shares for lot in self.tax_lots)
    
    @property
    def market_value(self) -> float:
        return self.shares * self.current_price
    
    @property
    def average_cost(self) -> float:
        total_cost = sum(lot.shares * lot.cost_basis for lot in self.tax_lots)
        return total_cost / self.shares if self.shares > 0 else 0

class TaxAwarePortfolioAnalyzer:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.long_term_tax_rate = 0.20  # 20% for long-term gains
        self.short_term_tax_rate = 0.37  # 37% for short-term gains
        
    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def suggest_tax_efficient_rebalancing(self, 
                                        positions: List[Position],
                                        tolerance: float = 0.05,
                                        tax_sensitivity: float = 0.5) -> Dict:
        """
        Suggest tax-efficient rebalancing trades
        
        Args:
            positions: List of portfolio positions with tax lots
            tolerance: Maximum deviation from target weight
            tax_sensitivity: 0-1 scale, higher means more tax-sensitive
        """
        try:
            total_value = sum(p.market_value for p in positions)
            suggestions = []
            tax_impact = 0
            
            # Calculate current vs target weights
            position_analysis = []
            for position in positions:
                current_weight = position.market_value / total_value
                weight_diff = position.weight - current_weight
                
                position_analysis.append({
                    'position': position,
                    'current_weight': current_weight,
                    'weight_diff': weight_diff,
                    'need_adjustment': abs(weight_diff) > tolerance
                })
            
            # Sort positions by weight difference
            position_analysis.sort(key=lambda x: abs(x['weight_diff']), reverse=True)
            
            # Process sells first (to fund buys)
            for pos in position_analysis:
                if pos['weight_diff'] < -tolerance:
                    sell_suggestion = self._suggest_tax_efficient_sell(
                        pos['position'],
                        abs(pos['weight_diff']) * total_value,
                        tax_sensitivity
                    )
                    if sell_suggestion:
                        suggestions.append(sell_suggestion)
                        tax_impact += sell_suggestion['tax_impact']
            
            # Process buys
            available_cash = sum(s['proceeds'] for s in suggestions if s['action'] == 'sell')
            for pos in position_analysis:
                if pos['weight_diff'] > tolerance:
                    target_buy_value = min(
                        pos['weight_diff'] * total_value,
                        available_cash
                    )
                    if target_buy_value > 0:
                        buy_suggestion = {
                            'action': 'buy',
                            'symbol': pos['position'].symbol,
                            'shares': target_buy_value / pos['position'].current_price,
                            'estimated_value': target_buy_value,
                            'tax_impact': 0
                        }
                        suggestions.append(buy_suggestion)
                        available_cash -= target_buy_value
            
            return {
                'suggestions': suggestions,
                'total_tax_impact': tax_impact,
                'tax_savings': self._calculate_tax_savings(suggestions),
                'remaining_cash': available_cash
            }
            
        except Exception as e:
            logger.error(f"Error in tax-efficient rebalancing: {str(e)}")
            return {}

    def _suggest_tax_efficient_sell(self, position: Position, 
                                  target_value: float,
                                  tax_sensitivity: float) -> Optional[Dict]:
        """
        Suggest tax-efficient selling strategy for a position
        """
        try:
            if not position.tax_lots:
                return None
                
            # Sort tax lots by tax impact (loss harvest first, then lowest gains)
            tax_lots = sorted(position.tax_lots, 
                            key=lambda lot: (lot.cost_basis - position.current_price) / lot.cost_basis)
            
            shares_to_sell = target_value / position.current_price
            selected_lots = []
            total_proceeds = 0
            total_tax_impact = 0
            
            # First, harvest tax losses if available
            for lot in tax_lots:
                if lot.cost_basis > position.current_price:  # Tax loss
                    shares = min(shares_to_sell, lot.shares)
                    if shares > 0:
                        selected_lots.append({
                            'shares': shares,
                            'cost_basis': lot.cost_basis,
                            'is_long_term': lot.is_long_term
                        })
                        total_proceeds += shares * position.current_price
                        total_tax_impact += (lot.cost_basis - position.current_price) * shares * \
                                         (self.long_term_tax_rate if lot.is_long_term 
                                          else self.short_term_tax_rate)
                        shares_to_sell -= shares
                
                if shares_to_sell <= 0:
                    break
            
            # If we still need to sell more, consider tax sensitivity
            if shares_to_sell > 0:
                remaining_lots = [lot for lot in tax_lots 
                                if lot.cost_basis <= position.current_price]
                
                # Sort by tax impact, weighted by tax sensitivity
                remaining_lots.sort(key=lambda lot: 
                    ((position.current_price - lot.cost_basis) / lot.cost_basis) * \
                    (1 if lot.is_long_term else 2) * tax_sensitivity)
                
                for lot in remaining_lots:
                    shares = min(shares_to_sell, lot.shares)
                    if shares > 0:
                        selected_lots.append({
                            'shares': shares,
                            'cost_basis': lot.cost_basis,
                            'is_long_term': lot.is_long_term
                        })
                        total_proceeds += shares * position.current_price
                        total_tax_impact += (position.current_price - lot.cost_basis) * shares * \
                                         (self.long_term_tax_rate if lot.is_long_term 
                                          else self.short_term_tax_rate)
                        shares_to_sell -= shares
                    
                    if shares_to_sell <= 0:
                        break
            
            return {
                'action': 'sell',
                'symbol': position.symbol,
                'lots': selected_lots,
                'proceeds': total_proceeds,
                'tax_impact': total_tax_impact
            }
            
        except Exception as e:
            logger.error(f"Error in tax-efficient sell suggestion: {str(e)}")
            return None

    def _calculate_tax_savings(self, suggestions: List[Dict]) -> float:
        """
        Calculate tax savings compared to naive selling
        """
        try:
            naive_tax_impact = 0
            actual_tax_impact = sum(s['tax_impact'] for s in suggestions 
                                  if s['action'] == 'sell')
            
            # Calculate what tax impact would have been without tax-aware selection
            for suggestion in suggestions:
                if suggestion['action'] == 'sell':
                    for lot in suggestion['lots']:
                        naive_impact = (suggestion['proceeds'] / len(suggestion['lots'])) * \
                                     (self.short_term_tax_rate)  # Assume all short-term
                        naive_tax_impact += naive_impact
            
            return max(0, naive_tax_impact - actual_tax_impact)
            
        except Exception as e:
            logger.error(f"Error calculating tax savings: {str(e)}")
            return 0.0

    def analyze_tax_efficiency(self, positions: List[Position]) -> Dict:
        """
        Analyze current tax efficiency of portfolio
        """
        try:
            analysis = {
                'unrealized_gains': 0.0,
                'unrealized_losses': 0.0,
                'harvesting_opportunities': [],
                'long_term_gains_percent': 0.0,
                'tax_efficiency_score': 0.0
            }
            
            total_value = sum(p.market_value for p in positions)
            total_gains = 0
            long_term_gains = 0
            
            for position in positions:
                for lot in position.tax_lots:
                    gain = (position.current_price - lot.cost_basis) * lot.shares
                    if gain > 0:
                        analysis['unrealized_gains'] += gain
                        total_gains += gain
                        if lot.is_long_term:
                            long_term_gains += gain
                    else:
                        analysis['unrealized_losses'] += abs(gain)
                        # Check for harvesting opportunities
                        if abs(gain) > 5000:  # Threshold for harvesting
                            analysis['harvesting_opportunities'].append({
                                'symbol': position.symbol,
                                'shares': lot.shares,
                                'potential_harvest': abs(gain)
                            })
            
            if total_gains > 0:
                analysis['long_term_gains_percent'] = long_term_gains / total_gains
            
            # Calculate tax efficiency score (0-100)
            analysis['tax_efficiency_score'] = self._calculate_tax_efficiency_score(
                analysis['long_term_gains_percent'],
                analysis['unrealized_losses'] / total_value if total_value > 0 else 0,
                len(analysis['harvesting_opportunities'])
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in tax efficiency analysis: {str(e)}")
            return {}

    def _calculate_tax_efficiency_score(self, long_term_ratio: float,
                                     loss_ratio: float,
                                     harvest_opportunities: int) -> float:
        """
        Calculate overall tax efficiency score
        """
        # Weights for different components
        weights = {
            'long_term_ratio': 0.4,
            'loss_harvest': 0.4,
            'opportunities': 0.2
        }
        
        # Score components
        long_term_score = long_term_ratio * 100
        loss_harvest_score = min(loss_ratio * 200, 100)  # Cap at 100
        opportunity_score = max(0, 100 - harvest_opportunities * 10)  # Fewer opportunities is better
        
        return (long_term_score * weights['long_term_ratio'] +
                loss_harvest_score * weights['loss_harvest'] +
                opportunity_score * weights['opportunities'])

    def analyze_cost_basis_methods(self, position: Position) -> Dict:
        """
        Analyze different cost basis methods and their tax implications
        """
        try:
            methods = {
                'fifo': self._analyze_fifo(position),
                'lifo': self._analyze_lifo(position),
                'specific_lot': self._analyze_specific_lots(position),
                'average': self._analyze_average_cost(position)
            }
            
            # Compare tax implications
            tax_impact = {}
            for method, analysis in methods.items():
                tax_impact[method] = {
                    'short_term_gain': analysis['short_term_gain'],
                    'long_term_gain': analysis['long_term_gain'],
                    'total_tax': analysis['short_term_gain'] * self.short_term_tax_rate +
                                analysis['long_term_gain'] * self.long_term_tax_rate
                }
            
            return {
                'methods': methods,
                'tax_impact': tax_impact,
                'recommended_method': self._recommend_cost_basis_method(tax_impact)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing cost basis methods: {str(e)}")
            return {}

    def _analyze_fifo(self, position: Position) -> Dict:
        """FIFO cost basis analysis"""
        sorted_lots = sorted(position.tax_lots, key=lambda x: x.purchase_date)
        return self._calculate_gains_by_lots(position, sorted_lots)

    def _analyze_lifo(self, position: Position) -> Dict:
        """LIFO cost basis analysis"""
        sorted_lots = sorted(position.tax_lots, 
                           key=lambda x: x.purchase_date, 
                           reverse=True)
        return self._calculate_gains_by_lots(position, sorted_lots)

    def _analyze_specific_lots(self, position: Position) -> Dict:
        """Specific lot optimization"""
        # Sort lots by tax efficiency (minimize tax impact)
        sorted_lots = sorted(position.tax_lots, 
                           key=lambda x: self._calculate_lot_tax_efficiency(x, position.current_price))
        return self._calculate_gains_by_lots(position, sorted_lots)

    def _analyze_average_cost(self, position: Position) -> Dict:
        """Average cost basis analysis"""
        total_shares = sum(lot.shares for lot in position.tax_lots)
        total_cost = sum(lot.shares * lot.cost_basis for lot in position.tax_lots)
        avg_cost = total_cost / total_shares if total_shares > 0 else 0
        
        long_term_shares = sum(lot.shares for lot in position.tax_lots if lot.is_long_term)
        short_term_shares = total_shares - long_term_shares
        
        gain_per_share = position.current_price - avg_cost
        
        return {
            'average_cost': avg_cost,
            'long_term_gain': gain_per_share * long_term_shares,
            'short_term_gain': gain_per_share * short_term_shares
        }

    def plan_year_end_taxes(self, positions: List[Position]) -> Dict:
        """
        Generate year-end tax planning recommendations
        """
        try:
            # Analyze current tax situation
            current_analysis = self.analyze_tax_efficiency(positions)
            
            # Generate harvest recommendations
            harvest_recommendations = []
            for position in positions:
                harvest_opps = self._find_harvest_opportunities(position)
                if harvest_opps:
                    harvest_recommendations.append({
                        'symbol': position.symbol,
                        'opportunities': harvest_opps
                    })
            
            # Check for wash sales
            wash_sale_risks = self._check_wash_sale_risks(positions)
            
            # Project year-end tax liability
            tax_projection = self._project_tax_liability(positions)
            
            return {
                'harvest_recommendations': harvest_recommendations,
                'wash_sale_risks': wash_sale_risks,
                'tax_projection': tax_projection,
                'action_items': self._generate_tax_action_items(
                    current_analysis,
                    harvest_recommendations,
                    tax_projection
                )
            }
            
        except Exception as e:
            logger.error(f"Error in year-end tax planning: {str(e)}")
            return {}

    def _find_harvest_opportunities(self, position: Position) -> List[Dict]:
        """Find tax loss harvesting opportunities"""
        opportunities = []
        
        for lot in position.tax_lots:
            unrealized_gain = (position.current_price - lot.cost_basis) * lot.shares
            if unrealized_gain < -5000:  # Minimum harvest threshold
                opportunities.append({
                    'lot_shares': lot.shares,
                    'cost_basis': lot.cost_basis,
                    'unrealized_loss': abs(unrealized_gain),
                    'tax_savings': abs(unrealized_gain) * (
                        self.long_term_tax_rate if lot.is_long_term 
                        else self.short_term_tax_rate
                    ),
                    'wash_sale_date': lot.purchase_date + timedelta(days=30)
                })
        
        return opportunities

    def _check_wash_sale_risks(self, positions: List[Position]) -> List[Dict]:
        """Check for potential wash sale risks"""
        risks = []
        today = datetime.now()
        
        for position in positions:
            recent_lots = [lot for lot in position.tax_lots 
                         if (today - lot.purchase_date).days < 30]
            if recent_lots:
                risks.append({
                    'symbol': position.symbol,
                    'recent_purchases': [{
                        'shares': lot.shares,
                        'purchase_date': lot.purchase_date,
                        'wash_sale_expiry': lot.purchase_date + timedelta(days=30)
                    } for lot in recent_lots]
                })
        
        return risks

    def _project_tax_liability(self, positions: List[Position]) -> Dict:
        """Project year-end tax liability"""
        realized_gains = {
            'short_term': 0.0,
            'long_term': 0.0
        }
        unrealized_gains = {
            'short_term': 0.0,
            'long_term': 0.0
        }
        
        for position in positions:
            for lot in position.tax_lots:
                gain = (position.current_price - lot.cost_basis) * lot.shares
                if lot.is_long_term:
                    unrealized_gains['long_term'] += gain
                else:
                    unrealized_gains['short_term'] += gain
        
        return {
            'realized_gains': realized_gains,
            'unrealized_gains': unrealized_gains,
            'projected_tax': {
                'short_term': realized_gains['short_term'] * self.short_term_tax_rate,
                'long_term': realized_gains['long_term'] * self.long_term_tax_rate
            },
            'potential_tax_unrealized': {
                'short_term': unrealized_gains['short_term'] * self.short_term_tax_rate,
                'long_term': unrealized_gains['long_term'] * self.long_term_tax_rate
            }
        }

    def _generate_tax_action_items(self, current_analysis: Dict,
                                harvest_recommendations: List[Dict],
                                tax_projection: Dict) -> List[Dict]:
        """Generate prioritized tax action items"""
        action_items = []
        
        # Check for harvest opportunities
        if harvest_recommendations:
            action_items.append({
                'priority': 'high',
                'action': 'harvest_losses',
                'details': harvest_recommendations,
                'deadline': 'December 31'
            })
        
        # Check for gains harvesting if in lower tax bracket
        if tax_projection['projected_tax']['total'] < 1000:
            action_items.append({
                'priority': 'medium',
                'action': 'harvest_gains',
                'details': 'Consider realizing gains while in lower tax bracket',
                'deadline': 'December 31'
            })
        
        # Long-term holding period planning
        near_long_term = self._find_near_long_term_lots(positions)
        if near_long_term:
            action_items.append({
                'priority': 'medium',
                'action': 'hold_for_long_term',
                'details': near_long_term,
                'deadline': 'Varies'
            })
        
        return action_items

if __name__ == "__main__":
    # Example usage
    analyzer = TaxAwarePortfolioAnalyzer("./data/investsage.db")
    
    # Example positions with tax lots
    positions = [
        Position("AAPL", 0.4, 150.0, [
            TaxLot(50, 120.0, datetime(2021, 1, 1), True),
            TaxLot(50, 140.0, datetime(2022, 1, 1), False)
        ]),
        Position("MSFT", 0.3, 280.0, [
            TaxLot(30, 250.0, datetime(2021, 6, 1), True),
            TaxLot(20, 290.0, datetime(2022, 6, 1), False)
        ])
    ]
    
    # Analyze cost basis methods
    cost_basis_analysis = analyzer.analyze_cost_basis_methods(positions[0])
    print("\nCost Basis Analysis:")
    print(cost_basis_analysis)
    
    # Get year-end tax planning recommendations
    tax_plan = analyzer.plan_year_end_taxes(positions)
    print("\nYear-End Tax Planning:")
    print(tax_plan)

    # Get tax-efficient rebalancing suggestions
    rebalancing = analyzer.suggest_tax_efficient_rebalancing(
        positions,
        tolerance=0.05,
        tax_sensitivity=0.8
    )
    print("\nTax-Efficient Rebalancing Suggestions:")
    print(rebalancing)
    
    # Analyze tax efficiency
    tax_efficiency = analyzer.analyze_tax_efficiency(positions)
    print("\nTax Efficiency Analysis:")
    print(tax_efficiency)