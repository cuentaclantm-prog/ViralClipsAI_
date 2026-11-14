from pathlib import Path
import os, sys

APP_NAME = "ViralClipsAI"
def app_dir():
    if getattr(sys, "frozen", False):
        return Path(os.getenv("LOCALAPPDATA", str(Path.home()))) / APP_NAME
    return Path(__file__).resolve().parent.parent

ROOT = app_dir()
WORK = ROOT / "workspace"
OUTPUT = ROOT / "clips"
HISTORY = ROOT / "history.json"
for p in (WORK, OUTPUT):
    p.mkdir(parents=True, exist_ok=True)
