#!/usr/bin/env python3
"""Draw the front page for Tuesday 24 November 2026.

Deterministic: fixed palette, fixed geometry, no randomness, no timestamps.
Writes entry.png (1024x1024) next to this file.
Run:  python3 draw.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

PAPER = (246, 241, 231)
INK = (23, 21, 18)
RED = (164, 31, 31)
BLUE = (31, 78, 121)
TEAL = (15, 118, 110)
AMBER = (180, 83, 9)
GREY = (90, 86, 78)
LIGHT = (233, 226, 212)
DARK = (28, 26, 24)
GREEN = (46, 110, 58)
SKY = (214, 230, 238)

FD = "/usr/share/fonts/truetype/dejavu"
F_SERIF = os.path.join(FD, "DejaVuSerif-Bold.ttf")
F_SERIF_R = os.path.join(FD, "DejaVuSerif.ttf")
F_SANS = os.path.join(FD, "DejaVuSans.ttf")
F_SANS_B = os.path.join(FD, "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap by pixel width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_centered(draw, cx, y, text, fnt, fill=INK, tracking=0):
    if tracking:
        # manual letter-spacing
        widths = [draw.textlength(ch, font=fnt) for ch in text]
        total = sum(widths) + tracking * (len(text) - 1)
        x = cx - total / 2
        for ch, w in zip(text, widths):
            draw.text((x, y), ch, font=fnt, fill=fill)
            x += w + tracking
        return total
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w


def rule(draw, x0, x1, y, w=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=w)


def kicker(draw, x, y, text, fill=RED):
    f = font(F_SANS_B, 15)
    draw.text((x, y), text, font=f, fill=fill)


def headline(draw, x, y, text, size, max_w, fill=INK, leading=None):
    f = font(F_SERIF, size)
    lines = wrap(draw, text, f, max_w)
    lh = leading or int(size * 1.12)
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


def body(draw, x, y, text, size, max_w, fill=INK):
    f = font(F_SANS, size)
    lh = int(size * 1.35)
    for ln in wrap(draw, text, f, max_w):
        draw.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


# ---------------------------------------------------------------- illustrations
def ill_chip(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 64, 44))
    cx, cy = x + w // 2, y + h // 2
    # circuit traces
    for i, (tx, ty) in enumerate([(x + 18, y + 16), (x + w - 18, y + 20),
                                 (x + 20, y + h - 18), (x + w - 22, y + h - 22)]):
        d.line([(tx, ty), (cx, cy)], fill=(120, 190, 150), width=2)
        d.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], outline=(120, 190, 150), width=2)
    # pins
    for i in range(6):
        px = x + 24 + i * ((w - 48) // 5)
        d.rectangle([px - 3, y - 8, px + 3, y], fill=(201, 162, 39))
        d.rectangle([px - 3, y + h, px + 3, y + h + 8], fill=(201, 162, 39))
    # die
    d.rectangle([cx - 52, cy - 42, cx + 52, cy + 42], fill=(10, 38, 26),
                outline=(201, 162, 39), width=3)
    d.text((cx, cy), "AI", font=font(F_SANS_B, 34), fill=(240, 235, 220),
           anchor="mm")
    d.text((cx, cy + 26), "CHIP", font=font(F_SANS_B, 13), fill=(201, 162, 39),
           anchor="mm")


def ill_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 200, 158))
    # cracked ground
    d.polygon([(x, y + h), (x, y + h * 0.55), (x + w * 0.3, y + h * 0.62),
               (x + w * 0.55, y + h * 0.5), (x + w * 0.8, y + h * 0.62),
               (x + w, y + h * 0.55), (x + w, y + h)], fill=(196, 164, 110))
    for (x0, y0, x1, y1) in [(0.12, 0.58, 0.3, 0.78), (0.3, 0.78, 0.24, 0.95),
                             (0.55, 0.52, 0.68, 0.72), (0.68, 0.72, 0.8, 0.9),
                             (0.8, 0.62, 0.92, 0.8)]:
        d.line([(x + w * x0, y + h * y0), (x + w * x1, y + h * y1)],
               fill=(120, 88, 52), width=3)
    # toxic cloud
    for (cx, cy, r, col) in [(0.3, 0.3, 26, (110, 125, 110)),
                             (0.5, 0.22, 32, (96, 112, 96)),
                             (0.68, 0.32, 24, (110, 125, 110)),
                             (0.42, 0.36, 20, (130, 140, 120))]:
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                   y + h * cy + r], fill=col)
    # dead tree
    bx, by = x + w * 0.82, y + h * 0.92
    d.line([(bx, by), (bx, by - 42)], fill=(74, 52, 32), width=4)
    d.line([(bx, by - 42), (bx - 18, by - 62)], fill=(74, 52, 32), width=3)
    d.line([(bx, by - 42), (bx + 16, by - 66)], fill=(74, 52, 32), width=3)


def ill_flags(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.ellipse([x + w * 0.78, y + 8, x + w * 0.98, y + 28], fill=(250, 244, 220))
    # ground
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(120, 160, 110))
    # Kenya flag (left pole)
    kx, ky = x + 26, y + 22
    d.line([(kx, ky), (kx, y + h - 18)], fill=INK, width=4)
    for i, col in enumerate([(0, 0, 0), (178, 34, 34), (0, 110, 60)]):
        d.rectangle([kx + 4, ky + i * 16, kx + 118, ky + (i + 1) * 16], fill=col)
    d.ellipse([kx + 52, ky + 12, kx + 70, ky + 36], fill=(255, 255, 255),
              outline=RED, width=2)
    # DRC flag (right pole)
    dx, dy = x + w - 26, y + 22
    d.line([(dx, dy), (dx, y + h - 18)], fill=INK, width=4)
    d.rectangle([dx - 118, dy, dx - 4, dy + 48], fill=(0, 91, 172))
    d.polygon([(dx - 118, dy), (dx - 4, dy + 48), (dx - 4, dy + 30),
               (dx - 100, dy)], fill=(206, 32, 40))
    d.polygon([(dx - 100, dy + 8), (dx - 96, dy + 18), (dx - 86, dy + 18),
               (dx - 94, dy + 26), (dx - 91, dy + 36), (dx - 100, dy + 30),
               (dx - 109, dy + 36), (dx - 106, dy + 26), (dx - 114, dy + 18),
               (dx - 104, dy + 18)], fill=(247, 214, 24))


def ill_drone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 34, 48))
    # stars
    for (sx, sy) in [(0.1, 0.15), (0.85, 0.1), (0.7, 0.22), (0.2, 0.3)]:
        d.ellipse([x + w * sx - 2, y + h * sy - 2, x + w * sx + 2,
                   y + h * sy + 2], fill=(240, 240, 220))
    # skyline
    base = y + h - 14
    for (bx, bw, bh) in [(0.02, 0.16, 0.3), (0.2, 0.12, 0.42), (0.34, 0.18, 0.26),
                         (0.54, 0.12, 0.38), (0.68, 0.14, 0.3), (0.84, 0.14, 0.45)]:
        d.rectangle([x + w * bx, base - h * bh, x + w * (bx + bw), base],
                    fill=(52, 58, 78))
        for wy in range(3):
            d.rectangle([x + w * (bx + 0.03), base - h * bh + 8 + wy * 12,
                         x + w * (bx + 0.07), base - h * bh + 16 + wy * 12],
                        fill=(250, 210, 90))
    # drone
    cx, cy = x + w // 2, y + h * 0.34
    d.ellipse([cx - 26, cy - 12, cx + 26, cy + 12], fill=(200, 205, 215),
              outline=INK, width=2)
    d.ellipse([cx - 8, cy - 6, cx + 8, cy + 6], fill=RED)
    for (ox, oy) in [(-38, -22), (38, -22), (-38, 22), (38, 22)]:
        d.line([(cx, cy), (cx + ox, cy + oy)], fill=(200, 205, 215), width=3)
        d.line([(cx + ox - 16, cy + oy), (cx + ox + 16, cy + oy)],
               fill=(240, 240, 220), width=3)
        d.ellipse([cx + ox - 5, cy + oy - 5, cx + ox + 5, cy + oy + 5],
                  fill=(120, 125, 140))
    # explosion star below
    ex, ey = x + w * 0.82, base - h * 0.5
    for ang in range(0, 360, 45):
        import math
        r1, r2 = 16, 7
        a1 = math.radians(ang)
        a2 = math.radians(ang + 22)
        d.polygon([(ex + r1 * math.cos(a1), ey + r1 * math.sin(a1)),
                   (ex + r2 * math.cos(a2), ey + r2 * math.sin(a2)),
                   (ex + r1 * math.cos(math.radians(ang + 45)),
                    ey + r1 * math.sin(math.radians(ang + 45)))],
                  fill=(250, 180, 40))


def ill_mercury(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(12, 12, 22))
    for (sx, sy) in [(0.08, 0.2), (0.9, 0.15), (0.75, 0.08), (0.15, 0.08),
                     (0.55, 0.3), (0.95, 0.45)]:
        d.ellipse([x + w * sx - 2, y + h * sy - 2, x + w * sx + 2,
                   y + h * sy + 2], fill=(240, 240, 220))
    # orbit ellipse
    d.ellipse([x + 8, y - h * 0.28, x + w - 8, y + h * 1.05],
              outline=(120, 130, 160), width=2)
    # Mercury
    cx, cy, r = x + w * 0.42, y + h * 0.58, 46
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(176, 132, 96))
    for (ccx, ccy, cr) in [(0.32, 0.48, 9), (0.5, 0.66, 12), (0.58, 0.42, 7),
                           (0.36, 0.68, 6), (0.52, 0.52, 5)]:
        d.ellipse([x + w * ccx - cr, y + h * ccy - cr, x + w * ccx + cr,
                   y + h * ccy + cr], fill=(140, 100, 70))
    # probe on orbit
    px, py = x + w * 0.78, y + h * 0.24
    d.rectangle([px - 22, py - 4, px - 6, py + 4], fill=(90, 140, 200))
    d.rectangle([px + 6, py - 4, px + 22, py + 4], fill=(90, 140, 200))
    d.rectangle([px - 6, py - 7, px + 6, py + 7], fill=(220, 225, 235),
                outline=INK, width=1)
    d.line([(px, py + 7), (px, py + 16)], fill=(240, 240, 220), width=2)
    d.ellipse([px - 3, py + 16, px + 3, py + 22], fill=(250, 180, 40))


def ill_fire(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 26, 44))
    # moon
    d.ellipse([x + w * 0.8, y + 10, x + w * 0.8 + 22, y + 32],
              fill=(240, 236, 210))
    # houses
    base = y + h - 10
    for (hx, hw, hh) in [(0.04, 0.24, 0.42), (0.3, 0.26, 0.55),
                         (0.58, 0.22, 0.46), (0.82, 0.16, 0.36)]:
        d.rectangle([x + w * hx, base - h * hh, x + w * (hx + hw), base],
                    fill=(48, 52, 74))
        d.polygon([(x + w * hx - 4, base - h * hh),
                   (x + w * (hx + hw / 2), base - h * hh - 16),
                   (x + w * (hx + hw) + 4, base - h * hh)], fill=(34, 38, 58))
        d.rectangle([x + w * (hx + 0.08), base - h * hh + 14,
                     x + w * (hx + 0.16), base - h * hh + 26],
                    fill=(250, 200, 90))
    # flames
    for (fx, fy, fs) in [(0.16, 0.42, 1.0), (0.42, 0.3, 1.25), (0.68, 0.46, 0.9)]:
        cx, cy = x + w * fx, base - h * fy
        s = 22 * fs
        d.polygon([(cx - s * 0.55, cy + s * 0.6), (cx - s * 0.35, cy - s * 0.4),
                   (cx, cy - s), (cx + s * 0.4, cy - s * 0.35),
                   (cx + s * 0.55, cy + s * 0.6)], fill=(230, 90, 20))
        d.polygon([(cx - s * 0.3, cy + s * 0.55), (cx - s * 0.18, cy - s * 0.2),
                   (cx, cy - s * 0.55), (cx + s * 0.2, cy - s * 0.15),
                   (cx + s * 0.3, cy + s * 0.55)], fill=(250, 180, 40))


# ---------------------------------------------------------------- page
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 26  # margin
    X1 = W - M

    # ---- masthead
    d.text((W // 2, 26), "THE WORLD IN ONE DAY", font=font(F_SERIF, 56),
           fill=INK, anchor="ma")
    draw_centered(d, W // 2, 96, "TUESDAY, 24 NOVEMBER 2026",
                  font(F_SANS_B, 19), fill=RED, tracking=6)
    rule(d, M, X1, 126, 4)
    rule(d, M, X1, 132, 1)

    # ---- lead story: Nvidia
    ly0, ly1 = 144, 392
    d.rectangle([M, ly0, X1, ly1], outline=INK, width=2)
    d.rectangle([M, ly0, X1, ly0 + 2], fill=INK)
    ill_chip(d, M + 14, ly0 + 16, 300, 216)
    tx = M + 336
    kicker(d, tx, ly0 + 18, "TECHNOLOGY  •  UNITED STATES")
    y = headline(d, tx, ly0 + 44, "THE CHIP KING RETURNS", 40, X1 - tx - 14)
    body(d, tx, y + 6,
         "Nvidia's board voted unanimously on Monday to reinstate Jensen "
         "Huang as chief executive — days after ruling it out — following "
         "direct pressure from President Donald Trump, who told CNBC his "
         "intervention was \u201cvery important\u201d. Shares soared 33%.",
         16, X1 - tx - 14)
    d.text((tx, ly1 - 52), "Huang resigned on 12 November after reports of an affair with an "
           "alleged Chinese spy;", font=font(F_SANS, 13), fill=GREY)
    d.text((tx, ly1 - 30), "the board now says his return poses no "
           "national-security risk.", font=font(F_SANS, 13), fill=GREY)

    # ---- grid of five stories + numbers panel
    gx, gy = M, 406
    cw, ch, gap = 312, 252, 16
    cells = [
        ("GAZA  •  ENVIRONMENT", "A TOXIC WASTELAND",
         "Oxfam: more than 99% of Gaza shows signs of toxic contamination "
         "— air, soil and water unsafe for decades.",
         ill_gaza),
        ("AFRICA  •  DIPLOMACY", "THREE YEARS ON ICE, OVER",
         "Kenya and DR Congo agree to restore full diplomatic ties at a "
         "summit in Oyo, ending a freeze since Dec 2023.",
         ill_flags),
        ("COLOMBIA  •  CONFLICT", "DRONES OVER CÚCUTA",
         "Explosive drones strike a police base in Cúcuta: three civilians "
         "hurt, including a baby, and 60 homes damaged.",
         ill_drone),
        ("SPACE  •  SCIENCE", "EIGHT YEARS TO MERCURY",
         "BepiColombo enters orbit around Mercury after eight years in "
         "space; a thruster glitch cut the burn short, but the craft is safe.",
         ill_mercury),
        ("WEST BANK  •  ISRAEL", "\u201cJEWISH TERRORISM\u201d",
         "Settlers torch vehicles in Palestinian villages near Ramallah; "
         "opposition leader Gadi Eisenkot condemns the arson in those words.",
         ill_fire),
        None,  # numbers panel
    ]
    for i, cell in enumerate(cells):
        cx = gx + (i % 3) * (cw + gap)
        cy = gy + (i // 3) * (ch + gap)
        d.rectangle([cx, cy, cx + cw, cy + ch], outline=INK, width=2)
        if cell is None:
            d.rectangle([cx, cy, cx + cw, cy + 34], fill=DARK)
            d.text((cx + 12, cy + 8), "THE DAY IN NUMBERS",
                   font=font(F_SANS_B, 15), fill=(246, 241, 231))
            nums = [("33%", "Nvidia shares jump"),
                    ("99%", "of Gaza flagged toxic"),
                    ("60", "homes damaged in Cúcuta"),
                    ("8 yrs", "BepiColombo's voyage"),
                    ("3 yrs", "Kenya–DR Congo freeze")]
            ny = cy + 46
            for val, lab in nums:
                d.text((cx + 12, ny), val, font=font(F_SANS_B, 20), fill=RED)
                d.text((cx + 92, ny + 3), lab, font=font(F_SANS, 14), fill=INK)
                ny += 40
            continue
        kick, head, txt, ill = cell
        ill(d, cx + 2, cy + 2, cw - 4, 100)
        d.line([(cx, cy + 102), (cx + cw, cy + 102)], fill=INK, width=1)
        kicker(d, cx + 12, cy + 110, kick)
        y = headline(d, cx + 12, cy + 130, head, 19, cw - 24)
        body(d, cx + 12, y + 4, txt, 13, cw - 24)

    # ---- footer ticker
    fy0, fy1 = 934, 1000
    d.rectangle([M, fy0, X1, fy1], fill=DARK)
    d.text((M + 12, fy0 + 8), "ALSO TODAY",
           font=font(F_SANS_B, 14), fill=(250, 200, 90))
    d.text((M + 118, fy0 + 8),
           "$TRUMP gala: token under $1, down ~99% from peak  •  FBI probes "
           "hack of crime database; USDA payments breached",
           font=font(F_SANS, 13), fill=(246, 241, 231))
    d.text((M + 12, fy0 + 34),
           "Sources: Reuters, AP, BBC, AFP, ESA, Oxfam, Xinhua  •  All pictures drawn "
           "by the author for this page  •  Tuesday 24 November 2026",
           font=font(F_SANS, 12), fill=(170, 165, 155))

    img.save(OUT, format="PNG")
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
