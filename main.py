from src.data.ingestor import MultiAssetIngestor
from src.simulation.broker import SimulatedBroker
from src.intelligence.engine import ClaudeOllamaEngine
from src.intelligence.social import EthicalFilter, ShadowTrader
from src.training.bots import AnalyzerBot, SentimentTrainer, ModelComparisonBot
from src.reporting.excel_generator import DailyExcelReport
from send_daily_report import send_email_report
from src.intelligence.quant_methods import MedallionEngine
from src.intelligence.empire_cycle import EmpireCycleAnalyst
from src.config import INITIAL_PURSE_NOK, EMAIL_RECIPIENT, LOGS_DIR
import pandas as pd
import datetime
import random
import json

def main():
    print("--- TradeX Advanced Multi-Model Hub ---")

    # 1. SETUP
    ingestor = MultiAssetIngestor()
    broker = SimulatedBroker(initial_purse_nok=INITIAL_PURSE_NOK)
    claude = ClaudeOllamaEngine()
    medallion = MedallionEngine()
    sentiment_bot = SentimentTrainer()
    ethics = EthicalFilter(min_score_threshold=40)

    # Empire-syklus makro-analyse (kjøres én gang per sesjon)
    print("\n[EmpireCycle] Kjører makro-regime analyse...")
    empire_analyst = EmpireCycleAnalyst()
    empire_analysis = empire_analyst.analyze()
    print(f"[EmpireCycle] Volatilitetsregime: {empire_analysis['volatility_regime']} | "
          f"Syklus: {empire_analysis['cycle_position']} ({empire_analysis['cycle_position_pct']}%) | "
          f"Kortsiktig bias: {empire_analysis['short_term_bias']}")
    print(f"[EmpireCycle] Kilde: {empire_analysis.get('source', '—')}")
    
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
        
        # Empire-syklus-justert terskel: HIGH/EXTREME volatilitet krever sterkere konsensus
        vol_regime = empire_analysis.get("volatility_regime", "MODERATE")
        required_votes = 3 if vol_regime in ("HIGH", "EXTREME") else 2

        # Strategi for kjøp: Flertall eller spesifikk trigger
        buy_votes = len([v for v in decision_matrix.values() if v == "BUY"])

        if buy_votes >= required_votes and symbol not in broker.positions:
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

    # 3. LAGRE BROKER-TILSTAND TIL DISK (leses av report01-containeren)
    broker_state = {
        "generated_at": datetime.datetime.now().isoformat(),
        "portfolio": {
            "total_value_nok": broker.get_portfolio_value(current_prices),
            "cash_nok": broker.purse,
            "initial_purse_nok": INITIAL_PURSE_NOK,
            "total_commission": broker.total_commission,
            "total_slippage": broker.total_slippage,
            "positions": broker.positions,
        },
        "trade_history": broker.history,
        "current_prices": current_prices,
        "news_headlines": headlines,
        "sentiment_mood": mood,
        "empire_cycle_analysis": empire_analysis,
    }
    broker_state_path = str(LOGS_DIR / "broker_state.json")
    with open(broker_state_path, "w") as f:
        json.dump(broker_state, f, indent=2, default=str)
    print(f"[Reporting] Broker-tilstand lagret: {broker_state_path}")

    # 4. RAPPORT-GENERERING
    print("\n[Reporting] Genererer fullstendig analyserapport...")
    report_gen = DailyExcelReport(broker)
    filename = report_gen.generate(current_prices)

    # Send rapport
    send_email_report(filename, EMAIL_RECIPIENT)
    print(f"Fullført. Rapport sendt: {filename}")

if __name__ == "__main__":
    main()
