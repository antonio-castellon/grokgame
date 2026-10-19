from __future__ import annotations

import logging
import sys

from mesa.config import load_config
from mesa.gm import create_gm
from mesa.store import Store
from mesa.telegram.handlers import build_application

log = logging.getLogger("mesa")


def main() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=logging.INFO,
    )
    config = load_config()
    if not config.telegram_bot_token:
        sys.exit("TELEGRAM_BOT_TOKEN is missing. Copy .env.example to .env.")
    if config.gm_backend == "webhook" and not config.webhook_url:
        sys.exit("GM_BACKEND=webhook requires WEBHOOK_URL.")
    store = Store(config.data_dir)
    gm = create_gm(config)
    log.info("GM backend=%s data_dir=%s", config.gm_backend, config.data_dir)
    application = build_application(config, store, gm)
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
