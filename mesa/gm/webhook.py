from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid
from typing import Any

import httpx

from mesa.gm.base import SCHEMA_REPLY
from mesa.gm.xai import XaiGM

HEADER_ID = "webhook-id"
HEADER_TIMESTAMP = "webhook-timestamp"
HEADER_SIGNATURE = "webhook-signature"

_UUID_RE = __import__("re").compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    __import__("re").I,
)


def wake_auth_mode(secret: str) -> str:
    """Return ``bearer`` for Cursor ``crsr_`` keys; else ``standard`` (whsec_)."""
    return "bearer" if (secret or "").strip().startswith("crsr_") else "standard"


def normalize_webhook_urls(url: str) -> list[str]:
    """Prefer api2.cursor.sh automations webhook when a UUID appears in the URL."""
    url = (url or "").strip().rstrip("/")
    if not url:
        return []
    out: list[str] = []
    m = _UUID_RE.search(url)
    if m:
        out.append(f"https://api2.cursor.sh/automations/webhook/{m.group(0)}")
    if url not in out:
        out.append(url)
    seen: set[str] = set()
    uniq: list[str] = []
    for u in out:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq



def secret_key(secret: str) -> bytes:
    """Standard Webhooks key: `whsec_` + base64, or raw utf-8 fallback."""
    raw = (secret or "").strip()
    if raw.startswith("whsec_"):
        raw = raw[len("whsec_") :]
        return base64.b64decode(raw)
    try:
        decoded = base64.b64decode(raw, validate=True)
        if decoded:
            return decoded
    except Exception:
        pass
    return raw.encode("utf-8")


def sign(secret: str, msg_id: str, timestamp: str | int, payload: bytes) -> str:
    """HMAC-SHA256 of `{id}.{timestamp}.{body}`, base64, without the `v1,` prefix."""
    key = secret_key(secret)
    signed = f"{msg_id}.{timestamp}.".encode("utf-8") + payload
    digest = hmac.new(key, signed, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("ascii")


def signature_header(secret: str, msg_id: str, timestamp: str | int, payload: bytes) -> str:
    return f"v1,{sign(secret, msg_id, timestamp, payload)}"


def verify(
    secret: str,
    msg_id: str,
    timestamp: str | int,
    payload: bytes,
    header: str,
) -> bool:
    expected = sign(secret, msg_id, timestamp, payload)
    for part in (header or "").split():
        version, _, candidate = part.partition(",")
        if version != "v1" or not candidate:
            continue
        if hmac.compare_digest(expected, candidate):
            return True
    return False


class WebhookGM:
    def __init__(
        self,
        url: str,
        secret: str,
        reply_mode: str = "http",
        xai_api_key: str = "",
        xai_model: str = "grok-4.6",
    ) -> None:
        self.url = url
        self.secret = secret
        self.reply_mode = reply_mode
        self._xai = XaiGM(xai_api_key, xai_model) if xai_api_key else None

    async def reply(self, request: dict[str, Any]) -> dict[str, Any] | None:
        if not self.url:
            raise RuntimeError("WEBHOOK_URL is empty")
        if wake_auth_mode(self.secret) == "bearer":
            parsed = await self._post_bearer(request)
        else:
            parsed = await self._post_standard(request)
        if parsed is not None:
            return parsed
        # Automations return 202 with an empty body. Grok still has to speak
        # in the group, so fall through to the synchronous API when keyed.
        if self._xai is not None:
            return await self._xai.reply(request)
        return None

    async def _post_standard(self, request: dict[str, Any]) -> dict[str, Any] | None:
        body = json.dumps(request, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
        msg_id = f"msg_{uuid.uuid4().hex}"
        timestamp = str(int(time.time()))
        headers = {
            "Content-Type": "application/json",
            HEADER_ID: msg_id,
            HEADER_TIMESTAMP: timestamp,
            HEADER_SIGNATURE: signature_header(self.secret, msg_id, timestamp, body),
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.url, content=body, headers=headers)
            response.raise_for_status()
            raw = response.content
        return self._parse_http_body(request, raw)

    async def _post_bearer(self, request: dict[str, Any]) -> dict[str, Any] | None:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.secret.strip()}",
        }
        last_exc: Exception | None = None
        async with httpx.AsyncClient(timeout=30.0) as client:
            for candidate in normalize_webhook_urls(self.url):
                try:
                    response = await client.post(
                        candidate, headers=headers, json=request
                    )
                    response.raise_for_status()
                    return self._parse_http_body(request, response.content)
                except Exception as exc:
                    last_exc = exc
                    continue
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("WEBHOOK_URL is empty")

    def _parse_http_body(
        self, request: dict[str, Any], raw: bytes
    ) -> dict[str, Any] | None:
        if not raw:
            return None
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            text = raw.decode("utf-8", errors="replace").strip()
            return {**_text_reply(request, text)}
        if isinstance(data, dict):
            if data.get("schema") == SCHEMA_REPLY or "say" in data:
                data.setdefault("schema", SCHEMA_REPLY)
                return data
            text = json.dumps(data, ensure_ascii=False)
            return _text_reply(request, text)
        return _text_reply(request, str(data))


def _text_reply(request: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA_REPLY,
        "say": text,
        "lang": request.get("lang") or "en",
        "dice_request": None,
    }
