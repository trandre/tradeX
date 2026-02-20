from src.data.ingestor import MultiAssetIngestor
from src.simulation.broker import SimulatedBroker
from src.intelligence.engine import IntelligenceEngine
from src.intelligence.social import EthicalFilter, ShadowTrader
from src.training.bots import AnalyzerBot, SentimentTrainer
import pandas as pd

def main():
    print("--- TradeX Intelligence, Ethics & Live Feed Hub ---")
    
    # --- 1. SETUP ---
    ingestor = MultiAssetIngestor()
    broker = SimulatedBroker(initial_purse_nok=20000)
    engine = IntelligenceEngine()
    social = ShadowTrader()
    analyzer = AnalyzerBot()
    sentiment_bot = SentimentTrainer()
    ethics = EthicalFilter(min_score_threshold=40, blocked_segments=["Arms", "Tobacco"])
    
    # --- 2. LIVE SENTIMENT CHECK ---
    print("\n[Intelligence] Checking live market sentiment...")
    headlines = ingestor.fetch_live_news()
    mood = sentiment_bot.run_training_session(headlines)
    print(f"Current Market Mood Index: {mood:.2f}")

    # --- 3. SELECT ACTOR & ADJUST PARAMETERS ---
    actor_id = "NBIM" # Let's follow the Norwegian Pension Fund's style
    print(f"\n[Social] Following mentor style: {actor_id}")
    params = social.get_mimicry_parameters(actor_id)

    # --- 4. MARKET SCAN WITH ETHICAL SCORING ---
    print("\n[Market] Scanning for assets with Ethical Scoring...")
    promising = ingestor.list_promising_assets(period="1mo")
    
    for _, row in promising.iterrows():
        symbol = row['symbol']
        
        # In production, metadata comes from a database. Here we mock it for the demo.
        # We assign 'Norway' to EQNR.OL and 'USA' to others for the ethical check.
        country = "Norway" if ".OL" in symbol else "USA"
        asset_info = {"ticker": symbol, "country": country, "segment": row['category']}
        
        allowed, reason = ethics.is_allowed(asset_info)
        
        if not allowed:
            print(f"Skipping {symbol}: {reason}")
            continue
            
        print(f"\nEthically Cleared Asset: {symbol} (Reason: {reason})")
        
        data = ingestor.fetch_data(symbol, period="1mo")
        current_price = data['Close']
        if isinstance(current_price, pd.DataFrame):
            current_price = current_price.iloc[:, 0]
        current_price = float(current_price.iloc[-1])
        
        # Execute trade
        success, message = broker.execute_trade(symbol, 1, current_price, side='buy')
        print(f"Trade Execution: {message}")
        break 

    # --- 5. POST-TRADE ANALYSIS ---
    print("\n[Analysis] Reviewing activity...")
    report = analyzer.run_training_session(broker.history)
    print(f"Learning report updated. Status: {report['summary']['status']}")

if __name__ == "__main__":
    main()
