#!/usr/bin/env bash
cd "$(dirname "$0")"
source venv/bin/activate
exec uvicorn orchestrator.server:app --host 0.0.0.0 --port "${ORCH_PORT:-8010}"
