"""
EmpireCycleAnalyst — Makro-regime analyse basert på historiske imperiers pengepolitiske sykluser.

Analyserer korrelasjonen mellom Spania, Nederland og Storbritannias hegemoni-sykluser
og USAs nåværende posisjon. Inkluderer Trumps innvirkning på volatilitet og markeder.

Gir handlingssignaler til resten av modellene i TradeX.
"""
import json
import logging
import requests

from src.config import OLLAMA_HOST, OLLAMA_MODEL_ANALYST


# ── Historiske empire-sykluser ────────────────────────────────────────────────

EMPIRE_CYCLES = {
    "Spain": {
        "hegemony_period": "1492–1640",
        "peak_years": "1580–1620",
        "duration_years": 148,
        "reserve_currency": "Spansk real (sølv-basert)",
        "decline_triggers": [
            "Inflasjon fra massiv sølvimport (New World) — Greshams lov i praksis",
            "Kronisk handelsunderskudd med Asia og Nord-Europa",
            "Militær overekspansjon: Flandern, Ottoman, England (Armada 1588)",
            "Gjeldsakkumulering: Philip II gikk konkurs 4 ganger (1557–1607)",
            "Tap av handelsmonopol til nederlandske og engelske rivaler",
        ],
        "currency_fate": "Real mistet kjøpekraft; Spania ble netto-importør av kapital",
        "cycle_end_signal": "Treaty of Westphalia 1648 — nederlandsk hegemoni bekreftet",
    },
    "Netherlands": {
        "hegemony_period": "1600–1720",
        "peak_years": "1650–1700",
        "duration_years": 120,
        "reserve_currency": "Hollandsk guilder (første moderne reservevaluta)",
        "decline_triggers": [
            "Tre Anglo-nederlandske kriger tappet Amsterdam-bankene",
            "Fransk invasjon 1672 (Rampjaar) — eksistensiell trussel",
            "Høy statsgjeld finansiert gjennom Amsterdam Wisselbank",
            "Tap av handelsruter til England (Navigation Acts)",
            "Britisk industriell revolusjon overgikk nederlandsk håndverk",
        ],
        "currency_fate": "Guilder erstattet av sterling som global reservevaluta ~1820",
        "cycle_end_signal": "Treaty of Utrecht 1713 — britisk sjøherredømme bekreftet",
    },
    "UK": {
        "hegemony_period": "1815–1945",
        "peak_years": "1870–1913",
        "duration_years": 130,
        "reserve_currency": "Britisk pund sterling (gullstandard 1821–1914)",
        "decline_triggers": [
            "WWI-gjeld til USA: Storbritannia ble netto-debitor for første gang",
            "Tap av industrielt lederskap til USA og Tyskland",
            "Sterling forlot gullstandard 1931 under Great Depression",
            "WWII tappet gullreservene — Lend-Lease låste UK til USD",
            "Bretton Woods 1944 bekreftet USD som global reservevaluta",
            "Suez-krisen 1956: USA tvang UK til tilbaketrekning — imperiet slutt",
        ],
        "currency_fate": "Sterling fra 50% av globale reserver (1950) til <5% (1980)",
        "cycle_end_signal": "Bretton Woods 1944 + Suez 1956 — pax americana etablert",
    },
}

# ── Amerikas nåværende indikatorer (2026) ─────────────────────────────────────

US_CURRENT_STATE = {
    "hegemony_start": 1944,
    "hegemony_duration_so_far": 82,
    "estimated_cycle_position_pct": 87,  # ~87. percentil av typisk 100-150 år syklus
    "indicators": {
        "debt_gdp_pct": 130,           # ~130% (UK hadde 250% etter WWII, men USD var ny)
        "usd_reserve_share_pct": 58,   # Ned fra 71% i 2000
        "manufacturing_gdp_pct": 11,   # Ned fra 28% i 1953
        "trade_deficit_bn_usd": 900,   # Kronisk, ~$900mrd/år
        "military_gdp_pct": 3.5,       # Overekspansjonsrisiko
        "challenger": "Kina + BRICS+ (petroyuan, CIPS, de-dollarisering)",
    },
    "analogies": {
        "Spain_parallel": "Kronisk handelsunderskudd + militær overekspansjon",
        "Netherlands_parallel": "Finansialisering av økonomi, tap av produksjonsbasis",
        "UK_parallel": "Gjeldsbyrde, reservevaluta-tap, utfordrer med ny økonomi",
        "stage": "Sen-hegemoni: Ligner UK i perioden 1918–1939",
    },
}

