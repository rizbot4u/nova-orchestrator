#!/usr/bin/env bash
cd "$(dirname "$0")"
OLD=$(pgrep -f "uvicorn orchestrator" | head -1)
echo "Killing old PID: ${OLD:-none}"
pkill -f "uvicorn orchestrator" 2>/dev/null
sleep 2
if pgrep -f "uvicorn orchestrator" >/dev/null; then
  echo "⚠️  Still running — force kill"
  pkill -9 -f "uvicorn orchestrator"
  sleep 1
fi
nohup ./start.sh > logs/orchestrator.log 2>&1 &
sleep 3
NEW=$(pgrep -f "uvicorn orchestrator" | head -1)
echo "New PID: ${NEW:-failed}"
if [ -n "$NEW" ] && [ "$NEW" != "$OLD" ]; then
  echo "✅ Restart confirmed"
else
  echo "❌ Restart failed"
fi
