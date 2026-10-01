import yaml
import os
from dotenv import load_dotenv
load_dotenv(os.path.expanduser("~/orchestrator/.env"))
from pathlib import Path
CONFIG = Path.home() / "orchestrator" / "config" / "routing.yaml"
def load_routing():
    with open(CONFIG) as f: return yaml.safe_load(f)
def current_version():
    return load_routing().get("version", "unknown")
