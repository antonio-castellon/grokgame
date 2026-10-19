"""Webhook wake: whsec_ Standard Webhooks vs crsr_ Bearer."""

from __future__ import annotations

import base64
from typing import Any

import httpx
import pytest

from mesa.gm.webhook import (
    HEADER_ID,
    HEADER_SIGNATURE,
    HEADER_TIMESTAMP,
    WebhookGM,
    normalize_webhook_urls,
    wake_auth_mode,
)


def test_wake_auth_mode():
    assert wake_auth_mode("whsec_abc") == "standard"
    assert wake_auth_mode("crsr_sender_key_here") == "bearer"
    assert wake_auth_mode("") == "standard"


def test_normalize_webhook_urls_prefers_api2():
    uid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    urls = normalize_webhook_urls(f"https://cursor.com/hook/{uid}?x=1")
    assert urls[0] == f"https://api2.cursor.sh/automations/webhook/{uid}"
    assert any(uid in u for u in urls)


@pytest.mark.asyncio
async def test_standard_whsec_sends_signature_headers(monkeypatch):
    secret = "whsec_" + base64.b64encode(b"0123456789abcdef01234567").decode("ascii")
    captured: dict[str, Any] = {}

    class _Resp:
        status_code = 200
        content = b'{"schema":"mesa.v1.reply","say":"hi"}'

        def raise_for_status(self) -> None:
            return None

    class _Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return None

        async def post(self, url, content=None, headers=None, json=None):
            captured["url"] = url
            captured["headers"] = dict(headers or {})
            captured["content"] = content
            captured["json"] = json
            return _Resp()

    monkeypatch.setattr(httpx, "AsyncClient", _Client)
    gm = WebhookGM(url="https://example.com/hook", secret=secret)
    out = await gm.reply({"schema": "mesa.v1", "verb": "status"})
    assert out is not None
    assert "say" in out
    assert HEADER_ID in captured["headers"]
    assert HEADER_TIMESTAMP in captured["headers"]
    assert HEADER_SIGNATURE in captured["headers"]
    assert "Authorization" not in captured["headers"]
    assert captured["content"]


@pytest.mark.asyncio
async def test_bearer_crsr_sends_authorization(monkeypatch):
    secret = "crsr_test_sender_key_001"
    captured: dict[str, Any] = {}

    class _Resp:
        status_code = 200
        content = b'{"say":"yo"}'

        def raise_for_status(self) -> None:
            return None

    class _Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return None

        async def post(self, url, content=None, headers=None, json=None):
            captured.setdefault("urls", []).append(url)
            captured["headers"] = dict(headers or {})
            captured["json"] = json
            return _Resp()

    monkeypatch.setattr(httpx, "AsyncClient", _Client)
    uid = "11111111-2222-3333-4444-555555555555"
    gm = WebhookGM(url=f"https://other.example/{uid}", secret=secret)
    out = await gm.reply({"schema": "mesa.v1", "verb": "help"})
    assert out is not None
    assert captured["headers"]["Authorization"] == f"Bearer {secret}"
    assert HEADER_SIGNATURE not in captured["headers"]
    assert captured["urls"][0].startswith("https://api2.cursor.sh/automations/webhook/")
    assert captured["json"]["verb"] == "help"
