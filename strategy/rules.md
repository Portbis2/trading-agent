# Trading Rules — SDS 掃地僧 Stage Analysis Methodology

Source: 掃地僧股票商學院 (SDS School of Trading)
Strategy: Stan Weinstein-style Stage Analysis adapted for US equities

Risk limits in `strategy/risk_limits.yaml` are enforced by code and OVERRIDE anything in this file.
The symbol universe in `strategy/universe.yaml` is also enforced by code.

---

## Core Philosophy

Only trade Stage 2 stocks. Never buy in Stage 1, 3, or 4.
The goal is to identify stocks in confirmed uptrends, enter at low-risk breakout points, and exit
before the trend ends. Cut losses fast. Let winners run.

---

## 1. The Four Stages (四個階段)

Every stock cycles through 4 stages. Use the 200-day MA (40-week MA) as the primary orientation.

### Stage 1 — Accumulation / Bottom (築底)
Stock is recovering from a downtrend and building a base.

Characteristics:
- Price flat, no trend — oscillates in a range like "still water"
- Price oscillates around the 200-day MA and 150-day MA (30-week MA)
- Volume is low, below the 50-day volume average; noticeably contracted vs. the prior downtrend
- 200-day MA is flat (no slope)
- Prior decline of ≥30–50% is typical (new IPOs may not satisfy this)
- Base-building lasts months to years

**Action: Do not trade. Wait for Stage 2 breakout.**

### Stage 2 — Uptrend / Bull Phase (上升) ← ONLY BUY HERE
Stock is in a sustained uptrend. This is the only stage where new longs are permitted.

Characteristics:
1. 150-day MA is above the 200-day MA
2. 200-day MA is trending upward (positive slope)
3. Price is consistently above the 200-day MA
4. 50-day MA is above the 150-day MA and 200-day MA (short-term MAs above long-term MAs)
5. More up weeks than down weeks (count last 20 weeks)
6. Higher volume on up weeks
7. Steady uptrend with relatively shallow pullbacks (a浪比一浪高)

**Action: Apply Trend Template screen. Enter on valid breakouts.**

### Stage 3 — Distribution / Top (見頂)
Stock is rolling over. Early Stage 3 is the last acceptable exit zone.

Characteristics:
1. Price volatility increases — drops of 20%+ begin to appear
2. 200-day MA flattens or begins rolling over
3. Price loses the 200-day MA as a support level; large breaks below it occur
4. Volume spikes on down moves

**Action: Exit all longs. Do not buy.**

### Stage 4 — Downtrend / Bear Phase (下跌)
Stock is in a sustained downtrend. 200-day MA acts as resistance.

Characteristics:
1. Price is below the 200-day MA (200-day MA is now resistance, not support)
2. 200-day MA is trending downward
3. 150-day MA is below the 200-day MA
4. Pattern of small bounces followed by larger drops (小漲大回)
5. More down weeks than up weeks
6. Higher volume on down weeks than up weeks
7. Price makes new 52-week lows

**Action: Never buy. (Shorting is disabled in Phase 1.)**

---

## 2. Trend Template Screen (趨勢模板)

Use this screen to find Stage 2 candidates from the universe. Run pre-market.

### Trend Template 1.0 — All 5 must be true to qualify

1. Price is above the 50-day MA (10-week MA)
2. 50-day MA is above the 200-day MA
3. More up weeks than down weeks over the last 20 weeks
4. Volume increases on up weeks (compare avg volume of up weeks vs. down weeks)
5. Higher highs pattern — each swing high is above the previous swing high
   (check weekly chart; if unclear, drop to daily)

Stock passes 1.0 → **60 points** → add to watchlist.

### Trend Template 2.0 — Ranking criteria (higher score = higher priority)

1. Price is ≥ 75% of the 52-week high (the closer to the high, the better)
2. Price is ≥ 130% of the 52-week low (at least 30% above the annual low)
3. Relative Strength Ranking ≥ 70 (target 80–90; use Finviz RS or IBD RS)

Stock near 52-week high → **70 points**
Stock also has high RS ranking → **80 points** → primary target

### Scoring rubric

| Score | Meaning | Action |
|---|---|---|
| 60 | Passes Trend Template 1.0 | Add to watchlist, monitor |
| 70 | Also near 52-week high | Elevate to primary watchlist |
| 80 | Also high RS ranking | Primary target — watch for entry signal |
| 100 | Meets all buy entry criteria (Section 3) | **BUY** |

### Transition failure (false breakout) — exit if any of these appear

1. Price breaks Stage 1 high then falls back below the 200-day MA
2. Lower lows develop after the break (stock starts making lower swing lows)
3. Largest single-week drop in the past 3–12 months, accompanied by above-average volume

If any transition failure signal appears, treat as Stage 4 entry — exit immediately.

---

