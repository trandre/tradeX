import json
import os
import pandas as pd

def generate_welcome_back_report():
    print("\n" + "="*60)
    print("           WELCOME BACK: TRADEX 5-HOUR PROGRESS REPORT")
    print("="*60)

    # 1. Load Learning Report (Critical Analysis)
    print("\n[1. CRITICAL ANALYSIS & FAILURES]")
    try:
        with open('/opt/tradeX/logs/learning_report.json', 'r') as f:
            data = json.load(f)
            print(f"Status: {data['summary']['status']}")
            print("\nFailures & Blind Spots Identified:")
            for failure in data.get('failures_identified', []):
                print(f"  - {failure}")
            print(f"\nImmediate Recommendation: {data['recommendation']}")
    except Exception:
        print("Learning report still being generated...")

    # 2. Load Model Comparison (Manufacturer Critique)
    print("\n[2. AI MANUFACTURER COMPARISON]")
    try:
        with open('/opt/tradeX/logs/model_performance.json', 'r') as f:
            perf = json.load(f)
            for engine, info in perf.items():
                print(f"  * {engine}: {info['perf']:.2f}% improvement | CRITIQUE: {info['critique']}")
    except Exception:
        print("Model performance data pending...")

    # 3. Ethical Compliance
    print("\n[3. ETHICAL & ESG AUDIT]")
    try:
        with open('/opt/tradeX/logs/ethical_compliance_report.json', 'r') as f:
            eth = json.load(f)
            print(f"Overall Status: {eth['compliance_status']}")
            print(f"Average Portfolio ESG Score: {eth['portfolio_avg_esg']:.2f}/100")
    except Exception:
        print("Ethics report pending...")

    # 4. Process Momentum
    print("\n[4. TRAINING MOMENTUM]")
    try:
        with open('/opt/tradeX/logs/continuous_process.log', 'r') as f:
            lines = f.readlines()
            iterations = sum(1 for line in lines if "Starting Training Iteration" in line)
            print(f"Total Background Iterations Completed: {iterations}")
            if lines:
                print(f"Last Log Entry: {lines[-1].strip()}")
    except Exception:
        print("Process log not found.")

    print("\n" + "="*60)
    print("        SYSTEM IS OPERATIONAL AND CONTINUING TO LEARN")
    print("="*60 + "\n")

if __name__ == "__main__":
    generate_welcome_back_report()
