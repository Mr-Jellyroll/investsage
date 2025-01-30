import logging
import sqlite3
from pathlib import Path
from typing import Dict

from .ml import MLAnalyzer
from .options import OptionsAnalyzer
from .portfolio import PortfolioAnalyzer
from .technical import TechnicalAnalyzer
from .sentiment import SentimentAnalyzer
from .risk import RiskAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Analyzer:
    """Main analyzer class combining all analysis capabilities"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'data' / 'investsage.db'
        self.db_path = str(db_path)
        
        # Initialize all analyzers
        self.ml = MLAnalyzer(self.db_path)
        self.options = OptionsAnalyzer(self.db_path)
        self.portfolio = PortfolioAnalyzer(self.db_path)
        self.technical = TechnicalAnalyzer(self.db_path)
        self.sentiment = SentimentAnalyzer(self.db_path)
        self.risk = RiskAnalyzer(self.db_path)

    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    def analyze_all(self, symbol: str) -> Dict:
        """Run complete analysis using all analyzers"""
        return {
            'technical': self.technical.analyze_technical_indicators(symbol),
            'ml_predictions': self.ml.predict_price(symbol),
            'sentiment': self.sentiment.analyze_sentiment(symbol),
            'risk': self.risk.analyze_risk(symbol),
            'options': self.options.analyze_options_chain(symbol),
            'portfolio_suggestion': self.portfolio.suggest_position_sizing(symbol, 100000)
        }

if __name__ == "__main__":
    # Example usage
    analyzer = Analyzer()
    
    symbol = "AAPL"
    analysis = analyzer.analyze_all(symbol)
    print("\nComplete Analysis:")
    print(analysis)