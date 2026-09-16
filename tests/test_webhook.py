import base64
import json

from mesa.gm.webhook import (
    HEADER_ID,
    HEADER_SIGNATURE,
    HEADER_TIMESTAMP,
    sign,
    signature_header,
    verify,
)


SECRET = "whsec_" + base64.b64encode(b"0123456789abcdef01234567").decode("ascii")


def test_sign_roundtrip():
    payload = b'{"schema":"mesa.v1"}'
    msg_id = "msg_test_1"
    ts = "1674087231"
    header = signature_header(SECRET, msg_id, ts, payload)
    assert header.startswith("v1,")
    assert verify(SECRET, msg_id, ts, payload, header)


def test_tampered_body_fails():
    payload = b'{"schema":"mesa.v1"}'
    header = signature_header(SECRET, "msg_1", "1", payload)
    assert not verify(SECRET, "msg_1", "1", b'{"schema":"nope"}', header)


def test_wrong_id_fails():
    payload = b"{}"
    header = signature_header(SECRET, "msg_a", "1", payload)
    assert not verify(SECRET, "msg_b", "1", payload, header)


def test_sign_matches_manual_hmac_shape():
    payload = json.dumps({"hello": "mesa"}, separators=(",", ":")).encode()
    sig = sign(SECRET, "msg_2", 42, payload)
    # base64 of 32-byte sha256
    raw = base64.b64decode(sig)
    assert len(raw) == 32


def test_header_names():
    assert HEADER_ID == "webhook-id"
    assert HEADER_TIMESTAMP == "webhook-timestamp"
    assert HEADER_SIGNATURE == "webhook-signature"
