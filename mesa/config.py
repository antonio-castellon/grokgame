from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    admin_telegram_ids: frozenset[int]
    gm_backend: str
    webhook_url: str
    webhook_secret: str
    webhook_reply: str
    data_dir: Path


def _parse_ids(raw: str) -> frozenset[int]:
    ids: set[int] = set()
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        ids.add(int(part))
    return frozenset(ids)


def load_config(env_file: Path | None = None) -> Config:
    load_dotenv(env_file or ROOT / ".env")
    backend = (os.getenv("GM_BACKEND") or "mock").strip().lower()
    if backend not in {"mock", "webhook"}:
        backend = "mock"
    data_dir = Path(os.getenv("DATA_DIR") or ROOT / "data")
    return Config(
        telegram_bot_token=(os.getenv("TELEGRAM_BOT_TOKEN") or "").strip(),
        admin_telegram_ids=_parse_ids(os.getenv("ADMIN_TELEGRAM_IDS") or ""),
        gm_backend=backend,
        webhook_url=(os.getenv("WEBHOOK_URL") or "").strip(),
        webhook_secret=(os.getenv("WEBHOOK_SECRET") or "").strip(),
        webhook_reply=(os.getenv("WEBHOOK_REPLY") or "http").strip().lower(),
        data_dir=data_dir,
    )
