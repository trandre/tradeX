"""
Central configuration — reads all settings from environment variables.
This is the single source of truth for paths, model names, and runtime config.
Set these vars in docker-compose.yml or a local .env file.
"""
import os
from pathlib import Path

# ── Project root & logs ───────────────────────────────────────────────────────
# Inside Docker: /app   On host: auto-detected relative to this file
_HERE = Path(__file__).resolve().parent.parent        # /app or /opt/tradeX
LOGS_DIR  = Path(os.environ.get("TRADEX_LOGS_DIR",  _HERE / "logs"))
DATA_DIR  = Path(os.environ.get("TRADEX_DATA_DIR",  _HERE / "data"))
REPORT_DIR= Path(os.environ.get("TRADEX_REPORT_DIR",_HERE / "reports"))

# Ensure directories exist at import time
LOGS_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ── Ollama ────────────────────────────────────────────────────────────────────
OLLAMA_HOST          = os.environ.get("OLLAMA_HOST",     "http://localhost:11434")
OLLAMA_MODEL_ANALYST = os.environ.get("OLLAMA_MODEL_ANALYST", "qwen2.5:7b")   # Financial analysis
OLLAMA_MODEL_MANAGER = os.environ.get("OLLAMA_MODEL_MANAGER", "mistral:7b")   # Orchestration

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_USER      = os.environ.get("TRADEX_EMAIL_USER", "")
EMAIL_PASS      = os.environ.get("TRADEX_EMAIL_PASS", "")
EMAIL_RECIPIENT = os.environ.get("TRADEX_EMAIL_RECIPIENT", "")

# ── Risk guardrails ───────────────────────────────────────────────────────────
MAX_DRAWDOWN_PCT     = float(os.environ.get("TRADEX_MAX_DRAWDOWN_PCT",     "0.10"))
MAX_POSITION_SIZE_PCT= float(os.environ.get("TRADEX_MAX_POSITION_SIZE_PCT","0.05"))
INITIAL_PURSE_NOK    = float(os.environ.get("TRADEX_INITIAL_PURSE_NOK",   "20000"))

# ── Training ──────────────────────────────────────────────────────────────────
TRAINING_INTERVAL_SEC= int(os.environ.get("TRADEX_TRAINING_INTERVAL_SEC", "3600"))
