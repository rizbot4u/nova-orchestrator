import httpx
from .base import BaseAgent
class ResearchAgent(BaseAgent):
    name = "research"
    description = "Fetch a URL and summarize"
    async def handle(self, prompt, url=None, **kw):
        if not url: return {"ok": False, "error": "research agent requires 'url'"}
        try:
            with httpx.Client(timeout=15) as c:
                r = c.get(url, headers={"User-Agent": "OrchestratorBot/1.0"}); text = r.text[:4000]
            from orchestrator import llm
            summary = llm.chat("Summarize the following in 3 bullet points.", text, max_tokens=300)
            return {"ok": True, "result": {"summary": summary, "source": url}}
        except Exception as e: return {"ok": False, "error": str(e)}
