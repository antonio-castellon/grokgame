"""Compose the 48-card Spanish deck from suit emblems + court figures."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "_src"
OUT = ROOT

W, H = 512, 768
RANKS = (1, 2, 3, 4, 5, 6, 7, 10, 11, 12)
SUITS = ("oros", "copas", "espadas", "bastos")
RANK_NAME = {1: "AS", 10: "SOTA", 11: "CABALLO", 12: "REY"}
SUIT_NAME = {
    "oros": "ORO",
    "copas": "COPA",
    "espadas": "ESPADA",
    "bastos": "BASTOS",
}
FACE_FILE = {10: "sota.jpg", 11: "caballo.jpg", 12: "rey.jpg"}

# pip (x, y) in 0-1 of the inner panel
PIPS = {
    1: [(0.50, 0.50)],
    2: [(0.50, 0.28), (0.50, 0.72)],
    3: [(0.50, 0.26), (0.50, 0.50), (0.50, 0.74)],
    4: [(0.32, 0.30), (0.68, 0.30), (0.32, 0.70), (0.68, 0.70)],
    5: [(0.32, 0.28), (0.68, 0.28), (0.50, 0.50), (0.32, 0.72), (0.68, 0.72)],
    6: [
        (0.32, 0.26),
        (0.68, 0.26),
        (0.32, 0.50),
        (0.68, 0.50),
        (0.32, 0.74),
        (0.68, 0.74),
    ],
    7: [
        (0.32, 0.24),
        (0.50, 0.24),
        (0.68, 0.24),
        (0.32, 0.50),
        (0.68, 0.50),
        (0.32, 0.76),
        (0.68, 0.76),
    ],
}


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("georgia.ttf", "times.ttf", "arial.ttf", "calibri.ttf"):
        path = Path(r"C:\Windows\Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _knock_cream(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    pix = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            if r > 210 and g > 195 and b > 165 and abs(r - g) < 45:
                pix[x, y] = (r, g, b, 0)
    bbox = im.getbbox()
    return im.crop(bbox) if bbox else im


def _fit(im: Image.Image, box: int) -> Image.Image:
    im = im.copy()
    im.thumbnail((box, box), Image.Resampling.LANCZOS)
    return im


def _fit_h(im: Image.Image, max_h: int, max_w: int) -> Image.Image:
    im = im.copy()
    im.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    return im


def _paste_center(base: Image.Image, spr: Image.Image, cx: int, cy: int) -> None:
    x = int(cx - spr.width / 2)
    y = int(cy - spr.height / 2)
    base.alpha_composite(spr, (x, y))


def build() -> None:
    blank = Image.open(SRC / "blank.jpg").convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
    suits = {s: _knock_cream(Image.open(SRC / f"{s}.jpg")) for s in SUITS}
    faces = {
        r: _knock_cream(Image.open(SRC / FACE_FILE[r])) for r in (10, 11, 12)
    }
    font_big = _font(52)
    font_small = _font(28)
    inner = (70, 90, W - 70, H - 90)

    OUT.mkdir(parents=True, exist_ok=True)
    for suit in SUITS:
        emblem = suits[suit]
        for rank in RANKS:
            card = blank.copy()
            draw = ImageDraw.Draw(card)
            label = RANK_NAME.get(rank, str(rank))
            sname = SUIT_NAME[suit]
            draw.text((inner[0], 42), label, fill=(40, 20, 10), font=font_big)
            tw = draw.textlength(sname, font=font_small)
            draw.text(((W - tw) / 2, H - 72), sname, fill=(80, 40, 20), font=font_small)

            ix0, iy0, ix1, iy1 = inner
            iw, ih = ix1 - ix0, iy1 - iy0
            if rank in faces:
                fig = _fit_h(faces[rank], int(ih * 0.72), int(iw * 0.85))
                _paste_center(card, fig, W // 2, H // 2 + 10)
                pip = _fit(emblem, 72)
                _paste_center(card, pip, inner[0] + 36, inner[3] - 40)
            elif rank == 1:
                pip = _fit(emblem, 280)
                _paste_center(card, pip, W // 2, H // 2)
            else:
                size = 110 if rank <= 3 else 88
                pip = _fit(emblem, size)
                for fx, fy in PIPS[rank]:
                    _paste_center(
                        card,
                        pip,
                        int(ix0 + fx * iw),
                        int(iy0 + fy * ih),
                    )
            path = OUT / f"{suit}_{rank}.jpg"
            card.convert("RGB").save(path, quality=88, optimize=True)
            print(path.name)


if __name__ == "__main__":
    build()