# ── Trump-faktor ──────────────────────────────────────────────────────────────

TRUMP_MACRO_FACTORS = {
    "tariff_policy": {
        "description": "Universelle importtariffer 10–25% + sektorspesifikke 50–145% (Kina)",
        "inflation_impact": "Stagflasjonsrisiko: importert inflasjon + svak vekst",
        "market_impact": "Høy volatilitet: rallies på 'deal-optimisme', fall på eskalering",
    },
    "dollar_policy": {
        "description": "Mar-a-Lago Accord spekulasjon: ønsker svakere USD for eksport",
        "currency_impact": "USD strukturelt svakere; safe-haven-etterspørsel gir motreaksjoner",
        "gold_btc": "Alternativ safe-haven: gull og BTC kan styrkes mot USD",
    },
    "geopolitical_volatility": {
        "description": "Uforutsigbar alliansepolitikk (NATO, Ukraina, Taiwan), handelskrig",
        "vix_impact": "VIX-spikes på Trump-tweets/executive orders — intradag reversaler",
        "pattern": "Short-term rally på 'America First'-narrativ, medium-term fall på fundamentals",
    },
    "fed_conflict": {
        "description": "Press på Fed for rentekutt, trussel om Powell-avskjedigelse",
        "bond_impact": "Langsiktige renter kan stige (inflasjonsforventninger) mens Fed holder",
        "yield_curve": "Bearish steepening = stress-signal for markedet",
    },
}


# ── Hoved-klassen ─────────────────────────────────────────────────────────────

