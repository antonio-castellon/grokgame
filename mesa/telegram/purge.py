"""Wipe Telegram messages in a chat, from anyone.

Bots cannot list history. We delete a recent id window (newest first) plus
any ids the process has seen. The bot must be a group admin with
Delete messages. Starting at id 1 is too slow: missing ids eat the flood
limit and the user never sees anything disappear.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)

BATCH = 100
# Recent sequential ids. A new game group is well under this.
WINDOW = 500


@dataclass
class PurgeStats:
    deleted: int = 0
    failed: int = 0
    denied: bool = False


def ids_for_purge(upto: int, extra: Iterable[int] = ()) -> list[int]:
    if upto < 1:
        return []
    lo = max(1, upto - WINDOW + 1)
    found = set(range(lo, upto + 1))
    found.update(i for i in extra if isinstance(i, int) and 1 <= i <= upto)
    return sorted(found, reverse=True)


async def purge_upto(
    bot: Any,
    chat_id: int,
    upto: int,
    extra_ids: Iterable[int] = (),
) -> PurgeStats:
    stats = PurgeStats()
    ids = ids_for_purge(upto, extra_ids)
    log.info("purge chat=%s upto=%s count=%s", chat_id, upto, len(ids))
    i = 0
    while i < len(ids) and not stats.denied:
        batch = ids[i : i + BATCH]
        i += BATCH
        await _delete_ids(bot, chat_id, batch, stats)
    log.info(
        "purge done chat=%s deleted=%s failed=%s denied=%s",
        chat_id,
        stats.deleted,
        stats.failed,
        stats.denied,
    )
    return stats


async def _delete_ids(
    bot: Any, chat_id: int, ids: list[int], stats: PurgeStats
) -> None:
    if not ids or stats.denied:
        return
    if len(ids) == 1:
        mid = ids[0]
        try:
            await bot.delete_message(chat_id=chat_id, message_id=mid)
            stats.deleted += 1
        except Exception as exc:
            await _on_error(exc, stats, bot, chat_id, ids)
        return
    try:
        await bot.delete_messages(chat_id=chat_id, message_ids=ids)
        stats.deleted += len(ids)
        return
    except Exception as exc:
        await _on_error(exc, stats, bot, chat_id, ids)


async def _on_error(
    exc: Exception,
    stats: PurgeStats,
    bot: Any,
    chat_id: int,
    ids: list[int],
) -> None:
    if _is_retry(exc):
        await asyncio.sleep(_retry_after(exc))
        await _delete_ids(bot, chat_id, ids, stats)
        return
    if _is_denied(exc):
        stats.denied = True
        log.warning("purge denied chat=%s: %s", chat_id, exc)
        return
    if len(ids) == 1:
        stats.failed += 1
        return
    mid = len(ids) // 2
    await _delete_ids(bot, chat_id, ids[:mid], stats)
    await _delete_ids(bot, chat_id, ids[mid:], stats)


def _is_retry(exc: Exception) -> bool:
    return type(exc).__name__ == "RetryAfter" or hasattr(exc, "retry_after")


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


async def bot_can_delete(bot: Any, chat_id: int) -> bool:
    try:
        me = await bot.get_chat_member(chat_id, bot.id)
    except Exception:
        log.debug("get_chat_member failed chat=%s", chat_id, exc_info=True)
        return True
    status = str(getattr(me, "status", "") or "")
    if status == "creator":
        return True
    if status != "administrator":
        return False
    flag = getattr(me, "can_delete_messages", None)
    return flag is not False
