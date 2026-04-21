"""Generate assets/icon.icns (macOS) and assets/icon.ico (Windows)."""
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Rounded square — deep indigo background
    pad = int(size * 0.01)
    d.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=int(size * 0.20),
        fill=(55, 48, 163),  # indigo-800
    )

    # Soft inner glow (top-centre highlight)
    gx, gy, gr = size * 0.5, size * 0.22, size * 0.52
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(99, 102, 241, 55))

    # Arrow dimensions (scale with icon size)
    lw   = max(4, size // 20)    # shaft thickness
    hw   = int(lw * 2.6)         # arrowhead width (along shaft axis)
    hh   = int(lw * 1.8)         # arrowhead half-height
    mx   = int(size * 0.19)      # left/right margin
    r2   = lw // 2               # cap radius

    def _right_arrow(y: int, color: tuple) -> None:
        x0, x1 = mx, size - mx
        shaft_end = x1 - hw + lw // 2
        d.rectangle([x0, y - r2, shaft_end, y + r2], fill=color)
        d.ellipse([x0 - r2, y - r2, x0 + r2, y + r2], fill=color)
        d.polygon([(x1, y), (x1 - hw, y - hh), (x1 - hw, y + hh)], fill=color)

    def _left_arrow(y: int, color: tuple) -> None:
        x0, x1 = size - mx, mx  # x0=right end, x1=tip on left
        shaft_start = x1 + hw - lw // 2
        d.rectangle([shaft_start, y - r2, x0, y + r2], fill=color)
        d.ellipse([x0 - r2, y - r2, x0 + r2, y + r2], fill=color)
        d.polygon([(x1, y), (x1 + hw, y - hh), (x1 + hw, y + hh)], fill=color)

    cy = size // 2
    offset = int(size * 0.145)
    _right_arrow(cy - offset, (255, 255, 255, 245))
    _left_arrow (cy + offset, (165, 180, 252, 210))  # indigo-300

    return img


def make_icns(img: Image.Image, out: Path) -> None:
    iconset = Path("_build_iconset.iconset")
    iconset.mkdir(exist_ok=True)
    for name, sz in [
        ("icon_16x16.png",      16),
        ("icon_16x16@2x.png",   32),
        ("icon_32x32.png",      32),
        ("icon_32x32@2x.png",   64),
        ("icon_128x128.png",   128),
        ("icon_128x128@2x.png",256),
        ("icon_256x256.png",   256),
        ("icon_256x256@2x.png",512),
        ("icon_512x512.png",   512),
        ("icon_512x512@2x.png",1024),
    ]:
        img.resize((sz, sz), Image.LANCZOS).save(iconset / name, "PNG")
    subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(out)], check=True)
    shutil.rmtree(iconset)


def make_ico(img: Image.Image, out: Path) -> None:
    sizes = [16, 32, 48, 64, 128, 256]
    frames = [img.resize((s, s), Image.LANCZOS).convert("RGBA") for s in sizes]
    frames[0].save(out, format="ICO", sizes=[(s, s) for s in sizes], append_images=frames[1:])


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
