from __future__ import annotations

import random
import re
from typing import Any

_EXPR_RE = re.compile(
    r"^\s*(\d*)d(\d+)\s*([+-]\s*\d+)?\s*$",
    re.IGNORECASE,
)


def parse_expr(expr: str) -> tuple[int, int, int]:
    match = _EXPR_RE.match(expr or "")
    if not match:
        raise ValueError(f"invalid dice expr: {expr!r}")
    count = int(match.group(1) or 1)
    sides = int(match.group(2))
    mod_raw = match.group(3)
    modifier = int(mod_raw.replace(" ", "")) if mod_raw else 0
    if count < 1 or count > 100 or sides < 2 or sides > 1000:
        raise ValueError(f"dice out of range: {expr!r}")
    return count, sides, modifier


def roll(expr: str, rng: random.Random | None = None) -> dict[str, Any]:
    """Roll `NdM+K`. Returns {expr, total, detail} for the GM."""
    rng = rng or random.SystemRandom()
    count, sides, modifier = parse_expr(expr)
    parts = [rng.randint(1, sides) for _ in range(count)]
    total = sum(parts) + modifier
    shown = f"{count}d{sides}"
    if modifier:
        shown += f"{modifier:+d}"
    inner = ",".join(str(p) for p in parts)
    detail = f"{shown}: [{inner}]"
    if modifier:
        detail += f"{modifier:+d}"
    detail += f"={total}"
    return {"expr": expr, "total": total, "detail": detail}