## 3. Entry Criteria — Best Buy Timing (最佳買入時機)

From lesson 6b "八大標準" (8 Standards). A stock must score 100 to enter.

All of Trend Template 1.0 must be true (base requirement). Then:

1. Stock is confirmed in Stage 2 (Trend Template 1.0 passes)
2. Trend Template 2.0 score ≥ 70 (near 52-week high and/or high RS)
3. A constructive chart pattern is forming: cup & handle, flat base, or triangle consolidation
   (see Chapter 7 of course for pattern details)
4. Price is breaking out of the consolidation pattern on volume ≥ 1.5× the 50-day average volume
5. Stock is a leader in a leading sector (not a laggard riding sector momentum)
6. Relative Strength Ranking ≥ 70 on Finviz or TradingView

**TODO — fill in standards 7 and 8 after watching lesson 6b.**

---

## 4. Exit Criteria — Stop Loss (止損)

From lesson 3.1a "止損方法." General principle: cut losses fast and without hesitation.

**Stop placement:**
TODO — fill in specific rule from lesson 3.1a.
Options taught in course: below the breakout pivot / below the base low / below the 50-day MA.

**Maximum loss per trade:**
TODO — fill in specific percentage from lesson 3.1a.

**Time stop:**
TODO — if stock does not make progress within X days/weeks, exit.

**Emergency stop (always active):**
- If the stock shows a transition failure signal (Section 2), exit same day.
- If daily loss hits the `max_daily_loss_pct` in `risk_limits.yaml`, no new opens.

---

## 5. Exit Criteria — Profit Taking (止盈)

From lessons 3.2a/3.2b (Strong) and 3.3a/3.3b (Weak).

### Strong-trend stocks (強勢止盈)
For stocks moving up quickly with high RS. Let the winner run.
Use the 3 sell signals to know when to exit:

**TODO — fill in the 3 specific sell signals from lesson 3.2b.**

### Weak-trend stocks (弱勢止盈)
For stocks that are moving but showing signs of slowing. Take profits earlier.

**TODO — fill in the exit rules from lesson 3.3a.**

---

## 6. Position Sizing and Discipline (控制倉位)

Hard limits enforced in code (`risk_limits.yaml` — cannot be bypassed):
- Max single position: 5% of equity
- Max daily loss: 2% of equity (stops new opens for the day)
- Max concurrent positions: 5
- No options, no shorts, no leverage

### 8 Disciplines of position control (八大紀律)
From lesson 4.1b. **TODO — fill in all 8 after watching lesson 4.1b.**

1. TODO
2. TODO
3. TODO
4. TODO
5. TODO
6. TODO
7. TODO
8. TODO

### Adding to positions (加倉)
Only pyramid into winning positions. Never average down into losers.

**TODO — fill in pyramid rules from lesson 4.2a/4.2b.**
General principle: add only when stock makes a new high with volume confirmation.

### Reducing positions (減倉)
Scale out on weakness or when sell signals appear.

**TODO — fill in specific rules from lesson 4.3.**

---

## 7. Market Regime Filters

- Skip new longs if SPY or QQQ is in Stage 3 or Stage 4 (market-wide downtrend)
- Reduce overall exposure if VIX is significantly above its 50-day moving average
- Avoid new entries in the 24 hours around FOMC decisions and major economic releases (CPI, NFP)
- Hard stop on any symbol if breaking negative news appears post-entry

---

## 8. Stock Screener — Finviz Setup

From lesson 5.3. Use Finviz to find candidates before applying the Trend Template manually:

- Market cap: Large (>$10B) — stays liquid
- Price above SMA 200
- 52-week high within 25% (i.e., price ≥ 75% of 52-week high)
- RS Rating ≥ 70
- Average volume > 500K

Cross-check results against `universe.yaml` whitelist before placing any order.

---

## 9. Research Integration (Perplexity — Phase 2)

- Premarket brief: scan for news on all watchlist names
- Skip any symbol with negative breaking news (earnings miss, SEC investigation, product recall, etc.)
- Post-entry: if negative breaking news appears during a live position, exit same day

---

## Quick-Reference: The Complete Decision Tree

```
Pre-market:
  1. Check HALT file → if present, stop.
  2. Check market regime → SPY/QQQ in Stage 2? If not, no new opens.
  3. Scan universe with Trend Template 1.0 → build watchlist.
  4. Score watchlist with Trend Template 2.0 → rank candidates.
  5. Check Perplexity for news → remove flagged names.

Intraday (open):
  6. Do any watchlist stocks show a breakout pattern on volume?
  7. Run through 8 buy criteria → must score 100 to enter.
  8. Run check_order() risk check → if blocked, do not submit.
  9. Submit order, write journal entry.

Ongoing:
  10. Monitor open positions for stop triggers and sell signals.
  11. Exit if stop hit, sell signal fires, or transition failure appears.
```
