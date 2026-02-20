from src.data.ingestor import MultiAssetIngestor
from src.simulation.broker import SimulatedBroker
from src.intelligence.engine import ClaudeOllamaEngine
from src.intelligence.social import EthicalFilter, ShadowTrader
from src.training.bots import AnalyzerBot, SentimentTrainer, ModelComparisonBot
from src.reporting.excel_generator import DailyExcelReport
from send_daily_report import send_email_report
from src.intelligence.quant_methods import MedallionEngine
import pandas as pd
import datetime
import random

def main():
    print("--- TradeX Advanced Multi-Model Hub ---")
    
    # 1. SETUP
    ingestor = MultiAssetIngestor()
    broker = SimulatedBroker(initial_purse_nok=20000)
    claude = ClaudeOllamaEngine()
    medallion = MedallionEngine()
    sentiment_bot = SentimentTrainer()
    ethics = EthicalFilter(min_score_threshold=40)
    
    # 2. LIVE DATA
    headlines = ingestor.fetch_live_news()
    mood = sentiment_bot.run_training_session(headlines)
    promising = ingestor.list_promising_assets(period="1mo")
    
    current_prices = {}
    for _, row in promising.iterrows():
        symbol = row['symbol']
        data = ingestor.fetch_data(symbol, period="1mo")
        if data.empty: continue
        
        close = data['Close']
        if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]
        price = float(close.iloc[-1])
        current_prices[symbol] = price
        
        # --- MULTI-MODEL DECISION MATRIX ---
        # Vi simulerer stemmene fra de ulike modellene
        claude_dec = claude.analyze_market_state(close, mood/100.0)
        
        regime, _ = medallion.fit_regime_detection(close.values)
        medallion_dec = "BUY" if regime == "Stable_Growth" else "HOLD"
        
        # Alpha og Gamma (Simulert basert på deres 'personlighet')
        alpha_dec = "BUY" if random.random() > 0.4 else "HOLD" # Aggressiv DL
        gamma_dec = "HOLD" if random.random() > 0.3 else "SELL" # Konservativ Stats
        
        decision_matrix = {
            "Claude": claude_dec['action'],
            "Medallion": medallion_dec,
            "Alpha": alpha_dec,
            "Gamma": gamma_dec
        }
        
        # Strategi for kjøp: Flertall eller spesifikk trigger
        buy_votes = len([v for v in decision_matrix.values() if v == "BUY"])
        
        if buy_votes >= 2 and symbol not in broker.positions:
            trigger = "Konsensus Flertall"
            if decision_matrix['Medallion'] == "BUY": trigger = "Medallion Regime-Trigger"
            elif decision_matrix['Claude'] == "BUY": trigger = "Claude Sentiment-Trigger"
            
            broker.execute_trade(
                symbol, 1, price, 
                category=row['category'], 
                side='buy',
                trigger_strategy=trigger,
                decision_matrix=decision_matrix
            )
            print(f"[DECISION] Kjøper {symbol}. Stemmer: {decision_matrix}")

    # 3. RAPPORT-GENERERING
    print("\n[Reporting] Genererer fullstendig analyserapport...")
    report_gen = DailyExcelReport(broker)
    filename = report_gen.generate(current_prices)
    
    # Send rapport
    send_email_report("tfemteh@gmail.com", filename)
    print(f"Fullført. Rapport sendt: {filename}")

if __name__ == "__main__":
    main()
