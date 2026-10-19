"""Compact phone-width ASCII cards for Telegram.

Keep WIDTH at 28 so a <pre> block fits a mobile bubble without wrapping
the box itself. Content wraps inside the card.
"""

from __future__ import annotations

WIDTH = 28
INNER = WIDTH - 4  # "│ " + text + " │"
DIV = "---"


def _hline(left: str, mid: str, right: str, title: str = "") -> str:
    if not title:
        return left + mid * (WIDTH - 2) + right
    label = f" {title.strip()} "
    if len(label) > WIDTH - 2:
        label = " " + title.strip()[: WIDTH - 5] + "… "
    fill = WIDTH - 2 - len(label)
    return left + label + mid * fill + right


def _row(text: str) -> str:
    return "│ " + text.ljust(INNER) + " │"


def _wrap(text: str) -> list[str]:
    raw = text or ""
    # ASCII art: keep spaces and never reflow (Telegram <pre> needs this).
    # Slash alone is not art — "/cmd …" must wrap. Keep "\\" and box chars.
    if any(ch in raw for ch in "+-|┌┐└┘│─\\") or "  " in raw:
        if not raw.strip():
            return [_row("")]
        if len(raw) <= INNER:
            return [_row(raw)]
        return [_row(raw[:INNER])]
    raw = " ".join(raw.split())
    if not raw:
        return [_row("")]
    lines: list[str] = []
    while raw:
        if len(raw) <= INNER:
            lines.append(_row(raw))
            break
        cut = raw.rfind(" ", 0, INNER + 1)
        if cut <= 0:
            cut = INNER
        lines.append(_row(raw[:cut].rstrip()))
        raw = raw[cut:].lstrip()
    return lines


def card(title: str, lines: list[str] | None = None) -> str:
    """Small framed block. Pass DIV in `lines` for a separator."""
    out = [_hline("┌", "─", "┐", title)]
    for item in lines or []:
        if item == DIV:
            out.append(_hline("├", "─", "┤"))
        else:
            out.extend(_wrap(item))
    out.append(_hline("└", "─", "┘"))
    return "\n".join(out)


def bullets(items: list[str], empty: str) -> list[str]:
    if not items:
        return [f"· {empty}"]
    return [f"· {item}" for item in items]


def as_html_pre(text: str) -> str:
    escaped = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"<pre>{escaped}</pre>"
