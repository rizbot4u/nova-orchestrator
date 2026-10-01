import os, subprocess
from .base import BaseAgent
JOB_DIR = os.environ.get("JOB_AGENT_DIR", os.path.expanduser("~/job-agent"))
class JobsAgent(BaseAgent):
    name = "jobs"
    description = "Job discovery, scoring, drafting applications"
    async def handle(self, prompt, command=None, **kw):
        if not command: return {"ok": False, "error": "jobs agent requires 'command'"}
        if command not in ("discover","score","queue","list","stats"): return {"ok": False, "error": f"unknown command: {command}"}
        venv_py = os.path.join(JOB_DIR, "venv", "bin", "python")
        if not os.path.exists(venv_py): return {"ok": False, "error": f"job-agent venv not found at {venv_py}"}
        try:
            r = subprocess.run([venv_py, "-m", "job_agent.main", command], cwd=JOB_DIR, capture_output=True, text=True, timeout=120)
            return {"ok": r.returncode == 0, "result": r.stdout[-2000:], "error": r.stderr[-500:] if r.returncode != 0 else None}
        except Exception as e: return {"ok": False, "error": str(e)}
