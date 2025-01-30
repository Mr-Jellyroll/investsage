
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

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

    symbol: str
    analysis_type: AnalysisType
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    params: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
        data = asdict(self)
        # Convert enum to string
        data['analysis_type'] = data['analysis_type'].value
        # Convert dates to ISO format
        if data['start_date']:
            data['start_date'] = data['start_date'].isoformat()
        if data['end_date']:
            data['end_date'] = data['end_date'].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> 'AnalysisRequest':
        """Create from dictionary format"""
        # Convert string to enum
        if 'analysis_type' in data:
            data['analysis_type'] = AnalysisType(data['analysis_type'])
        # Convert ISO dates to datetime
        if 'start_date' in data and data['start_date']:
            data['start_date'] = datetime.fromisoformat(data['start_date'])
        if 'end_date' in data and data['end_date']:
            data['end_date'] = datetime.fromisoformat(data['end_date'])
        return cls(**data)

@dataclass
class TechnicalAnalysisResponse:
    """Technical analysis response data"""
    trend_indicators: Dict[str, float]
    momentum_indicators: Dict[str, float]
    volatility_indicators: Dict[str, float]
    volume_indicators: Dict[str, float]
    support_resistance: Dict[str, List[float]]
    patterns: List[Dict[str, str]]

@dataclass
class SentimentAnalysisResponse:
    """Sentiment analysis response data"""
    news_sentiment: float
    social_sentiment: float
    overall_sentiment: float
    sentiment_trends: List[Dict[str, Union[str, float]]]
    key_mentions: List[Dict[str, str]]
    article_count: int
    social_post_count: int

@dataclass
class MLPredictionResponse:
    """Machine learning prediction response data"""
    predictions: List[float]
    confidence_scores: List[float]
    feature_importance: Dict[str, float]
    model_metrics: Dict[str, float]
    last_updated: datetime

@dataclass
class OptionsAnalysisResponse:
    """Options analysis response data"""
    implied_volatility: float
    greeks: Dict[str, float]
    put_call_ratio: float
    volume_analysis: Dict[str, Union[int, float]]
    suggested_strategies: List[Dict[str, Union[str, float]]]

@dataclass
class RiskAnalysisResponse:
    """Risk analysis response data"""
    volatility: float
    var_95: float
    var_99: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    beta: float
    correlation_matrix: Dict[str, float]

@dataclass
class PortfolioAnalysisResponse:
    """Portfolio analysis response data"""
    position_sizing: Dict[str, float]
    risk_contribution: Dict[str, float]
    suggested_rebalancing: Dict[str, float]
    tax_implications: Dict[str, Union[float, str]]
    diversification_metrics: Dict[str, float]

@dataclass
class AnalysisResponse:
    """Standard analysis response format"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    warnings: Optional[List[str]] = None
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def success_response(cls, 
                        data: Dict, 
                        warnings: Optional[List[str]] = None,
                        metadata: Optional[Dict] = None) -> 'AnalysisResponse':
        """Create a success response"""
        return cls(
            success=True,
            data=data,
            warnings=warnings,
            metadata=metadata
        )

    @classmethod
    def error_response(cls,
                      error: str,
                      metadata: Optional[Dict] = None) -> 'AnalysisResponse':
        """Create an error response"""
        return cls(
            success=False,
            error=error,
            metadata=metadata
        )

@dataclass
class SystemStatus:
    """System status information"""
    status: str
    version: str
    last_updated: datetime
    components: Dict[str, str]
    database_connection: bool
    data_freshness: Dict[str, datetime]

    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
        data = asdict(self)
        # Convert datetime objects
        data['last_updated'] = data['last_updated'].isoformat()
        data['data_freshness'] = {
            k: v.isoformat() for k, v in data['data_freshness'].items()
        }
        return data

@dataclass
class APICapabilities:
    """API capabilities information"""
    analysis_types: List[str]
    data_sources: List[str]
    max_lookback_days: int
    supported_symbols: List[str]
    rate_limits: Dict[str, int]
    features: Dict[str, List[str]]

    def to_dict(self) -> Dict:
        """Convert to dictionary format"""
        return asdict(self)