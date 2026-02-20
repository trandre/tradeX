# TradeX Runbook

## 1. Setup Environment
Ensure you have Python 3.12+ and `pip` installed.

```bash
# Initialize virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Execute Training Phase
Run this to train the bots on historical data and generate the initial learning reports.

```bash
python train_system.py
```
- **Check Training Logs**: `tail -f logs/training.log`
- **View Lessons Learned**: `cat logs/learning_report.json`

## 3. Run Trading Operations
Execute the main trading loop with live news sentiment and ethical scoring.

```bash
python main.py
```
- **Check Compliance**: `cat logs/ethical_compliance_report.json`
- **Check Mimicry Progress**: `tail -f logs/trader_analysis.log`

## 4. System Status Check
Generate a high-level overview of functionality and training progress.

```bash
python status_report.py
```

## 5. Docker Deployment
Deploy the whole system in an isolated container.

```bash
# Build and Start
docker-compose up --build -d

# View Logs from outside
tail -f logs/trader_analysis.log
```

## 6. Troubleshooting
- **YFinance Errors**: Ensure your network allows connections to Yahoo Finance. The ingestor has retry logic for news feeds.
- **Syntax Errors**: If editing, ensure f-strings do not contain unescaped newlines.
- **Permission Denied**: Ensure the current user has write access to the `logs/` directory.
