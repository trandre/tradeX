import logging
import os

class CorruptionIndex:
    """
    Provides ethical and corruption scores for countries and companies.
    A score of 100 is perfectly clean, while 0 is highly corrupt/unethical.
    """
    def __init__(self):
        # Mock data representing Corruption Perception Index (CPI) and ESG scores
        self.country_scores = {
            "Norway": 84,
            "Denmark": 90,
            "USA": 69,
            "Germany": 79,
            "COUNTRY_X": 15
        }
        self.company_esg_scores = {
            "AAPL": 75,
            "EQNR.OL": 82,
            "COAL_CORP": 12,
            "WEAPONS_INC": 20
        }

    def get_score(self, entity_name, entity_type="country"):
        if entity_type == "country":
            return self.country_scores.get(entity_name, 50) # Default to neutral
        return self.company_esg_scores.get(entity_name, 50)

class EthicalFilter:
    """
    Ensures the trading system stays within ethical boundaries.
    Uses CorruptionIndex to block assets with low ethical scores.
    """
    
    def __init__(self, min_score_threshold=40, blocked_segments=None):
        self.index = CorruptionIndex()
        self.min_score_threshold = min_score_threshold
        self.blocked_segments = blocked_segments or []

    def is_allowed(self, asset_metadata):
        ticker = asset_metadata.get('ticker')
        country = asset_metadata.get('country')
        segment = asset_metadata.get('segment')

        # 1. Segment Check
        if segment in self.blocked_segments:
            return False, f"Segment {segment} is ethically prohibited."

        # 2. Country Score Check
        country_score = self.index.get_score(country, "country")
        if country_score < self.min_score_threshold:
            return False, f"Country {country} failed ethical score ({country_score})."

        # 3. Company Score Check
        company_score = self.index.get_score(ticker, "company")
        if company_score < self.min_score_threshold:
            return False, f"Company {ticker} failed ethical score ({company_score})."

        return True, "Asset is ethically cleared."


class ShadowTrader:
    """
    Analyzes and mimics successful institutional investors.
    Automatically adjusts trading parameters based on the chosen actor's style.
    """
    
    def __init__(self):
        self.monitored_actors = {
            "NBIM": {
                "name": "Norwegian Pension Fund Global",
                "style": "Long-term Value, ESG Focused",
                "params": {"short_window": 50, "long_window": 200, "risk_level": "Conservative"}
            },
            "BLACKROCK": {
                "name": "BlackRock iShares",
                "style": "Broad Market Momentum, Tech-Heavy",
                "params": {"short_window": 20, "long_window": 50, "risk_level": "Moderate"}
            },
            "RENAISSANCE": {
                "name": "Renaissance Technologies (Medallion)",
                "style": "High-Frequency, Quantitative, Volatility-based",
                "params": {"short_window": 5, "long_window": 20, "risk_level": "Aggressive"}
            }
        }
        self.log_path = '/opt/tradeX/logs/trader_analysis.log'
        self._setup_logger()

    def _setup_logger(self):
        self.logger = logging.getLogger("ShadowTrader")
        if not self.logger.handlers:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            handler = logging.FileHandler(self.log_path)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def get_mimicry_parameters(self, actor_id):
        """
        Returns specific trading parameters suggested by the actor's style.
        """
        actor = self.monitored_actors.get(actor_id)
        if not actor:
            return None
        
        self.logger.info(f"Mimicking {actor['name']}. Setting parameters to {actor['params']}.")
        return actor['params']

    def analyze_actor(self, actor_id):
        actor = self.monitored_actors.get(actor_id)
        if not actor:
            return "Actor not found."

        analysis = (
            f"ANALYSIS OF {actor['name']}:\n"
            f"Style: {actor['style']}\n"
            f"Target Parameters: {actor['params']}\n"
            "Learning Note: By mimicking this actor, we adjust our sensitivity to market noise."
        )
        self.logger.info(analysis)
        return analysis
