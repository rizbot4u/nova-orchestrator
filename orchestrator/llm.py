import os, json, re, httpx, time
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/orchestrator/.env"))
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
CALL_DELAY = float(os.environ.get("LLM_CALL_DELAY", "1.5"))
_last = [0.0]
def chat(system, user, max_tokens=800, temperature=0.2):
    if not GROQ_KEY: raise RuntimeError("GROQ_API_KEY missing")
    wait = CALL_DELAY - (time.time() - _last[0])
    if wait > 0: time.sleep(wait)
    _last[0] = time.time()
    payload = {"model": GROQ_MODEL, "messages": [{"role":"system","content":system},{"role":"user","content":user}], "max_tokens": max_tokens, "temperature": temperature}
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    last_err = None
    for attempt in range(5):
        try:
            with httpx.Client(timeout=60) as c:
                r = c.post(GROQ_URL, json=payload, headers=headers)
                if r.status_code == 429:
                    time.sleep(min(60, 5 * (2 ** attempt))); continue
                r.raise_for_status()
                data = r.json(); msg = data["choices"][0]["message"]
                return msg.get("content","").strip() or msg.get("reasoning","").strip()
        except Exception as e:
            last_err = e; time.sleep(2 ** attempt)
    raise RuntimeError(f"LLM failed: {last_err}")
def json_chat(system, user, max_tokens=800):
    content = chat(system, user, max_tokens=max_tokens, temperature=0.1)
    content = re.sub(r"^```(?:json)?", "", content).strip()
    content = re.sub(r"```$", "", content).strip()
    m = re.search(r"\{.*\}", content, re.DOTALL)
    if not m: return {}
    try: return json.loads(m.group(0))
    except json.JSONDecodeError: return {}
