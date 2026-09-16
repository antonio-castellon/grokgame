from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MESA = ROOT / "mesa"


def test_no_characters_module():
    assert not (MESA / "characters.py").exists()
    assert not (ROOT / "characters.py").exists()


def test_no_llm_sdks_or_xai():
    hits = []
    for path in MESA.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for needle in ("api.x.ai", "openai", "from xai", "import xai", "/elegir"):
            if needle in text:
                if needle == "api.x.ai" and path.name == "xai.py":
                    continue
                hits.append(f"{path}: {needle}")
        lowered = text.lower()
        if "warrior" in lowered and "mage" in lowered:
            hits.append(f"{path}: warrior/mage")
    assert hits == []
