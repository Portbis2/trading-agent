#!/usr/bin/env bash
# Wrapper for cron — loads .env and runs a single orchestrator task.
# Usage: run_task.sh <task_name>
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
TASK="${1:?usage: run_task.sh <task_name>}"
LOG_DIR="$REPO/logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/${TASK}_$(date +%Y-%m-%d).log"

# Load secrets
if [ -f "$REPO/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "$REPO/.env"
  set +a
fi

export PATH="/Users/cy/Library/Python/3.9/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) $TASK ===" >> "$LOG"
cd "$REPO"
/Users/cy/Library/Python/3.9/bin/uv run python -m src.orchestrator "$TASK" >> "$LOG" 2>&1
echo "=== done ===" >> "$LOG"
