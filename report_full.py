#!/usr/bin/env python3
"""
TradeX Full Status Report - report01
Covers: training overview, last-24h activity, Ollama verification, latest findings.
"""

import json
import os
import re
from datetime import datetime, timedelta, timezone

LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
SEP  = "=" * 62
SEP2 = "-" * 62

# ── helpers ──────────────────────────────────────────────────────────────────

def load_json(filename):
    path = os.path.join(LOGS_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def parse_training_log(cutoff: datetime):
    """Return (all_sessions, recent_sessions, bot_stats) from training.log."""
    log_path = os.path.join(LOGS_DIR, "training.log")
    if not os.path.exists(log_path):
        return [], [], {}

    session_re = re.compile(
        r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ - (\w+) - TRAINING SESSION: \2\s*\n"
        r"Parameters Tested: (.+?)\s*\n"
        r"Resulting Performance: ([+-]?\d+\.?\d*)%\s*\n"
        r"Coach's Notes: (.+)",
        re.MULTILINE
    )
    with open(log_path) as f:
        content = f.read()

    all_sessions, recent_sessions = [], []
    bot_stats: dict[str, dict] = {}

    for m in session_re.finditer(content):
        ts_str, bot, params, perf_str, notes = m.groups()
        ts  = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        perf = float(perf_str)

        record = {"ts": ts, "bot": bot, "params": params, "perf": perf, "notes": notes}
        all_sessions.append(record)

        if ts >= cutoff:
            recent_sessions.append(record)

        s = bot_stats.setdefault(bot, {"count": 0, "perfs": [], "best": None, "worst": None})
        s["count"] += 1
        s["perfs"].append(perf)
        if s["best"] is None or perf > s["best"]:
            s["best"] = perf
        if s["worst"] is None or perf < s["worst"]:
            s["worst"] = perf

    for s in bot_stats.values():
        s["avg"] = sum(s["perfs"]) / len(s["perfs"]) if s["perfs"] else 0.0

    return all_sessions, recent_sessions, bot_stats

def check_ollama():
    """Return (online: bool, models: list[str], note: str)."""
    try:
        import ollama
        result = ollama.list()
        models = [m.model for m in result.models] if hasattr(result, "models") else []
        return True, models, "Ollama service is ONLINE and responding."
    except ImportError:
        return False, [], "ollama Python package not installed."
    except Exception as e:
        err = str(e)
        if "connection" in err.lower() or "connect" in err.lower() or "refused" in err.lower():
            note = "Ollama daemon not reachable at localhost:11434 — using HEURISTIC FALLBACK."
        else:
            note = f"Ollama error: {err}"
        return False, [], note

# ── report sections ──────────────────────────────────────────────────────────

def print_header(now: datetime):
    print(SEP)
    print("   TRADEX — FULL TRAINING & MODEL STATUS REPORT")
    print(f"   Generated : {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(SEP)

def print_ollama(online: bool, models: list[str], note: str):
    print("\n[1] OLLAMA MODEL MANAGEMENT")
    print(SEP2)
    status_label = "ONLINE" if online else "OFFLINE"
    print(f"  Service   : {status_label}")
    print(f"  Note      : {note}")
    if online and models:
        print("  Models managed by Ollama:")
        for m in models:
            print(f"    * {m}")
    elif online:
        print("  No models currently loaded in Ollama.")
    else:
        print("  Active model : Engine_Claude falling back to heuristic LLM logic.")
        print("  Impact       : Engine_Claude still operates but without local LLM inference.")

def print_engine_performance(perf_data: dict | None):
    print("\n[2] ENGINE PERFORMANCE OVERVIEW (latest snapshot)")
    print(SEP2)
    if not perf_data:
        print("  model_performance.json not found.")
        return
    rows = sorted(perf_data.items(), key=lambda kv: kv[1].get("perf", 0), reverse=True)
    for rank, (engine, data) in enumerate(rows, 1):
        perf = data.get("perf", 0)
        note = data.get("critique", "—")
        bar  = "#" * min(int(abs(perf) / 2), 20)
        sign = "+" if perf >= 0 else ""
        print(f"  #{rank} {engine}")
        print(f"     Perf    : {sign}{perf:.2f}%  [{bar}]")
        print(f"     Critique: {note}")

def print_24h_training(recent: list, bot_stats: dict, cutoff: datetime):
    print(f"\n[3] TRAINING ACTIVITY — LAST 24 h  (since {cutoff.strftime('%Y-%m-%d %H:%M')} UTC)")
    print(SEP2)

    if not recent:
        print("  No training sessions recorded in the last 24 hours.")
    else:
        print(f"  Total sessions   : {len(recent)}")
        bots_seen = {}
        for r in recent:
            bots_seen.setdefault(r["bot"], []).append(r["perf"])
        print(f"  Bots active      : {len(bots_seen)}")
        print()
        for bot, perfs in sorted(bots_seen.items()):
            avg  = sum(perfs) / len(perfs)
            best = max(perfs)
            worst= min(perfs)
            sign = "+" if avg >= 0 else ""
            print(f"  {bot}")
            print(f"    Sessions : {len(perfs)}  |  Avg: {sign}{avg:.2f}%  |  Best: +{best:.2f}%  |  Worst: {worst:.2f}%")

    # Full bot stats from all-time log
    print()
    print("  All-time bot summary (from full training.log):")
    for bot, s in sorted(bot_stats.items()):
        sign = "+" if s["avg"] >= 0 else ""
        print(f"  {bot:30s}  runs={s['count']:4d}  avg={sign}{s['avg']:7.2f}%"
              f"  best=+{s['best']:.2f}%  worst={s['worst']:.2f}%")

def print_learning_report(lr: dict | None):
    print("\n[4] LATEST LEARNING REPORT")
    print(SEP2)
    if not lr:
        print("  learning_report.json not found.")
        return
    summary = lr.get("summary", {})
    print(f"  Status       : {summary.get('status', 'N/A')}")
    print(f"  Total Trades : {summary.get('total_trades', 'N/A')}")
    print()
    print("  Key Findings / Insights:")
    for item in lr.get("failures_identified", []):
        tag = "  [OK]  " if item.startswith("SUCCESS") else \
              "  [OPT] " if item.startswith("OPTIM") else \
              "  [POL] " if item.startswith("POLICY") else \
              "  [RSK] " if item.startswith("RISK") else \
              "  [!]   "
        print(f"{tag}{item}")
    print()
    print("  Known Blind Spots:")
    for b in lr.get("blind_spots", []):
        print(f"    - {b}")
    print()
    recommendation = lr.get("recommendation", "")
    if recommendation:
        print(f"  Recommendation: {recommendation}")

def print_compliance(ec: dict | None):
    print("\n[5] ETHICAL COMPLIANCE")
    print(SEP2)
    if not ec:
        print("  ethical_compliance_report.json not found.")
        return
    avg_esg = ec.get("portfolio_avg_esg", 0)
    status  = ec.get("compliance_status", "UNKNOWN")
    ts      = ec.get("timestamp", "—")
    print(f"  Portfolio Avg ESG : {avg_esg:.1f} / 100")
    print(f"  Compliance Status : {status}")
    print(f"  Checked At        : {ts}")
    print()
    for detail in ec.get("details", []):
        icon = "[PASS]" if detail.get("status") == "PASS" else "[FAIL]"
        print(f"  {icon}  {detail['asset']:12s}  ESG={detail['esg_score']}")

def print_footer():
    print()
    print(SEP)
    print("  END OF REPORT  |  TradeX report01")
    print(SEP)

# ── main ─────────────────────────────────────────────────────────────────────

def main():
    now    = datetime.now(timezone.utc).replace(tzinfo=None)
    cutoff = now - timedelta(hours=24)

    print_header(now)

    online, models, note = check_ollama()
    print_ollama(online, models, note)

    perf_data = load_json("model_performance.json")
    print_engine_performance(perf_data)

    _all, recent, bot_stats = parse_training_log(cutoff)
    print_24h_training(recent, bot_stats, cutoff)

    lr = load_json("learning_report.json")
    print_learning_report(lr)

    ec = load_json("ethical_compliance_report.json")
    print_compliance(ec)

    print_footer()

if __name__ == "__main__":
    main()
