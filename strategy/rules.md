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
7. Base quality — the consolidation before the breakout must be at least 3 weeks long and
   the correction depth must not exceed 35% from the base high to base low. A tight, shallow
   base indicates low selling pressure and institutional accumulation (the VCP pattern from Ch 7).
8. Volume dry-up during consolidation — in the final 5 trading days before the breakout, daily
   volume should be consistently below the 50-day average (sellers exhausted). The breakout day
   itself must then show a volume surge ≥ 1.5× the 50-day average. This combination of
   volume contraction → volume expansion is the strongest confirmation of a valid breakout.

*Default values derived from Chapter 5 ("一個一買就賺錢的圖表形態"), Chapter 7 chart patterns,
and Minervini-style VCP criteria consistent with the SDS Stage 2 methodology.
Refine after watching lesson 6b for SDS-specific numbers.*

---

## 4. Exit Criteria — Stop Loss (止損)

From lesson 3.1a "止損方法." General principle: cut losses fast and without hesitation.

**Stop placement — 2-step rule:**
1. *Structural stop*: place the stop just below the lowest close of the consolidation base
   (the 10-day low before breakout). This is the level where the trade thesis is invalidated —
   if price falls back below the breakout pivot, the breakout failed.
2. *Hard cap*: if the structural stop is more than 7% below entry, use 7% instead.
   Never risk more than 7% on any single trade regardless of base shape.
Use whichever stop is tighter (closer to entry = smaller loss).

**Maximum loss per trade:** 7% from entry (hard cap). Position size is calculated so that
hitting the stop costs no more than 0.5% of total account equity.

**Time stop:** 8 weeks. If the stock has not made meaningful progress (price no higher than
entry + 5%) after 8 weeks, exit at market close on Friday of week 8. Capital should be
deployed in a more active opportunity.

**Trailing stop after a 20% gain:** Once unrealised profit reaches +20%, trail the stop up
to the 50-day MA. Never let a +20% winner turn into a loss.

*Default values consistent with Minervini SEPA / SDS Stage 2 methodology.
Refine specific % after watching lesson 3.1a.*

**Emergency stop (always active):**
- If the stock shows a transition failure signal (Section 2), exit same day.
- If daily loss hits the `max_daily_loss_pct` in `risk_limits.yaml`, no new opens.

---

## 5. Exit Criteria — Profit Taking (止盈)

From lessons 3.2a/3.2b (Strong) and 3.3a/3.3b (Weak).

### Strong-trend stocks (強勢止盈)
For stocks moving up quickly with high RS. Let the winner run.
Use the 3 sell signals to know when to exit:

**Signal 1 — Climax top / exhaustion run (高潮頂部)**
The stock makes its largest single-week price gain in the past 3–6 months,
accompanied by the highest weekly volume in that same period. This is
institutional distribution into retail euphoria — exit into the strength, not
after it. Do not wait for confirmation; the climax run IS the signal.

**Signal 2 — First decisive close below the 50-day MA on high volume**
After a sustained Stage 2 run, when price closes below the 50-day MA on
above-average volume (≥1.5× the 50-day vol average), the uptrend structure is
breaking. Exit at or near the close that day. This is distinct from the stop
loss (which triggers at a fixed price); this is a discretionary read on trend
health. Do not wait for a second close below — the first one with volume is
enough.

**Signal 3 — Lower high confirmed (型態破壞)**
Price makes a swing high that is lower than the previous swing high, then
fails to recover. Two consecutive lower highs = Stage 3 entry confirmed.
Exit the position in full. Do not "wait to see" — by the time a lower low is
also confirmed, the best exit price has already passed.

*Default values derived from Weinstein Stage Analysis Chapter 4 and Minervini
SEPA sell rules. Refine exact thresholds after watching lesson 3.2b.*

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
From lesson 4.1b. *Defaults below are consistent with Weinstein/Minervini — refine after watching lesson 4.1b.*

1. **Set the stop before entry, not after.** The exit price is decided at the
   moment of entry. If you cannot define where the trade is wrong, you cannot
   enter it.

2. **Never average down into a loser.** A stock that falls after entry is
   giving you information — the thesis is weakening. Adding more capital into
   weakness compounds the loss. Only add to positions that are moving in your
   favour.

3. **Never let a +20% winner turn into a loss.** Once unrealised profit reaches
   +20%, trail the stop up to the 50-day MA (Section 4). Locking in a floor is
   more important than maximising the upside.

4. **One position, one risk unit.** Each trade risks exactly RISK_PER_TRADE_PCT
   (0.5%) of equity — no "high-conviction" sizing up. Conviction comes from the
   screen criteria, not from feeling. Consistency in sizing is what makes the
   statistics work.

5. **Do not trade in a Stage 3 or Stage 4 market.** Check SPY and QQQ first.
   If the market regime fails the Stage 2 check, hold cash. Individual stock
   strength cannot overcome a falling market tide.

6. **Exit the full position on a stop or sell signal — no partial holds.**
   When a signal fires, exit completely and immediately. "I'll sell half and see"
   is how small losses become large ones. Partial exits are only used when
   deliberately scaling out on strength (Section 5).

7. **Take the 8-week time stop without exception.** If a stock has not made
   meaningful progress (less than +5%) after 8 weeks, exit on Friday close.
   Dead capital has an opportunity cost. Move to a more active candidate.

8. **Record every trade in the journal before moving on.** No journal entry =
   the trade did not happen in the system's memory. Reviewing past entries is
   the only way to identify pattern errors. The journal is not optional.

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
