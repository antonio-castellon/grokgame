import asyncio

from mesa.telegram.handlers import PurgeAll
from mesa.telegram.purge import purge_upto
from tests.test_bridge import _ctx, _plain, _run


def test_purge_requires_all(tmp_path):
    ctx = _ctx(tmp_path)
    say = _run(ctx, "/cmd purge")
    assert isinstance(say, str)
    assert "/cmd purge all" in _plain(say)


def test_purge_all_returns_sentinel(tmp_path):
    ctx = _ctx(tmp_path)
    result = _run(ctx, "/cmd purge all")
    assert isinstance(result, PurgeAll)
    assert result.lang == "en"
    result2 = _run(ctx, "/cmd clear todo")
    assert isinstance(result2, PurgeAll)


def test_clear_alias(tmp_path):
    ctx = _ctx(tmp_path)
    assert isinstance(_run(ctx, "/cmd clear all"), PurgeAll)


class _FakeBot:
    def __init__(self) -> None:
        self.deleted: list[int] = []
        self.fail_ids: set[int] = set()

    async def delete_messages(self, chat_id: int, message_ids: list[int]) -> None:
        if any(mid in self.fail_ids for mid in message_ids):
            raise RuntimeError("message to delete not found")
        self.deleted.extend(message_ids)

    async def delete_message(self, chat_id: int, message_id: int) -> None:
        if message_id in self.fail_ids:
            raise RuntimeError("message to delete not found")
        self.deleted.append(message_id)


def test_purge_upto_batches_and_skips():
    bot = _FakeBot()
    bot.fail_ids = {3}
    stats = asyncio.run(purge_upto(bot, -100, 5))
    assert stats.denied is False
    assert 1 in bot.deleted
    assert 5 in bot.deleted
    assert 3 not in bot.deleted
    assert stats.failed >= 1
    assert stats.deleted == 4
