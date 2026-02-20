from src.training.bots import RiskTrainer, GrowthTrainer, SentimentTrainer, AnalyzerBot, ModelComparisonBot, EthicsBot, QuantTrainer
from src.data.ingestor import MultiAssetIngestor
import pandas as pd
import time

def training_phase():
    """
    Main Training Hub with Improved Iterative Loops.
    Includes James Simons (Medallion) Quant Methods.
    """
    print("="*60)
    print("      TRADEX ADVANCED ITERATIVE TRAINING PHASE")
    print("      (Featuring HMM Regime Detection & Claude LLM)")
    print("="*60)
    
    # 1. SETUP
    ingestor = MultiAssetIngestor()
    risk_coach = RiskTrainer()
    growth_coach = GrowthTrainer()
    sentiment_coach = SentimentTrainer()
    analyzer = AnalyzerBot()
    model_comparator = ModelComparisonBot()
    quant_coach = QuantTrainer() # The new Simons Bot
    
    # 2. ASSETS TO TRAIN ON
    assets = ["AAPL", "BTC-USD", "USDNOK=X"]
    
    # 3. IMPROVED ITERATIVE TRAINING LOOP
    print("\n[Phase: Learning] Iterating through asset classes...")
    for symbol in assets:
        print(f"\n--- Training on {symbol} ---")
        
        # Data fetching with error handling
        try:
            df = ingestor.fetch_data(symbol, period="1y", interval="1d")
            if df.empty:
                print(f"Skipping {symbol}: No data.")
                continue
            
            close_prices = df['Close']
            if isinstance(close_prices, pd.DataFrame):
                close_prices = close_prices.iloc[:, 0]
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            continue

        # Fetch news context
        headlines = ingestor.fetch_live_news()
        
        # A. Sentiment Training
        mood_perf = sentiment_coach.run_training_session(headlines)
        
        # B. Risk Optimization
        risk_coach.run_training_session(close_prices)
        
        # C. Growth Optimization
        for window in [14, 21]:
            growth_coach.run_training_session(close_prices, rsi_window=window)

        # D. Quant / Simons Method (New)
        quant_coach.run_training_session(close_prices)
            
        # E. Model Comparison (Claude LLM Integration + Medallion)
        model_comparator.run_training_session(close_prices, sentiment=mood_perf/100.0)

    # 4. FINAL COMPLIANCE & ANALYSIS
    print("\n[Phase: Governance] Running ethics and final analysis...")
    ethics = EthicsBot()
    ethics.run_training_session(assets)

    mock_history = [{'symbol': 'AAPL', 'side': 'buy', 'price': 150}]
    analyzer.run_training_session(mock_history)
    
    print("\n" + "="*60)
    print("      ITERATIVE TRAINING COMPLETE")
    print("="*60)

if __name__ == "__main__":
    training_phase()
