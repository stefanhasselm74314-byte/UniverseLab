#!/usr/bin/env python3
"""Generate original 2.5D depth plates for the UniverseLab Holo-6D face.

The geometry is deterministic and does not purport to be a physical hologram.
Each transparent PNG acts as a separate Watch Face Format Gyro layer.
"""

from __future__ import annotations

import colorsys
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



def draw_skeleton_gear(draw, x: float, y: float, radius: float,
                       teeth: int, phase: float = 0.0) -> None:
    """Anti-aliased original skeleton gear for the rear parallax plane."""
    tooth_pitch = 2 * math.pi / teeth
    for k in range(teeth):
        angle = phase + k * tooth_pitch
        a0, a1 = angle - tooth_pitch * 0.31, angle + tooth_pitch * 0.31
        outer = radius * 1.13
        pts = [px(x + rr * math.cos(a), y + rr * math.sin(a))
               for rr, a in ((radius * .91, a0), (outer, a0),
                             (outer, a1), (radius * .91, a1))]
        draw.polygon(pts, fill=(86, 96, 107, 236))
    draw.ellipse(bbox(x, y, radius, radius), fill=(34, 40, 49, 238),
                 outline=(171, 181, 191, 238), width=2*SCALE)
    draw.ellipse(bbox(x, y, radius*.74, radius*.74),
                 fill=(7, 11, 18, 216),
                 outline=(99, 111, 128, 216), width=2*SCALE)
    for spoke in range(5):
        a = phase + spoke * 2*math.pi / 5
        p0 = px(x + radius*.14*math.cos(a),
                y + radius*.14*math.sin(a))
        p1 = px(x + radius*.76*math.cos(a),
                y + radius*.76*math.sin(a))
        draw.line([p0, p1], fill=(174, 182, 191, 227),
                  width=5*SCALE)
    draw.ellipse(bbox(x, y, 5.8, 5.8), fill=(13, 17, 24, 245),
                 outline=(214, 220, 225, 240), width=2*SCALE)
    draw.ellipse(bbox(x, y, 2.4, 2.4), fill=(160, 26, 62, 250))


def draw_skeleton_bridges(draw) -> None:
    """Brushed-metal skeleton bridges joining visible virtual bearings."""
    for points in [
        [(130, 188), (153, 244), (127, 307)],
        [(320, 188), (296, 244), (322, 307)],
        [(180, 149), (225, 175), (270, 149)],
        [(178, 348), (225, 320), (272, 348)],
    ]:
        coords = [px(x, y) for x, y in points]
        draw.line(coords, fill=(14, 18, 27, 240),
                  width=11*SCALE, joint="curve")
        draw.line(coords, fill=(157, 168, 179, 236),
                  width=6*SCALE, joint="curve")
        for x, y in (points[0], points[-1]):
            draw.ellipse(bbox(x, y, 3.8, 3.8),
                         fill=(46, 56, 70, 254),
                         outline=(219, 224, 231, 255),
                         width=SCALE)


def make_void() -> Image.Image:
    image, d = canvas()
    cx, cy = CENTER
    d.ellipse(bbox(cx, cy, 128, 128), fill=(6, 10, 16, 194))
    for r in (123, 116, 103, 88, 68):
        d.ellipse(bbox(cx, cy, r, r), outline=(100, 112, 126, 132), width=SCALE)
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
    # Original gunmetal skeleton escapement under the moving axial gimbal.
    for gx, gy, radius, count, phase in [
        (160, 205, 30, 18, .09), (289, 205, 28, 17, .14),
        (162, 306, 33, 21, .02), (289, 307, 32, 19, .18),
        (225, 248, 40, 25, .08), (225, 174, 18, 13, .05),
        (226, 340, 20, 14, .19)
    ]:
        draw_skeleton_gear(d, gx, gy, radius, count, phase)
    draw_skeleton_bridges(d)
    glow = image.filter(ImageFilter.GaussianBlur(3.5*SCALE))
    glow.alpha_composite(image)
    return scaled(glow)


def make_front() -> Image.Image:
    image, d = canvas()
    cx, cy = CENTER
    # Ultra-thin complete spectrum rim, on the moving foreground plate.
    # The RGB hues are a visual accent, not a measured physical spectrum.
    for deg in range(360):
        red, green, blue = colorsys.hsv_to_rgb(
            ((deg + 215) % 360) / 360, .82, .99)
        d.arc(bbox(225, 225, 190, 190), deg, deg+1,
              fill=(round(red*255), round(green*255),
                    round(blue*255), 191),
              width=2*SCALE)
    # Fine brushed metallic arcs preserve the gimbal's depth separation.
    for r, a0, a1, alpha in [(124, 17, 105, 145),
                            (124, 199, 310, 176),
                            (114, 48, 140, 102),
                            (105, 204, 316, 82)]:
        d.arc(bbox(cx, cy, r, r), a0, a1,
              fill=(167, 188, 210, alpha), width=2*SCALE)
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
    print("Generated Holo-6D v0.4 Titan-Spectrum depth layers and preview")


if __name__ == "__main__":
    run()
