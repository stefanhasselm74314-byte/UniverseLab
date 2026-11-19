#!/usr/bin/env python3
"""Reproducible, original graphics for UniverseLab 6D Gyroscope.

Only Python/Pillow is needed. All compass positions are calculated, not drawn
by a generative model. Artwork uses a 450x450 Wear OS reference coordinate grid.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "watchface/src/main/res/drawable"
ASSETS = ROOT / "assets"
S = 2
C = 225
BLUE = (110, 207, 255)
LIGHT = (225, 240, 251)
RED = (255, 85, 92)


def font(size: float, bold: bool = False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    paths = [
        f"/usr/share/fonts/truetype/dejavu/{name}",
        f"/usr/share/fonts/truetype/liberation2/{name}",
    ]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, round(size * S))
    return ImageFont.load_default()


def pt(cx: float, cy: float, r: float, angle_degrees: float):
    """Compass geometry: 0° north/up, 90° east/right."""
    a = math.radians(angle_degrees)
    return (cx + r * math.sin(a), cy - r * math.cos(a))


def p2(xy):
    return tuple(round(v * S) for v in xy)


def ellipse(draw: ImageDraw.ImageDraw, box, **kwargs):
    draw.ellipse(tuple(round(v * S) for v in box), **kwargs)


def text_center(draw: ImageDraw.ImageDraw, xy, value: str, size, fill, bold=False):
    draw.text(p2(xy), value, font=font(size, bold), fill=fill, anchor="mm")


def make_background() -> Image.Image:
    im = Image.new("RGBA", (450 * S, 450 * S), (0, 0, 0, 0))
    px = im.load()
    for y in range(450 * S):
        for x in range(450 * S):
            dx = x / S - C
            dy = y / S - C
            r = math.hypot(dx, dy)
            if r > 224:
                continue
            shimmer = max(0, 1 - r / 224)
            px[x, y] = (int(5 + 4 * shimmer), int(11 + 9 * shimmer),
                        int(20 + 17 * shimmer), 255)
    d = ImageDraw.Draw(im)

    # Brushed titanium edge with accurately spaced compass graduations.
    for radius, color, width in [
        (223, (90, 110, 128), 2),
        (218, (181, 206, 223), 1),
        (204, (39, 79, 104), 1),
        (190, (33, 51, 67), 1),
    ]:
        ellipse(d, (C-radius, C-radius, C+radius, C+radius), outline=color,
                width=width * S)
    for deg in range(360):
        prominent = deg % 30 == 0
        main = deg % 10 == 0
        r0 = 206 if prominent else (211 if main else 216)
        a = p2(pt(C, C, r0, deg))
        b = p2(pt(C, C, 220, deg))
        d.line((a, b), fill=(189, 216, 236, 255) if main else (62, 91, 115, 255),
               width=(2 if prominent else 1) * S)
    directions = [(0, "N"), (45, "NE"), (90, "E"), (135, "SE"),
                  (180, "S"), (225, "SW"), (270, "W"), (315, "NW")]
    for deg, label in directions:
        where = pt(C, C, 193 if len(label) == 1 else 193, deg)
        text_center(d, where, label, 16 if len(label) == 1 else 9,
                    RED if deg == 0 else (190, 229, 250), bold=True)
    for deg in range(0, 360, 30):
        if deg % 90 == 0:
            continue
        text_center(d, pt(C, C, 180, deg), str(deg) + "°", 7, (100, 139, 165))
    # North alignment marker fixed at the top (ring itself is decorative in WFF).
    d.polygon([p2((C, 3)), p2((C-7, 17)), p2((C+7, 17))], fill=RED)
    d.line((p2((C, 27)), p2((C, 36))), fill=RED, width=2*S)

    # Central recessed instrument chamber.
    for r, col, wd in [(141, (21, 43, 57), 8), (136, (139, 163, 178), 3),
                       (130, (23, 51, 69), 2), (123, (10, 20, 32), 3)]:
        ellipse(d, (C-r, 250-r, C+r, 250+r), outline=col, width=wd*S)
    for r in range(46, 123, 19):
        ellipse(d, (C-r, 250-r, C+r, 250+r), outline=(16, 39, 57), width=S)
    for a in range(0, 360, 30):
        d.line((p2(pt(C, 250, 33, a)), p2(pt(C, 250, 122, a))),
               fill=(17, 45, 66), width=S)

    # Four gauges; numerical values remain dynamic WFF data sources.
    gauges = [
        (82, 145, "BAT"), (368, 145, "SCHRITTE"),
        (82, 324, "PULS"), (368, 324, "DATUM"),
    ]
    for x, y, label in gauges:
        ellipse(d, (x-40, y-40, x+40, y+40), fill=(7, 15, 24),
                outline=(104, 136, 155), width=2*S)
        ellipse(d, (x-35, y-35, x+35, y+35), outline=(21, 67, 95), width=2*S)
        d.arc(tuple(round(v*S) for v in (x-36, y-36, x+36, y+36)),
              -85, 0, fill=BLUE, width=4*S)
        text_center(d, (x, y+24), label, 8, (127, 177, 205), bold=True)
    text_center(d, (C, 51), "U N I V E R S E L A B", 9.5, LIGHT)
    text_center(d, (C, 67), "6D  ·  HYPERZEIT", 9, BLUE, bold=True)
    text_center(d, (C, 396), "KOMPASS", 8, (114, 186, 226))
    return im.resize((450, 450), Image.Resampling.LANCZOS)


def rot_x(v, a):
    x, y, z = v
    return (x, y*math.cos(a)-z*math.sin(a), y*math.sin(a)+z*math.cos(a))


def rot_y(v, a):
    x, y, z = v
    return (x*math.cos(a)+z*math.sin(a), y, -x*math.sin(a)+z*math.cos(a))


def rot_z(v, a):
    x, y, z = v
    return (x*math.cos(a)-y*math.sin(a), x*math.sin(a)+y*math.cos(a), z)


def transform(v, ax, ay, az):
    return rot_z(rot_y(rot_x(v, ax), ay), az)


def project(v, size=300):
    x, y, z = v
    scale = 1.0 + z / 500
    return (size / 2 + x * scale, size / 2 + y * scale)


def make_gyro_frame(phase: float, size=300) -> Image.Image:
    """Depth-ordered toroidal segments, 3 independent axis motions."""
    Q = 2
    im = Image.new("RGBA", (size*Q, size*Q), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    center = size / 2
    f = lambda xy: tuple(round(Q*v) for v in xy)
    # Soft structure glow and a dark central movement, transparent surroundings.
    for radius, alpha in [(118, 10), (105, 13), (90, 13)]:
        d.ellipse(f((center-radius, center-radius, center+radius, center+radius)),
                  outline=(67, 175, 230, alpha), width=2*Q)

    segments = []
    rings = [
        # radius, base normal/plane, x-y-z angular motion, thickness
        (111, "xy", (0.92, 0.17, phase*2*math.pi), 7),
        (91, "yz", (phase*2*math.pi, 0.22, 0.46), 6),
        (72, "xz", (0.21, phase*4*math.pi, 0.33), 5),
    ]
    for ring_id, (r, plane, angles, thickness) in enumerate(rings):
        points = []
        for k in range(181):
            a = math.pi * 2 * k / 180
            v = ((r*math.cos(a), r*math.sin(a), 0) if plane == "xy" else
                 (0, r*math.cos(a), r*math.sin(a)) if plane == "yz" else
                 (r*math.cos(a), 0, r*math.sin(a)))
            v = transform(v, *angles)
            points.append(v)
        for k in range(180):
            v0, v1 = points[k], points[k+1]
            z = (v0[2] + v1[2]) / 2
            segments.append((z, ring_id, thickness, project(v0, size), project(v1, size)))
    segments.sort(key=lambda seg: seg[0])
    for z, ring_id, width, a, b in segments:
        bright = max(0, min(1, 0.53 + z / 220))
        metal = tuple(int((74 + n) * bright) for n in (40, 58, 70))
        metal = tuple(min(255, v) for v in metal)
        d.line((f(a), f(b)), fill=(*metal, 255), width=width*Q)
        d.line((f((a[0]-1, a[1]-1)), f((b[0]-1, b[1]-1))),
               fill=(210, 224, 234, 225), width=1*Q)
        if ring_id == 2 and z > 0:
            d.line((f((a[0]+1, a[1]+1)), f((b[0]+1, b[1]+1))),
                   fill=(70, 204, 255, 210), width=1*Q)

    # Teeth on outer gear plane, following the same 3D transform.
    for k in range(72):
        a = 2*math.pi*k/72
        vv = []
        for rr in (113, 119):
            v = transform((rr*math.cos(a), rr*math.sin(a), 0),
                          0.92, 0.17, phase*2*math.pi)
            vv.append(v)
        col = (184, 198, 211, 255) if vv[0][2] > 0 else (77, 95, 111, 220)
        d.line((f(project(vv[0], size)), f(project(vv[1], size))),
               fill=col, width=2*Q)

    # Suspended bridges, bearings, and jeweled pivot points.
    for x0, y0, x1, y1 in [(31, 151, 76, 151), (224, 151, 269, 151),
                           (150, 31, 150, 69), (150, 231, 150, 267)]:
        d.line((f((x0, y0)), f((x1, y1))), fill=(57, 73, 86), width=12*Q)
        d.line((f((x0, y0-1)), f((x1, y1-1))), fill=(197, 213, 222), width=2*Q)
    for x, y in [(30, 151), (270, 151), (150, 28), (150, 270)]:
        d.ellipse(f((x-10,y-10,x+10,y+10)), fill=(49,58,68),
                  outline=(185,201,212), width=2*Q)
        d.ellipse(f((x-4,y-4,x+4,y+4)), fill=(142,28,76),
                  outline=(242,144,183), width=Q)

    # Inner nested gears make the movement recognizably mechanical.
    for ox, oy, r, speed in [(104, 218, 17, 3), (196, 218, 17, -3)]:
        d.ellipse(f((ox-r,oy-r,ox+r,oy+r)), fill=(29,42,55),
                  outline=(194,204,213), width=3*Q)
        for tooth in range(12):
            a = 2*math.pi*(tooth/12 + phase*speed)
            d.line((f((ox+(r-3)*math.cos(a), oy+(r-3)*math.sin(a))),
                    f((ox+(r+3)*math.cos(a), oy+(r+3)*math.sin(a)))),
                   fill=(160,174,187), width=3*Q)
        d.ellipse(f((ox-4,oy-4,ox+4,oy+4)), fill=(20,24,34),
                  outline=(127,163,187), width=Q)
    d.ellipse(f((136,136,164,164)), fill=(40,52,63),
              outline=(209,224,234), width=3*Q)
    d.ellipse(f((144,144,156,156)), fill=(154,28,76),
              outline=(255,170,197), width=2*Q)
    d.ellipse(f((147,147,150,150)), fill=(255,235,242))
    return im.resize((size,size), Image.Resampling.LANCZOS)


def run():
    RES.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    bg = make_background()
    bg.save(RES / "watch_bg.png", optimize=True)
    n = 30
    frames = [make_gyro_frame(i / n) for i in range(n)]
    frames[0].save(RES / "gyro_still.png", optimize=True)
    frames[0].save(RES / "gyro_anim.webp", format="WEBP", save_all=True,
                   append_images=frames[1:], duration=100, loop=0,
                   lossless=False, quality=76, method=5)
    # Preview with conspicuously example-only values; runtime WFF uses real data.
    preview = bg.convert("RGBA")
    preview.alpha_composite(frames[0], (75, 111))
    dd = ImageDraw.Draw(preview)
    def txt(x, y, value, sz, color=LIGHT, bold=True):
        dd.text((x, y), value, font=ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            sz), fill=color, anchor="mm")
    txt(225, 93, "20:59", 47)
    txt(82, 138, "78%", 22)
    txt(368, 138, "12.846", 15)
    txt(82, 317, "72", 22)
    txt(368, 317, "28.01", 17)
    preview.save(RES / "preview.png", optimize=True)
    # A large preview is useful for inspection and user-facing documentation.
    preview.resize((900,900), Image.Resampling.LANCZOS).save(
        ASSETS / "watchface-preview.png", optimize=True)
    print(f"Generated compass dial, 30-frame movement and preview: {RES}")


if __name__ == "__main__":
    run()
