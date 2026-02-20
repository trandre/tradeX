from src.training.bots import RiskTrainer, GrowthTrainer, SentimentTrainer, AnalyzerBot, EthicsBot
from src.data.ingestor import MultiAssetIngestor
from src.security.guardrails import Guardrail
import pandas as pd
import time

def hardcore_training():
    """
    Intensive Training Phase:
    - Multi-asset (Stocks, Forex, Crypto, Bonds)
    - Multi-year (5 years where available)
    - Stress-testing under various market conditions
    """
    print("="*60)
    print("      TRADEX HARDCORE TRAINING: COMMENCING INTENSIVE PHASE")
    print("="*60)
    
    ingestor = MultiAssetIngestor()
    risk_coach = RiskTrainer()
    growth_coach = GrowthTrainer()
    sentiment_coach = SentimentTrainer()
    analyzer = AnalyzerBot()
    ethics = EthicsBot()
    
    assets = [
        {"symbol": "AAPL", "cat": "STOCKS"},
        {"symbol": "BTC-USD", "cat": "CRYPTO"},
        {"symbol": "USDNOK=X", "cat": "FOREX"},
        {"symbol": "^TNX", "cat": "BONDS"}
    ]
    
    training_results = []

    for asset in assets:
        symbol = asset['symbol']
        print(f"\n[Training] Processing asset: {symbol} ({asset['cat']})")
        
        # 1. FETCH 5 YEARS OF DATA
        print(f"  -> Downloading 5-year historical timeline for {symbol}...")
        df = ingestor.fetch_data(symbol, period="5y", interval="1d")
        if df.empty:
            print(f"  -> Skipping {symbol}: No data found.")
            continue
            
        prices = df['Close']
        if isinstance(prices, pd.DataFrame): prices = prices.iloc[:, 0]

        # 2. INTENSIVE RISK STRESS-TESTING
        print(f"  -> Running RiskManager stress tests...")
        for sl in [0.01, 0.03, 0.05, 0.08, 0.12]:
            perf = risk_coach.run_training_session(prices, stop_loss_pct=sl)
            training_results.append({"symbol": symbol, "type": "Risk", "param": sl, "perf": perf})

        # 3. GROWTH OPTIMIZATION
        print(f"  -> Running GrowthSeeker RSI/Trend optimization...")
        for rsi_w in [7, 14, 21, 28]:
            perf = growth_coach.run_training_session(prices, rsi_window=rsi_w)
            training_results.append({"symbol": symbol, "type": "Growth", "param": rsi_w, "perf": perf})

    # 4. GLOBAL SENTIMENT DEEP DIVE
    print("\n[Training] Running Global Sentiment Analysis...")
    sectors = ["business", "market"]
    for sector in sectors:
        headlines = ingestor.fetch_live_news(category=sector)
        sentiment_coach.run_training_session(headlines)

    # 5. POST-TRAINING AUDIT & LEARNING
    print("\n" + "-"*40)
    print("[Audit] EthicsBot generating final compliance report...")
    mock_portfolio = [a['symbol'] for a in assets]
    ethics.run_training_session(mock_portfolio)
    
    print("[Audit] AnalyzerBot generating consolidated lessons learned...")
    mock_history = [{"symbol": a['symbol'], "side": "buy", "price": 100} for a in assets]
    analyzer.run_training_session(mock_history)

    print("\n" + "="*60)
    print("      HARDCORE TRAINING COMPLETE: SYSTEM INTELLIGENCE UPDATED")
    print("="*60)

if __name__ == "__main__":
    hardcore_training()
