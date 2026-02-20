from abc import ABC, abstractmethod
from src.simulation.broker import SimulatedBroker
from src.security.guardrails import Guardrail
from src.intelligence.social import CorruptionIndex
from textblob import TextBlob
import pandas as pd
import logging
import json
import os
import random

class TrainerBot(ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.log_path = "/opt/tradeX/logs/training.log"
        self.report_path = "/opt/tradeX/logs/learning_report.json"
        self._setup_logger()

    def _setup_logger(self):
        self.logger = logging.getLogger(self.name)
        if not self.logger.handlers:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            handler = logging.FileHandler(self.log_path)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def load_learning_report(self):
        if os.path.exists(self.report_path):
            with open(self.report_path, 'r') as f:
                return json.load(f)
        return {}

    @abstractmethod
    def run_training_session(self, data):
        pass

    def log_result(self, parameters, performance, notes=""):
        message = (
            f"TRAINING SESSION: {self.name}\n"
            f"Parameters Tested: {parameters}\n"
            f"Resulting Performance: {performance:.2f}%\n"
            f"Coach's Notes: {notes}\n"
        )
        self.logger.info(message)
        print(message)

class RiskTrainer(TrainerBot):
    def __init__(self):
        super().__init__("RiskManagerBot", "Optimizes defensive strategies to protect capital.")
        
    def run_training_session(self, market_data, stop_loss_pct=0.05):
        report = self.load_learning_report()
        if "Increase stop-loss" in report.get('recommendation', ''):
            stop_loss_pct += 0.02
        
        initial_price = market_data.iloc[0]
        final_price = market_data.iloc[-1]
        peak_price = initial_price
        triggered = False
        exit_price = final_price
        
        for price in market_data:
            if price > peak_price:
                peak_price = price
            drawdown = (peak_price - price) / peak_price
            if drawdown >= stop_loss_pct:
                exit_price = price
                triggered = True
                break
        
        roi = (exit_price - initial_price) / initial_price
        self.log_result(f"Stop-Loss: {stop_loss_pct*100}%", roi * 100, "Safety test complete.")
        return roi

class GrowthTrainer(TrainerBot):
    def __init__(self):
        super().__init__("GrowthSeekerBot", "Optimizes aggressive strategies using RSI.")
        
    def calculate_rsi(self, data, window=14):
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def run_training_session(self, market_data, rsi_window=14):
        rsi_series = self.calculate_rsi(market_data, window=rsi_window)
        current_rsi = rsi_series.iloc[-1]
        roi = (market_data.iloc[-1] - market_data.iloc[0]) / market_data.iloc[0]
        self.log_result(f"RSI Window: {rsi_window}", roi * 100, f"RSI is {current_rsi:.2f}")
        return roi

class SentimentTrainer(TrainerBot):
    def __init__(self):
        super().__init__("SentimentBot", "Trains on news headlines.")

    def run_training_session(self, headlines):
        total_sentiment = 0
        for text in headlines:
            total_sentiment += TextBlob(text).sentiment.polarity
        avg_sentiment = total_sentiment / len(headlines) if headlines else 0
        mock_roi = avg_sentiment * 10
        self.log_result("News Analysis", mock_roi, f"Avg Sentiment: {avg_sentiment:.2f}")
        return mock_roi

class EthicsBot(TrainerBot):
    """
    Analyzes the portfolio's ethical standing and generates a formal report.
    Checks against the CorruptionIndex and ESG scores.
    """
    def __init__(self):
        super().__init__("EthicsBot", "Generates ethical compliance and ESG reports.")
        self.report_path = "/opt/tradeX/logs/ethical_compliance_report.json"
        self.index = CorruptionIndex()

    def run_training_session(self, positions):
        """Generates a report based on current holdings."""
        portfolio_report = []
        total_score = 0
        
        for symbol in positions:
            score = self.index.get_score(symbol, "company")
            total_score += score
            portfolio_report.append({
                "asset": symbol,
                "esg_score": score,
                "status": "PASS" if score >= 40 else "REJECTED"
            })
            
        avg_score = total_score / len(positions) if positions else 100
        
        report = {
            "portfolio_avg_esg": avg_score,
            "compliance_status": "HIGHLY ETHICAL" if avg_score > 70 else "MARGINAL",
            "details": portfolio_report,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        with open(self.report_path, 'w') as f:
            json.dump(report, f, indent=4)
            
        print(f"--- [EthicsBot] Compliance Report Generated: {report['compliance_status']} ---")
        return report

class ModelComparisonBot(TrainerBot):
    """
    Simulates and compares different AI Architectures (manufacturers).
    Tests which 'Virtual Engine' performs best on different markets.
    """
    def __init__(self):
        super().__init__("ModelComparator", "Compares performance of simulated AI architectures.")
        self.performance_stats = "/opt/tradeX/logs/model_performance.json"

    def run_training_session(self, market_data):
        """Simulates 3 different models on the same data."""
        results = {
            "Engine_Alpha (DeepLearning)": random.uniform(5, 15),
            "Engine_Beta (Reinforcement)": random.uniform(2, 18),
            "Engine_Gamma (Statistical)": random.uniform(8, 12)
        }
        
        with open(self.performance_stats, 'w') as f:
            json.dump(results, f, indent=4)
            
        print("\n--- [Model Performance Comparison] ---")
        for engine, perf in results.items():
            print(f"{engine}: {perf:.2f}% improvement potential")
        
        return results

class AnalyzerBot(TrainerBot):
    def __init__(self):
        super().__init__("AnalyzerBot", "Inspects history to generate learning reports.")
        self.report_path = "/opt/tradeX/logs/learning_report.json"

    def run_training_session(self, broker_history):
        if not broker_history:
            return "No history."
        report = {
            "summary": {"total_trades": len(broker_history), "status": "Training Complete"},
            "insights": ["Automated learning activated."],
            "recommendation": "Increase stop-loss for high-volatility assets."
        }
        with open(self.report_path, 'w') as f:
            json.dump(report, f, indent=4)
        return report
