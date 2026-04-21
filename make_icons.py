"""Generate assets/icon.icns (macOS) and assets/icon.ico (Windows)."""
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw


# ── drawing helpers ───────────────────────────────────────────────────────────

def _arrow_right(d: ImageDraw.ImageDraw, x0: int, x1: int, y: int,
                 half_h: int, color: tuple) -> None:
    """Rightward pill-arrow from x0 to x1."""
    head_h = int(half_h * 2.0)   # arrowhead half-height
    head_w = int(half_h * 2.4)   # arrowhead depth along axis
    shaft_x1 = x1 - head_w
    r = half_h

    # shaft
    d.rectangle([x0, y - half_h, shaft_x1, y + half_h], fill=color)
    # left rounded cap
    d.ellipse([x0 - r, y - r, x0 + r, y + r], fill=color)
    # shaft/head junction (fills the gap)
    d.ellipse([shaft_x1 - r, y - r, shaft_x1 + r, y + r], fill=color)
    # arrowhead
    d.polygon([(x1, y), (shaft_x1, y - head_h), (shaft_x1, y + head_h)], fill=color)


def _arrow_left(d: ImageDraw.ImageDraw, x0: int, x1: int, y: int,
                half_h: int, color: tuple) -> None:
    """Leftward pill-arrow from x0 to x1 (x1 < x0)."""
    head_h = int(half_h * 2.0)
    head_w = int(half_h * 2.4)
    shaft_x0 = x1 + head_w
    r = half_h

    # shaft
    d.rectangle([shaft_x0, y - half_h, x0, y + half_h], fill=color)
    # right rounded cap
    d.ellipse([x0 - r, y - r, x0 + r, y + r], fill=color)
    # shaft/head junction
    d.ellipse([shaft_x0 - r, y - r, shaft_x0 + r, y + r], fill=color)
    # arrowhead
    d.polygon([(x1, y), (shaft_x0, y - head_h), (shaft_x0, y + head_h)], fill=color)


# ── icon composer ─────────────────────────────────────────────────────────────

def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # ── background: dark slate with rounded corners ──
    d.rounded_rectangle(
        [0, 0, size - 1, size - 1],
        radius=int(size * 0.21),
        fill=(10, 15, 30),         # near-black navy
    )

    # ── subtle radial glow bands ──
    cx, cy = size / 2, size / 2
    for alpha, r_frac in [(35, 0.60), (22, 0.44), (12, 0.30)]:
        gr = size * r_frac
        d.ellipse([cx - gr, cy - gr, cx + gr, cy + gr],
                  fill=(80, 90, 220, alpha))

    # ── arrow geometry ──
    pad   = int(size * 0.13)          # outer horizontal margin
    half  = max(5, size // 14)        # half-height of primary arrow shaft
    half2 = max(4, int(half * 0.72))  # half-height of secondary arrow shaft

    y1 = int(size * 0.375)            # primary arrow y-position
    y2 = int(size * 0.640)            # secondary arrow y-position

    # ── primary arrow: → (white) ──
    _arrow_right(d, pad, size - pad, y1, half, (255, 255, 255, 252))

    # ── connector: small vertical hint linking the two arrows ──
    gap_x_right = size - pad - int(half * 2.4)  # near tip of right arrow
    gap_x_left  = pad + int(half2 * 2.4)        # near tip of left arrow
    line_w = max(2, size // 60)
    d.line([(size - pad, y1), (size - pad, y2)], fill=(120, 130, 200, 80), width=line_w)
    d.line([(pad, y1), (pad, y2)],               fill=(120, 130, 200, 80), width=line_w)

    # ── secondary arrow: ← (indigo-400) ──
    pad2 = int(size * 0.13)
    _arrow_left(d, size - pad2, pad2, y2, half2, (130, 140, 255, 230))

    return img


# ── export helpers ────────────────────────────────────────────────────────────

def make_icns(img: Image.Image, out: Path) -> None:
    iconset = Path("_build_iconset.iconset")
    iconset.mkdir(exist_ok=True)
    for name, sz in [
        ("icon_16x16.png",       16),
        ("icon_16x16@2x.png",    32),
        ("icon_32x32.png",       32),
        ("icon_32x32@2x.png",    64),
        ("icon_128x128.png",    128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png",    256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png",    512),
        ("icon_512x512@2x.png",1024),
    ]:
        img.resize((sz, sz), Image.LANCZOS).save(iconset / name, "PNG")
    subprocess.run(
        ["iconutil", "-c", "icns", str(iconset), "-o", str(out)], check=True
    )
    shutil.rmtree(iconset)


def make_ico(img: Image.Image, out: Path) -> None:
    sizes = [16, 32, 48, 64, 128, 256]
    frames = [img.resize((s, s), Image.LANCZOS).convert("RGBA") for s in sizes]
    frames[0].save(
        out, format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=frames[1:],
    )


if __name__ == "__main__":
    assets = Path("assets")
    assets.mkdir(exist_ok=True)

    base = draw_icon(1024)
    base.save(assets / "icon.png", "PNG")
    print("Generated assets/icon.png")

    make_icns(base, assets / "icon.icns")
    print("Generated assets/icon.icns")

    make_ico(base, assets / "icon.ico")
    print("Generated assets/icon.ico")
