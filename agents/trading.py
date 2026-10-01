import os, httpx
from .base import BaseAgent
class TradingAgent(BaseAgent):
    name = "trading"
    description = "Live prices, balances, order placement, on-chain transfers"
    def __init__(self):
        self.bridge = os.environ.get("BRIDGE_URL", "http://127.0.0.1:8001")
        self.token = os.environ.get("BRIDGE_TOKEN", "")
    async def handle(self, prompt, skill=None, params=None, **kw):
        if not skill: return {"ok": False, "error": "trading agent requires 'skill' + 'params'"}
        payload = {"skill_name": skill, "tenant_id": kw.get("tenant_id","orchestrator"), "org_id": kw.get("org_id","orchestrator"), "actor": kw.get("actor","orchestrator"), "parameters": params or {}}
        try:
            with httpx.Client(timeout=30) as c:
                r = c.post(f"{self.bridge}/skills/execute", headers={"X-Bridge-Token": self.token, "Content-Type": "application/json"}, json=payload)
                if r.status_code >= 400: return {"ok": False, "error": f"HTTP {r.status_code}: {r.text[:200]}"}
                return {"ok": True, "result": r.json()}
        except Exception as e: return {"ok": False, "error": str(e)}
