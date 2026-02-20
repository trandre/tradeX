from src.training.bots import RiskTrainer, GrowthTrainer, SentimentTrainer, AnalyzerBot
from src.data.ingestor import MultiAssetIngestor
import pandas as pd

def training_phase():
    """
    Main Training Hub: 
    Coordinates different AI coaches to improve the overall trading strategy.
    """
    print("--- TradeX Advanced Training & Learning Phase ---")
    
    # 1. SETUP
    ingestor = MultiAssetIngestor()
    risk_coach = RiskTrainer()
    growth_coach = GrowthTrainer()
    sentiment_coach = SentimentTrainer()
    analyzer = AnalyzerBot()
    
    # 2. GET DATA
    print("\n[Data] Fetching market data and LIVE news headlines...")
    df = ingestor.fetch_data("AAPL", period="1y", interval="1d")
    close_prices = df['Close']
    if isinstance(close_prices, pd.DataFrame):
        close_prices = close_prices.iloc[:, 0]

    # Fetch real headlines for SentimentBot
    headlines = ingestor.fetch_live_news()
    print(f"Top Live Headline: {headlines[0] if headlines else 'None found'}")

    # 3. SENTIMENT TRAINING (The Mood Analyst)
    print("\n[Coach: SentimentBot] Analyzing LIVE market news...")
    sentiment_coach.run_training_session(headlines)

    # ... (rest of the coaches)

    # 6. ETHICAL INDEX DEMONSTRATION
    print("\n[Security] Testing New Ethical/Corruption Index Scores...")
    from src.intelligence.social import EthicalFilter
    ethics = EthicalFilter(min_score_threshold=40)
    
    # Test a 'Clean' asset
    asset_ok = {"ticker": "EQNR.OL", "country": "Norway", "segment": "Energy"}
    allowed, reason = ethics.is_allowed(asset_ok)
    print(f"Asset Norway/EQNR: {allowed} ({reason})")

    # Test a 'Corrupt/Unethical' asset
    asset_bad = {"ticker": "COAL_CORP", "country": "COUNTRY_X", "segment": "Energy"}
    allowed_bad, reason_bad = ethics.is_allowed(asset_bad)
    print(f"Asset COUNTRY_X/COAL_CORP: {allowed_bad} ({reason_bad})")

    # Mock some history for the analyzer to look at
    mock_history = [{'symbol': 'AAPL', 'side': 'buy', 'price': 150}]
    report = analyzer.run_training_session(mock_history)
    print("\nTraining Phase Complete. Learning report has been updated for the next session.")

if __name__ == "__main__":
    training_phase()
