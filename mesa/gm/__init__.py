from __future__ import annotations

from mesa.config import Config
from mesa.gm.base import GameMaster
from mesa.gm.mock import MockGM
from mesa.gm.webhook import WebhookGM


def create_gm(config: Config) -> GameMaster:
    if config.gm_backend == "webhook":
        return WebhookGM(
            url=config.webhook_url,
            secret=config.webhook_secret,
            reply_mode=config.webhook_reply,
        )
    return MockGM()
