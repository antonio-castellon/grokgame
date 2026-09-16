import random

from mesa.dice import parse_expr, roll


def test_parse_1d20_plus_2():
    assert parse_expr("1d20+2") == (1, 20, 2)


def test_parse_bare_d6():
    assert parse_expr("d6") == (1, 6, 0)


def test_roll_seeded():
    rng = random.Random(0)
    result = roll("1d20+2", rng=rng)
    assert result["expr"] == "1d20+2"
    assert 3 <= result["total"] <= 22
    assert "1d20+2" in result["detail"]
    assert "=" in result["detail"]
