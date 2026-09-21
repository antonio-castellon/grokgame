"""Inline button helpers: claim, short tokens, normalize."""

from __future__ import annotations

from pathlib import Path

from mesa.buttons import (
    build_inline_keyboard,
    claim_message_tap,
    label_from_callback_message,
    normalize_buttons,
    resolve_callback_data,
)


def test_claim_message_tap_first_wins(tmp_path: Path):
    assert claim_message_tap(tmp_path, -100, 42, verb="hit", uid=1) is True
    assert claim_message_tap(tmp_path, -100, 42, verb="hit", uid=2) is False
    assert claim_message_tap(tmp_path, -100, 43, verb="stand", uid=2) is True


def test_long_id_maps_to_short_callback(tmp_path: Path):
    long_id = "verb-" + ("x" * 80)
    kb = build_inline_keyboard(
        [{"id": long_id, "label": "Go"}],
        chat_id=7,
        data_dir=tmp_path,
    )
    cb = kb.inline_keyboard[0][0].callback_data
    assert cb is not None
    assert len(cb.encode("utf-8")) <= 64
    assert resolve_callback_data(tmp_path, 7, cb) == long_id


def test_short_id_passthrough(tmp_path: Path):
    kb = build_inline_keyboard(
        [{"id": "hit", "label": "Hit"}],
        chat_id=1,
        data_dir=tmp_path,
    )
    assert kb.inline_keyboard[0][0].callback_data == "hit"
    assert resolve_callback_data(tmp_path, 1, "hit") == "hit"


def test_normalize_buttons_accepts_text_alias():
    assert normalize_buttons([{"id": "a", "text": "A"}]) == [{"id": "a", "label": "A"}]
    assert normalize_buttons(None) == []
    assert normalize_buttons("nope") == []


def test_label_from_callback_message_dict():
    msg = {
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "Hit me", "callback_data": "hit"}],
            ]
        }
    }
    assert label_from_callback_message(msg, "hit") == "Hit me"
    assert label_from_callback_message(msg, "miss") is None
