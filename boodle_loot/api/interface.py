from typing import Dict, List, Optional, Union
from datetime import datetime
import logging
from pathlib import Path
import sqlite3

from .models import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisType,
    TechnicalAnalysisResponse,
    SentimentAnalysisResponse,
    MLPredictionResponse,
    OptionsAnalysisResponse,
    RiskAnalysisResponse,
    PortfolioAnalysisResponse
)

from ..analysis.base import Analyzer
from ..analysis.technical import TechnicalAnalyzer
from ..analysis.sentiment import SentimentAnalyzer
from ..analysis.ml import MLAnalyzer
from ..analysis.options import OptionsAnalyzer
from ..analysis.portfolio import PortfolioAnalyzer
from ..analysis.risk import RiskAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InvestSageAPI:
    """Main API interface for InvestSage analysis system"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the API interface"""
        try:
            # Set up database path
            if db_path is None:
                db_path = str(Path(__file__).parent.parent.parent / 'data' / 'investsage.db')
            
            # Initialize analyzers
            self.analyzer = Analyzer(db_path)
            self.technical = TechnicalAnalyzer(db_path)
            self.sentiment = SentimentAnalyzer(db_path)
            self.ml = MLAnalyzer(db_path)
            self.options = OptionsAnalyzer(db_path)
            self.portfolio = PortfolioAnalyzer(db_path)
            self.risk = RiskAnalyzer(db_path)
            
            logger.info(f"InvestSage API initialized with database at {db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing InvestSage API: {str(e)}")
            raise

    def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        try:
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'symbol': request.symbol,
                'analysis_type': request.analysis_type
            }
            
            if request.analysis_type == AnalysisType.ALL:
                data = self._perform_all_analysis(request)
            else:
                data = self._perform_single_analysis(request)
            
            return AnalysisResponse(
                success=True,
                data=data,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return AnalysisResponse(
                success=False,
                error=str(e)
            )

    def _perform_single_analysis(self, request: AnalysisRequest) -> Dict:
        if request.analysis_type == AnalysisType.TECHNICAL:
            return self.technical.analyze_technicals(request.symbol)
        elif request.analysis_type == AnalysisType.SENTIMENT:
            return self.sentiment.analyze_sentiment(request.symbol)
        elif request.analysis_type == AnalysisType.ML:
            return self.ml.predict_price(request.symbol)
        elif request.analysis_type == AnalysisType.OPTIONS:
            return self.options.analyze_options_chain(request.symbol)
        elif request.analysis_type == AnalysisType.PORTFOLIO:
            # Create a single position portfolio for analysis
            positions = [{"symbol": request.symbol, "weight": 1.0}]
            return self.portfolio.analyze_portfolio(positions)
        elif request.analysis_type == AnalysisType.RISK:
            return self.risk.analyze_risk(request.symbol)
        else:
            raise ValueError(f"Unknown analysis type: {request.analysis_type}")

    def _perform_all_analysis(self, request: AnalysisRequest) -> Dict:
        positions = [{"symbol": request.symbol, "weight": 1.0}]
        
        return {
            'technical': self.technical.analyze_technicals(request.symbol),
            'sentiment': self.sentiment.analyze_sentiment(request.symbol),
            'ml': self.ml.predict_price(request.symbol),
            'options': self.options.analyze_options_chain(request.symbol),
            'portfolio': self.portfolio.analyze_portfolio(positions),
            'risk': self.risk.analyze_risk(request.symbol)
        }

    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols"""
        try:
            with sqlite3.connect(self.analyzer.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT symbol FROM stocks ORDER BY symbol")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting symbols: {str(e)}")
            return []

    def get_analysis_capabilities(self) -> Dict:
        """Get available analysis capabilities"""
        return {
            'analysis_types': [at.value for at in AnalysisType],
            'supported_data_sources': [
                'market_data',
                'technical_indicators',
                'sentiment_analysis',
                'options_data',
                'sec_filings',
                'social_media'
            ]
        }