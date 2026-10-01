from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from . import core, db
app = FastAPI(title="Nova Orchestrator")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET","POST"], allow_headers=["*"])
class Req(BaseModel):
    prompt: str
    tenant_id: str = "orchestrator"
    org_id: str = "orchestrator"
    actor: str = "orchestrator"
@app.get("/health")
def health():
    return {"service": "Nova Orchestrator", "stage": 8, "agents": list(core.AGENTS.keys()), "routing_version": core.router.current_version()}
@app.post("/orchestrate")
async def orchestrate(req: Req):
    if not req.prompt.strip(): raise HTTPException(400, "empty prompt")
    return await core.orchestrate(req.prompt, req.tenant_id, req.org_id, req.actor)
@app.get("/delegations")
def delegations(limit: int = 20): return db.recent(limit)
