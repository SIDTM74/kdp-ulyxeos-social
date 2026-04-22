from datetime import datetime
import json
import os
from app.config import SOCIAL_LOG_DIR


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def save_log(filename: str, data: dict) -> None:
    path = os.path.join(SOCIAL_LOG_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)