class EmpireCycleAnalyst:
    """
    Makro-analytiker som sammenligner historiske imperiers pengepolitiske sykluser
    med USAs nåværende posisjon og gir handlingssignaler til TradeX-modellene.

    Bruker Ollama LLM for dyp analyse, faller tilbake på heuristikk hvis offline.
    """

    def __init__(self):
        self.host   = OLLAMA_HOST.rstrip("/")
        self.model  = OLLAMA_MODEL_ANALYST
        self.logger = logging.getLogger("EmpireCycleAnalyst")
        self.active = self._check_ollama()

    def _check_ollama(self) -> bool:
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=3)
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            return self.model in models
        except Exception:
            return False

    # ── Hoved-metode ─────────────────────────────────────────────────────────

    def analyze(self) -> dict:
        """
        Kjører full makro-regime analyse.
        Returnerer dict med: cycle_position, volatility_regime, short_term_bias,
        risk_level, trading_implications, full_analysis (tekst).
        """
        if not self.active:
            self.active = self._check_ollama()

        if self.active:
            result = self._llm_analysis()
        else:
            result = self._heuristic_analysis()

        self.logger.info(
            "EmpireCycle analyse fullført. Regime: %s | Bias: %s | Risiko: %s",
            result.get("volatility_regime"),
            result.get("short_term_bias"),
            result.get("risk_level"),
        )
        return result

    # ── LLM-analyse via Ollama ────────────────────────────────────────────────

    def _build_prompt(self) -> str:
        empires_text = ""
        for name, data in EMPIRE_CYCLES.items():
            empires_text += f"\n=== {name} ({data['hegemony_period']}) ===\n"
            empires_text += f"Reservevaluta: {data['reserve_currency']}\n"
            empires_text += f"Varighet: {data['duration_years']} år\n"
            empires_text += "Nedgangsårsaker:\n"
            for t in data["decline_triggers"]:
                empires_text += f"  - {t}\n"
            empires_text += f"Valutaskjebne: {data['currency_fate']}\n"

        us = US_CURRENT_STATE
        ind = us["indicators"]
        trump = TRUMP_MACRO_FACTORS

        return f"""Du er en ekspert i makroøkonomi, monetær historie og finansmarkeder.

## HISTORISKE EMPIRE-SYKLUSER
{empires_text}

## USA I 2026 — NÅVÆRENDE TILSTAND
- Hegemoni-varighet: {us['hegemony_duration_so_far']} år (siden Bretton Woods 1944)
- Estimert syklusposisjon: {us['estimated_cycle_position_pct']}. percentil
- Statsgjeld/BNP: {ind['debt_gdp_pct']}%
- USD-andel av globale reserver: {ind['usd_reserve_share_pct']}% (ned fra 71% i 2000)
- Produksjon/BNP: {ind['manufacturing_gdp_pct']}% (ned fra 28% i 1953)
- Handelsunderskudd: ${ind['trade_deficit_bn_usd']} mrd/år (kronisk)
- Utfordrer: {ind['challenger']}
- Historisk parallell: {us['analogies']['stage']}

## TRUMP-FAKTOREN (2025–2029)
- Tariffer: {trump['tariff_policy']['description']}
  → Markedseffekt: {trump['tariff_policy']['market_impact']}
- Dollarpolitikk: {trump['dollar_policy']['description']}
  → Valutaeffekt: {trump['dollar_policy']['currency_impact']}
- Geopolitisk volatilitet: {trump['geopolitical_volatility']['description']}
  → VIX-effekt: {trump['geopolitical_volatility']['vix_impact']}
- Fed-konflikt: {trump['fed_conflict']['description']}
  → Renteeffekt: {trump['fed_conflict']['bond_impact']}

## ANALYSE-OPPGAVE
Basert på de historiske imperiesyklusene og USAs nåværende posisjon:

1. Korreler USAs nåværende tilstand med de historiske empire-nedgangsmønstrene
2. Estimer sannsynlighet for at USA er i sen-hegemoni-fase (dvs. nær "the turn")
3. Vurder Trumps kortsiktige vs. langsiktige markedsinnvirkning
4. Gi konkrete handlingssignaler for en kvantitativ handelsbot

RETURNER KUN gyldig JSON med disse nøklene:
{{
  "cycle_position": "<Early|Mid|Late|Terminal>",
  "cycle_position_pct": <tall 0-100>,
  "volatility_regime": "<LOW|MODERATE|HIGH|EXTREME>",
  "short_term_bias": "<BULLISH|NEUTRAL|BEARISH>",
  "medium_term_bias": "<BULLISH|NEUTRAL|BEARISH>",
  "risk_level": "<LOW|MODERATE|HIGH|EXTREME>",
  "usd_outlook": "<STRENGTHEN|STABLE|WEAKEN|COLLAPSE>",
  "trump_short_term": "<string: 1 setning om kortsiktig Trump-effekt>",
  "trump_medium_term": "<string: 1 setning om mellomlangsiktig Trump-effekt>",
  "historical_parallel": "<string: hvilken empire-fase ligner dette mest>",
  "trading_implications": ["<implikasjon 1>", "<implikasjon 2>", "..."],
  "full_analysis": "<string: grundig 200-300 ord analyse på norsk>"
}}"""

    def _llm_analysis(self) -> dict:
        prompt = self._build_prompt()
        try:
            resp = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "stream": False,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Du er en makroøkonomisk analytiker spesialisert på "
                                "monetær historie og empire-sykluser. Svar alltid med gyldig JSON."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=120,
            )
            resp.raise_for_status()
            content = resp.json()["message"]["content"]
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            result = json.loads(content.strip())
            result["source"] = f"Ollama ({self.model})"
            return result
        except Exception as exc:
            self.logger.error("Ollama empire-analyse feilet: %s — bruker heuristikk.", exc)
            return self._heuristic_analysis()

    # ── Heuristisk fallback ───────────────────────────────────────────────────

    def _heuristic_analysis(self) -> dict:
        """
        Regelbasert analyse når Ollama er offline.
        Basert på hardkodede indikatorer og historiske mønstre.
        """
        pos_pct = US_CURRENT_STATE["estimated_cycle_position_pct"]

        if pos_pct >= 85:
            cycle_pos      = "Late"
            vol_regime     = "HIGH"
            risk_level     = "HIGH"
            st_bias        = "NEUTRAL"   # Trump-rallies mulig kort sikt
            mt_bias        = "BEARISH"
            usd_outlook    = "WEAKEN"
        elif pos_pct >= 70:
            cycle_pos      = "Mid"
            vol_regime     = "MODERATE"
            risk_level     = "MODERATE"
            st_bias        = "BULLISH"
            mt_bias        = "NEUTRAL"
            usd_outlook    = "STABLE"
        else:
            cycle_pos      = "Early"
            vol_regime     = "LOW"
            risk_level     = "LOW"
            st_bias        = "BULLISH"
            mt_bias        = "BULLISH"
            usd_outlook    = "STRENGTHEN"

        return {
            "cycle_position": cycle_pos,
            "cycle_position_pct": pos_pct,
            "volatility_regime": vol_regime,
            "short_term_bias": st_bias,
            "medium_term_bias": mt_bias,
            "risk_level": risk_level,
            "usd_outlook": usd_outlook,
            "trump_short_term": (
                "Tolleskandaler og deal-optimisme gir kraftige intradag-svingninger "
                "med mulige kortsiktige rallies på positive signal."
            ),
            "trump_medium_term": (
                "Stagflasjonsrisiko fra tariffer kombinert med høy gjeld "
                "øker sannsynligheten for korreksjon innen 6–18 måneder."
            ),
            "historical_parallel": (
                f"Ligner Storbritannia i perioden 1918–1939: høy gjeld, "
                f"utfordret reservevaluta, politisk ustabilitet og volatil handelspolitikk."
            ),
            "trading_implications": [
                "Øk kontantandel til minimum 20% — kapital til å kjøpe dips",
                "Stram inn stop-loss til 5% (ned fra standard 10%) pga. høy volatilitet",
                "Unngå konsentrasjon i USD-denominerte eiendeler langsiktig",
                "BTC og gull som hedge mot USD-svekkelse",
                "Kortsiktige rallies mulig på Trump-nyheter — bruk som exit-muligheter",
                "Medallion/HMM-regime særlig viktig: High_Risk_Crash = hold kontanter",
                "Prioriter ESG-godkjente ikke-amerikanske aksjer (EQNR, DNB) som diversifisering",
            ],
            "full_analysis": (
                f"HEURISTISK ANALYSE (Ollama offline):\n\n"
                f"USA befinner seg på estimert {pos_pct}. percentil av den typiske "
                f"hegemoni-syklusen på 100–150 år. Dette korrelerer sterkt med "
                f"Storbritannia i mellomkrigstiden (1918–1939): høy statsgjeld "
                f"({US_CURRENT_STATE['indicators']['debt_gdp_pct']}% av BNP), "
                f"fallende reservevaluta-andel (fra 71% til 58% siden 2000), "
                f"og tap av industriell lederstilling "
                f"({US_CURRENT_STATE['indicators']['manufacturing_gdp_pct']}% av BNP).\n\n"
                f"Trumps tariffer introduserer stagflasjonsrisiko og høy intradag-volatilitet. "
                f"Historisk mønster fra empire-syklusene: 'rally-og-fall'-dynamikk "
                f"akselererer i sen-hegemoni-fase. Kjøp-på-dip-strategier fungerer "
                f"kortsiktig, men medium-term trend er nedadgående for USD og US-aksjer "
                f"relativt til alternativer. BRICS-ekspansjon og petroyuan-initiativer "
                f"er strukturelle motvinder for USD-hegemoni."
            ),
            "source": "Heuristisk fallback (Ollama offline)",
        }
