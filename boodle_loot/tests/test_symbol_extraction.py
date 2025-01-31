import sys
from pathlib import Path
import logging

sys.path.append(str(Path(__file__).parent.parent))

from collectors.reddit_collector import RedditCollector

def test_symbol_extraction():
    collector = RedditCollector()
    
    test_cases = [
        (
            "Bought some $AAPL and MSFT today.",
            ["AAPL", "MSFT"]
        ),
        (
            "The NVIDIA (NVDA) CEO said AI is the future.",
            ["NVDA"]
        ),
        (
            "IMO the P/E ratio of TSLA is too high.",
            ["TSLA"]
        ),
        (
            "A CEO of INC CORP said IT IS good.",
            []  # Ignore common words and company terms
        ),
        (
            "Investing in AI and ML stocks like $AI",
            []  # Ignore AI as it's a common term
        ),
        (
            "Q&A with CEO about M&A and R&D impact on EPS",
            [] # Ignore business abbreviations
        ),
        (
            "The PM said UK GDP and USA CPI affected the ETF",
            [] # Ignore economic terms
        ),
        (
            "This company's P/E ratio and EPS look good IMO",
            [] # Ignore financial metrics
        ),
        (
            "FAANG stocks (FB META AAPL AMZN NFLX GOOG) are trending",
            ["META", "AAPL", "AMZN", "NFLX", "GOOG",]
        ),
        (
            "Looking at $AMD, NVDA, and INTC for semiconductor plays",
            ["AMD", "NVDA", "INTC"]
        )
    ]
    
    for text, expected in test_cases:
        result = collector.extract_ticker_symbols(text)
        print(f"\nText: {text}")
        print(f"Expected: {expected}")
        print(f"Got: {result}")
        assert result == expected, f"Expected {expected}, but got {result}"
    
    print("\nAll symbol extraction tests passed!")

if __name__ == "__main__":
    test_symbol_extraction()