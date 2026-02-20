# GEMINI.md - TradeX Project Context

This file provides critical context and instructions for AI agents (like Gemini) interacting with the TradeX codebase.

## Project Overview
**TradeX** is an AI-driven multi-asset trading and learning system. It integrates institutional mimicry (e.g., following NBIM or BlackRock styles), sentiment analysis from live news feeds, and rigorous ethical scoring (ESG and Corruption Index) to provide a robust algorithmic trading environment.

### Core Technologies
- **Language**: Python 3.12+
- **Data**: `pandas`, `numpy`, `yfinance`, `ccxt` (for live market data and news).
- **AI/ML**: `scikit-learn`, `torch` (PyTorch), `textblob` (NLP/Sentiment).
- **Web Scraping**: `beautifulsoup4`, `requests`.
- **Infrastructure**: Docker & Docker Compose.

### System Architecture
The codebase is organized under the `src/` directory with a modular approach:
- `src/data/`: Data ingestion from various sources (`ingestor.py`).
- `src/intelligence/`: AI logic, including the core engine (`engine.py`), ethical filtering, and institutional mimicry (`social.py`).
- `src/simulation/`: Mock trading environment and portfolio management (`broker.py`).
- `src/strategies/`: Trading strategy implementations (e.g., `moving_average.py`).
- `src/training/`: Specialized AI "coaches" for Risk, Growth, and Sentiment (`bots.py`).
- `src/security/`: Financial safety limits and guardrails (`guardrails.py`).

## Building and Running
The system is designed to be executed in phases: training followed by live trading.

### 1. Setup
```bash
# Recommended: use a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Training Phase
Trains the AI bots on historical data and live headlines to generate learning reports.
```bash
python train_system.py
```

### 3. Execution Phase
Runs the main trading loop, integrating live sentiment and ethical checks.
```bash
python main.py
```

### 4. Monitoring & Reporting
- **Status Report**: `python status_report.py`
- **Summary Generation**: `python generate_summary.py`
- **Logs**: Check the `logs/` directory for `training.log`, `ethical_compliance_report.json`, and `trader_analysis.log`.

### 5. Docker Deployment
```bash
docker-compose up --build -d
```

## Scaling and Integrity
- **Plug-and-Play Architecture**: The system supports adding new assets, indicators (MACD, Bollinger), or trainer bots by subclassing base components.
- **Distributed Training**: Specialized bots (Sentiment, Growth, Risk) can run independently, sharing insights via `learning_report.json`.
- **Safety & Auditability**: Every decision (mimicry, trade execution, ethical rejection) is logged in the `logs/` directory. Financial guardrails (Max Drawdown, Position Sizing) are enforced at the execution level.
- **Simulation-to-Live**: The architecture separates the `SimulatedBroker` from the strategy logic, allowing for a seamless transition to live exchange APIs (e.g., CCXT) by swapping the broker module.

## Development Conventions
- **Surgical Changes**: When modifying logic, prioritize updates within the `src/` subdirectories to maintain separation of concerns.
- **Ethics First**: Any new trading strategy or asset ingestion should be piped through the `EthicalFilter` in `src/intelligence/social.py`.
- **Data Safety**: All trades must be validated by the `SimulatedBroker` and adhere to `guardrails.py`.
- **Logging**: Ensure significant events (trade execution, sentiment shifts, ethical rejections) are logged to the appropriate file in `logs/`.
- **Testing**: Add or update tests in the `tests/` directory when introducing new features. Use `pytest` for running tests.
