import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import pandas as pd
import ollama
import json
import logging

class IntelligenceEngine:
    """Collects news and suggests algorithms based on volatility."""
    
    def __init__(self):
        self.news_sources = {
            "reuters": "https://www.reuters.com/business/finance/",
            "bloomberg": "https://www.bloomberg.com/markets"
        }
        self.logger = logging.getLogger("IntelligenceEngine")

    def fetch_latest_sentiment(self, query="trading"):
        """Simple mockup for news sentiment analysis."""
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

class ClaudeOllamaEngine:
    """
    An actual model implementation using Ollama to provide 'Claude-level' 
    intelligence for market analysis.
    """
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        self.logger = logging.getLogger("ClaudeOllamaEngine")
        self._check_ollama()

    def _check_ollama(self):
        try:
            ollama.list()
            self.active = True
        except Exception as e:
            self.logger.warning(f"Ollama service not detected. Falling back to heuristic model. Error: {e}")
            self.active = False

    def analyze_market_state(self, price_data, sentiment_score):
        """
        Uses LLM to analyze price trends and sentiment.
        """
        prompt = f"""
        Analyze the following market data and provide a trade recommendation.
        Price Trend (last 5 days): {price_data[-5:].tolist()}
        Current Sentiment Score: {sentiment_score:.2f} (-1 to 1)
        
        Return your answer as JSON with keys: 'confidence' (0-1), 'action' (BUY/SELL/HOLD), 'reasoning'.
        """
        
        if not self.active:
            # Heuristic fallback if Ollama is down
            confidence = 0.6 if abs(sentiment_score) > 0.2 else 0.4
            action = "BUY" if sentiment_score > 0 else "SELL" if sentiment_score < -0.1 else "HOLD"
            return {
                "confidence": confidence,
                "action": action,
                "reasoning": "Heuristic fallback (Ollama offline). Analysis based on sentiment magnitude."
            }

        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'system', 'content': 'You are a professional trading analyst.'},
                {'role': 'user', 'content': prompt},
            ])
            # Attempt to parse JSON from the response
            content = response['message']['content']
            # Simple extractor for json block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            return json.loads(content)
        except Exception as e:
            self.logger.error(f"Error calling Ollama: {e}")
            return {"confidence": 0.5, "action": "HOLD", "reasoning": f"LLM Error: {e}"}
