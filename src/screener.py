"""SDS Stage Analysis screener — Trend Template implementation.

Implements the 掃地僧 (SDS) methodology:
  - Trend Template 1.0: 5 pass/fail criteria (Stage 2 qualification)
  - Trend Template 2.0: 3 ranking criteria (prioritisation within watchlist)
  - Breakout detection: new 20-day close high + volume surge

Scoring:  60 = passes TT 1.0
          70 = also near 52-week high
          80 = also outperforming SPY (RS)
         100 = 80 + confirmed breakout today → assigned by open_trade at entry

All computation is pure Python; no pandas/numpy required.
"""

from __future__ import annotations

from datetime import datetime
from itertools import groupby
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.broker import Broker

LOOKBACK_DAYS = 320  # calendar days → ~220 trading days; enough for 200-day MA
STOP_PCT = 0.07      # default stop loss: 7% below entry
RISK_PER_TRADE_PCT = 0.005  # risk 0.5% of equity per trade


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sma(values: list[float], n: int) -> float | None:
    if len(values) < n:
        return None
    return sum(values[-n:]) / n


def _week_key(bar: dict) -> tuple[int, int]:
    dt = datetime.fromisoformat(bar["t"].replace("Z", "+00:00"))
    return dt.isocalendar()[:2]  # (iso_year, iso_week)


# ---------------------------------------------------------------------------
# Core indicator computation
# ---------------------------------------------------------------------------

def compute_indicators(bars: list[dict]) -> dict | None:
    """Compute all SDS technical indicators from a list of daily OHLCV bars.

    Returns None when there are fewer than 210 bars (cannot compute 200-day MA).
    Each bar must be a dict with keys: t (ISO timestamp), o, h, l, c, v.
    """
    if len(bars) < 210:
        return None

    closes = [b["c"] for b in bars]
    volumes = [b["v"] for b in bars]

    ma50 = _sma(closes, 50)
    ma150 = _sma(closes, 150)
    ma200 = _sma(closes, 200)
    if not (ma50 and ma150 and ma200):
        return None

    current = closes[-1]

    # 52-week high/low (last 252 trading days)
    lk = closes[-252:] if len(closes) >= 252 else closes
    high_52w = max(lk)
    low_52w = min(lk)

    vol_ma50 = _sma(volumes, 50) or 1.0
    today_vol = volumes[-1]

    # --- Weekly stats (last ~26 weeks) ---
    recent_bars = sorted(bars[-130:], key=lambda b: b["t"])
    up_weeks = down_weeks = 0
    vol_up: list[float] = []
    vol_dn: list[float] = []
    weekly_highs: list[float] = []

    for _, week_iter in groupby(recent_bars, key=_week_key):
        wk = list(week_iter)
        w_open = wk[0]["o"]
        w_close = wk[-1]["c"]
        w_high = max(b["h"] for b in wk)
        w_vol = float(sum(b["v"] for b in wk))
        weekly_highs.append(w_high)
        if w_close > w_open:
            up_weeks += 1
            vol_up.append(w_vol)
        elif w_close < w_open:
            down_weeks += 1
            vol_dn.append(w_vol)

    avg_vol_up = sum(vol_up) / len(vol_up) if vol_up else 0.0
    avg_vol_dn = sum(vol_dn) / len(vol_dn) if vol_dn else 1.0

    # Higher highs: last 4 consecutive weekly highs must all be ascending
    rh = weekly_highs[-4:] if len(weekly_highs) >= 4 else []
    higher_highs = len(rh) == 4 and rh[0] < rh[1] < rh[2] < rh[3]

    # 3-month (63 trading day) performance
    idx_3m = -min(63, len(closes) - 1)
    perf_3m = (closes[-1] / closes[idx_3m]) - 1.0

    # Breakout: new 20-day closing high + volume ≥ 1.5× 50-day avg
    prior_20 = closes[-21:-1]
    high_20d = max(prior_20) if prior_20 else current
    breakout = (current > high_20d) and (today_vol >= 1.5 * vol_ma50)

    return {
        "close": current,
        "ma50": ma50,
        "ma150": ma150,
        "ma200": ma200,
        "high_52w": high_52w,
        "low_52w": low_52w,
        "vol_today": today_vol,
        "vol_ma50": vol_ma50,
        "up_weeks": up_weeks,
        "down_weeks": down_weeks,
        "avg_vol_up": avg_vol_up,
        "avg_vol_dn": avg_vol_dn,
        "higher_highs": higher_highs,
        "perf_3m": perf_3m,
        "breakout_today": breakout,
    }


# ---------------------------------------------------------------------------
# Trend Template checks
# ---------------------------------------------------------------------------

def trend_template_10(ind: dict) -> tuple[bool, dict]:
    """Trend Template 1.0 — all 5 criteria must pass."""
    checks = {
        "price_above_ma50": ind["close"] > ind["ma50"],
        "ma50_above_ma200": ind["ma50"] > ind["ma200"],
        "more_up_weeks": ind["up_weeks"] > ind["down_weeks"],
        "vol_higher_on_up_weeks": ind["avg_vol_up"] > ind["avg_vol_dn"],
        "higher_highs": ind["higher_highs"],
    }
    return all(checks.values()), checks


