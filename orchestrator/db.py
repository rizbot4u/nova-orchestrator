import sqlite3, os, json, time
import os
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/orchestrator/.env"))
from pathlib import Path
DB_PATH = Path(os.environ.get("ORCH_DB", Path.home() / "orchestrator" / "data" / "orchestrator.db"))
def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row; return con
def init():
    with connect() as c:
        c.executescript("CREATE TABLE IF NOT EXISTS delegations (id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, prompt TEXT, agent TEXT, model_id TEXT, prompt_hash TEXT, routing_version TEXT, status TEXT, result TEXT, error TEXT, confirmed INTEGER DEFAULT 0);")
def log_delegation(prompt, agent, model_id, prompt_hash, routing_version, status, result=None, error=None, confirmed=False):
    with connect() as c:
        c.execute("INSERT INTO delegations (ts, prompt, agent, model_id, prompt_hash, routing_version, status, result, error, confirmed) VALUES (?,?,?,?,?,?,?,?,?,?)", (time.strftime("%Y-%m-%dT%H:%M:%S"), prompt, agent, model_id, prompt_hash, routing_version, status, json.dumps(result) if result else None, error, 1 if confirmed else 0))
def recent(limit=20):
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT * FROM delegations ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
