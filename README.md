# trading-agent

Autonomous trading agent designed to run on **Claude Code Routines**. Each run
is stateless — wake up, read files for context, execute, write state, commit,
push. The git repo IS the memory.

- **Broker:** Alpaca (paper only in phase 1)
- **Research:** Perplexity (stubbed in phase 1)
- **Notify:** ClickUp (falls back to stdout)
- **Runtime:** Python 3.11, [uv](https://docs.astral.sh/uv/) for deps

For the operating manual future agent runs must follow, see [`CLAUDE.md`](CLAUDE.md).

---

## Setup

```bash
# 1. Install deps (uv recommended)
uv sync
# or: pip install -e ".[dev]"

# 2. Configure secrets
cp .env.example .env
# then fill in ALPACA_API_KEY and ALPACA_SECRET_KEY (paper creds)

# 3. Run tests
uv run pytest -q
```

## Run a task locally

```bash
uv run python -m src.orchestrator premarket_brief
uv run python -m src.orchestrator open_trade
uv run python -m src.orchestrator midday_review
uv run python -m src.orchestrator close_summary
uv run python -m src.orchestrator weekly_review
```

All tasks are stubs in phase 1 — they print and exit cleanly.

## Kill switch

```bash
echo "reason" > HALT
```

Any subsequent run will log the reason, notify, and exit 0 without trading.
Delete the file to resume:

```bash
rm HALT
```

## Paper vs. live

Paper mode is forced unless BOTH of these are true:

1. Env var `LIVE_TRADING=true`
2. `./ARMED` file exists with today's date (`YYYY-MM-DD`) on it

```bash
# To arm for live (phase 2+ only)
date +%Y-%m-%d > ARMED
export LIVE_TRADING=true
```

The date check means ARMED expires every calendar day — intentional.

## Guardrails enforced in code

- Symbol universe whitelist (`strategy/universe.yaml`)
- Max position size (% of equity)
- Max daily loss (blocks new opens, permits closes)
- Max concurrent positions
- No options, no shorts, no leverage (all toggleable in `strategy/risk_limits.yaml`)

See [`src/risk.py`](src/risk.py).

## Project layout

```
.
├── CLAUDE.md                # operating manual for agent runs
├── strategy/
│   ├── rules.md             # human-readable trading logic (edit freely)
│   ├── universe.yaml        # whitelisted tickers
│   └── risk_limits.yaml     # hard guardrails
├── memory/
│   ├── positions.json       # last-known positions
│   ├── account.json         # last-known account
│   └── journal/YYYY-MM-DD.md
├── src/                     # config, broker, risk, state, notify, orchestrator
├── tasks/                   # one file per routine
└── tests/                   # risk, paper-mode, kill-switch
```

## Phase 1 status

- [x] Scaffold + all Phase 1 modules (`config`, `state`, `risk`, `broker`, `notify`, `orchestrator`)
- [x] Tests: risk limits, paper-mode gate, kill switch
- [ ] Real trading logic in tasks (phase 2)
- [ ] Perplexity research wiring (phase 2)
- [ ] Claude Code Routines scheduling (phase 3)
