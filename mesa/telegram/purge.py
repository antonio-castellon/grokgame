"""Wipe every Telegram message in a chat, from anyone.

Bots cannot list history. Message ids in a group are sequential, so we
delete 1..upto in batches of 100. Missing ids are skipped. The bot must
be a group admin with the Delete messages permission.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)

BATCH = 100


@dataclass
class PurgeStats:
    deleted: int = 0
    failed: int = 0
    denied: bool = False


async def purge_upto(bot: Any, chat_id: int, upto: int) -> PurgeStats:
    stats = PurgeStats()
    if upto < 1:
        return stats
    start = 1
    while start <= upto:
        end = min(start + BATCH - 1, upto)
        batch = list(range(start, end + 1))
        await _delete_batch(bot, chat_id, batch, stats)
        if stats.denied:
            return stats
        start = end + 1
    return stats


async def _delete_batch(
    bot: Any, chat_id: int, batch: list[int], stats: PurgeStats
) -> None:
    try:
        await bot.delete_messages(chat_id=chat_id, message_ids=batch)
        stats.deleted += len(batch)
        return
    except Exception as exc:
        if _is_retry(exc):
            await asyncio.sleep(_retry_after(exc))
            await _delete_batch(bot, chat_id, batch, stats)
            return
        if _is_denied(exc):
            stats.denied = True
            log.warning("purge denied chat=%s: %s", chat_id, exc)
            return
        log.debug("batch delete failed chat=%s, falling back: %s", chat_id, exc)

    for mid in batch:
        if stats.denied:
            return
        try:
            await bot.delete_message(chat_id=chat_id, message_id=mid)
            stats.deleted += 1
        except Exception as exc:
            if _is_retry(exc):
                await asyncio.sleep(_retry_after(exc))
                try:
                    await bot.delete_message(chat_id=chat_id, message_id=mid)
                    stats.deleted += 1
                    continue
                except Exception:
                    stats.failed += 1
                    continue
            if _is_denied(exc):
                stats.denied = True
                return
            stats.failed += 1


def _is_retry(exc: Exception) -> bool:
    name = type(exc).__name__
    return name == "RetryAfter" or hasattr(exc, "retry_after")


def _retry_after(exc: Exception) -> float:
    wait = getattr(exc, "retry_after", 1) or 1
    try:
        return float(wait) + 0.2
    except (TypeError, ValueError):
        return 1.2


def _is_denied(exc: Exception) -> bool:
    if type(exc).__name__ == "Forbidden":
        return True
    text = str(exc).lower()
    return (
        "not enough rights" in text
        or "need administrator" in text
        or "chat_admin_required" in text
    )
