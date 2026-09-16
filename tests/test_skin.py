from mesa.skin import WIDTH, card


def test_card_fits_phone_width():
    text = card("mesa", ["hello world", "a slightly longer line of text here"])
    for line in text.splitlines():
        assert len(line) == WIDTH, line
    assert "hello world" in text
    assert text.startswith("┌")
    assert text.endswith("┘")
