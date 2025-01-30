from typing import Dict, List, Optional, Union
from datetime import datetime
import logging
from pathlib import Path
import sqlite3

from .validation import RequestValidator
from .errors import ValidationError, create_error_response
from .models import (
    AnalysisRequest, AnalysisResponse, AnalysisType,
    TechnicalAnalysisResponse, SentimentAnalysisResponse,
    MLPredictionResponse, OptionsAnalysisResponse,
    RiskAnalysisResponse, PortfolioAnalysisResponse
)

from ..analysis.base import Analyzer
from ..analysis.technical import TechnicalAnalyzer
from ..analysis.sentiment import SentimentAnalyzer
from ..analysis.ml import MLAnalyzer
from ..analysis.options import OptionsAnalyzer
from ..analysis.portfolio import TaxAwarePortfolioAnalyzer
from ..analysis.risk import RiskAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    TECHNICAL = "technical"
    SENTIMENT = "sentiment"
    ML = "ml"
    OPTIONS = "options"
    PORTFOLIO = "portfolio"
    RISK = "risk"
    ALL = "all"

@dataclass
class AnalysisRequest:
    """Standardized analysis request format"""
    symbol: str
    analysis_type: AnalysisType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    params: Optional[Dict] = None

@dataclass
class AnalysisResponse:
    """Standardized analysis response format"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    warnings: Optional[List[str]] = None
    metadata: Optional[Dict] = None

class ValidationError(Exception):
    """Custom exception for input validation errors"""
    pass

class InvestSageAPI:
    """Main API interface for InvestSage analysis system"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the API interface"""
        try:
            # Set up database path
            if db_path is None:
                db_path = str(Path(__file__).parent.parent / 'data' / 'investsage.db')
            
            # Initialize analyzers
            self.analyzer = Analyzer(db_path)
            self.technical = TechnicalAnalyzer(db_path)
            self.sentiment = SentimentAnalyzer(db_path)
            self.ml = MLAnalyzer(db_path)
            self.options = OptionsAnalyzer(db_path)
            self.portfolio = TaxAwarePortfolioAnalyzer(db_path)
            self.risk = RiskAnalyzer(db_path)
            
            logger.info(f"InvestSage API initialized with database at {db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing InvestSage API: {str(e)}")
            raise

    def analyze(self, request: Union[AnalysisRequest, Dict]) -> AnalysisResponse:
      
        try:

            if isinstance(request, dict):
                request = self._convert_dict_to_request(request)
            
            self._validate_request(request)
            
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'symbol': request.symbol,
                'analysis_type': request.analysis_type.value
            }
            
            # Perform requested analysis
            if request.analysis_type == AnalysisType.ALL:
                data = self._perform_all_analysis(request)
            else:
                data = self._perform_single_analysis(request)
            
            return AnalysisResponse(
                success=True,
                data=data,
                metadata=metadata
            )
            
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return AnalysisResponse(
                success=False,
                error=f"Validation error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error performing analysis: {str(e)}")
            return AnalysisResponse(
                success=False,
                error=f"Analysis error: {str(e)}"
            )

    def _validate_request(self, request: AnalysisRequest) -> None:
        """Validate analysis request"""
        if not request.symbol:
            raise ValidationError("Symbol is required")
        
        if not isinstance(request.symbol, str):
            raise ValidationError("Symbol must be a string")
        
        if len(request.symbol) > 10:
            raise ValidationError("Symbol is too long")
        
        if request.start_date and request.end_date:
            if request.start_date > request.end_date:
                raise ValidationError("Start date must be before end date")
        
        # Check if symbol exists in database
        try:
            with sqlite3.connect(self.analyzer.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM stocks WHERE symbol = ?", 
                    (request.symbol,)
                )
                if not cursor.fetchone():
                    raise ValidationError(f"Symbol {request.symbol} not found in database")
                
        except sqlite3.Error as e:
            logger.error(f"Database error during validation: {str(e)}")
            raise ValidationError(f"Database error: {str(e)}")

    def _perform_single_analysis(self, request: AnalysisRequest) -> Dict:
        """Perform a single type of analysis"""
        if request.analysis_type == AnalysisType.TECHNICAL:
            return self.technical.analyze_technicals(
                request.symbol,
                days=self._calculate_days(request.start_date, request.end_date)
            )
        
        elif request.analysis_type == AnalysisType.SENTIMENT:
            return self.sentiment.analyze_sentiment(
                request.symbol,
                days=self._calculate_days(request.start_date, request.end_date)
            )
        
        elif request.analysis_type == AnalysisType.ML:
            return self.ml.predict_price(
                request.symbol,
                days_ahead=request.params.get('days_ahead', 5) if request.params else 5
            )
        
        elif request.analysis_type == AnalysisType.OPTIONS:
            return self.options.analyze_options_chain(request.symbol)
        
        elif request.analysis_type == AnalysisType.PORTFOLIO:
            return self.portfolio.analyze_tax_efficiency([{
                'symbol': request.symbol,
                'weight': 1.0
            }])
        
        elif request.analysis_type == AnalysisType.RISK:
            return self.risk.analyze_risk(
                request.symbol,
                days=self._calculate_days(request.start_date, request.end_date)
            )
        
        else:
            raise ValidationError(f"Unknown analysis type: {request.analysis_type}")

    def _perform_all_analysis(self, request: AnalysisRequest) -> Dict:
        """Perform all types of analysis"""
        return {
            'technical': self.technical.analyze_technicals(request.symbol),
            'sentiment': self.sentiment.analyze_sentiment(request.symbol),
            'ml_predictions': self.ml.predict_price(request.symbol),
            'options': self.options.analyze_options_chain(request.symbol),
            'portfolio': self.portfolio.analyze_tax_efficiency([{
                'symbol': request.symbol,
                'weight': 1.0
            }]),
            'risk': self.risk.analyze_risk(request.symbol)
        }

    def _convert_dict_to_request(self, request_dict: Dict) -> AnalysisRequest:
        """Convert dictionary to AnalysisRequest object"""
        try:
            # Convert string to AnalysisType enum
            analysis_type = AnalysisType(request_dict.get('analysis_type', 'all'))
            
            # Convert date strings to datetime objects if provided
            start_date = None
            if 'start_date' in request_dict:
                start_date = datetime.fromisoformat(request_dict['start_date'])
                
            end_date = None
            if 'end_date' in request_dict:
                end_date = datetime.fromisoformat(request_dict['end_date'])
            
            return AnalysisRequest(
                symbol=request_dict['symbol'],
                analysis_type=analysis_type,
                start_date=start_date,
                end_date=end_date,
                params=request_dict.get('params')
            )
            
        except (KeyError, ValueError) as e:
            raise ValidationError(f"Error converting request dict: {str(e)}")

    def _calculate_days(self, start_date: Optional[datetime], 
                       end_date: Optional[datetime]) -> int:
        """Calculate number of days between dates, default to 90 if not specified"""
        if start_date and end_date:
            return (end_date - start_date).days
        return 90  # Default analysis period

    def get_available_symbols(self) -> List[str]:
        """Get list of available symbols in database"""
        try:
            with sqlite3.connect(self.analyzer.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT symbol FROM stocks ORDER BY symbol")
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error getting available symbols: {str(e)}")
            return []

    def get_analysis_capabilities(self) -> Dict:
        """Get information about available analysis capabilities"""
        return {
            'analysis_types': [at.value for at in AnalysisType],
            'supported_data_sources': [
                'market_data',
                'technical_indicators',
                'sentiment_analysis',
                'options_data',
                'sec_filings',
                'social_media'
            ],
            'available_timeframes': [
                '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'
            ],
            'ml_capabilities': [
                'price_prediction',
                'trend_analysis',
                'anomaly_detection'
            ]
        }

def main():
    """Example usage of the API"""
    # Initialize API
    api = InvestSageAPI()
    
    # Example 1: Basic technical analysis
    request = AnalysisRequest(
        symbol="AAPL",
        analysis_type=AnalysisType.TECHNICAL
    )
    response = api.analyze(request)
    print("\nTechnical Analysis Response:")
    print(response)
    
    # Example 2: All analysis using dict input
    request_dict = {
        'symbol': 'MSFT',
        'analysis_type': 'all',
        'start_date': '2024-01-01T00:00:00',
        'end_date': '2024-01-30T00:00:00'
    }
    response = api.analyze(request_dict)
    print("\nComplete Analysis Response:")
    print(response)

if __name__ == "__main__":
    main()