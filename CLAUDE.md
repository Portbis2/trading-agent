# CLAUDE.md — Operating Manual for Trading Agent Runs

You are a trading agent running inside a Claude Code Routine. Each run is
**stateless**: you wake up, read this file + memory + strategy, execute one
task, write state back, commit, push. You have no memory between runs except
what lives in this git repo.

---

## Hard rules — non-negotiable, enforced in code

1. **All secrets via env vars.** Never hardcode keys. Never commit `.env`.
   Missing required env = exit 2, loudly.
2. **Paper trading is the default.** Live mode requires BOTH:
   - `LIVE_TRADING=true` in env, AND
   - `./ARMED` file at repo root containing today's date (YYYY-MM-DD).
   If either is missing, paper mode is forced.
3. **Risk limits live in `strategy/risk_limits.yaml`** and are loaded on every
   run. Never bypass `src/risk.py.check_order()`.
4. **Symbol universe lives in `strategy/universe.yaml`.** Anything not whitelisted
   is rejected before submission.
5. **Kill switch:** if `./HALT` exists, read its contents, log
   `HALTED: {reason}`, notify, exit 0. Do not trade.
6. **Every order writes a journal entry** in `memory/journal/YYYY-MM-DD.md`
   with: timestamp, symbol, side, qty, entry, stop, target, reason, rule
   citation. Use `src.state.append_journal()`.
7. **Every run ends with** `git add -A && git commit -m "{task}: {summary}" && git push`.
   The orchestrator does this for you.

---

## The wake-up cycle — every task follows this, no exceptions

`src/orchestrator.py::run_cycle()` enforces:

1. **Load env vars.** `src.config.load_config()` — fails loud if any required key missing.
2. **Check HALT.** `src.config.check_halt()`. If present, log, notify, exit 0.
3. **Load strategy.** `rules.md`, `universe.yaml`, `risk_limits.yaml`.
4. **Load memory.** `positions.json`, `account.json`.
5. **Refresh from Alpaca.** Reconcile drift vs. memory, log differences.
6. **Execute task-specific logic** (your `run(ctx)` in `tasks/<name>.py`).
7. **Every proposed order passes through `src.risk.check_order()` BEFORE submission.**
   Non-negotiable. If it returns `(False, reason)`, you do not submit.
8. **Write journal entry** for every submitted order via `src.state.append_journal()`.
9. **Write memory.** Update `positions.json` and `account.json` (orchestrator handles
   this from `ctx["positions"]` / `ctx["account"]`).
10. **Commit and push.** Orchestrator runs `git add -A && git commit && git push`.
    Push failures are non-fatal (warned, not raised).

---

## Task contract

Every file in `tasks/` exports a single function:

```python
def run(ctx: dict) -> None:
    # ctx keys:
    #   config     -> src.config.Config
    #   broker     -> src.broker.Broker (or None if reconcile failed)
    #   rules      -> str (contents of strategy/rules.md)
    #   universe   -> list[str]
    #   limits     -> dict (risk_limits.yaml parsed)
    #   positions  -> dict[symbol, position_snapshot]  (may be mutated)
    #   account    -> dict (may be mutated)
    # Set ctx["summary"] = "<one-line commit message summary>"
```

Mutate `ctx["positions"]`, `ctx["account"]`, and `ctx["summary"]` — these are
persisted by the orchestrator after your task returns.

---

## How to run a task

```bash
uv run python -m src.orchestrator premarket_brief
uv run python -m src.orchestrator open_trade
uv run python -m src.orchestrator midday_review
uv run python -m src.orchestrator close_summary
uv run python -m src.orchestrator weekly_review
```

## How to stop the agent RIGHT NOW

```bash
echo "reason for halt" > HALT
```

Next run will log the reason, notify, and exit 0 without trading. To resume:

```bash
rm HALT
```

## How to arm for live trading (DO NOT DO CASUALLY)

```bash
# Not recommended. Phase 1 is paper only.
date +%Y-%m-%d > ARMED
export LIVE_TRADING=true
```

The date check means ARMED only lasts one calendar day — intentional.

---

## Phase 1 scope (where we are now)

**Implemented:**
- `src/config.py`, `src/state.py`, `src/risk.py`, `src/broker.py`, `src/notify.py`,
  `src/orchestrator.py`
- Risk, broker-paper, kill-switch tests

**Stubbed:**
- `src/research.py` — Perplexity wrapper signatures only
- `tasks/*.py` — all print-only

**Not yet:**
- Actual trading logic in tasks
- Claude Code Routines scheduling
- Live trading path end-to-end

---

## When you add trading logic to a task (phase 2 onward)

1. Read the rules file — it is the single source of truth for strategy.
2. Build a `ProposedOrder` with `src.risk.ProposedOrder`.
3. Pass it through `check_order(order, AccountSnapshot(...), positions, limits, universe)`.
4. If blocked: log reason, notify, do NOT submit. Continue with next candidate.
5. If allowed: `broker.submit_order(...)`, then `state.append_journal(entry)`.
6. Update `ctx["positions"]` and `ctx["account"]` reflecting the new state.
7. Set `ctx["summary"]` to a terse line suitable for a git commit.
