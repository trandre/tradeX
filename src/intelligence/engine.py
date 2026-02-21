"""
Intelligence engine — ClaudeOllamaEngine connects to the local Ollama service.
Model and host are read from environment variables via src.config.
"""
import json
import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd

from src.config import OLLAMA_HOST, OLLAMA_MODEL_ANALYST


class IntelligenceEngine:
    """Provides algorithm recommendations based on market volatility."""

    def __init__(self):
        self.logger = logging.getLogger("IntelligenceEngine")

    def recommend_algorithm(self, market_data: pd.DataFrame) -> str:
        close = market_data["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        volatility = close.pct_change().std()
        if volatility > 0.02:
            return "Momentum (Trend Following) — high volatility suggests clear direction."
        if volatility < 0.005:
            return "Mean Reversion (Grid Trading) — low volatility suggests range-bound market."
        return "Random Forest Classifier — balanced market conditions."


class ClaudeOllamaEngine:
    """
    LLM-powered market analyst backed by Ollama.
    Falls back to a heuristic model when Ollama is unavailable.
    Model: OLLAMA_MODEL_ANALYST env var (default: qwen2.5:7b).
    Host:  OLLAMA_HOST env var         (default: http://localhost:11434).
    """

    def __init__(self):
        self.model = OLLAMA_MODEL_ANALYST
        self.host  = OLLAMA_HOST.rstrip("/")
        self.logger = logging.getLogger("ClaudeOllamaEngine")
        self.active = self._check_ollama()

    # ── connectivity ─────────────────────────────────────────────────────────

    def _check_ollama(self) -> bool:
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=3)
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            if self.model not in models:
                self.logger.warning(
                    "Ollama reachable but model '%s' not yet loaded — "
                    "using heuristic fallback until pull completes.", self.model
                )
                return False
            self.logger.info("Ollama ONLINE — model '%s' ready.", self.model)
            return True
        except Exception as exc:
            self.logger.warning("Ollama not reachable at %s: %s — heuristic fallback active.", self.host, exc)
            return False

    # ── public API ───────────────────────────────────────────────────────────

    def analyze_market_state(self, price_data: pd.Series, sentiment_score: float) -> dict:
        """
        Returns dict with keys: confidence (0-1), action (BUY/SELL/HOLD), reasoning.
        """
        prompt = (
            "Analyze the following market data and return a JSON trade recommendation.\n"
            f"Price Trend (last 5 days): {price_data.iloc[-5:].tolist()}\n"
            f"Sentiment Score: {sentiment_score:.3f}  (range -1 to +1)\n\n"
            "Return ONLY valid JSON with keys: "
            '"confidence" (float 0-1), "action" (BUY|SELL|HOLD), "reasoning" (string).'
        )

        if not self.active:
            # Re-check: the model may have finished downloading since startup
            self.active = self._check_ollama()

        if not self.active:
            return self._heuristic(sentiment_score)

        try:
            resp = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "stream": False,
                    "messages": [
                        {"role": "system", "content": "You are a professional trading analyst. Always reply with valid JSON only."},
                        {"role": "user",   "content": prompt},
                    ],
                },
                timeout=60,
            )
            resp.raise_for_status()
            content = resp.json()["message"]["content"]
            # Strip optional markdown fences
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content.strip())
        except Exception as exc:
            self.logger.error("Ollama inference error: %s — falling back to heuristic.", exc)
            return self._heuristic(sentiment_score)

    # ── private ──────────────────────────────────────────────────────────────

    @staticmethod
    def _heuristic(sentiment_score: float) -> dict:
        confidence = 0.6 if abs(sentiment_score) > 0.2 else 0.4
        if sentiment_score > 0.05:
            action = "BUY"
        elif sentiment_score < -0.05:
            action = "SELL"
        else:
            action = "HOLD"
        return {
            "confidence": confidence,
            "action": action,
            "reasoning": (
                f"Heuristic fallback (Ollama offline or model not loaded). "
                f"Sentiment magnitude={abs(sentiment_score):.3f}."
            ),
        }
