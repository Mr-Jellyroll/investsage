
import logging
from typing import Dict
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon')
        
        self.sia = SentimentIntensityAnalyzer()
        
        # Add stock-specific terms to the lexicon
        self.add_stock_terms()

    def add_stock_terms(self):
        """Add stock market specific terms to the lexicon"""
        stock_terms = {
            # Bullish terms
            'bullish': 2.0,
            'buy': 1.5,
            'long': 1.0,
            'calls': 1.0,
            'moon': 2.0,
            'rocket': 2.0,
            'breaking out': 1.5,
            'breakout': 1.5,
            'support': 0.5,
            'undervalued': 1.5,
            
            # Bearish terms
            'bearish': -2.0,
            'sell': -1.5,
            'short': -1.0,
            'puts': -1.0,
            'drill': -2.0,
            'crash': -2.5,
            'dump': -2.0,
            'resistance': -0.5,
            'overvalued': -1.5,
            
            # Other market terms
            'volatility': -0.5,
            'squeeze': 1.0,
            'hold': 0.5,
            'hodl': 1.0,  # Crypto
            'diamond hands': 1.5,
            'paper hands': -1.0,
        }
        
        # Add terms to the lexicon
        self.sia.lexicon.update(stock_terms)
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze text and return sentiment scores
        Returns dict with compound, pos, neu, neg scores
        """
        try:
            scores = self.sia.polarity_scores(text)
            logger.debug(f"Sentiment scores: {scores}")
            return scores
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {'compound': 0.0, 'pos': 0.0, 'neg': 0.0, 'neu': 1.0}

    def get_sentiment_label(self, compound_score: float) -> str:
        """Convert compound score to sentiment label"""
        if compound_score >= 0.05:
            return 'bullish'
        elif compound_score <= -0.05:
            return 'bearish'
        else:
            return 'neutral'