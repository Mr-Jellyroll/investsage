from typing import Optional, Dict, List, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class AnalysisType(str, Enum):
    TECHNICAL = "technical"
    SENTIMENT = "sentiment"
    ML = "ml"
    OPTIONS = "options"
    PORTFOLIO = "portfolio"
    RISK = "risk"
    ALL = "all"

# Request Models
class AnalysisRequest(BaseModel):
    symbol: str
    analysis_type: AnalysisType = Field(default=AnalysisType.ALL)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    params: Optional[Dict] = None

# Technical Analysis Models
class TechnicalIndicators(BaseModel):
    sma20: float
    sma50: float
    rsi: float
    macd: Dict[str, float]

class TechnicalAnalysisResponse(BaseModel):
    indicators: TechnicalIndicators
    signals: List[Dict[str, str]]
    trends: Dict[str, str]

# Sentiment Analysis Models
class SentimentScore(BaseModel):
    score: float
    confidence: float

class SentimentAnalysisResponse(BaseModel):
    overall_sentiment: SentimentScore
    news_sentiment: Optional[SentimentScore]
    social_sentiment: Optional[SentimentScore]
    trends: List[Dict[str, Union[str, float]]]

# ML Models
class MLPredictionResponse(BaseModel):
    predictions: List[float]
    confidence_scores: List[float]
    feature_importance: Dict[str, float]
    timestamps: List[str]

# Options Models
class OptionGreeks(BaseModel):
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float

class OptionsAnalysisResponse(BaseModel):
    implied_volatility: float
    greeks: OptionGreeks
    recommendations: List[Dict[str, Union[str, float]]]

# Risk Models
class RiskMetrics(BaseModel):
    var_95: float
    cvar_95: float
    sharpe_ratio: float
    sortino_ratio: float
    beta: float

class RiskAnalysisResponse(BaseModel):
    metrics: RiskMetrics
    stress_tests: Dict[str, float]
    correlations: Dict[str, float]

# Portfolio Models
class PortfolioMetrics(BaseModel):
    allocation: Dict[str, float]
    risk_contribution: Dict[str, float]
    expected_return: float

class PortfolioAnalysisResponse(BaseModel):
    metrics: PortfolioMetrics
    recommendations: List[Dict[str, Union[str, float]]]
    rebalancing: Optional[Dict[str, float]]

# General Response
class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    warnings: Optional[List[str]] = None
    metadata: Optional[Dict] = None