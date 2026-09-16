import asyncio

from mesa.telegram.handlers import PurgeAll
from mesa.telegram.purge import ids_for_purge, purge_upto
from tests.test_bridge import _ctx, _plain, _run


def test_clear_requires_all(tmp_path):
    ctx = _ctx(tmp_path)
    say = _run(ctx, "/cmd clear")
    assert isinstance(say, str)
    assert "/cmd clear all" in _plain(say)


def test_clear_all_returns_sentinel(tmp_path):
    ctx = _ctx(tmp_path)
    result = _run(ctx, "/cmd clear all")
    assert isinstance(result, PurgeAll)
    assert result.lang == "en"
    result2 = _run(ctx, "/cmd clear todo")
    assert isinstance(result2, PurgeAll)


def test_purge_is_not_a_system_verb(tmp_path):
    ctx = _ctx(tmp_path)
    say = _run(ctx, "/cmd purge all")
    assert isinstance(say, str)
    assert "unknown" in say.lower() or "desconocido" in say.lower()


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


def test_ids_newest_first_bounded_window():
    ids = ids_for_purge(5)
    assert ids[0] == 5
    assert 1 in ids
    wide = ids_for_purge(10_000)
    assert 10_000 in wide
    assert 1 not in wide
    assert min(wide) == 10_000 - 500 + 1


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
