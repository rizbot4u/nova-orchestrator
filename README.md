# Nova Orchestrator

**Multi-agent delegation layer.** An orchestrator LLM routes each user prompt to the right sub-agent, enforces policy, and logs every decision with model + routing attribution.

Stage 8 of the Nova agent stack — the layer that turns a single agent into a system.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-green)
![Groq](https://img.shields.io/badge/Groq-gpt--oss--120b-orange)

---

## What This Is

A single REST endpoint (`/orchestrate`) that receives a natural-language prompt, asks an LLM to pick the correct sub-agent, delegates, and returns the result. Every delegation is logged with:

- **`agent`** — which sub-agent ran (trading, jobs, research)
- **`model_id`** — which LLM made the routing decision
- **`prompt_hash`** — SHA-256 fingerprint of the prompt (reproducible)
- **`routing_version`** — which policy version decided the route

This closes a common gap in agent systems: **audit logs prove what ran, but not what decided it.** Nova Orchestrator logs both.

---

## Architecture

```
User prompt
    │
    ▼
┌────────────────────────────────┐
│  Orchestrator (Groq LLM)       │
│  Picks one sub-agent           │
└────────────┬───────────────────┘
             │
   ┌─────────┼──────────┬───────────────┐
   ▼         ▼          ▼               ▼
┌───────┐ ┌───────┐ ┌────────┐    ┌────────────┐
│trading│ │ jobs  │ │research│    │  (future)  │
└───┬───┘ └───┬───┘ └───┬────┘    └────────────┘
    │         │         │
    ▼         ▼         ▼
Nova MCP   Job Agent  Fetch +
Bridge      CLI       Summarize
    │
    ▼
Bybit V5 / Base Mainnet
```

Each sub-agent returns `{"ok": bool, "result": ..., "error": ...}`. The orchestrator logs the outcome either way.

---

## Sub-Agents

| Agent | Wraps | What it does |
|---|---|---|
| **trading** | [Nova MCP Bridge](https://github.com/rizbot4u/nova_mcp) | Live prices, balances, order placement, on-chain transfers |
| **jobs** | [Job Agent](https://github.com/rizbot4u/job-agent) | Job discovery, scoring, drafting applications |
| **research** | (built-in) | Fetch a URL, summarize with the LLM |

Add a new sub-agent by dropping a file in `agents/`, subclassing `BaseAgent`, and registering it in `orchestrator/core.py`.

---

## The Audit Gap This Solves

An audit log without model attribution cannot distinguish:

- a **policy error** (the routing rule said wrong)
- a **model error** (the LLM picked wrong)

Adding `model_id`, `prompt_hash`, and `routing_version` to every record makes both diagnosable. It also makes the routing decision itself versionable — bump `config/routing.yaml` and the version flows through every log entry.

---

## Versioned Routing Policy

`config/routing.yaml`:

```yaml
version: "routing@v1"
rules:
  trading:
    agent: trading
    description: "Live prices, balances, on-chain transfers"
  jobs:
    agent: jobs
    description: "Job discovery, scoring, drafting"
  research:
    agent: research
    description: "Fetch a URL and summarize"
```

Bump `version` on every change. Now when a model swap or rule change alters behavior, you can correlate it with the audit log.

---

## Quick Start

```bash
git clone https://github.com/rizbot4u/nova-orchestrator.git
cd nova-orchestrator
cp .env.example .env
nano .env                    # fill GROQ_API_KEY + BRIDGE_TOKEN
./start.sh
```

Server runs on `http://127.0.0.1:8010`.

### Test it

```bash
# In another terminal
python cli.py "what is btc doing"
python cli.py "find me jobs above 70 fit score"
python cli.py "summarize https://example.com"
```

### Check the audit log

```bash
curl -s http://127.0.0.1:8010/delegations?limit=10 | python3 -m json.tool
```

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Orchestrator status, agents, routing version |
| `POST` | `/orchestrate` | Main entry — `{"prompt": "..."}` |
| `GET` | `/delegations` | Last N delegation records |

Full OpenAPI docs at `/docs` when running.

---

## Example Response

```json
{
  "prompt": "what is btc doing",
  "agent": "trading",
  "model_id": "openai/gpt-oss-120b",
  "prompt_hash": "eaa5220f3d032f0f",
  "routing_version": "routing@v1",
  "result": {
    "skill": "bybit.ticker",
    "result": {
      "retCode": 0,
      "result": {
        "list": [{ "symbol": "BTCUSD", "lastPrice": "83723.10" }]
      }
    }
  },
  "error": null
}
```

Every field is either the LLM's decision (agent, model_id) or the policy that constrained it (routing_version). Both are logged.

---

## Repository Structure

```
nova-orchestrator/
├── agents/           Sub-agents
│   ├── base.py       Abstract BaseAgent
│   ├── trading.py    → Nova MCP Bridge
│   ├── jobs.py       → Job Agent CLI
│   └── research.py   → fetch + summarize
├── orchestrator/     Core
│   ├── core.py       Routing + delegation logic
│   ├── db.py         SQLite audit log
│   ├── llm.py        Groq client (throttle + retry)
│   ├── router.py     Loads versioned routing policy
│   └── server.py     FastAPI app
├── config/
│   └── routing.yaml  Versioned policy
├── cli.py            Quick CLI client
├── start.sh
└── requirements.txt
```

---

## Tech Stack

Python · FastAPI · httpx · SQLite · PyYAML · Groq (gpt-oss-120b)

---

## Status

| Component | Status |
|---|---|
| Orchestrator + LLM routing | Live |
| Trading sub-agent | Live — real Bybit V5 |
| Jobs sub-agent | Live — real Job Agent CLI |
| Research sub-agent | Live — fetch + summarize |
| Versioned routing policy | Live — `routing@v1` |
| Model attribution in audit log | Live |
| Rate limiting / auth | Planned |
| Sentinel guardrail agent | Planned (Stage 9) |

---

## Why This Exists

Most agent demos stop at Stage 5 or 6 (a single agent with tools). Stage 8 is the layer above — the one that decides *which* specialist handles *what*, and logs that decision so it can be reviewed later.

That layer is what stays constant when models change.

---

## Contact

**Rizwan Ali**
Founder · Nova Global Keys

- GitHub: [github.com/rizbot4u](https://github.com/rizbot4u)
- LinkedIn: [linkedin.com/in/rizwan-ali-974073377](https://www.linkedin.com/in/rizwan-ali-974073377)
- Bybit Broker: Kr000820

---

MIT License
