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

def print_portfolio_positions(broker_state: dict | None):
    print("\n[6] PORTEFØLJE — ÅPNE POSISJONER OG HORISONT")
    print(SEP2)
    if not broker_state:
        print("  broker_state.json ikke funnet — kjør main.py for å generere.")
        return

    portfolio = broker_state.get("portfolio", {})
    positions = portfolio.get("positions", {})
    current_prices = broker_state.get("current_prices", {})
    initial    = portfolio.get("initial_purse_nok", 0)
    total_val  = portfolio.get("total_value_nok", 0)
    cash       = portfolio.get("cash_nok", 0)
    fees       = portfolio.get("total_commission", 0) + portfolio.get("total_slippage", 0)
    generated  = broker_state.get("generated_at", "—")[:16].replace("T", " ")

    pnl_pct = ((total_val - initial) / initial * 100) if initial else 0
    sign = "+" if pnl_pct >= 0 else ""
    print(f"  Sist oppdatert  : {generated}")
    print(f"  Startkapital    : {initial:>12,.2f} NOK")
    print(f"  Totalverdi      : {total_val:>12,.2f} NOK  ({sign}{pnl_pct:.2f}%)")
    print(f"  Kontanter       : {cash:>12,.2f} NOK")
    print(f"  Transaksjonskost: {fees:>12,.2f} NOK")

    if not positions:
        print("\n  Ingen åpne posisjoner.")
        return

    print()
    print(f"  {'Symbol':<12} {'Inngang':>10} {'Nå':>10} {'P&L':>9}  {'Horisont':<22} Trigger")
    print(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*9}  {'-'*22} {'-'*28}")
    for sym, pos in positions.items():
        entry   = pos.get("avg_price", 0)
        curr    = current_prices.get(sym, entry)
        pnl     = (curr - entry) / entry * 100 if entry else 0
        s       = "+" if pnl >= 0 else ""
        horizon = pos.get("expected_horizon", "—")
        trigger = pos.get("trigger_strategy", "—")
        print(f"  {sym:<12} {entry:>10,.2f} {curr:>10,.2f} {s}{pnl:>8.2f}%  {horizon:<22} {trigger}")


def print_trade_history(broker_state: dict | None):
    print("\n[7] HANDELSHISTORIKK — INNGANG OG EXIT")
    print(SEP2)
    if not broker_state:
        print("  broker_state.json ikke funnet.")
        return

    history = broker_state.get("trade_history", [])
    if not history:
        print("  Ingen handler registrert.")
        return

    for t in history:
        side_label  = "KJØP" if t["side"] == "buy" else "SALG"
        result      = t.get("result", 0)
        result_str  = f"+{result:,.2f} NOK" if result > 0 else f"{result:,.2f} NOK" if result != 0 else "—"
        ts          = str(t["timestamp"])[:16].replace("T", " ")
        dm          = t.get("decision_matrix", {})
        dm_str      = "  ".join(f"{k}:{v}" for k, v in dm.items()) if dm else "—"

        print(f"  {ts}  {side_label:<5} {t['symbol']:<12}  "
              f"Antall: {t['qty']}  Kurs: {t['price']:,.2f}  Resultat: {result_str}")
        print(f"    Trigger  : {t.get('trigger', '—')}")
        if dm:
            print(f"    Stemmer  : {dm_str}")
        print(f"    Gebyr    : {t.get('total_fees', 0):.2f} NOK  "
              f"(kurtasje {t.get('commission',0):.2f} + slippage {t.get('slippage',0):.2f})")
        print()


def print_news_impact(broker_state: dict | None):
    print("\n[8] NYHETER OG SENTIMENTPÅVIRKNING")
    print(SEP2)
    if not broker_state:
        print("  broker_state.json ikke funnet.")
        return

    headlines = broker_state.get("news_headlines", [])
    mood      = broker_state.get("sentiment_mood")

    if mood is not None:
        mood_label = "Positiv" if mood > 55 else "Negativ" if mood < 45 else "Nøytral"
        print(f"  Sentiment-score : {mood:.1f} / 100  ({mood_label})")
        print(f"  Effekt          : Brukt av Engine_Claude til kjøpsbeslutning")
    else:
        print("  Ingen sentiment-score lagret.")

    if headlines:
        print(f"\n  Nyhetsoverskrifter analysert ({len(headlines)} stk):")
        for i, h in enumerate(headlines, 1):
            print(f"    {i:2}. {h}")
    else:
        print("\n  Ingen nyhetsoverskrifter lagret.")


def print_empire_cycle(broker_state: dict | None):
    print("\n[9] EMPIRE-SYKLUS MAKRO-ANALYSE")
    print(SEP2)
    print("  Korrelasjon: Spania / Nederland / Storbritannia → USA i dag")
    print(SEP2)

    if not broker_state or "empire_cycle_analysis" not in broker_state:
        print("  Ingen empire-syklus analyse funnet — kjør main.py for å generere.")
        return

    ec = broker_state["empire_cycle_analysis"]

    # Syklusposisjon
    pos      = ec.get("cycle_position", "—")
    pos_pct  = ec.get("cycle_position_pct", "—")
    vol      = ec.get("volatility_regime", "—")
    risk     = ec.get("risk_level", "—")
    st_bias  = ec.get("short_term_bias", "—")
    mt_bias  = ec.get("medium_term_bias", "—")
    usd      = ec.get("usd_outlook", "—")
    parallel = ec.get("historical_parallel", "—")
    source   = ec.get("source", "—")

    print(f"  Syklusposisjon  : {pos} ({pos_pct}. percentil)")
    print(f"  Volatilitetsreg.: {vol}")
    print(f"  Risikonivå      : {risk}")
    print(f"  Kortsiktig bias : {st_bias}")
    print(f"  Mellomlangsikt  : {mt_bias}")
    print(f"  USD-utsikt      : {usd}")
    print(f"  Historisk par.  : {parallel}")
    print(f"  Analysekilde    : {source}")

    trump_st = ec.get("trump_short_term", "")
    trump_mt = ec.get("trump_medium_term", "")
    if trump_st or trump_mt:
        print()
        print("  Trump-faktor:")
        if trump_st:
            print(f"    Kort sikt  : {trump_st}")
        if trump_mt:
            print(f"    Mellomsikt : {trump_mt}")

    implications = ec.get("trading_implications", [])
    if implications:
        print()
        print("  Handlingssignaler til modellene:")
        for imp in implications:
            print(f"    • {imp}")

    full = ec.get("full_analysis", "")
    if full:
        print()
        print("  Fullstendig analyse:")
        for line in full.split("\n"):
            print(f"    {line}")


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

    broker_state = load_json("broker_state.json")
    print_portfolio_positions(broker_state)
    print_trade_history(broker_state)
    print_news_impact(broker_state)
    print_empire_cycle(broker_state)

    print_footer()

if __name__ == "__main__":
    main()
