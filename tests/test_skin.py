from mesa.skin import WIDTH, card


def test_card_fits_phone_width():
    text = card("mesa", ["hello world", "a slightly longer line of text here"])
    for line in text.splitlines():
        assert len(line) == WIDTH, line
    assert "hello world" in text
    assert text.startswith("┌")
    assert text.endswith("┘")


def test_card_wraps_slash_cmd_lines():
    """A lone '/' (as in /cmd) must not freeze wrapping as ASCII art."""
    text = card(
        "clear",
        ["Deletes EVERY message from anyone. Confirm: /cmd clear all"],
    )
    joined = " ".join(
        line[1:-1].strip()
        for line in text.splitlines()
        if line.startswith("│") and line.endswith("│")
    )
    assert "/cmd clear all" in joined
    for line in text.splitlines():
        assert len(line) == WIDTH, line
