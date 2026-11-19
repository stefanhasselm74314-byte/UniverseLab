#!/usr/bin/env python3
"""Generate original 2.5D depth plates for the UniverseLab Holo-6D face.

The geometry is deterministic and does not purport to be a physical hologram.
Each transparent PNG acts as a separate Watch Face Format Gyro layer.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DRAWABLE = ROOT / "holoface/src/main/res/drawable"
PREVIEW_DIR = ROOT / "assets"
BASE_DRAWABLE = ROOT / "watchface/src/main/res/drawable"
SIZE = 450
SCALE = 2
CENTER = (225, 248)


def px(x: float, y: float) -> tuple[int, int]:
    return (round(x * SCALE), round(y * SCALE))


def bbox(cx: float, cy: float, rx: float, ry: float) -> tuple[int, ...]:
    return (round((cx-rx)*SCALE), round((cy-ry)*SCALE),
            round((cx+rx)*SCALE), round((cy+ry)*SCALE))


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (SIZE*SCALE, SIZE*SCALE), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def scaled(image: Image.Image) -> Image.Image:
    return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def make_void() -> Image.Image:
    image, d = canvas()
    cx, cy = CENTER
    d.ellipse(bbox(cx, cy, 128, 128), fill=(3, 7, 26, 176))
    for r in (123, 116, 103, 88, 68):
        d.ellipse(bbox(cx, cy, r, r), outline=(34, 91, 155, 130), width=SCALE)
    # A layered elliptical chamber gives the mechanism a perceived floor.
    for i, ry in enumerate((54, 43, 29, 17)):
        d.ellipse(bbox(cx, cy+39+i*2, 125-i*15, ry),
                  outline=(74, 203, 255, 65+i*19), width=2*SCALE)
    shadow = image.filter(ImageFilter.GaussianBlur(3*SCALE))
    shadow.alpha_composite(image)
    return scaled(shadow)


def make_back() -> Image.Image:
    image, d = canvas()
    cx, cy = CENTER
    # Rear reference plane: stars, fine arcs and glowing virtual bearings.
    rng = random.Random(20261119)
    for _ in range(110):
        x = rng.randrange(88, 362)
        y = rng.randrange(120, 382)
        if (x-cx)**2 + (y-cy)**2 > 116**2:
            continue
        brightness = rng.randrange(80, 185)
        r = rng.choice((0.5, 0.7, 1.1))
        d.ellipse(bbox(x, y, r, r), fill=(138, 195, 255, brightness))
    for r, col, width in [(112, (110, 194, 255, 105), 2),
                          (96, (79, 119, 244, 95), 1),
                          (75, (93, 230, 254, 90), 1)]:
        d.arc(bbox(cx, cy, r, r), 5, 168, fill=col, width=width*SCALE)
        d.arc(bbox(cx, cy, r, r), 185, 352, fill=col, width=width*SCALE)
    d.ellipse(bbox(cx, cy, 109, 42), outline=(81, 215, 255, 180), width=2*SCALE)
    d.ellipse(bbox(cx, cy, 86, 98), outline=(112, 143, 255, 95), width=SCALE)
    for deg in range(0, 360, 30):
        a = math.radians(deg)
        x = cx + 110*math.cos(a)
        y = cy + 42*math.sin(a)
        d.ellipse(bbox(x, y, 2.5, 2.5), fill=(117, 226, 255, 180))
    glow = image.filter(ImageFilter.GaussianBlur(3.5*SCALE))
    glow.alpha_composite(image)
    return scaled(glow)


def make_front() -> Image.Image:
    image, d = canvas()
    cx, cy = CENTER
    # Holographic scan arcs in front of the metal gyro. Transparency is crucial.
    for r, a0, a1, alpha in [(124, 17, 105, 145),
                            (124, 199, 310, 176),
                            (114, 48, 140, 102),
                            (105, 204, 316, 82)]:
        d.arc(bbox(cx, cy, r, r), a0, a1,
              fill=(99, 219, 255, alpha), width=2*SCALE)
    d.arc(bbox(cx, cy+23, 117, 46), 12, 166,
          fill=(118, 217, 255, 158), width=2*SCALE)
    d.line((px(cx-16, cy), px(cx-6, cy)), fill=(116, 230, 255, 115), width=SCALE)
    d.line((px(cx+6, cy), px(cx+16, cy)), fill=(116, 230, 255, 115), width=SCALE)
    d.line((px(cx, cy-16), px(cx, cy-6)), fill=(116, 230, 255, 115), width=SCALE)
    d.line((px(cx, cy+6), px(cx, cy+16)), fill=(116, 230, 255, 115), width=SCALE)
    for x, y in ((119, 200), (321, 288), (155, 345), (297, 167)):
        d.line((px(x-7,y),px(x+7,y)), fill=(148, 234, 255, 164), width=SCALE)
        d.line((px(x,y-7),px(x,y+7)), fill=(148, 234, 255, 164), width=SCALE)
    glow = image.filter(ImageFilter.GaussianBlur(2*SCALE))
    glow.alpha_composite(image)
    return scaled(glow)


def font(size: int):
    return ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def preview(layers: dict[str, Image.Image]) -> Image.Image:
    scene = Image.open(BASE_DRAWABLE / "watch_bg.png").convert("RGBA")
    scene.alpha_composite(layers["holo_void"])
    scene.alpha_composite(layers["holo_back"])
    with Image.open(BASE_DRAWABLE / "gyro_still.png") as image:
        scene.alpha_composite(image.convert("RGBA"), (75, 111))
    scene.alpha_composite(layers["holo_front"])
    d = ImageDraw.Draw(scene)
    def label(x: int, y: int, value: str, size: int, color=(223, 244, 255)):
        d.text((x,y), value, font=font(size), fill=color, anchor="mm")
    label(225, 94, "20:59", 43)
    label(82, 138, "76%", 20)
    label(368, 138, "12846", 15)
    label(82, 317, "72", 20)
    label(368, 317, "19.11", 16)
    return scene


def run():
    DRAWABLE.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    layers = {"holo_void": make_void(),
              "holo_back": make_back(),
              "holo_front": make_front()}
    for name, layer in layers.items():
        layer.save(DRAWABLE / f"{name}.png", optimize=True)
    for name in ("gyro_still.png", "gyro_anim.webp", "watch_bg.png"):
        (DRAWABLE / name).write_bytes((BASE_DRAWABLE / name).read_bytes())
    p = preview(layers)
    p.save(DRAWABLE / "preview.png", optimize=True)
    p.resize((900, 900), Image.Resampling.LANCZOS).save(
        PREVIEW_DIR / "holo6d-preview.png", optimize=True)
    print("Generated Holo-6D rear/mid/front depth layers and preview")


if __name__ == "__main__":
    run()
