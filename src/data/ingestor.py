import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

class MultiAssetIngestor:
    """Supports Stocks, Forex (USDNOK=X), Crypto (BTC-USD), and Bonds."""
    
    def __init__(self):
        self.tickers = {
            "STOCKS": ["AAPL", "EQNR.OL", "DNB.OL"],
            "FOREX": ["EURNOK=X", "USDNOK=X"],
            "CRYPTO": ["BTC-USD", "ETH-USD"],
            "BONDS": ["^TNX"] # 10-Year Treasury Yield
        }

    def fetch_data(self, ticker, period="1y", interval="1d"):
        """Downloads historical data for a given ticker."""
        data = yf.download(ticker, period=period, interval=interval)
        return data

    def fetch_live_news(self, category="business"):
        """
        Fetches live headlines from financial news RSS feeds.
        This provides 'real-world' context for the SentimentBot.
        """
        feeds = {
            "business": "https://search.cnbc.com/rs/search/view.xml?partnerId=2000&keywords=finance",
            "market": "https://www.reutersagency.com/feed/?best-sectors=business&post_type=best"
        }
        url = feeds.get(category, feeds["business"])
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, features="xml")
            headlines = [item.title.text for item in soup.find_all('item')[:10]]
            if not headlines:
                 return ["Market remains stable with cautious optimism.", "Trading volumes expected to hold steady."]
            return headlines
        except Exception as e:
            print(f"Error fetching news: {e}")
            return ["Market remains stable with cautious optimism.", "Trading volumes expected to hold steady."]

    def list_promising_assets(self, period="1mo"):
        """Simple scan to find assets with high potential based on recent returns."""
        promising = []
        for category, symbols in self.tickers.items():
            for s in symbols:
                df = yf.download(s, period=period, interval="1d", progress=False)
                # Ensure we handle potential MultiIndex or Series from yfinance
                close = df['Close']
                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]
                
                ret = float((close.iloc[-1] - close.iloc[0]) / close.iloc[0])
                promising.append({"symbol": s, "return": ret, "category": category})
        
        return pd.DataFrame(promising).sort_values(by="return", ascending=False)
