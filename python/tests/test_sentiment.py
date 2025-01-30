
import sys
from pathlib import Path
import logging

sys.path.append(str(Path(__file__).parent.parent))

from collectors.sentiment_analyzer import SentimentAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sentiment_analysis():
    analyzer = SentimentAnalyzer()
    
    test_cases = [
        (
            "AAPL is breaking out! Strong support at current levels, highly bullish 🚀",
            'bullish'
        ),
        (
            "Looks like TSLA is heading for a crash. Massive resistance and overbought.",
            'bearish'
        ),
        (
            "MSFT trading sideways today with average volume.",
            'neutral'
        ),
        (
            "To the moon! 🚀🚀🚀 Diamond hands on NVDA! Breaking out!",
            'bullish'
        ),
        (
            "Time to buy puts. This stock is overvalued and about to drill. 📉",
            'bearish'
        )
    ]
    
    for text, expected_sentiment in test_cases:
        scores = analyzer.analyze_text(text)
        sentiment = analyzer.get_sentiment_label(scores['compound'])
        
        print(f"\nText: {text}")
        print(f"Scores: {scores}")
        print(f"Overall sentiment: {sentiment}")
        print(f"Expected: {expected_sentiment}")
        
        assert sentiment == expected_sentiment, \
            f"Expected {expected_sentiment}, got {sentiment}"
    
    print("\nAll sentiment analysis tests passed!")

if __name__ == "__main__":
    test_sentiment_analysis()