def trend_template_20(ind: dict, spy_perf_3m: float | None) -> dict:
    """Trend Template 2.0 — ranking / prioritisation metrics."""
    c, high, low = ind["close"], ind["high_52w"], ind["low_52w"]
    near_high = (c >= 0.75 * high) if high > 0 else False
    above_low = (c >= 1.30 * low) if low > 0 else False
    rs = ind["perf_3m"] - (spy_perf_3m or 0.0)
    return {
        "near_52w_high": near_high,
        "above_52w_low": above_low,
        "pct_from_high": round((c / high - 1.0) * 100, 1) if high > 0 else -100.0,
        "rs_vs_spy_pct": round(rs * 100, 1),
        "outperforming_spy": rs > 0,
    }


def sds_score(t10_passes: bool, t20: dict) -> int:
    """SDS watchlist score. 100 is reserved for confirmed-breakout buys (set in open_trade)."""
    if not t10_passes:
        return 0
    score = 60
    if t20["near_52w_high"]:
        score = 70
    if t20["outperforming_spy"] and t20["near_52w_high"]:
        score = 80
    return score


# ---------------------------------------------------------------------------
# Position sizing
# ---------------------------------------------------------------------------

def calc_position(equity: float, entry_price: float, max_pos_pct: float = 0.05) -> dict:
    """Calculate shares, stop, and target for a new entry.

    Risk model: lose at most RISK_PER_TRADE_PCT of equity if stop is hit.
    Stop: STOP_PCT below entry. Target: 3:1 reward/risk.
    """
    risk_dollars = equity * RISK_PER_TRADE_PCT
    shares = int(risk_dollars / (entry_price * STOP_PCT))
    max_shares = int((equity * max_pos_pct) / entry_price)
    shares = max(1, min(shares, max_shares))
    stop = round(entry_price * (1 - STOP_PCT), 2)
    target = round(entry_price * (1 + STOP_PCT * 3), 2)  # 3:1 reward
    return {"shares": shares, "stop": stop, "target": target}


# ---------------------------------------------------------------------------
# Full universe screen
# ---------------------------------------------------------------------------

def screen_universe(broker: "Broker", universe: list[str]) -> list[dict]:
    """Screen every symbol in universe with the SDS Trend Template.

    Returns a list sorted by score (descending), then by RS vs SPY.
    Each entry is a flat dict suitable for JSON serialisation.
    """
    spy_perf: float | None = None
    if "SPY" in universe:
        try:
            spy_bars = broker.get_bars("SPY", timeframe="1Day", lookback_days=LOOKBACK_DAYS)
            spy_ind = compute_indicators(spy_bars)
            if spy_ind:
                spy_perf = spy_ind["perf_3m"]
        except Exception:
            pass

    results: list[dict] = []
    for symbol in universe:
        try:
            bars = broker.get_bars(symbol, timeframe="1Day", lookback_days=LOOKBACK_DAYS)
            ind = compute_indicators(bars)
            if ind is None:
                results.append({"symbol": symbol, "score": 0, "error": "insufficient data"})
                continue

            t10_ok, t10_checks = trend_template_10(ind)
            t20 = trend_template_20(ind, spy_perf)
            score = sds_score(t10_ok, t20)

            results.append({
                "symbol": symbol,
                "score": score,
                "close": round(ind["close"], 2),
                "ma50": round(ind["ma50"], 2),
                "ma200": round(ind["ma200"], 2),
                "high_52w": round(ind["high_52w"], 2),
                "pct_from_high": t20["pct_from_high"],
                "rs_vs_spy_pct": t20["rs_vs_spy_pct"],
                "breakout_today": ind["breakout_today"],
                "up_weeks": ind["up_weeks"],
                "down_weeks": ind["down_weeks"],
                "perf_3m_pct": round(ind["perf_3m"] * 100, 1),
                "t10_pass": t10_ok,
                "t10_checks": t10_checks,
                "t20": t20,
                "indicators": ind,
            })
        except Exception as e:
            results.append({"symbol": symbol, "score": 0, "error": str(e)})

    results.sort(key=lambda x: (x["score"], x.get("rs_vs_spy_pct", 0)), reverse=True)
    return results


# ---------------------------------------------------------------------------
# Sell-signal checks (for open positions)
# ---------------------------------------------------------------------------

def check_sell_signals(ind: dict, entry_price: float, stop_price: float) -> dict:
    """Evaluate sell signals for an open long position.

    Returns dict with {triggered: bool, reason: str, signal_name: str}.
    """
    c = ind["close"]

    # Hard stop
    if c <= stop_price:
        return {"triggered": True, "signal_name": "hard_stop",
                "reason": f"close {c:.2f} ≤ stop {stop_price:.2f} (−7%)"}

    # Below 50-day MA on above-average volume — strong sell signal
    if c < ind["ma50"] and ind["vol_today"] > 1.5 * ind["vol_ma50"]:
        return {"triggered": True, "signal_name": "below_ma50_high_vol",
                "reason": f"close {c:.2f} < MA50 {ind['ma50']:.2f} on high volume"}

    # Stage 3 transition: close below 200-day MA
    if c < ind["ma200"]:
        return {"triggered": True, "signal_name": "below_ma200",
                "reason": f"close {c:.2f} < MA200 {ind['ma200']:.2f} — Stage 3 signal"}

    return {"triggered": False, "signal_name": "", "reason": ""}
