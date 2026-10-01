import hashlib
import os
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/orchestrator/.env"))
from . import llm, db, router
from agents.trading import TradingAgent
from agents.jobs import JobsAgent
from agents.research import ResearchAgent
AGENTS = {"trading": TradingAgent(), "jobs": JobsAgent(), "research": ResearchAgent()}
SYSTEM = """Pick EXACTLY ONE sub-agent. Return JSON only: {"agent":"<name>","skill":"<skill>","params":{},"command":"<cmd>","url":""}
Valid agents: trading, jobs, research.
- trading: set "skill" (e.g. "bybit.ticker", "bybit.balance", "dkhyr.info", "dkhyr.balance") + "params".
  For bybit.ticker, params MUST be {"symbol": "<BASE>USDT", "category": "linear"} — always append USDT to the
  base asset (e.g. "BTCUSDT", not "BTCUSD" or "BTC"). Never use any other quote currency.
- jobs: set "command" (discover|score|queue|list|stats)
- research: set "url"
If nothing matches: {"agent": null}"""
async def orchestrate(prompt, tenant_id="orchestrator", org_id="orchestrator", actor="orchestrator"):
    menu = "\n".join(f"- {n}: {a.description}" for n, a in AGENTS.items())
    choice = llm.json_chat(SYSTEM, f"Available agents:\n{menu}\n\nPrompt: {prompt}", max_tokens=400)
    agent_name = choice.get("agent")
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
    routing_ver = router.current_version()
    model_id = llm.GROQ_MODEL
    if not agent_name or agent_name not in AGENTS:
        db.log_delegation(prompt, "none", model_id, prompt_hash, routing_ver, "no_match", error="no agent matched")
        return {"ok": False, "error": "no matching agent", "routing_version": routing_ver}
    agent = AGENTS[agent_name]
    result = await agent.handle(prompt, skill=choice.get("skill"), params=choice.get("params", {}), command=choice.get("command"), url=choice.get("url"), tenant_id=tenant_id, org_id=org_id, actor=actor)
    db.log_delegation(prompt, agent_name, model_id, prompt_hash, routing_ver, "ok" if result.get("ok") else "error", result=result.get("result"), error=result.get("error"))
    return {"prompt": prompt, "agent": agent_name, "model_id": model_id, "prompt_hash": prompt_hash, "routing_version": routing_ver, "result": result.get("result"), "error": result.get("error")}
