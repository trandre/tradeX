# TradeX System Documentation

## 1. Project Overview
TradeX is an AI-driven, multi-asset trading simulation and training environment. It integrates real-world data, sentiment analysis, institutional mimicry, and strict ethical guardrails to provide a safe and intelligent platform for algorithmic trading development.

## 2. Core Architecture

### A. Data Layer (`src/data/`)
- **`ingestor.py`**: Handles all data acquisition. Supports historical market data for Stocks, Forex, Crypto, and Bonds via `yfinance`. Features a live news fetcher that scrapes financial headlines via RSS feeds for sentiment analysis.

### B. Intelligence Layer (`src/intelligence/`)
- **`engine.py`**: The technical core. Analyzes market volatility and suggests specific algorithms (Momentum, Mean Reversion, etc.).
- **`social.py`**: 
    - **Institutional Mimicry**: Allows the system to adopt the trading parameters (windows, risk levels) of major actors like NBIM, BlackRock, and Renaissance Technologies.
    - **Ethical Filter & Corruption Index**: Uses a scoring-based system (0-100) to block assets from corrupt countries or unethical companies (low ESG).

### C. Simulation Layer (`src/simulation/`)
- **`broker.py`**: A simulated environment that tracks the "Purse" (Cash), positions, and trade history. Calculates commissions and prevents over-leveraging.

### D. Security Layer (`src/security/`)
- **`guardrails.py`**: Enforces financial safety. Monitors Maximum Drawdown (Halt trading at 10% loss) and Position Sizing (Limit single trades to 5% of portfolio).

### E. Training & Bot Layer (`src/training/`)
- **`bots.py`**: A multi-bot ecosystem where specialized AI "Coaches" perform different tasks:
    - **RiskManagerBot**: Optimizes defensive settings.
    - **GrowthSeekerBot**: Optimizes trend-following (RSI/MA).
    - **SentimentBot**: Analyzes news mood (NLP).
    - **EthicsBot**: Audits portfolio compliance and generates JSON reports.
    - **AnalyzerBot**: Performs post-trade reviews and writes "Lessons Learned."
    - **ModelComparator**: Tests different AI "Engines" (Alpha, Beta, Gamma) against current markets.

## 3. Scaling Philosophy

### Modular Expansion
The system is built on a "Plug-and-Play" architecture. New assets, new indicators (MACD, Bollinger), or new trainer bots can be added by subclassing the base components without disrupting existing logic.

### Distributed Training
The `TrainerBot` architecture allows for horizontal scaling. In a production environment, different bots (Sentiment vs. Growth) could run on separate containers or nodes, sharing their insights via the centralized `learning_report.json` or a distributed database.

### Real-to-Paper Transition
The separation between the `SimulatedBroker` and the `Strategy` logic means that moving from simulation to real-world trading only requires replacing the broker module with a live exchange API (e.g., CCXT or Interactive Brokers), leaving the intelligence and safety layers intact.

## 4. Integrity Statement
- **Security**: The system uses SSH for GitHub and environment variables for configuration. Guardrails are enforced at the execution level to prevent catastrophic loss.
- **Redundancy**: Ethical checks are performed both at the scan phase (`EthicalFilter`) and the execution phase (`Guardrail`).
- **Auditability**: Every decision—from institutional mimicry to trade execution—is logged in the `logs/` directory for human and AI inspection.
