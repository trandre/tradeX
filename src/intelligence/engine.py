import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import pandas as pd

class IntelligenceEngine:
    """Collects news and suggests algorithms based on volatility."""
    
    def __init__(self):
        self.news_sources = {
            "reuters": "https://www.reuters.com/business/finance/",
            "bloomberg": "https://www.bloomberg.com/markets"
        }

    def fetch_latest_sentiment(self, query="trading"):
        """Simple mockup for news sentiment analysis."""
        # For a production setup, we'd use a real news API
        # This will return a sentiment score (Polarity: -1 to 1)
        sentiment = 0.1 # Placeholder
        return sentiment

    def recommend_algorithm(self, market_data):
        """Analyze market and suggest which strategy to apply."""
        close = market_data['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
            
        volatility = close.pct_change().std()
        
        if volatility > 0.02:
            return "Momentum (Trend Following) - High volatility suggests clear direction."
        elif volatility < 0.005:
            return "Mean Reversion (Grid Trading) - Low volatility suggests range-bound movement."
        else:
            return "Random Forest Classifier - Balanced market."

    def get_news_summary(self, symbol):
        """Simulate getting news context for a specific asset."""
        return f"Recent news for {symbol} indicates a mixed market sentiment with a focus on interest rates."
